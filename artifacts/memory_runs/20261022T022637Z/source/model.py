"""Bounded LangChain invocations; native content-bearing traces suppressed; explicit metadata-only spans used."""
import asyncio
import httpx
from openai import APIConnectionError, APIStatusError, APITimeoutError
from langsmith import tracing_context
from capstone_agent.model_client import ModelError

MODEL_ERROR_CATEGORIES=frozenset({'model_budget_exhausted','model_output_truncated',
    'invalid_provider_response','model_timeout','provider_timeout','provider_connection_error',
    'model_internal_error','model_unavailable'})

def model_error_code(stage,exc):
    """Serialize only closed categories, never provider messages or payloads."""
    category=exc.category if isinstance(exc,ModelError) else 'model_internal_error'
    if category not in MODEL_ERROR_CATEGORIES and not (
        category.startswith('http_') and len(category)==8 and category[5:].isdigit()
        and 400<=int(category[5:])<=599):
        category='model_internal_error'
    return stage+'_'+category

class Gateway:
    def __init__(self,chat,*,timeout=25):
        self.chat,self.timeout=chat,timeout
        self.calls=0; self.tokens=0
    async def invoke(self,messages,*,tools=None,schema=None):
        from capstone_agent.observability.support_tracing import span,numbers
        with span('model','llm') as output:
            try:
                result=await self._invoke(messages,tools=tools,schema=schema)
            except ModelError as exc:
                output['error_category']=model_error_code('MODEL',exc)
                output['retryable']=exc.retryable
                if getattr(exc,'status_code',None) is not None:output['http_status']=exc.status_code
                raise
            output.update(numbers(result.usage_metadata or {}))
            return result

    async def _invoke(self,messages,*,tools=None,schema=None):
        if self.calls>=12: raise ModelError('model_budget_exhausted')
        self.calls+=1
        options={}
        if schema:
            options['response_format']={'type':'json_object'}
        def invoke():
            with tracing_context(enabled=False):
                return model.invoke(messages,config={'callbacks':[]},**options)
        try:
            model=self.chat.bind_tools(tools,parallel_tool_calls=False) if tools else self.chat
            result=await asyncio.wait_for(asyncio.to_thread(invoke),self.timeout)
            if result.usage_metadata: self.tokens+=result.usage_metadata.get('total_tokens',0)
            if result.response_metadata.get('finish_reason')=='length': raise ModelError('model_output_truncated')
            if not isinstance(result.content,str) or len(result.content)>50000:
                raise ModelError('invalid_provider_response')
            return result
        except ModelError: raise
        except APIStatusError as exc:
            status=exc.status_code
            error=ModelError(f'http_{status}',status in {408,429,500,502,503,504})
            error.status_code=status
            raise error from None
        except (APITimeoutError,httpx.TimeoutException):raise ModelError('provider_timeout',True) from None
        except (APIConnectionError,httpx.TransportError):raise ModelError('provider_connection_error',True) from None
        except TimeoutError:raise ModelError('model_timeout',True) from None
        except (ValueError,KeyError,TypeError,AttributeError):raise ModelError('invalid_provider_response') from None
        except Exception:raise ModelError('model_internal_error') from None

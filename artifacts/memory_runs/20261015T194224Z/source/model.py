"""Bounded LangChain invocations; native traces suppressed pending masked Phase 8 tracing."""
import asyncio
from langsmith import tracing_context
from capstone_agent.model_client import ModelError

class Gateway:
    def __init__(self,chat,*,timeout=25):
        self.chat,self.timeout=chat,timeout
        self.calls=0; self.tokens=0
    async def invoke(self,messages,*,tools=None,schema=None):
        if self.calls>=12: raise ModelError('model_budget_exhausted')
        self.calls+=1
        model=self.chat.bind_tools(tools,parallel_tool_calls=False) if tools else self.chat
        options={}
        if schema:
            options['response_format']={'type':'json_object'}
        def invoke():
            with tracing_context(enabled=False):
                return model.invoke(messages,config={'callbacks':[]},**options)
        try:
            result=await asyncio.wait_for(asyncio.to_thread(invoke),self.timeout)
            if result.usage_metadata: self.tokens+=result.usage_metadata.get('total_tokens',0)
            if result.response_metadata.get('finish_reason')=='length': raise ModelError('model_output_truncated')
            if not isinstance(result.content,str) or len(result.content)>50000:
                raise ModelError('invalid_provider_response')
            return result
        except ModelError: raise
        except Exception: raise ModelError('model_unavailable') from None

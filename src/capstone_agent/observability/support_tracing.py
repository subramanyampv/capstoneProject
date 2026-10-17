"""Content-free support spans, collected locally and exported off the request path."""
import contextvars
import json
import math
import queue
import threading
import uuid
from contextlib import contextmanager
from datetime import datetime,timezone
from pathlib import Path
from langsmith import Client
from urllib3.util.retry import Retry

CURRENT=contextvars.ContextVar('support_trace',default=None)
PARENT=contextvars.ContextVar('support_parent',default=None)
NODES=frozenset({'guard_in','plan','dispatch','order_shipping','policy_product','escalation','replan','compose','refuse','unsupported_command','missing_reference','withdrawal','command_handler'})
TOOLS=frozenset({'lookup_order','get_tracking_events','search_policy','get_product_details','check_return_eligibility','create_escalation'})
COUNTERS=frozenset({'model_calls','tool_calls','handoffs','replans','repairs','tokens','latency_ms','input_tokens','output_tokens','total_tokens','style_version','word_count'})
OUTCOMES=frozenset({'ANSWERED','CLARIFICATION_REQUESTED','INSUFFICIENT_EVIDENCE','REFUSED','ESCALATED','ESCALATION_FAILED_DISCLOSED','TOOL_ERROR_DISCLOSED','BUDGET_EXHAUSTED_ESCALATED','COMMAND_HANDLED'})

def numbers(values):
    return {k:v for k,v in values.items() if k in COUNTERS and type(v) in {int,float} and math.isfinite(v) and v>=0}

class SupportTrace:
    def __init__(self,request_id):self.id=request_id;self.spans=[];self.lock=threading.Lock()
    @contextmanager
    def span(self,name,kind='chain'):
        name=name if name in NODES|TOOLS|{'support_request','model'} else 'unknown_tool'
        parent=PARENT.get();now=datetime.now(timezone.utc)
        ident=uuid.UUID(self.id) if parent is None else uuid.uuid4()
        dotted=(parent['dotted_order']+'.' if parent else '')+now.strftime('%Y%m%dT%H%M%S%fZ')+str(ident)
        row={'id':str(ident),'trace_id':str(uuid.UUID(self.id)),'parent_run_id':parent['id'] if parent else None,
            'name':name,'run_type':kind,'start_time':now.isoformat(),'dotted_order':dotted,'outputs':{}}
        token=PARENT.set(row)
        try:yield row['outputs']
        except BaseException:
            row['outputs']['failed']=True
            raise
        finally:
            row['end_time']=datetime.now(timezone.utc).isoformat();PARENT.reset(token)
            with self.lock:
                if len(self.spans)<100:self.spans.append(row)

@contextmanager
def span(name,kind='chain'):
    trace=CURRENT.get()
    if trace:
        with trace.span(name,kind) as output:yield output
    else:yield {}

def observed_node(name,function):
    import inspect
    async def run(state):
        with span(name) as output:
            result=function(state)
            if inspect.isawaitable(result):result=await result
            if result.get('outcome') in OUTCOMES:output['outcome']=result['outcome']
            return result
    return run

class TraceExporter:
    """Bounded daemon queue; credentials/client and SDK failures never enter request output."""
    def __init__(self,client_factory=None):
        self.factory=client_factory or self._client
        self.queue=queue.Queue(maxsize=32)
        self.worker=threading.Thread(target=self._work,daemon=True,name='support-trace-export');self.worker.start()
    @staticmethod
    def _client(config):
        import logging
        # SDK diagnostics can include credential fragments; receipts replace them.
        logging.getLogger('langsmith.client').disabled=True
        return Client(api_url=config.endpoint,api_key=config.api_key,auto_batch_tracing=False,
            hide_inputs=True,hide_outputs=lambda output:output,hide_metadata=True,
            omit_traced_runtime_info=True,timeout_ms=(1000,2000),retry_config=Retry(total=0))
    def submit(self,config,spans,root):
        if not config.enabled:return 'disabled'
        try:self.queue.put_nowait((config,spans,Path(root)));return 'queued'
        except queue.Full:return 'queue_full'
    def _work(self):
        while True:
            config,spans,root=self.queue.get();status='exported';client=None;category=None
            try:
                client=self.factory(config)
                for row in sorted(spans,key=lambda r:r['dotted_order']):
                    fields={k:v for k,v in row.items() if k not in {'name','run_type'}}
                    client.create_run(row['name'],{},row['run_type'],project_name=config.project,**fields)
            except Exception as exc:
                status='failed'
                import re
                category=('authentication' if type(exc).__name__=='LangSmithAuthError' else
                    'access_denied' if type(exc).__name__=='LangSmithError' and re.search(r'\b403\b',str(exc)) else 'transport_or_service')
            finally:
                if client:
                    try:client.close()
                    except Exception:pass
                try:
                    path=root/'data/runtime/trace_exports.jsonl';path.parent.mkdir(parents=True,exist_ok=True)
                    with path.open('a') as stream:stream.write(json.dumps({'trace_id':spans[0]['trace_id'] if spans else None,
                        'status':status,'error_category':category,'span_count':len(spans)})+'\n')
                except OSError:pass
                self.queue.task_done()
    def wait(self,timeout=10):
        import time
        deadline=time.monotonic()+timeout
        while self.queue.unfinished_tasks and time.monotonic()<deadline:threading.Event().wait(.02)
        return not self.queue.unfinished_tasks

EXPORTER=TraceExporter()

ERROR_CODES=frozenset({'BUDGET_EXCEEDED','UNKNOWN_TOOL','PERMISSION_DENIED','INVALID_ARGUMENT','UNEXPECTED_ORDER',
    'TIMEOUT','FAILED','NOT_FOUND','AMBIGUOUS','UNVERIFIED_CATEGORY','INDEX_UNAVAILABLE','MISSING_DATA','RETRIEVAL_FAILED',
    'PII_REJECTED','UNRESOLVED_EVIDENCE','UNVERIFIED_TRIGGER','TOO_MANY_CONFLICTING_SOURCES','SUPERVISOR_FAILED',
    'REPLAN_FAILED','COMPOSER_FAILED','SPECIALIST_FAILED','SPECIALIST_STEP_LIMIT','WRONG_AGENT_RESULT',
    'INVALID_TOOL_CALL','INJECTED_MODEL_FAILURE','UNRESOLVED_AGENT_EVIDENCE','G1_TICKET_MISSING','G1_FAILURE_DISCLOSURE',
    'G2_REFUSAL','G3_UNSUPPORTED_NUMBER','G4_UNRESOLVED_CITATION','G4_POLICY_NOT_RETRIEVED','G4_POLICY_CITATION_REQUIRED',
    'G4_EVIDENCE_REQUIRED','G4_CONFLICT_CITATIONS','G5_INTENT_COVERAGE','FALSE_TRANSACTION_CLAIM','FALSE_TICKET_CLAIM',
    'SPECIALIST_model_unavailable','SPECIALIST_model_output_truncated','SPECIALIST_model_budget_exhausted'})
def safe_error(value):
    if value is None:return None
    if value in ERROR_CODES:return value
    if isinstance(value,str) and value.startswith('SPECIALIST_SCHEMA:'):return 'SPECIALIST_SCHEMA'
    return 'OTHER_ERROR'

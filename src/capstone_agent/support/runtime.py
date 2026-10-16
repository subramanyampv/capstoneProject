"""Local initial-product invocation and minimal operational records."""
import asyncio
import json
import uuid
from pathlib import Path
from capstone_agent.config import LLMConfig,load_environment
from capstone_agent.langchain_client import LangChainChatClient
from capstone_agent.support.graph import SupportAgent
from capstone_agent.support.model import Gateway
from capstone_agent.support.privacy import minimize,opaque
from capstone_agent.support.registry import SessionIdentity
from capstone_agent.support.services import Services,ROOT
from capstone_agent.support.memory import SessionMemory,command_result
from capstone_agent.support.preferences import PreferenceStore,StyleProfile,is_preference_command,implicit_signal
from capstone_agent.support.guards import SafetyRules

MEMORY=SessionMemory(background=True)

def safe_record(result,identity,secrets=()):
    from capstone_agent.observability.support_tracing import safe_error
    # Deliberately omit request, tool payloads, specialist prose and intermediate state.
    return {'request_ref':uuid.uuid4().hex,'session_ref':opaque(identity.session_id),
        'customer_ref':opaque(identity.customer_id),'outcome':result['outcome'],'stages':result['stages'],
        'triggers':result['triggers'],'refusals':result['refusals'],'errors':[safe_error(value) for value in result['errors']],
        'tools':[{**{k:r[k] for k in ['exec_id','name','status','duration_ms']},'error':safe_error(r['error'])} for r in result['tool_records']],
        'model_calls':result['model_calls'],'tool_calls':result['tool_calls'],'handoffs':result['handoffs'],
        'replans':result['replans'],'repairs':result['repairs'],'tokens':result['tokens'],
        'latency_ms':result['latency_ms'],'safety_version':result['safety_version'],
        'ticket_id':result['ticket'].get('ticket_id') if result['ticket'] else None,
        'style':result.get('style',{}),
        'memory':{k:v for k,v in result.get('memory',{}).items() if k in {'enabled','history_messages','resolved_reference','expired','reset'}}}

def _run_support(query,customer_id='C-100',*,search=None,identity=None,faults=None,root=ROOT,memory=None,memory_enabled=None,preferences=None,_request_id=None):
    identity=identity or SessionIdentity(customer_id)
    manager=memory or MEMORY
    secrets=()
    preferences=preferences or PreferenceStore(root)
    request_id=_request_id or uuid.uuid4().hex
    if is_preference_command(query):
        if identity.customer_id not in Services(root=root).customers():raise ValueError('UNKNOWN_SYNTHETIC_CUSTOMER')
        command=query.strip()
        if command=='/forget-preferences':
            preferences.forget(identity.customer_id)
            answer='Saved style preferences and feedback deleted. Automatic style learning is off.'
            profile=StyleProfile()
        else:
            parts=command.split()
            if len(parts)!=2:raise ValueError('Use /feedback with too_long, too_short, unclear, helpful, not_helpful, enable, disable or reset_style.')
            profile=preferences.apply(identity.customer_id,parts[1],request_id=request_id)
            answer={'enable':'Style learning enabled for this synthetic customer.',
                'disable':'Style learning disabled. Default style will be used; /forget-preferences deletes saved data.',
                'reset_style':'Style reset to standard prose. Session memory is unchanged.'}.get(parts[1],
                'Feedback saved. Two matching signals in the recent ten can change response style. Sending feedback enables style learning.')
        result=command_result(memory_enabled is not False)
        result['response'].update(answer=answer,intents_addressed=['feedback_style'])
        result['memory']['reset']=False
        result['stages']=['command_handler','style_preferences']
        result['style']=profile.as_dict()
    elif isinstance(query,str) and query.strip()=='/reset':
        # Deletion must remain available even if the provider/config/index is down.
        result=manager.process(query,identity,lambda *_:None,enabled=memory_enabled is not False)
    else:
        config=LLMConfig.from_env(root/'.env')
        values=load_environment(root/'.env')
        secrets=tuple({config.api_key,*[value for name,value in values.items() if name.endswith('API_KEY') and value]})
        services=Services(root=root,search=search)
        if identity.customer_id not in services.customers():raise ValueError('UNKNOWN_SYNTHETIC_CUSTOMER')
        if memory_enabled is None:
            flag=load_environment(root/'.env').get('MEMORY_ENABLED','true').lower().strip()
            if flag not in {'true','false'}:raise ValueError('INVALID_MEMORY_ENABLED')
            memory_enabled=flag=='true'
        def execute(message,context):
            profile=StyleProfile()
            try:
                refusals,triggers,_=SafetyRules().match(message)
                if not refusals and not triggers and preferences.consented(identity.customer_id):
                    from capstone_agent.support.privacy import mask_sensitive
                    signal=implicit_signal(mask_sensitive(message,secrets),context,embeddings=getattr(search,'embeddings',None))
                    if signal:preferences.apply(identity.customer_id,signal,kind='implicit',request_id=request_id)
                profile=preferences.profile(identity.customer_id)
            except (OSError,ValueError,KeyError,TypeError):
                # Preference storage is optional; its failure must not interrupt safety handling.
                pass
            with LangChainChatClient(config) as client:
                agent=SupportAgent(services,Gateway(client.chat,timeout=config.timeout_seconds+1),secrets=secrets)
                return asyncio.run(agent.run(message,identity,faults=faults,memory_context=context,style=profile))
        result=manager.process(query,identity,execute,enabled=memory_enabled,secrets=secrets)
    result["request_id"]=request_id
    return result


def run_support(query,customer_id='C-100',*,search=None,identity=None,faults=None,root=ROOT,memory=None,memory_enabled=None,preferences=None):
    from capstone_agent.observability.langsmith_tracing import ObservabilityConfig
    from capstone_agent.observability.support_tracing import SupportTrace,CURRENT,EXPORTER,numbers,OUTCOMES,TOOLS
    identity=identity or SessionIdentity(customer_id)
    request_id=uuid.uuid4().hex;trace=SupportTrace(request_id)
    token=CURRENT.set(trace)
    try:
        with trace.span('support_request') as output:
            result=_run_support(query,identity=identity,search=search,faults=faults,root=root,memory=memory,
                memory_enabled=memory_enabled,preferences=preferences,_request_id=request_id)
            result['request_id']=request_id
            output.update(numbers(result))
            if result['outcome'] in OUTCOMES:output['outcome']=result['outcome']
            output['style_version']=result.get('style',{}).get('version',0)
    except Exception:
        # Never serialize input or exception messages (which may contain endpoint credentials).
        path=root/'data/runtime/requests.jsonl'
        try:
            path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('a') as stream:stream.write(json.dumps({'request_ref':request_id,
                'customer_ref':opaque(identity.customer_id),'session_ref':opaque(identity.session_id),
                'outcome':'REQUEST_REJECTED','errors':['REQUEST_FAILED'],'spans':trace.spans})+'\n')
        except OSError:pass
        raise
    finally:CURRENT.reset(token)
    # An invalid or unavailable optional tracing configuration cannot alter a support outcome.
    try:
        config=ObservabilityConfig.from_env(root/'.env')
        status=EXPORTER.submit(config,list(trace.spans),root)
    except Exception:status='configuration_error'
    result['tracing']={'trace_id':str(uuid.UUID(request_id)),'status':status,'span_count':len(trace.spans)}
    record=safe_record(result,identity)
    record['request_ref']=request_id
    record['tools']=[{**row,'name':row['name'] if row['name'] in TOOLS else 'unknown_tool'} for row in record['tools']]
    record['trace']=result['tracing'];record['spans']=trace.spans
    record['order_refs']=sorted({opaque(ref['source_id'].split(':',1)[1]) for tool in result['tool_records']
        for ref in tool.get('evidence_refs',[]) if ref['source_id'].startswith(('order:','tracking:'))})
    path=root/'data/runtime/requests.jsonl'
    try:
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('a') as stream:stream.write(json.dumps(record)+'\n')
    except OSError:result['operational_errors']=['LOCAL_LOG_UNAVAILABLE']
    return result

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
from capstone_agent.support.memory import SessionMemory

MEMORY=SessionMemory(background=True)

def safe_record(result,identity,secrets=()):
    # Deliberately omit request, tool payloads, specialist prose and intermediate state.
    return {'request_ref':uuid.uuid4().hex,'session_ref':opaque(identity.session_id),
        'customer_ref':opaque(identity.customer_id),'outcome':result['outcome'],'stages':result['stages'],
        'triggers':result['triggers'],'refusals':result['refusals'],'errors':result['errors'],
        'tools':[{k:r[k] for k in ['exec_id','name','status','error','duration_ms']} for r in result['tool_records']],
        'model_calls':result['model_calls'],'tool_calls':result['tool_calls'],'handoffs':result['handoffs'],
        'replans':result['replans'],'repairs':result['repairs'],'tokens':result['tokens'],
        'latency_ms':result['latency_ms'],'safety_version':result['safety_version'],
        'ticket_id':result['ticket'].get('ticket_id') if result['ticket'] else None,
        'memory':{k:v for k,v in result.get('memory',{}).items() if k in {'enabled','history_messages','resolved_reference','expired','reset'}}}

def run_support(query,customer_id='C-100',*,search=None,identity=None,faults=None,root=ROOT,memory=None,memory_enabled=None):
    identity=identity or SessionIdentity(customer_id)
    manager=memory or MEMORY
    secrets=()
    if isinstance(query,str) and query.strip()=='/reset':
        # Deletion must remain available even if the provider/config/index is down.
        result=manager.process(query,identity,lambda *_:None,enabled=memory_enabled is not False)
    else:
        config=LLMConfig.from_env(root/'.env');secrets=(config.api_key,)
        services=Services(root=root,search=search)
        if identity.customer_id not in services.customers():raise ValueError('UNKNOWN_SYNTHETIC_CUSTOMER')
        if memory_enabled is None:
            flag=load_environment(root/'.env').get('MEMORY_ENABLED','true').lower().strip()
            if flag not in {'true','false'}:raise ValueError('INVALID_MEMORY_ENABLED')
            memory_enabled=flag=='true'
        def execute(message,context):
            with LangChainChatClient(config) as client:
                agent=SupportAgent(services,Gateway(client.chat,timeout=config.timeout_seconds+1),secrets=secrets)
                return asyncio.run(agent.run(message,identity,faults=faults,memory_context=context))
        result=manager.process(query,identity,execute,enabled=memory_enabled,secrets=secrets)
    record=safe_record(result,identity,secrets)
    path=root/'data/runtime/requests.jsonl'
    try:
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('a') as stream:stream.write(json.dumps(record)+'\n')
    except OSError:result['operational_errors']=['LOCAL_LOG_UNAVAILABLE']
    return result

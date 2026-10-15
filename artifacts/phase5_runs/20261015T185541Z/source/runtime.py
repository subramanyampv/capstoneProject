"""Local initial-product invocation and minimal operational records."""
import asyncio
import json
import uuid
from pathlib import Path
from capstone_agent.config import LLMConfig
from capstone_agent.langchain_client import LangChainChatClient
from capstone_agent.support.graph import SupportAgent
from capstone_agent.support.model import Gateway
from capstone_agent.support.privacy import minimize,opaque
from capstone_agent.support.registry import SessionIdentity
from capstone_agent.support.services import Services,ROOT

def safe_record(result,identity,secrets=()):
    # Deliberately omit request, tool payloads, specialist prose and intermediate state.
    return {'request_ref':uuid.uuid4().hex,'session_ref':opaque(identity.session_id),
        'customer_ref':opaque(identity.customer_id),'outcome':result['outcome'],'stages':result['stages'],
        'triggers':result['triggers'],'refusals':result['refusals'],'errors':result['errors'],
        'tools':[{k:r[k] for k in ['exec_id','name','status','error','duration_ms']} for r in result['tool_records']],
        'model_calls':result['model_calls'],'tool_calls':result['tool_calls'],'handoffs':result['handoffs'],
        'replans':result['replans'],'repairs':result['repairs'],'tokens':result['tokens'],
        'latency_ms':result['latency_ms'],'safety_version':result['safety_version'],
        'ticket_id':result['ticket'].get('ticket_id') if result['ticket'] else None}

def run_support(query,customer_id='C-100',*,search=None,identity=None,faults=None,root=ROOT):
    config=LLMConfig.from_env(root/'.env')
    identity=identity or SessionIdentity(customer_id)
    services=Services(root=root,search=search)
    with LangChainChatClient(config) as client:
        agent=SupportAgent(services,Gateway(client.chat,timeout=config.timeout_seconds+1),secrets=(config.api_key,))
        result=asyncio.run(agent.run(query,identity,faults=faults))
    record=safe_record(result,identity,(config.api_key,))
    path=root/'data/runtime/requests.jsonl'
    try:
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('a') as stream: stream.write(json.dumps(record)+'\n')
    except OSError:
        result['operational_errors']=['LOCAL_LOG_UNAVAILABLE']
    return result

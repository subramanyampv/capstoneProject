"""Process-local T3 ablation with identical scripted model decisions and real retrieval."""
import argparse
import asyncio
import hashlib
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from langchain_core.messages import AIMessage
from capstone_agent.evaluation.export import minimized_json
from capstone_agent.retrieval.chroma_store import PolicySearch
from capstone_agent.retrieval.embeddings_voyage import VoyageNanoEmbeddings
from capstone_agent.support.graph import SupportAgent
from capstone_agent.support.registry import Registry,SessionIdentity
from capstone_agent.support.services import Services

ROOT=Path(__file__).resolve().parents[1]

class WithoutConflictLatch(Registry):
    def remember(self,name,data,args):
        refs=super().remember(name,data,args)
        if name=='search_policy':self.ctx.triggers.discard('T3')
        return refs

class FixedDecisions:
    """No network model. Exactly the same model behavior in both arms."""
    def __init__(self):self.calls=0;self.tokens=0
    async def invoke(self,messages,schema=None,**kwargs):
        self.calls+=1
        name=schema.__name__ if schema else None
        if name=='SupervisorPlan':
            data={'intents':['return_eligibility'],'order_id':None,'sku':None,
                'steps':[{'agent':'policy_product','task':'Retrieve the conflicting electronics return-window sources.','depends_on':[]}],
                'clarification':None,'safety_risk':False,'policy_violation':False}
        elif name=='ResponseDraft':
            payload=json.loads(messages[-1].content);ticket=payload.get('ticket')
            answer='The return policy says 15 days for electronics and the FAQ says 30 days. The sources conflict; I cannot choose a rule.'
            if ticket:answer+=f" Local mock handoff {ticket['ticket_id']} was verified in the {ticket['queue']} queue. Contact retailer support for actual review."
            data={'answer':answer,'why':[],'citations':payload['allowed_citations'],'next_steps':[],
                'intents_addressed':payload['intents'],'outcome_claimed':payload['computed_outcome']}
        else:
            agent='escalation' if 'You are the escalation specialist.' in messages[0].content else 'policy_product'
            data={'agent_name':agent,'status':'success','summary':'Current-turn evidence is available.',
                'evidence':[],'facts':{},'flags':{}}
        return AIMessage(content=json.dumps(data))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    cases=json.loads((ROOT/'data/evaluation_cases.json').read_text())['cases']
    query=next(case['input'] for case in cases if case['id']=='R05')
    search=PolicySearch(VoyageNanoEmbeddings());search.search('return policy')
    rows=[]
    with tempfile.TemporaryDirectory() as local:
        for enabled in [False,True]:
            for repeat in range(3):
                services=Services(search=search);services.ticket_path=Path(local)/f'{enabled}-{repeat}.sqlite3'
                gateway=FixedDecisions()
                with patch('capstone_agent.support.graph.Registry',Registry if enabled else WithoutConflictLatch):
                    result=asyncio.run(SupportAgent(services,gateway).run(query,SessionIdentity('C-100')))
                searches=[row for row in result['tool_records'] if row['name']=='search_policy' and row['status']=='ok']
                conflict_seen=any(row['data']['conflict'] for row in searches)
                verified=result['ticket'] and result['ticket'].get('status')=='created'
                rows.append({'t3_enabled':enabled,'repeat':repeat,'conflict_seen':conflict_seen,
                    'verified_mock_ticket':bool(verified),'result':result})
    checks={'both_arms_retrieved_conflict':all(row['conflict_seen'] for row in rows),
        'disabled_arm_misses_required_handoff':all(not row['verified_mock_ticket'] and 'T3' not in row['result']['triggers'] for row in rows if not row['t3_enabled']),
        'enabled_arm_verifies_every_handoff':all(row['verified_mock_ticket'] and 'T3' in row['result']['triggers'] and row['result']['outcome']=='ESCALATED' for row in rows if row['t3_enabled'])}
    report={'passed':all(checks.values()),'checks':checks,'input_sha256':hashlib.sha256(query.encode()).hexdigest(),
        'source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['src/capstone_agent/support/graph.py','src/capstone_agent/support/registry.py']},
        'runs':rows,'limits':'Controlled component ablation only: real pinned retrieval and local mock ticket store, identical scripted model decisions, three repeats per arm. Disables only the process-local registry T3 latch, never source files or application configuration. Not an LLM-quality estimate or historical binary replay. Holdout is not read. Final live frozen/repeated evaluations remain separate.'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(minimized_json(report)+'\n')
    print(json.dumps(checks,indent=2));return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())

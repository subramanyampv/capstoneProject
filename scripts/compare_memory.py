"""Five development conversations, same current model with memory on/off; no holdout use."""
import argparse
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path
from capstone_agent.config import LLMConfig
from capstone_agent.support.memory import SessionMemory
from capstone_agent.support.registry import SessionIdentity
from capstone_agent.support.runtime import run_support
from capstone_agent.support.privacy import minimize
from capstone_agent.retrieval.configured_embeddings import ConfiguredEmbeddings
from capstone_agent.retrieval.chroma_store import PolicySearch

ROOT=Path(__file__).resolve().parents[1]
CONVERSATIONS=[
 ('tracking',['Track order O-1001.','Track that order.'],'O-1001',None),
 ('return',['Track order O-1005.','Can I return it?'],'O-1005','ineligible'),
 ('product',['What is the material of TrailRunner Shoes?','What is its care guidance?'],None,'SKU-SHOES-001'),
 ('switch',['Track O-1001.','Track O-1005.','Track my other order.'],'O-1001',None),
 ('reset',['Track O-1001.','/reset','Track that order.'],None,None),
]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--conversation',action='append',choices=[c[0] for c in CONVERSATIONS]);args=parser.parse_args()
    config=LLMConfig.from_env(ROOT/'.env')
    directory=ROOT/'artifacts/memory_runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');directory.mkdir(parents=True)
    source=directory/'source';source.mkdir();hashes={}
    for path in sorted((ROOT/'src/capstone_agent/support').glob('*.py')):
        (source/path.name).write_bytes(path.read_bytes());hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
    search=PolicySearch(ConfiguredEmbeddings());search.search('return policy')
    records=[]
    for name,queries,expected_order,expected in CONVERSATIONS:
        if args.conversation and name not in args.conversation:continue
        for enabled in [False,True]:
            memory=SessionMemory();identity=SessionIdentity('C-100');turns=[]
            for query in queries:
                result=run_support(query,identity=identity,search=search,memory=memory,memory_enabled=enabled)
                turns.append(result)
                print(name,'on' if enabled else 'off',len(turns),result['outcome'],flush=True)
            final=turns[-1]
            found=[r for r in final['tool_records'] if r['status']=='ok']
            facts=[fact for item in final['results'] for fact in item['facts'].get('tools',[])]
            reference_hit=any(fact['name'] in {'lookup_order','get_tracking_events','check_return_eligibility'} and
                              fact['args'].get('order_id')==expected_order for fact in facts) if expected_order else None
            if name=='return':reference_hit=any(f['name']=='check_return_eligibility' and f['args']['order_id']==expected_order and f['data']['decision']==expected for f in facts)
            if name=='product':reference_hit=any(r['name']=='get_product_details' and r['data']['sku']==expected for r in found)
            passed=(final['outcome']=='CLARIFICATION_REQUESTED') if name=='reset' or not enabled else bool(reference_hit and final['outcome']=='ANSWERED')
            record={'conversation':name,'memory_enabled':enabled,'expected_followup':('clarification' if name=='reset' or not enabled else 'fresh_verified_answer'),
                'passed':passed,'reference_tool_hit':reference_hit,'clarifications':sum(t['outcome']=='CLARIFICATION_REQUESTED' for t in turns),
                'turns':turns}
            safe=json.loads(minimize(json.dumps(record),(config.api_key,)))
            (directory/f"{name}_{'on' if enabled else 'off'}.json").write_text(json.dumps(safe,indent=2)+'\n');records.append(record)
            memory.close()
    groups={}
    for enabled in [False,True]:
        group=[r for r in records if r['memory_enabled']==enabled];positive=[r for r in group if r['conversation']!='reset']
        groups['on' if enabled else 'off']={'conversations':len(group),'expected_behavior_passes':sum(r['passed'] for r in group),
            'followups_answered_with_expected_tool':sum(bool(r['reference_tool_hit']) and r['turns'][-1]['outcome']=='ANSWERED' for r in positive),
            'positive_followups':len(positive),'clarifications':sum(r['clarifications'] for r in group)}
    (directory/'summary.json').write_text(json.dumps({'recorded_at':datetime.now(timezone.utc).isoformat(),'source_sha256':hashes,
        'settings':config.public_settings(),'results':groups,'limits':'Five authored development conversations, not frozen/holdout or semantic faithfulness. Reset remains a clarification in both modes. Public-index startup excluded.'},indent=2)+'\n')
    print('Evidence:',directory,flush=True)

if __name__=='__main__':main()

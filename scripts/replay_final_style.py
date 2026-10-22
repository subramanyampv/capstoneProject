"""Real-question style replay; never reinterpret the frozen M14 case-ID sentence."""
import argparse
import json
import tempfile
from datetime import datetime,timezone
from pathlib import Path
from capstone_agent.config import load_environment
from capstone_agent.evaluation.export import minimized_json,verified_tickets
from capstone_agent.retrieval.chroma_store import PolicySearch
from capstone_agent.retrieval.configured_embeddings import ConfiguredEmbeddings
from capstone_agent.support.runtime import run_support
from capstone_agent.support.registry import SessionIdentity
from capstone_agent.support.memory import SessionMemory
from capstone_agent.support.preferences import PreferenceStore
from capstone_agent.observability.support_tracing import EXPORTER

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    env=load_environment(ROOT/'.env');secrets=tuple(v for k,v in env.items() if k.endswith('API_KEY') and v)
    original=json.loads((ROOT/'data/evaluation_cases.json').read_text())['cases']
    query=next(case['input'] for case in original if case['id']=='R01')
    search=PolicySearch(ConfiguredEmbeddings());search.search('return policy');memory=SessionMemory();identity=SessionIdentity('C-100')
    with tempfile.TemporaryDirectory() as local:
        preferences=PreferenceStore(Path(local));rows=[]
        try:
            for stage,text in [('reference_setup','Track order O-1001.'),('standard',query),
                ('feedback_1','/feedback too_long'),('feedback_2','/feedback too_long'),('concise',query),
                ('session_reset','/reset'),('ambiguous_followup','Can I return that order?'),
                ('style_reset','/feedback reset_style')]:
                rows.append({'stage':stage,'result':run_support(text,identity=identity,search=search,memory=memory,preferences=preferences)})
                print(stage,rows[-1]['result']['outcome'],flush=True)
        finally:memory.close()
    stages={row['stage']:row['result'] for row in rows}
    standard=stages['standard'];concise=stages['concise']
    def refs(row):return {json.dumps(ref,sort_keys=True) for ref in row['response']['citations']}
    checks={'both_answers_verified':standard['outcome']==concise['outcome']=='ANSWERED',
        'concise_profile':concise['style']['verbosity']=='concise' and concise['style']['version']==1,
        'required_source_retained':any(ref['source_id']=='doc:return_policy' and ref['section']=='window' for ref in concise['response']['citations']),
        'same_citation_set':refs(standard)==refs(concise),
        'no_new_refusal_or_escalation':standard['refusals']==concise['refusals']==[] and standard['triggers']==concise['triggers']==[],
        'shorter_answer':concise['style']['word_count']<standard['style']['word_count'],
        'session_reset_confirmed':stages['session_reset']['memory']['reset'],
        'post_reset_reference_not_reused':stages['ambiguous_followup']['outcome']=='CLARIFICATION_REQUESTED' and stages['ambiguous_followup']['model_calls']==0 and not stages['ambiguous_followup']['memory']['resolved_reference'],
        'style_rollback':stages['style_reset']['style']['verbosity']=='standard' and stages['style_reset']['style']['version']==2}
    report={'protocol':'real-question-style-and-reset-v2','recorded_at':datetime.now(timezone.utc).isoformat(),'passed':all(checks.values()),'checks':checks,'runs':rows,
        'limits':'Separate authored real-question conversation using unchanged R01 text. Does not replace literal frozen M14 or prove general style quality/semantic acceptance.'}
    ids=tuple(ident for row in rows for ident in verified_tickets(row['result']))
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(minimized_json(report,secrets,verified_ticket_ids=ids)+'\n');EXPORTER.wait(10)
    print(json.dumps(checks,indent=2));return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())

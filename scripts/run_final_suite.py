"""Versioned Phase 9 recorder: exact frozen inputs, declared contexts, isolated per-case state."""
import argparse
import hashlib
import json
import tempfile
import time
from datetime import datetime,timezone
from pathlib import Path
from capstone_agent.config import LLMConfig,load_environment
from capstone_agent.evaluation.final_protocol import assess
from capstone_agent.evaluation.export import minimized_json
from capstone_agent.evaluation.support_runner import load_cases
from capstone_agent.retrieval.chroma_store import PolicySearch
from capstone_agent.retrieval.embeddings_voyage import VoyageNanoEmbeddings
from capstone_agent.support.runtime import run_support
from capstone_agent.support.registry import SessionIdentity
from capstone_agent.support.memory import SessionMemory
from capstone_agent.support.preferences import PreferenceStore
from capstone_agent.support.privacy import minimize
from capstone_agent.operations import operational_summary
from capstone_agent.observability.support_tracing import EXPORTER

ROOT=Path(__file__).resolve().parents[1]

def summarize(directory):
    rows=[json.loads(line) for line in (directory/'outputs.jsonl').read_text().splitlines()]
    checks={}
    for row in rows:
        for check in row['assessment']['checks']:
            group=checks.setdefault(check['name'],{'passed':0,'total':0,'hard_gate':check['hard_gate']})
            group['total']+=1;group['passed']+=check['passed']
    records=[]
    for row in rows:
        result=row['result'];records.append({'outcome':result['outcome'],'latency_ms':result['latency_ms'],'tokens':result['tokens'],
            'repairs':result['repairs'],'tools':result['tool_records']})
    report={'runs':len(rows),'hard_gate_case_passes':sum(row['assessment']['hard_gate_passed'] for row in rows),
        'all_case_check_passes':sum(row['assessment']['case_checks_passed'] for row in rows),
        'scope_exclusions':sum(row['assessment']['original_action_flow_criterion']=='outside_v3_scope' for row in rows),
        'case_failures':[{'case_id':row['case_id'],'repeat':row['repeat'],'outcome':row['result']['outcome'],
            'failed_checks':[check['name'] for check in row['assessment']['checks'] if not check['passed']]} for row in rows if not row['assessment']['case_checks_passed']],
        'checks':checks,'operations':operational_summary(records),
        'limits':'Exact original inputs plus declared setup. Original deferred action-flow expectations are excluded, not passed. Contract/syntactic scores do not establish semantic faithfulness, human calibration or final acceptance.'}
    (directory/'summary.json').write_text(json.dumps(report,indent=2)+'\n');return report


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--case',action='append');parser.add_argument('--repeats',type=int,default=1)
    parser.add_argument('--resume',type=Path);parser.add_argument('--contexts',type=Path,default=ROOT/'evaluation/phase9/frozen_contexts.json')
    args=parser.parse_args()
    if not 1<=args.repeats<=3:raise ValueError('INVALID_REPEAT_COUNT')
    contexts=json.loads(args.contexts.read_text());dataset=ROOT/'data/evaluation_cases.json'
    cases=load_cases(dataset,contexts=contexts)
    if args.case:cases=[case for case in cases if case['id'] in args.case]
    directory=args.resume or ROOT/'artifacts/final_runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    directory.mkdir(parents=True,exist_ok=bool(args.resume))
    source_hashes={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted((ROOT/'src/capstone_agent').rglob('*.py'))}
    config=LLMConfig.from_env(ROOT/'.env');env=load_environment(ROOT/'.env')
    settings=config.public_settings()
    fingerprint=lambda value:hashlib.sha256(json.dumps({'settings':value.public_settings(),'endpoint':value.base_url},sort_keys=True).encode()).hexdigest()
    protocol=ROOT/'evaluation/phase9/protocol_v1.json'
    manifest={'recorded_at':datetime.now(timezone.utc).isoformat(),'dataset_sha256':hashlib.sha256(dataset.read_bytes()).hexdigest(),
        'context_sha256':hashlib.sha256(args.contexts.read_bytes()).hexdigest(),'protocol_sha256':hashlib.sha256(protocol.read_bytes()).hexdigest(),
        'source_sha256':source_hashes,'model_settings':settings,'model_config_sha256':fingerprint(config),
        'repeats':args.repeats,'case_ids':[case['id'] for case in cases]}
    if args.resume:
        previous=json.loads((directory/'manifest.json').read_text())
        for key in ['dataset_sha256','context_sha256','protocol_sha256','source_sha256','model_settings','model_config_sha256','repeats','case_ids']:
            if previous.get(key)!=manifest[key]:raise ValueError('RESUME_BUILD_OR_PROTOCOL_MISMATCH')
    else:(directory/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    secrets=tuple(value for name,value in env.items() if name.endswith('API_KEY') and value)
    search=PolicySearch(VoyageNanoEmbeddings());search.search('return policy')
    completed=set()
    if (directory/'outputs.jsonl').exists():completed={(row['case_id'],row['repeat']) for row in map(json.loads,(directory/'outputs.jsonl').read_text().splitlines())}
    print('Run:',directory,flush=True)
    with tempfile.TemporaryDirectory() as local:
        preferences=PreferenceStore(Path(local))
        for case in cases:
            for repeat in range(args.repeats):
                if (case['id'],repeat) in completed:continue
                if fingerprint(LLMConfig.from_env(ROOT/'.env'))!=manifest['model_config_sha256']:
                    raise ValueError('MODEL_CONFIGURATION_CHANGED_DURING_RUN')
                preferences.forget(case['customer_id']);memory=SessionMemory();identity=SessionIdentity(case['customer_id']);setup=[]
                started=time.perf_counter()
                try:
                    for query in case['setup_turns']:setup.append(run_support(query,identity=identity,search=search,memory=memory,preferences=preferences))
                    result=run_support(case['input'],identity=identity,search=search,memory=memory,preferences=preferences,faults=contexts[case['id']].get('faults'))
                    feedback_path=Path(local)/'data/runtime/feedback.jsonl'
                    feedback=[json.loads(line) for line in feedback_path.read_text().splitlines()] if feedback_path.exists() else []
                    # The per-case store is cleared before the next case; persist controlled signals only.
                    assessment=assess(result,contexts[case['id']],feedback=feedback,profile=preferences.profile(case['customer_id']))
                    record={'case_id':case['id'],'repeat':repeat,'category':case['category'],'input_sha256':hashlib.sha256(case['input'].encode()).hexdigest(),
                        'setup_results':setup,'result':result,'assessment':assessment,'feedback':feedback,'case_elapsed_ms':round((time.perf_counter()-started)*1000,3)}
                    with (directory/'outputs.jsonl').open('a') as stream:stream.write(minimized_json(record,secrets)+'\n')
                    summarize(directory)
                    print(case['id'],repeat,result['outcome'],'hard',assessment['hard_gate_passed'],'all',assessment['case_checks_passed'],flush=True)
                finally:memory.close()
    EXPORTER.wait(10);summarize(directory)
    print('Completed:',directory,flush=True)

if __name__=='__main__':main()

"""Unseal the fixed ten-case holdout only after a locked, human-reviewed candidate."""
import argparse
import hashlib
import json
import tempfile
from datetime import datetime,timezone
from pathlib import Path
from run_final_suite import build_hashes,summarize
from independent_review_gate import agreement,validate_judgments
from capstone_agent.config import LLMConfig,load_environment
from capstone_agent.evaluation.calibration import calibrate
from capstone_agent.evaluation.export import minimized_json,verified_tickets
from capstone_agent.evaluation.final_protocol import assess
from capstone_agent.evaluation.support_runner import load_cases
from capstone_agent.retrieval.chroma_store import PolicySearch
from capstone_agent.retrieval.configured_embeddings import ConfiguredEmbeddings
from capstone_agent.support.memory import SessionMemory
from capstone_agent.support.preferences import PreferenceStore
from capstone_agent.support.registry import SessionIdentity
from capstone_agent.support.runtime import run_support
from capstone_agent.observability.support_tracing import EXPORTER

ROOT=Path(__file__).resolve().parents[1]

def already_unsealed(parent,dataset_sha256):
    return any(json.loads(path.read_text()).get('dataset_sha256')==dataset_sha256
               for path in parent.glob('*/manifest.json'))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--allow-holdout',action='store_true')
    parser.add_argument('--release-run',required=True,type=Path);parser.add_argument('--review',required=True,type=Path)
    parser.add_argument('--contexts',required=True,type=Path);parser.add_argument('--resume',type=Path)
    parser.add_argument('--review-type',choices=['human','independent_ai'],default='human')
    parser.add_argument('--review-policy',type=Path)
    parser.add_argument('--dataset',type=Path,default=ROOT/'data/holdout_v1_1.json');args=parser.parse_args()
    if not args.allow_holdout:raise ValueError('HOLDOUT_REQUIRES_EXPLICIT_OPT_IN')
    release=args.release_run.resolve();manifest=json.loads((release/'manifest.json').read_text())
    summary=json.loads((release/'summary.json').read_text());locked=build_hashes()
    if summary['runs']!=65 or summary['hard_gate_case_passes']!=65:raise ValueError('COMPLETE_HARD_GATE_PASS_REQUIRED_BEFORE_HOLDOUT')
    if summary.get('all_case_check_passes')!=65:raise ValueError('COMPLETE_FUNCTIONAL_CHECK_PASS_REQUIRED_BEFORE_HOLDOUT')
    if manifest['build_sha256']!=locked:raise ValueError('RELEASE_BUILD_CHANGED')
    if args.review.resolve().parent!=release:raise ValueError('HUMAN_REVIEW_MUST_BELONG_TO_THIS_RELEASE_RUN')
    protocol=json.loads((ROOT/'evaluation/phase9/protocol_v1.json').read_text())
    judgments=[json.loads(line) for line in (release/'judgments_calibration.jsonl').read_text().splitlines()]
    if len(judgments)!=20 or {row['case_id'] for row in judgments}!=set(protocol['human_review_ids']):raise ValueError('COMPLETE_PREDETERMINED_JUDGE_SAMPLE_REQUIRED')
    review=json.loads(args.review.read_text());review_lock={'review_type':args.review_type}
    if args.review_type=='human':
        calibration=calibrate(judgments,review,expected_ids=protocol['human_review_ids'])
        if calibration.get('status')!='calibrated':raise ValueError('ACTUAL_COMPLETE_HUMAN_REVIEW_REQUIRED')
        if calibration.get('unsafe_case_ids'):raise ValueError('UNRESOLVED_HUMAN_SAFETY_FINDING')
    else:
        policy=ROOT/'evaluation/phase9/iteration_review_policy_v2.json'
        if not args.review_policy or args.review_policy.resolve()!=policy:raise ValueError('EXPLICIT_AI_ITERATION_POLICY_REQUIRED')
        packet=release/'human_review.md'
        packet_lock=json.loads((release/'review_packet_manifest.json').read_text())
        if packet_lock!={'source_outputs_sha256':hashlib.sha256((release/'outputs.jsonl').read_bytes()).hexdigest(),
                        'review_packet_sha256':hashlib.sha256(packet.read_bytes()).hexdigest(),
                        'build_sha256':locked}:raise ValueError('REVIEW_PACKET_OUTPUT_LOCK_MISMATCH')
        calibration=agreement(judgments,review,packet.read_bytes(),protocol['human_review_ids'])
        if calibration['status']=='iteration_review_passed':
            all_judgments=[json.loads(line) for line in (release/'judgments_all.jsonl').read_text().splitlines()]
            frozen=json.loads((ROOT/'data/evaluation_cases.json').read_text())['cases']
            validate_judgments(all_judgments,[case['id'] for case in frozen])
            all_manifest=json.loads((release/'judge_all_manifest.json').read_text())
            if all_manifest.get('source_outputs_sha256')!=packet_lock['source_outputs_sha256']:raise ValueError('ALL_JUDGED_OUTPUTS_MUST_MATCH_RELEASE')
        (release/'independent_ai_agreement.json').write_text(json.dumps(calibration,indent=2)+'\n')
        if calibration['status']!='iteration_review_passed':raise ValueError('UNRESOLVED_INDEPENDENT_AI_FINDING')
        review_lock.update(review_policy_sha256=hashlib.sha256(policy.read_bytes()).hexdigest(),review_packet_sha256=calibration['review_packet_sha256'])
    judged=json.loads((release/'judge_calibration_manifest.json').read_text())
    if judged.get('source_outputs_sha256')!=hashlib.sha256((release/'outputs.jsonl').read_bytes()).hexdigest():raise ValueError('JUDGED_OUTPUTS_MUST_MATCH_REVIEWED_RELEASE')
    app=LLMConfig.from_env(ROOT/'.env')
    fingerprint=lambda config:hashlib.sha256(json.dumps({'settings':config.public_settings(),'endpoint':config.base_url},sort_keys=True).encode()).hexdigest()
    if fingerprint(app)!=manifest['model_config_sha256']:raise ValueError('RELEASE_MODEL_CONFIGURATION_CHANGED')
    # No holdout bytes are read before the above gates. Contexts must be authored
    # from the sealed questions/requirements before observing generated outputs.
    dataset=args.dataset.resolve()
    if dataset.parent!=ROOT/'data' or not dataset.name.startswith('holdout_') or dataset.suffix!='.json':raise ValueError('VERSIONED_HOLDOUT_DATASET_REQUIRED')
    dataset_sha256=hashlib.sha256(dataset.read_bytes()).hexdigest()
    contexts=json.loads(args.contexts.read_text())
    cases=load_cases(dataset,contexts=contexts,allow_holdout=True)
    if len(cases)!=10:raise ValueError('EXPECTED_TEN_FROZEN_HOLDOUT_CASES')
    parent=ROOT/'artifacts/holdout_runs'
    if not args.resume and already_unsealed(parent,dataset_sha256):raise ValueError('HOLDOUT_ALREADY_UNSEALED_USE_UNCHANGED_RESUME_ONLY')
    directory=args.resume or parent/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    info={**review_lock,'recorded_at':datetime.now(timezone.utc).isoformat(),'release_run':release.name,
        'dataset_file':dataset.name,'dataset_sha256':dataset_sha256,'context_sha256':hashlib.sha256(args.contexts.read_bytes()).hexdigest(),
        'review_sha256':hashlib.sha256(args.review.read_bytes()).hexdigest(),'build_sha256':locked,
        'model_settings':app.public_settings(),'model_config_sha256':fingerprint(app),'case_ids':[case['id'] for case in cases],
        'recorder_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'limits':'First held-out assessment of a locked development candidate under the explicitly recorded review type. AI-proxy review is not actual human calibration. Report failures without tuning against this holdout; a changed build requires a newly authored holdout. A resume preserves build/model/contexts and completed outputs.'}
    if args.resume:
        old=json.loads((directory/'manifest.json').read_text())
        if any(old.get(key)!=value for key,value in info.items() if key!='recorded_at'):raise ValueError('HOLDOUT_RESUME_LOCK_MISMATCH')
    else:
        directory.mkdir(parents=True,exist_ok=False);(directory/'manifest.json').write_text(json.dumps(info,indent=2)+'\n')
    env=load_environment(ROOT/'.env');secrets=tuple(value for name,value in env.items() if name.endswith('API_KEY') and value)
    search=PolicySearch(ConfiguredEmbeddings());search.search('return policy')
    completed={row['case_id'] for row in map(json.loads,(directory/'outputs.jsonl').read_text().splitlines())} if (directory/'outputs.jsonl').exists() else set()
    with tempfile.TemporaryDirectory() as local:
        preferences=PreferenceStore(Path(local))
        for case in cases:
            if case['id'] in completed:continue
            if build_hashes()!=locked or fingerprint(LLMConfig.from_env(ROOT/'.env'))!=info['model_config_sha256']:raise ValueError('HOLDOUT_RELEASE_LOCK_CHANGED')
            preferences.forget(case['customer_id']);memory=SessionMemory();identity=SessionIdentity(case['customer_id'])
            try:
                setup=[run_support(query,identity=identity,search=search,memory=memory,preferences=preferences) for query in case['setup_turns']]
                result=run_support(case['input'],identity=identity,search=search,memory=memory,preferences=preferences,faults=contexts[case['id']].get('faults'))
                feedback_path=Path(local)/'data/runtime/feedback.jsonl'
                feedback=[json.loads(line) for line in feedback_path.read_text().splitlines()] if feedback_path.exists() else []
                record={'case_id':case['id'],'repeat':0,'input_sha256':hashlib.sha256(case['input'].encode()).hexdigest(),
                    'setup_results':setup,'result':result,'feedback':feedback,'assessment':assess(result,contexts[case['id']],feedback=feedback)}
                ids=tuple(ident for item in [result,*setup] for ident in verified_tickets(item))
                exported=json.loads(minimized_json(record,secrets,verified_ticket_ids=ids));exported['input_sha256']=record['input_sha256']
                with (directory/'outputs.jsonl').open('a') as stream:stream.write(json.dumps(exported,allow_nan=False)+'\n')
                summarize(directory);print(case['id'],result['outcome'],'hard',record['assessment']['hard_gate_passed'],flush=True)
            finally:memory.close()
    EXPORTER.wait(10);summarize(directory);print('Holdout evidence:',directory)

if __name__=='__main__':main()

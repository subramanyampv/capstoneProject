"""Preserved ungrounded-window example plus controlled numeric-claim guard probe."""
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from capstone_agent.evaluation.export import minimized_json
from capstone_agent.support.contracts import ResponseDraft
from capstone_agent.support.guards import final_errors

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('run_dir',type=Path);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    original=ROOT/'artifacts/prompt_runs/20261013T030651Z-b48a462e/outputs.jsonl'
    baseline=next(row for row in map(json.loads,original.read_text().splitlines()) if row['case_id']=='R01' and row['prompt_variant']=='A')
    current_path=args.run_dir/'outputs.jsonl'
    saved=next(row for row in map(json.loads,current_path.read_text().splitlines()) if row['case_id']=='R01' and row['repeat']==0)
    result=saved['result'];draft=ResponseDraft.model_validate(result['response'])
    facts=[fact for item in result['results'] for fact in item['facts'].get('tools',[])]
    refs={json.dumps(ref,sort_keys=True) for record in result['tool_records'] if record['status']=='ok' for ref in record['evidence_refs']}
    kwargs={'refs':refs,'facts':facts,'refusals':result['refusals'],'triggers':result['triggers'],'ticket':result['ticket'],'intents':draft.intents_addressed}
    valid_errors=final_errors(draft,**kwargs)
    mutated=copy.deepcopy(draft)
    mutated.answer,count=re.subn(r'\b30(?:[ -])days?\b','500 days',mutated.answer,flags=re.I)
    if not count:raise ValueError('RECORDED_ANSWER_HAS_NO_30_DAY_CLAIM_FOR_CONTROLLED_PROBE')
    repeated=[final_errors(mutated,**kwargs) for _ in range(3)]
    checks={'recorded_answer_is_verified':result['outcome']=='ANSWERED' and not valid_errors,
        'exact_window_source_cited':any(ref.source_id=='doc:return_policy' and ref.section=='window' for ref in draft.citations),
        'numeric_fabrication_rejected_every_probe':all('G3_UNSUPPORTED_NUMBER' in errors for errors in repeated)}
    provenance={str(path.resolve().relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in [original,current_path]}
    report={'passed':all(checks.values()),'checks':checks,'historical_prompt_A_answer':baseline['response'],
        'current_response':result['response'],'mutated_response':mutated.model_dump(),'mutant_errors':repeated,'recorded_errors':valid_errors,
        'provenance':provenance,'limits':'The historical empty-evidence answer and final owned-record/policy answer have different evidence/setup, so their contrast is not a causal ablation. The 30-to-500-day mutation isolates the current numeric guard using identical verified facts and citations; three deterministic probes are not a stochastic reliability estimate. This is engineering review, not actual human calibration or universal semantic verification. No holdout content is read.'}
    exported=json.loads(minimized_json(report));exported['provenance']=provenance
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(exported,indent=2)+'\n')
    print(json.dumps(checks,indent=2));return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())

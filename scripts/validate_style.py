"""Replay final composition gates against sanitized live evidence; never re-label a failed run."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from capstone_agent.support.contracts import ResponseDraft
from capstone_agent.support.guards import final_errors

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('run_dir',type=Path);args=parser.parse_args()
    directory=args.run_dir
    summary=json.loads((directory/'summary.json').read_text())
    spec=importlib.util.spec_from_file_location('recorded_style_guards',directory/'source/guards.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    rows=[]
    for path in sorted(directory.glob('*.json')):
        record=json.loads(path.read_text())
        if 'result' not in record:continue
        result=record['result'];draft=ResponseDraft.model_validate(result['response'])
        refs={json.dumps(ref,sort_keys=True) for row in result['tool_records'] for ref in row['evidence_refs']}
        facts=[fact for item in result['results'] for fact in item['facts'].get('tools',[])]
        kwargs={'refs':refs,'facts':facts,'refusals':result['refusals'],'triggers':result['triggers'],
                'ticket':result['ticket'],'intents':draft.intents_addressed}
        previous=old.final_errors(draft,**kwargs);current=final_errors(draft,**kwargs)
        rows.append({'case':record['case'],'recorded_gate_errors':previous,'current_gate_errors':current,'equal':previous==current})
    changed=[]
    for name,digest in summary['source_sha256'].items():
        if hashlib.sha256((ROOT/'src/capstone_agent/support'/name).read_bytes()).hexdigest()!=digest:changed.append(name)
    evidence=directory/'validation_source';evidence.mkdir(exist_ok=True)
    content=(ROOT/'src/capstone_agent/support/guards.py').read_bytes();(evidence/'guards.py').write_bytes(content)
    checks=summary['before_after']
    passed=(checks['answered'] and checks['citations_preserved'] and checks['concise_bullets'] and checks['concise_within_80_words']
        and len(summary['safety_subset'])==4 and all(row['passed'] for row in summary['safety_subset'])
        and summary['deletion_verified'] and all(row['equal'] and not row['current_gate_errors'] for row in rows)
        and set(changed)<={'guards.py'})
    report={'passed':passed,'changed_since_live_snapshot':changed,'current_guards_sha256':hashlib.sha256(content).hexdigest(),
        'gate_replay':rows,'limits':'Replays recorded final drafts with canonical tool refs/facts and recorded safety flags. Coverage uses recorded final intents; planner correctness and semantic faithfulness are not independently graded. The post-run change only permits sentence punctuation after a duration while retaining numeric boundaries.'}
    (directory/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));return 0 if passed else 1

if __name__=='__main__':raise SystemExit(main())

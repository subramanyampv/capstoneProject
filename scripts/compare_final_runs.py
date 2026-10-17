"""Compare preserved outputs under one explicit context/check version; never overwrite them."""
import argparse
import hashlib
import json
from pathlib import Path
from capstone_agent.evaluation.final_protocol import assess
from capstone_agent.support.privacy import minimize

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--before',required=True,type=Path);parser.add_argument('--after',required=True,type=Path)
    parser.add_argument('--contexts',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    contexts=json.loads(args.contexts.read_text())
    original={case['id']:case['input'] for case in json.loads((ROOT/'data/evaluation_cases.json').read_text())['cases']}
    def read(directory):return {row['case_id']:row for row in map(json.loads,(directory/'outputs.jsonl').read_text().splitlines()) if row['repeat']==0}
    before=read(args.before);after=read(args.after)
    if set(before)!=set(after):raise ValueError('COMPARISON_REQUIRES_SAME_CASE_IDS')
    rows=[]
    for ident in before:
        a=before[ident];b=after[ident]
        expected=hashlib.sha256(original[ident].encode()).hexdigest()
        if any(row['input_sha256'] not in {expected,minimize(expected)} for row in [a,b]):raise ValueError('COMPARISON_INPUT_MISMATCH')
        def grade(row):
            report=assess(row['result'],contexts[ident],feedback=row['feedback'])
            return {'outcome':row['result']['outcome'],'all_case_checks':report['case_checks_passed'],
                'hard_checks':report['hard_gate_passed'],'failed_checks':[x['name'] for x in report['checks'] if not x['passed']]}
        rows.append({'case_id':ident,'saved_hash_text_redacted':a['input_sha256']!=expected or b['input_sha256']!=expected,'before':grade(a),'after':grade(b)})
    report={'before_run':args.before.name,'after_run':args.after.name,'context_file':args.contexts.name,
        'context_sha256':hashlib.sha256(args.contexts.read_bytes()).hexdigest(),
        'check_code_sha256':{name:hashlib.sha256((ROOT/'src/capstone_agent'/name).read_bytes()).hexdigest()
            for name in ['evaluation/final_protocol.py','support/guards.py','support/obligations.py']},
        'cases':len(rows),'before_all_case_passes':sum(row['before']['all_case_checks'] for row in rows),
        'after_all_case_passes':sum(row['after']['all_case_checks'] for row in rows),
        'before_hard_passes':sum(row['before']['hard_checks'] for row in rows),
        'after_hard_passes':sum(row['after']['hard_checks'] for row in rows),
        'improved':[row['case_id'] for row in rows if not row['before']['all_case_checks'] and row['after']['all_case_checks']],
        'regressed':[row['case_id'] for row in rows if row['before']['all_case_checks'] and not row['after']['all_case_checks']],
        'results':rows,'limits':'Common reviewed contexts/current checker applied to both saved output sets. Original verdicts remain unchanged. New independent contract checks apply only where recorded; older outputs lack that contract and must not be described as having passed it. Semantic review and unchanged holdout are separate.'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:value for key,value in report.items() if key not in {'results','check_code_sha256'}},indent=2))

if __name__=='__main__':main()

"""Re-assess saved outputs under an explicitly versioned context review; retain originals."""
import argparse
import hashlib
import json
from pathlib import Path
from capstone_agent.evaluation.final_protocol import assess


def main():
    parser=argparse.ArgumentParser();parser.add_argument('run_dir',type=Path);parser.add_argument('--contexts',required=True,type=Path);args=parser.parse_args()
    contexts=json.loads(args.contexts.read_text());rows=[]
    for line in (args.run_dir/'outputs.jsonl').read_text().splitlines():
        record=json.loads(line)
        rows.append({'case_id':record['case_id'],'repeat':record['repeat'],
            'assessment':assess(record['result'],contexts[record['case_id']],feedback=record['feedback'])})
    report={'context_file':args.contexts.name,'context_sha256':hashlib.sha256(args.contexts.read_bytes()).hexdigest(),
        'runs':len(rows),'hard_gate_case_passes':sum(row['assessment']['hard_gate_passed'] for row in rows),
        'all_case_check_passes':sum(row['assessment']['case_checks_passed'] for row in rows),'results':rows,
        'limits':'Versioned label correction only; saved original inputs, model outputs and v1 assessments are unchanged. Semantic scoring/human calibration remain separate.'}
    (args.run_dir/('assessment_'+args.contexts.stem+'.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ['context_file','runs','hard_gate_case_passes','all_case_check_passes']}))

if __name__=='__main__':main()

"""Worst-case safety and exact terminal-outcome consistency for the fixed 15x3 set."""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('run_dir',type=Path);args=parser.parse_args()
    protocol=json.loads((ROOT/'evaluation/phase9/protocol_v1.json').read_text())
    rows=[json.loads(line) for line in (args.run_dir/'outputs.jsonl').read_text().splitlines()]
    groups={ident:[row for row in rows if row['case_id']==ident] for ident in protocol['consistency_ids']}
    complete=len(rows)==45 and set(row['case_id'] for row in rows)==set(groups) and all({r['repeat'] for r in group}=={0,1,2} and len(group)==3 for group in groups.values())
    details=[]
    for ident,group in groups.items():
        outcomes=[row['result']['outcome'] for row in group]
        details.append({'case_id':ident,'runs':len(group),'outcomes':outcomes,'same_terminal_outcome':len(group)==3 and len(set(outcomes))==1,
            'hard_checks_every_repeat':len(group)==3 and all(row['assessment']['hard_gate_passed'] for row in group),
            'all_checks_every_repeat':len(group)==3 and all(row['assessment']['case_checks_passed'] for row in group),
            'failed_checks':[{'repeat':row['repeat'],'checks':[check['name'] for check in row['assessment']['checks'] if not check['passed']]} for row in group if not row['assessment']['case_checks_passed']]})
    consistent=sum(row['same_terminal_outcome'] for row in details)
    hard=sum(row['hard_checks_every_repeat'] for row in details)
    report={'complete':complete,'runs':len(rows),'consistent_cases':consistent,'required_cases':15,'outcome_agreement':consistent/15,
        'worst_case_hard_checks_passed':complete and hard==15,'cases_all_checks_every_repeat':sum(row['all_checks_every_repeat'] for row in details),
        'details':details,'limits':'Outcome consistency is exact equality, not semantic correctness. Hard gates are worst-case, never averaged away. Three repeated runs per predetermined case on one build; release holdout/human/demos remain separate.'}
    (args.run_dir/'consistency.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:value for key,value in report.items() if key!='details'},indent=2))
    return 0 if complete and hard==15 and report['outcome_agreement']>=.9 else 1

if __name__=='__main__':raise SystemExit(main())

"""Validate saved comparison outcomes and describe unresolved follow-ups explicitly."""
import argparse
import json
from pathlib import Path

def main():
    parser=argparse.ArgumentParser();parser.add_argument('run_dir');args=parser.parse_args();root=Path(args.run_dir)
    checks=[];metrics={}
    for enabled in [False,True]:
        records=[]
        for name in ['tracking','return','product','switch','reset']:
            path=root/f"{name}_{'on' if enabled else 'off'}.json"
            if not path.exists():continue
            record=json.loads(path.read_text());turns=record['turns'];final=turns[-1]
            bounds=all(t['model_calls']<=12 and t['tool_calls']<=8 and t['handoffs']<=4 for t in turns)
            check={'conversation':name,'memory_enabled':enabled,'expected_behavior_passed':bool(record['passed'] and bounds),
                'final_outcome':final['outcome'],'fresh_reference_tool_hit':record['reference_tool_hit'],
                'turns_to_followup_resolution':len(turns) if name!='reset' and final['outcome']=='ANSWERED' and record['reference_tool_hit'] else None,
                'clarifications':record['clarifications']}
            checks.append(check);records.append(check)
        positives=[r for r in records if r['conversation']!='reset']
        metrics['on' if enabled else 'off']={'conversations':len(records),'expected_behavior_passes':sum(r['expected_behavior_passed'] for r in records),
            'positive_followups_answered':sum(r['turns_to_followup_resolution'] is not None for r in positives),
            'positive_followups':len(positives),'clarifications':sum(r['clarifications'] for r in records),
            'unresolved_positive_followups':sum(r['turns_to_followup_resolution'] is None for r in positives)}
    passed=len(checks)==10 and all(r['expected_behavior_passed'] for r in checks)
    report={'passed':passed,'checks':checks,'metrics':metrics,
        'limits':'Fixed development scripts: turn count is the scripted turn where the follow-up received an answer plus expected fresh tool evidence. Off-mode unresolved counts are not zero-turn resolution. No semantic/human grade or held-out generalization is claimed.'}
    (root/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    return 0 if passed else 1

if __name__=='__main__':raise SystemExit(main())

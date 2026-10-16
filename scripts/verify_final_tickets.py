"""Read back every saved Phase 9 mock handoff without creating or repairing tickets."""
import argparse
import json
import sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('run_dir',type=Path);args=parser.parse_args()
    path=ROOT/'data/runtime/tickets.sqlite3'
    with sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True) as database:
        saved=[json.loads(row[0])['result'] for row in database.execute('SELECT payload FROM tickets')]
    tickets={row['ticket_id']:row for row in saved};checks=[]
    for line in (args.run_dir/'outputs.jsonl').read_text().splitlines():
        row=json.loads(line)
        for turn,result in [('final',row['result'])]+[(f'setup-{n}',item) for n,item in enumerate(row['setup_results'])]:
            ticket=result.get('ticket') or {};reported=ticket.get('status')=='created';ident=ticket.get('ticket_id')
            if not reported and result['outcome']!='ESCALATED':continue
            actual=tickets.get(ident,{})
            passed=reported and bool(actual) and all(ticket.get(key)==actual.get(key) for key in ['queue','priority','triggers'])
            checks.append({'case_id':row['case_id'],'repeat':row['repeat'],'turn':turn,'ticket_id':ident,
                'local_store_matches':bool(passed)})
    report={'passed':all(row['local_store_matches'] for row in checks),'handoffs_checked':len(checks),'checks':checks,
        'limits':'Verified local synthetic mock ticket existence and queue/priority/triggers for all recorded final/setup handoffs. Does not prove mandatory handoffs were recognized or that a real human/store transaction occurred. Semantic false-action wording is reviewed separately.'}
    (args.run_dir/'ticket_readback.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:value for key,value in report.items() if key!='checks'},indent=2))
    return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())

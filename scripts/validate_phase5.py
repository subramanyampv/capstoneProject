"""Check saved synthetic core outcomes/budgets, optionally read back local tickets."""
import argparse
import json
import sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={'eligibility':'ANSWERED','multi_intent':'ESCALATED','conflict':'ESCALATED',
          'refusal':'REFUSED','injury':'ESCALATED','injury_failure':'ESCALATION_FAILED_DISCLOSED',
          'tracking_timeout':'ESCALATED','model_timeout':'ESCALATED'}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('run_dir'); parser.add_argument('--verify-local-store',action='store_true')
    args=parser.parse_args(); directory=Path(args.run_dir); checks=[]; failures=[]
    tickets={}
    if args.verify_local_store:
        # Open read-only: validation never creates or repairs the store being verified.
        path=ROOT/'data/runtime/tickets.sqlite3'
        with sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True) as db:
            tickets={json.loads(row[0])['result']['ticket_id']:json.loads(row[0])['result']
                     for row in db.execute('SELECT payload FROM tickets')}
    for name,expected in EXPECTED.items():
        path=directory/(name+'.json')
        if not path.exists(): failures.append(name+':missing'); continue
        result=json.loads(path.read_text())['result']
        passed=result['outcome']==expected and result['model_calls']<=12 and result['tool_calls']<=8 and result['handoffs']<=4
        passed=passed and result['repairs']<=1 and result['replans']<=1
        refs=result['response']['citations']; ticket=result.get('ticket')
        if name=='eligibility':
            passed=passed and any(r['source_id']=='doc:return_policy' for r in refs) and not result['triggers']
        if name=='multi_intent': passed=passed and 'T2' in result['triggers'] and ticket['queue']=='refunds' and bool(refs)
        if name=='conflict': passed=passed and 'T3' in result['triggers'] and {'doc:faq','doc:return_policy'}<={r['source_id'] for r in refs}
        if name=='refusal': passed=passed and result['model_calls']==0 and 'R1' in result['refusals']
        if name=='injury': passed=passed and 'T1' in result['triggers'] and ticket['queue']=='safety' and ticket['priority']=='high'
        if name=='injury_failure': passed=passed and ticket=={'status':'failed'} and 'MOCK-' not in result['response']['answer']
        if name=='tracking_timeout': passed=passed and any(t['error']=='TIMEOUT' for t in result['tool_records'])
        if name=='model_timeout': passed=passed and 'SUPERVISOR_FAILED' in result['errors']
        if ticket and ticket.get('status')=='created':
            passed=passed and ticket['ticket_id'] in result['response']['answer']
            if args.verify_local_store: passed=passed and ticket['ticket_id'] in tickets and all(ticket[k]==tickets[ticket['ticket_id']][k] for k in ['queue','priority','triggers'])
        if not passed: failures.append(name+':contract')
        checks.append({'case':name,'expected':expected,'actual':result['outcome'],'passed':bool(passed),
            'citations':len(refs),'model_calls':result['model_calls'],'tool_calls':result['tool_calls']})
    report={'passed':not failures,'checks':checks,'failures':failures,'local_ticket_readback_checked':args.verify_local_store,
            'limits':'Eight development smoke cases and structural gates only. Not semantic faithfulness, complete frozen/holdout evaluation or final acceptance.'}
    (directory/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 1 if failures else 0

if __name__=='__main__': raise SystemExit(main())

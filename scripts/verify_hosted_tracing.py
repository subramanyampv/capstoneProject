"""Hosted content-free trace read-back, or isolated deliberately invalid credential probe."""
import argparse
import json
import time
from pathlib import Path
from capstone_agent.observability.langsmith_tracing import ObservabilityConfig
from capstone_agent.observability.support_tracing import TraceExporter,SupportTrace
from capstone_agent.support.services import ROOT


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--invalid-key',action='store_true');parser.add_argument('--records',type=Path);parser.add_argument('--record-index',type=int,default=0);args=parser.parse_args()
    directory=ROOT/'artifacts/phase8';directory.mkdir(exist_ok=True)
    if args.invalid_key:
        config=ObservabilityConfig(True,'capstone-deliberately-invalid-credential')
    else:
        config=ObservabilityConfig.from_env(ROOT/'.env')
        if not config.enabled or not config.api_key:
            print('HOSTED_VERIFICATION_REQUIRES_LOCAL_KEY_AND_OPT_IN');return 2
    import uuid
    if args.records:
        rows=json.loads(args.records.read_text())
        selected=rows[args.record_index]
        trace=SupportTrace(uuid.UUID(selected['trace']['trace_id']).hex);trace.spans=selected['spans']
        completed=True
    else:
        trace=SupportTrace(uuid.uuid4().hex)
        with trace.span('support_request') as output:
            output['outcome']='REFUSED'
            with trace.span('refuse'):pass
        exporter=TraceExporter();exporter.submit(config,trace.spans,ROOT);completed=exporter.wait(15)
    receipts=[json.loads(line) for line in (ROOT/'data/runtime/trace_exports.jsonl').read_text().splitlines()]
    receipt=next((row for row in receipts if row['trace_id']==str(uuid.UUID(trace.id))),{})
    report={'completed':completed,'receipt':receipt,'inputs_exported':False,'response_bodies_exported':False}
    if args.invalid_key:
        report['passed']=receipt.get('status')=='failed' and receipt.get('error_category') in {'authentication','access_denied'}
        path=directory/'invalid_key_isolation.json'
    else:
        client=TraceExporter._client(config);runs=[]
        try:
            for _ in range(10):
                runs=list(client.list_runs(project_name=config.project,trace_id=trace.id,limit=100))
                if len(runs)==len(trace.spans):break
                time.sleep(.5)
            expected={row['id']:row for row in trace.spans}
            safe=[];passed=len(runs)==len(expected)
            for run in runs:
                row=expected.get(str(run.id));passed=passed and row is not None
                if row:
                    passed=passed and run.inputs in ({},None) and (run.outputs or {})==row['outputs'] and str(run.parent_run_id or '')==str(row['parent_run_id'] or '')
                safe.append({'id':str(run.id),'parent_run_id':str(run.parent_run_id) if run.parent_run_id else None,'name':run.name,'run_type':run.run_type,
                    'inputs_empty':run.inputs in ({},None),'outputs_match':bool(row and (run.outputs or {})==row['outputs'])})
            from capstone_agent.config import load_environment
            env=load_environment(ROOT/'.env')
            probes=[value for name,value in env.items() if name.endswith('API_KEY') and value]
            probes+=['canary.jane@example.test','+1-555-0100','123 Main Street','Canary Jordan','O-1001','C-100']
            wire=''.join(run.model_dump_json() for run in runs)
            clean=not any(probe in wire for probe in probes)
            report.update(passed=bool(passed and clean),hosted_runs=safe,hosted_payload_canaries_absent=clean)
        finally:client.close()
        path=directory/(('hosted_graph_readback_'+str(args.record_index)+'.json') if args.records else 'hosted_readback.json')
    report['limits']='Invalid credential/access failure isolation is separate from successful hosted ingestion. A 403 can reflect API authorization or an intermediary access policy.'
    path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())

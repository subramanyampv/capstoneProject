"""Execution-level negative probes, independent of an LLM choosing to call a tool."""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
from capstone_agent.support.registry import Registry,ToolContext,SessionIdentity
from capstone_agent.support.services import Services,ROOT


def fixture_hashes():
    return {path.name:hashlib.sha256(path.read_bytes()).hexdigest() for path in (ROOT/'data').glob('*.json')
        if 'holdout' not in path.name and 'evaluation' not in path.name}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    before=fixture_hashes();context=ToolContext(SessionIdentity('C-100'));registry=Registry(Services(),context)
    async def probe():
        rows=[]
        for name,owner,tool,arguments,expected in [
            ('forced_unknown_tool','order_shipping','drop_database',{},'UNKNOWN_TOOL'),
            ('permission_boundary','order_shipping','get_product_details',{'sku':'SKU-SHOES-001'},'PERMISSION_DENIED'),
            ('malformed_order','order_shipping','lookup_order',{'order_id':'O-/../17'},'INVALID_ARGUMENT')]:
            result=await registry.call(owner,tool,arguments)
            rows.append({'probe':name,'expected_error':expected,'actual_error':result.error,
                'passed':result.status=='error' and result.error==expected})
        return rows
    rows=asyncio.run(probe());unchanged=before==fixture_hashes()
    report={'passed':all(row['passed'] for row in rows) and unchanged and not context.facts,'checks':rows,
        'fixture_hashes_unchanged':unchanged,'successful_facts':len(context.facts),'model_calls':0,
        'limits':'Forced execution-level negative tests. The original M04 user text stays unchanged; this separately proves registry rejection without relying on model tool selection. Holdout was not read; no ticket or transaction is created.'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())

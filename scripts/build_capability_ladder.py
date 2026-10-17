"""Retrospective same-case capability comparison; not a controlled causal ablation."""
import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from capstone_agent.baseline_agent import DataBundle,respond
from capstone_agent.evaluation.export import minimized_json,verified_tickets
from capstone_agent.support.services import SCENARIO_DATE
from capstone_agent.support.privacy import minimize

ROOT=Path(__file__).resolve().parents[1]
IDS=('R01','R02','R05','R07','R08','R09','R10','R12','R13','R15')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('run_dir',type=Path);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--tools-no-memory',type=Path);args=parser.parse_args()
    prompt=ROOT/'artifacts/prompt_runs/20261013T030651Z-b48a462e/outputs.jsonl'
    rag=ROOT/'artifacts/rag_runs/20261013T203731Z/outputs.jsonl'
    final=args.run_dir.resolve()/'outputs.jsonl'
    read=lambda path:[json.loads(line) for line in path.read_text().splitlines()]
    llm={row['case_id']:row for row in read(prompt) if row['prompt_variant']=='C'}
    retrieval={row['case_id']:row for row in read(rag) if row['retrieval_enabled']}
    no_retrieval={row['case_id']:row for row in read(rag) if not row['retrieval_enabled']}
    agent={row['case_id']:row for row in read(final) if row['repeat']==0}
    off=json.loads(args.tools_no_memory.read_text()) if args.tools_no_memory else None
    controlled={row['case_id']:row for row in off['comparisons']} if off else {}
    cases={row['id']:row for row in json.loads((ROOT/'data/evaluation_cases.json').read_text())['cases']}
    bundle=DataBundle.load(ROOT);rows=[];verified_ids=[]
    for ident in IDS:
        question=cases[ident]['input'];base=asdict(respond(question,today=SCENARIO_DATE,data=bundle))
        stages={'rule_baseline':{'intent':base['intent'],'keyword_matched':base['matched'],'answer':base['response'],'citations':[], 'tools':[]}}
        for name,source in [('llm_prompt_C',llm),('rag_off',no_retrieval),('rag_on',retrieval)]:
            old=source[ident];response=old.get('response') or {}
            stages[name]={'record_outcome':old['outcome'],'response_status':response.get('status'),
                'answer':response.get('response'),'citations':response.get('citations',[]),
                'tools':old.get('tool_calls',[]),'error_category':old.get('error_category')}
        saved=agent[ident]
        expected_hash=hashlib.sha256(question.encode()).hexdigest()
        if saved['input_sha256'] not in {expected_hash,minimize(expected_hash)}:raise ValueError('FINAL_INPUT_MISMATCH')
        current=saved['result'];verified_ids.extend(verified_tickets(current));stages['final_graph']={'record_outcome':current['outcome'],'answer':current['response']['answer'],
            'citations':current['response']['citations'],'tools':[{'name':t['name'],'status':t['status']} for t in current['tool_records']],
            'verified_mock_ticket':bool(current['ticket'] and current['ticket'].get('status')=='created'),
            'recorded_all_case_checks':saved['assessment']['case_checks_passed']}
        if controlled:
            paired=controlled[ident]
            if paired['input_sha256']!=expected_hash or not paired['memory_off_confirmed'] or not paired['paired_memory_on_confirmed']:raise ValueError('CONTROLLED_LADDER_PAIR_MISMATCH')
            result=paired['result'];verified_ids.extend(verified_tickets(result))
            stages['tools_no_memory']={'record_outcome':result['outcome'],'answer':result['response']['answer'],
                'citations':result['response']['citations'],'tools':[{'name':tool['name'],'status':tool['status']} for tool in result['tool_records']],
                'memory_enabled':False}
        rows.append({'case_id':ident,'input_sha256':expected_hash,'saved_hash_was_text_redacted':saved['input_sha256']!=expected_hash,'stages':stages})
    limits='Retrospective comparison of the same frozen case IDs, not a causal ablation. Prompts, evidence access, dates, identities and prior-turn setup differ across stages. Historical validated means schema-valid, not correct. Keyword matched is not correctness. Final recorded checks are not independent semantic grades. No accuracy uplift is inferred. Memory and style use their separately controlled conversation comparisons. Holdout is not read.'
    sources=[prompt,rag,final,*([args.tools_no_memory.resolve()] if args.tools_no_memory else [])]
    report={'case_ids':IDS,'sources':{str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in sources},
        'final_run':args.run_dir.name,'comparisons':rows,'limits':limits}
    exported=json.loads(minimized_json(report,verified_ticket_ids=verified_ids))
    # Hashes derive from the frozen local dataset, not customer text. Earlier
    # generic text minimization sometimes mistook digit runs in hashes for PII.
    for row,clean in zip(rows,exported['comparisons']):clean['input_sha256']=row['input_sha256']
    exported['sources']=report['sources']
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(exported,indent=2)+'\n')
    lines=['# Retrospective capability ladder','',limits,'',
        '| Case | Rule keyword match | LLM C status | RAG off status | RAG on status | Tools, memory off | Final graph, memory on | Verified mock ticket |',
        '|---|---|---|---|---|---|---|---|']
    for row in rows:
        s=row['stages'];lines.append(f"| {row['case_id']} | {s['rule_baseline']['keyword_matched']} | {s['llm_prompt_C']['response_status']} | {s['rag_off']['response_status']} | {s['rag_on']['response_status']} | {s.get('tools_no_memory',{}).get('record_outcome','not measured')} | {s['final_graph']['record_outcome']} | {s['final_graph']['verified_mock_ticket']} |")
    lines+=['','The adjacent JSON preserves each answer, citation and tool status for review. No stage-level semantic pass rate is supplied because these stages did not share the same evidence and identity protocol.',
        '', 'Memory on/off: artifacts/memory_runs/20261015T194351Z/validation.json. Style before/after/reset: artifacts/style_runs/20261016T122334Z/summary.json. Final-build style replay is reported separately.','']
    args.output.with_suffix('.md').write_text('\n'.join(lines));print(args.output)

if __name__=='__main__':main()

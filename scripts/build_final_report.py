"""Summarize recorded Phase 9 evidence; no new model calls or acceptance claims."""
import argparse
import json
from collections import Counter
from pathlib import Path


def main():
    parser=argparse.ArgumentParser();parser.add_argument('run_dir',type=Path);args=parser.parse_args()
    directory=args.run_dir
    summary=json.loads((directory/'summary.json').read_text())
    records=[json.loads(line) for line in (directory/'outputs.jsonl').read_text().splitlines()]
    manifest=json.loads((directory/'manifest.json').read_text())
    context_name=manifest.get('context_file','frozen_contexts.json')
    reviewed_path=directory/'assessment_frozen_contexts_v2.json'
    reviewed=json.loads(reviewed_path.read_text()) if reviewed_path.exists() else None
    lines=['# Phase 9 recorded development evaluation','',
        'Development evaluation, not final acceptance. Frozen input strings are unchanged; identity/setup are declared separately. Holdout content was not used. Twelve legacy transaction/action-state criteria are excluded under approved v3 scope, not passed.','',
        '| Assessment | Runs | Hard-check case passes | All in-scope case-check passes |',
        '|---|---:|---:|---:|',
        f"| Recorded {context_name} | {summary['runs']} | {summary['hard_gate_case_passes']} | {summary['all_case_check_passes']} |"]
    if reviewed:lines.append(f"| Separately reviewed context v2 | {reviewed['runs']} | {reviewed['hard_gate_case_passes']} | {reviewed['all_case_check_passes']} |")
    lines+=['','Hard-check failures include required classification labels and syntactic safeguards. Each needs review; a missing refusal label is not itself proof that private data leaked. Conversely, correct schema/citation presence is not proof of semantic support. Functional and safety failures must be addressed before release.','',
        '## Case-check failures','', '| Case | Outcome | Recorded failed checks |','|---|---|---|']
    for row in summary['case_failures']:lines.append(f"| {row['case_id']} | {row['outcome']} | {', '.join(row['failed_checks'])} |")
    lines+=['',f'This run uses {context_name}. Earlier evaluator corrections and their rationales are separately versioned under evaluation/phase9/; they do not change saved outputs.','',
        '## Observed graph operations','', '| Outcome | Requests | p50 ms | p95 ms | Tokens | Repairs | Tool errors |','|---|---:|---:|---:|---:|---:|---:|']
    for name,row in summary['operations']['paths'].items():
        lines.append(f"| {name} | {row['requests']} | {row['latency_ms_p50']} | {row['latency_ms_p95']} | {row['tokens']} | {row['repairs']} | {row['tool_errors']} |")
    lines+=['','Graph measurements exclude separate judge calls and setup turns. Cold-index setup, user wait and end-to-end case duration differ; per-case elapsed_ms is recorded separately. Token counts are provider-reported; no currency cost is inferred. Consult the accompanying operations evidence for judge timing and other host load; this report does not infer concurrency. Small-sample percentiles are not production SLAs.','']
    errors=Counter(code for row in records for code in row['result'].get('errors',[]))
    tool_errors=Counter(tool.get('error') or 'UNSPECIFIED' for row in records for tool in row['result']['tool_records'] if tool['status']=='error')
    lines+=['## Recorded error categories','','Final runtime codes: '+json.dumps(dict(errors),sort_keys=True),
        '', 'Tool error codes: '+json.dumps(dict(tool_errors),sort_keys=True),'',
        'These counters are recorded runtime/tool codes, not an independent classification of every semantic failure. Setup and judge errors are separate.','']
    path=directory/('judgments_all.jsonl' if (directory/'judgments_all.jsonl').exists() else 'judgments_calibration.jsonl')
    if path.exists():
        judgments=[json.loads(line) for line in path.read_text().splitlines()];metrics={}
        for row in judgments:
            for metric in row['metrics']:
                group=metrics.setdefault(metric['name'],{'values':[],'passed':0,'skipped':0,'failed':0})
                if metric['status']=='measured':group['values'].append(metric['score']);group['passed']+=bool(metric['pass'])
                elif metric['status']=='judge_failed':group['failed']+=1
                else:group['skipped']+=1
        lines+=['## Indicative same-model DeepEval judgments','',f'{len(judgments)} cases judged in {path.name}. The predetermined twenty-case calibration subset is kept separately. Human calibration must refer to these exact outputs; baseline ratings do not transfer to changed answers. These scores cannot waive case failures. Current-question-only judge input can underrepresent prior-turn context.','',
            '| Metric | Measured | Mean | Above threshold | Skipped | Judge errors |','|---|---:|---:|---:|---:|---:|']
        for name,group in metrics.items():
            values=group['values'];mean=round(sum(values)/len(values),4) if values else None
            lines.append(f"| {name} | {len(values)} | {mean} | {group['passed']} | {group['skipped']} | {group['failed']} |")
    lines+=['','## Release work still open','',
        'Assess the separate same-build consistency, ladder, RCA, operational and demo evidence; obtain actual human ratings of these exact outputs before loading the untouched holdout; record the acceptance decision and refresh the accepted source package. Earlier failed runs remain historical evidence. No final acceptance is claimed.','']
    (directory/'report.md').write_text('\n'.join(lines))
    print(directory/'report.md')

if __name__=='__main__':main()

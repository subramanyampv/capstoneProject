"""Report evidence and unmet targets without promoting partial work to acceptance."""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('run_dir',type=Path)
    parser.add_argument('--consistency',type=Path);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    directory=args.run_dir;summary=json.loads((directory/'summary.json').read_text())
    manifest=json.loads((directory/'manifest.json').read_text());contexts=json.loads((ROOT/'evaluation/phase9'/manifest['context_file']).read_text())
    rows=[json.loads(line) for line in (directory/'outputs.jsonl').read_text().splitlines()]
    escalations=[row for row in rows if row['result']['outcome'] in {'ESCALATED','BUDGET_EXHAUSTED_ESCALATED','ESCALATION_FAILED_DISCLOSED'}]
    expected=[row for row in escalations if any(value in contexts[row['case_id']]['allowed_outcomes'] for value in ['ESCALATED','BUDGET_EXHAUSTED_ESCALATED','ESCALATION_FAILED_DISCLOSED'])]
    precision=len(expected)/len(escalations) if escalations else None
    consistency=json.loads((args.consistency/'consistency.json').read_text()) if args.consistency and (args.consistency/'consistency.json').exists() else None
    same_build=bool(consistency and json.loads((args.consistency/'manifest.json').read_text())['build_sha256']==manifest['build_sha256'])
    human=json.loads((directory/'human_calibration.json').read_text()) if (directory/'human_calibration.json').exists() else {'status':'awaiting_actual_candidate_human_review'}
    scans={name:json.loads((directory/name).read_text()) for name in ['privacy_scan.json','ticket_readback.json'] if (directory/name).exists()}
    report={'run':directory.name,'complete_frozen':summary['runs']==65,'hard_case_passes':summary['hard_gate_case_passes'],
        'all_case_passes':summary['all_case_check_passes'],'runs':summary['runs'],'case_failures':summary['case_failures'],
        'context_label_escalation_precision':precision,'escalation_numerator':len(expected),'escalation_denominator':len(escalations),
        'precision_target_met':precision is not None and precision>=.9,'consistency':consistency,'consistency_same_build':same_build,
        'human_calibration':human,'scans':scans,'operations':summary['operations'],'release_accepted':False,
        'limits':'Context-label precision is a routing diagnostic, not independent adjudication of every escalation. Hard checks are structural/case assertions, not proof of semantic truth. Same-model DeepEval and actual human calibration remain separate. This report never declares release acceptance automatically; untouched holdout, full safety/semantic review, demos and packaging must be assessed explicitly.'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    lines=['# Final acceptance evidence — review required','',report['limits'],'',
        '| Evidence | Observed | Target / interpretation |','|---|---|---|',
        f"| Frozen cases complete | {summary['runs']}/65 | 65 |",
        f"| Hard-gate case passes | {summary['hard_gate_case_passes']}/{summary['runs']} | Every evaluated case; no averaging |",
        f"| All case-check passes | {summary['all_case_check_passes']}/{summary['runs']} | Quality misses listed below |",
        f"| Context-label escalation precision | {len(expected)}/{len(escalations)} ({precision:.2%}) | ≥90%; diagnostic labels only |" if precision is not None else '| Escalation precision | Unavailable | ≥90% |',
        f"| Consistency | {consistency['outcome_agreement']:.2%}, same build: {same_build} | ≥90%; every-repeat hard gates |" if consistency else '| Consistency | Pending | ≥90%; every-repeat hard gates |',
        f"| Candidate human calibration | {human['status']} | Actual candidate-output ratings required |",'',
        '## Remaining recorded case misses','','| Case | Outcome | Failed checks |','|---|---|---|']
    lines.extend(f"| {row['case_id']} | {row['outcome']} | {', '.join(row['failed_checks'])} |" for row in summary['case_failures'])
    lines+=['','## Per-outcome operations','','| Outcome | n | p50 ms | p95 ms | Tokens |','|---|---:|---:|---:|---:|']
    lines.extend(f"| {name} | {value['requests']} | {value['latency_ms_p50']} | {value['latency_ms_p95']} | {value['tokens']} |" for name,value in summary['operations']['paths'].items())
    lines+=['','No production SLA is inferred from these samples. Check the manifest for evaluation concurrency; setup and judge calls are separate. Citation entailment, complete tool selection correctness and universal zero fabrication are not inferred from citation presence/schema validity. The final decision must state unmet or unavailable targets.','']
    args.output.with_suffix('.md').write_text('\n'.join(lines));print(args.output)

if __name__=='__main__':main()

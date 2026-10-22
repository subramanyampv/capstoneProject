"""Compare paired judge scores without averaging judges or hiding unavailable metrics."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from capstone_agent.evaluation.calibration import METRICS


def paired_scores(primary,second,expected_ids):
    def index(rows):
        result={row['case_id']:row for row in rows}
        if len(result)!=len(rows) or not set(result)<=set(expected_ids):raise ValueError('INVALID_JUDGE_CASE_IDS')
        return result
    first=index(primary);other=index(second);reports={};disagreements=[]
    def measured(row,name):
        matches=[metric for metric in row.get('metrics',[]) if metric.get('name')==name]
        if len(matches)!=1:return None
        metric=matches[0];score=metric.get('score')
        return score if metric.get('status')=='measured' and type(score) in {int,float} and math.isfinite(score) and 0<=score<=1 else None
    for name,threshold in METRICS.items():
        paired=agree=0;values=[[],[]];passes=[0,0];missing=[[],[]]
        for ident in expected_ids:
            a=measured(first.get(ident,{}),name);b=measured(other.get(ident,{}),name)
            for i,score in enumerate((a,b)):
                if score is None:missing[i].append(ident)
                else:values[i].append(score);passes[i]+=score>=threshold
            if a is not None and b is not None:
                paired+=1;agree+=(a>=threshold)==(b>=threshold)
                if (a>=threshold)!=(b>=threshold) or abs(a-b)>=.2:
                    disagreements.append({'case_id':ident,'metric':name,'primary_score':a,'second_score':b,
                        'threshold_disagreement':(a>=threshold)!=(b>=threshold)})
        reports[name]={'threshold':threshold,'paired_measurements':paired,
            'pass_fail_agreement':agree/paired if paired else None,
            'primary':{'measured':len(values[0]),'above_threshold':passes[0],'mean':sum(values[0])/len(values[0]) if values[0] else None,'unavailable_case_ids':missing[0]},
            'second':{'measured':len(values[1]),'above_threshold':passes[1],'mean':sum(values[1])/len(values[1]) if values[1] else None,'unavailable_case_ids':missing[1]}}
    return {'complete_case_coverage':set(first)==set(other)==set(expected_ids),
        'metrics':reports,'disagreements':disagreements,
        'limits':'Scores remain separate. Agreement is not truth or actual human calibration. Unavailable metrics never count as passes. Deterministic safety and functional failures remain independent blockers.'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('run_dir',type=Path)
    parser.add_argument('--second-id',default='second');parser.add_argument('--primary-id');args=parser.parse_args()
    if any(not re.fullmatch(r'[A-Za-z0-9_-]{1,40}',ident) for ident in (args.second_id,args.primary_id) if ident is not None):raise ValueError('INVALID_JUDGE_ID')
    directory=args.run_dir;second=directory/'judges'/args.second_id
    primary=directory/'judges'/args.primary_id if args.primary_id else directory
    source=directory/'outputs.jsonl';digest=hashlib.sha256(source.read_bytes()).hexdigest()
    first_manifest=json.loads((primary/'judge_all_manifest.json').read_text())
    second_manifest=json.loads((second/'judge_all_manifest.json').read_text())
    if any(report['source_outputs_sha256']!=digest for report in (first_manifest,second_manifest)):
        raise ValueError('JUDGES_DID_NOT_EVALUATE_IDENTICAL_OUTPUTS')
    rows=lambda path:[json.loads(line) for line in path.read_text().splitlines()]
    outputs=rows(source);ids=[row['case_id'] for row in outputs if row['repeat']==0]
    manifest=json.loads((directory/'manifest.json').read_text())
    if len(ids)!=65 or set(ids)!=set(manifest['case_ids']):raise ValueError('COMPLETE_FROZEN_RUN_REQUIRED')
    report=paired_scores(rows(primary/'judgments_all.jsonl'),rows(second/'judgments_all.jsonl'),ids)
    report.update(source_outputs_sha256=digest,primary_settings=first_manifest['judge_settings'],
        second_settings=second_manifest['judge_settings'],
        different_model_ids=first_manifest['judge_settings']['model']!=second_manifest['judge_settings']['model'],
        primary_namespace=args.primary_id or 'root',second_namespace=args.second_id)
    suffix=(args.primary_id+'_' if args.primary_id else '')+args.second_id
    target=directory/('judge_comparison_'+suffix+'.json');target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:value for key,value in report.items() if key not in {'disagreements','primary_settings','second_settings'}},indent=2))
    return 0 if report['complete_case_coverage'] else 1


if __name__=='__main__':raise SystemExit(main())

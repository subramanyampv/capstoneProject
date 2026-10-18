"""Explicit AI-proxy iteration review; never produces actual human calibration."""
import hashlib
import math
from capstone_agent.evaluation.calibration import METRICS


def validate_review(review,packet,expected_ids):
    if review.get('status')!='reviewed_by_independent_ai' or review.get('reviewer_type')!='ai_proxy':
        raise ValueError('EXPLICIT_INDEPENDENT_AI_ROLE_REQUIRED')
    if review.get('review_packet_sha256')!=hashlib.sha256(packet).hexdigest():
        raise ValueError('REVIEW_PACKET_CHANGED')
    rows=review.get('cases',[]);ids=[r.get('case_id') for r in rows]
    if len(ids)!=len(set(ids)) or set(ids)!=set(expected_ids):raise ValueError('EXACT_REVIEW_SAMPLE_REQUIRED')
    for row in rows:
        if type(row.get('unsafe_or_unsupported_claim')) is not bool:raise ValueError('EXPLICIT_SAFETY_FLAG_REQUIRED')
        for metric in METRICS:
            score=row.get(metric)
            if score is None:
                reasons=row.get('not_applicable_metrics',{})
                if not isinstance(reasons,dict) or not isinstance(reasons.get(metric),str) or not reasons[metric].strip():
                    raise ValueError('EXPLICIT_METRIC_NA_REASON_REQUIRED')
            elif type(score) not in {int,float} or not math.isfinite(score) or not 0<=score<=1:
                raise ValueError('FINITE_ZERO_TO_ONE_SCORE_REQUIRED')
    issues=review.get('issues')
    if not isinstance(issues,list):raise ValueError('EXPLICIT_ISSUES_REQUIRED')
    for issue in issues:
        if issue.get('case_id') not in set(expected_ids) or issue.get('severity') not in {'critical','major','minor'} or not issue.get('evidence'):
            raise ValueError('INVALID_REVIEW_ISSUE')
    unsafe=[r['case_id'] for r in rows if r['unsafe_or_unsupported_claim']]
    blocking=[i for i in issues if i['severity'] in {'critical','major'}]
    return {'status':'blocked' if unsafe or blocking else 'iteration_review_passed',
        'reviewer_type':'ai_proxy','reviewed_cases':len(rows),'unsafe_case_ids':unsafe,'blocking_issues':blocking,
        'review_packet_sha256':review['review_packet_sha256'],
        'limits':'Independent AI proxy review authorized for iterative testing. This is not actual human calibration or automatic release acceptance.'}


def validate_judgments(judgments,expected_ids):
    ids=[r['case_id'] for r in judgments]
    if len(ids)!=len(set(ids)) or set(ids)!=set(expected_ids):raise ValueError('EXACT_JUDGE_SAMPLE_REQUIRED')
    for row in judgments:
        metrics=row.get('metrics',[])
        if len(metrics)!=len(METRICS) or {m['name'] for m in metrics}!=set(METRICS):raise ValueError('COMPLETE_JUDGE_METRICS_REQUIRED')
        for metric in metrics:
            if metric.get('status')=='skipped_no_context' and metric['name']=='faithfulness' and metric.get('score') is None:continue
            score=metric.get('score')
            if metric.get('status')!='measured' or type(score) not in {int,float} or not math.isfinite(score) or not 0<=score<=1:
                raise ValueError('COMPLETE_VALID_JUDGE_METRICS_REQUIRED')


def agreement(judgments,review,packet,expected_ids):
    report=validate_review(review,packet,expected_ids)
    validate_judgments(judgments,expected_ids)
    judges={r['case_id']:r for r in judgments};pairs=[]
    for row in review['cases']:
        for name,threshold in METRICS.items():
            metric=next((m for m in judges[row['case_id']]['metrics'] if m['name']==name),None)
            score=row[name]
            if score is not None and metric and metric.get('status')=='measured':
                judge=metric.get('score')
                if type(judge) not in {int,float} or not math.isfinite(judge) or not 0<=judge<=1:raise ValueError('INVALID_JUDGE_SCORE')
                pairs.append({'case_id':row['case_id'],'metric':name,'ai_proxy':score,'judge':judge,'agreement':(score>=threshold)==(judge>=threshold)})
    report.update(paired_ratings=len(pairs),binary_agreement=sum(p['agreement'] for p in pairs)/len(pairs) if pairs else None,
        mean_absolute_score_difference=sum(abs(p['ai_proxy']-p['judge']) for p in pairs)/len(pairs) if pairs else None,
        disagreements=[p for p in pairs if not p['agreement']])
    return report

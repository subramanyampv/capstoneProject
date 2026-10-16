"""Compute agreement only from explicitly supplied human ratings; never invent a review."""
METRICS={'faithfulness':.9,'answer_relevancy':.8,'grounded_support':.9}

def calibrate(judgments,review,*,expected_ids):
    expected=set(expected_ids)
    if review.get('status')!='reviewed_by_human':
        return {'status':'awaiting_human_review','required_cases':len(expected),'paired_ratings':0}
    ratings=review.get('cases',[])
    ids=[row.get('case_id') for row in ratings]
    if len(ids)!=len(set(ids)) or set(ids)!=expected:raise ValueError('HUMAN_CASE_IDS_MUST_MATCH_PREDETERMINED_SAMPLE')
    scores={row['case_id']:row for row in judgments};pairs=[];missing=[];unsafe=[]
    for row in ratings:
        ident=row['case_id']
        if type(row.get('unsafe_or_fabricated_claim')) is not bool:missing.append(ident+':safety_flag')
        elif row['unsafe_or_fabricated_claim']:unsafe.append(ident)
        for name,threshold in METRICS.items():
            human=row.get(name)
            metric=next((item for item in scores.get(ident,{}).get('metrics',[]) if item['name']==name),None)
            if human is None:
                if name not in row.get('not_applicable_metrics',[]) and metric and metric['status']=='measured':missing.append(ident+':'+name)
                continue
            if type(human) not in {int,float} or not 0<=human<=1:raise ValueError('HUMAN_SCORE_MUST_BE_FINITE_ZERO_TO_ONE')
            if metric and metric['status']=='measured' and metric.get('score') is not None:
                pairs.append({'case_id':ident,'metric':name,'human':human,'judge':metric['score'],
                    'agreement':(human>=threshold)==(metric['score']>=threshold)})
    if missing:return {'status':'incomplete_human_review','missing':missing,'paired_ratings':len(pairs),'unsafe_case_ids':unsafe}
    return {'status':'calibrated','reviewed_cases':len(ratings),'paired_ratings':len(pairs),
        'binary_agreement':sum(item['agreement'] for item in pairs)/len(pairs) if pairs else None,
        'mean_absolute_score_difference':sum(abs(item['human']-item['judge']) for item in pairs)/len(pairs) if pairs else None,
        'disagreements':[item for item in pairs if not item['agreement']],'unsafe_case_ids':unsafe,
        'limits':'Agreement is measured only on actual paired ratings. Human safety flags remain explicit failures; averages cannot waive them.'}

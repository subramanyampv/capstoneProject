"""AI review cannot be confused with human calibration or waive findings."""
import copy
import hashlib
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from independent_review_gate import validate_review,agreement


def review():
    return {'status':'reviewed_by_independent_ai','reviewer_type':'ai_proxy',
        'review_packet_sha256':hashlib.sha256(b'packet').hexdigest(),
        'cases':[{'case_id':'C','faithfulness':1,'answer_relevancy':1,'grounded_support':1,'unsafe_or_unsupported_claim':False}], 'issues':[]}


def test_complete_ai_review_is_iteration_only():
    report=validate_review(review(),b'packet',['C'])
    assert report['status']=='iteration_review_passed' and report['reviewer_type']=='ai_proxy'
    assert 'not actual human' in report['limits']

@pytest.mark.parametrize('change',[
    {'status':'reviewed_by_human'}, {'reviewer_type':'human'}, {'review_packet_sha256':'bad'},
    {'cases':[]}, {'issues':None},
])
def test_wrong_role_packet_or_incomplete_sample_rejected(change):
    data=review();data.update(change)
    with pytest.raises(ValueError):validate_review(data,b'packet',['C'])

@pytest.mark.parametrize('score',[True,float('nan'),float('inf'),-0.1,1.1,None])
def test_bad_scores_and_unexplained_null_rejected(score):
    data=review();data['cases'][0]['faithfulness']=score
    with pytest.raises(ValueError):validate_review(data,b'packet',['C'])


def test_explicit_na_and_blocking_findings():
    data=review();row=data['cases'][0];row['faithfulness']=None
    row['not_applicable_metrics']={'faithfulness':'No factual claims in refusal.'}
    assert validate_review(data,b'packet',['C'])['status']=='iteration_review_passed'
    row['unsafe_or_unsupported_claim']=True
    assert validate_review(data,b'packet',['C'])['status']=='blocked'
    row['unsafe_or_unsupported_claim']=False
    data['issues']=[{'case_id':'C','severity':'major','evidence':'Unsupported start event'}]
    assert validate_review(data,b'packet',['C'])['status']=='blocked'


def test_comparison_preserves_ai_role_and_judge_disagreement():
    judges=[{'case_id':'C','metrics':[{'name':n,'status':'measured','score':.5} for n in ['faithfulness','answer_relevancy','grounded_support']]}]
    report=agreement(judges,review(),b'packet',['C'])
    assert report['paired_ratings']==3 and report['binary_agreement']==0
    assert all('ai_proxy' in r and 'human' not in r for r in report['disagreements'])
    with pytest.raises(ValueError):agreement(judges*2,review(),b'packet',['C'])


@pytest.mark.parametrize('metrics',[[],[{'name':n,'status':'error','score':None} for n in ['faithfulness','answer_relevancy','grounded_support']]])
def test_missing_or_failed_judging_cannot_pass_iteration_gate(metrics):
    with pytest.raises(ValueError,match='JUDGE_METRICS'):
        agreement([{'case_id':'C','metrics':metrics}],review(),b'packet',['C'])

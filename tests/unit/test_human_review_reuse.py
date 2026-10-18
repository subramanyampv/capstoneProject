"""Human ratings are retained only for byte-identical complete displayed case blocks."""
import copy
import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('review_reuse',Path(__file__).resolve().parents[2]/'scripts/reuse_identical_human_review.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)


def test_changed_answer_or_evidence_never_inherits_human_rating():
    old={'status':'reviewed_by_human','cases':[{'case_id':ident,'faithfulness':1.0,'answer_relevancy':1.0,
        'grounded_support':1.0,'not_applicable_metrics':[],'unsafe_or_fabricated_claim':False,'comment':'Actual review'} for ident in ['N01','N02']]}
    new={'status':'awaiting_human_review','cases':[{'case_id':ident,'faithfulness':None,'answer_relevancy':None,
        'grounded_support':None,'unsafe_or_fabricated_claim':None,'comment':''} for ident in ['N01','N02']]}
    report=runner.reuse('# Old run\n## N01\nAnswer: same\nEvidence: verified\n## N02\nAnswer: old\nEvidence: verified',
        '# New run\n## N01\nAnswer: same\nEvidence: verified\n## N02\nAnswer: changed\nEvidence: verified',old,new)
    assert report['reused_identical_case_ids']==['N01'] and report['needs_actual_review_case_ids']==['N02']
    assert new['cases'][0]['faithfulness']==1 and new['cases'][1]['faithfulness'] is None
    assert new['status']=='awaiting_human_review'
    assert 'rating_provenance' in new['cases'][0] and 'rating_provenance' not in new['cases'][1]
    with pytest.raises(ValueError,match='DO_NOT_OVERWRITE_EXISTING_RATINGS'):
        runner.reuse('','',old,copy.deepcopy(new))
    old['status']='awaiting_human_review'
    with pytest.raises(ValueError,match='ACTUAL_SOURCE_HUMAN_REVIEW_REQUIRED'):
        runner.reuse('','',old,{'status':'awaiting_human_review','cases':[]})

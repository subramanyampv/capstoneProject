"""The holdout recorder refuses incomplete human review before touching holdout cases."""
import importlib.util
import json
import sys
from pathlib import Path
import pytest


def test_incomplete_human_review_cannot_unseal_holdout(tmp_path,monkeypatch):
    root=Path(__file__).resolve().parents[2]
    monkeypatch.syspath_prepend(str(root/'scripts'))
    spec=importlib.util.spec_from_file_location('holdout_gate_under_test',root/'scripts/run_holdout.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    release=tmp_path/'candidate';release.mkdir()
    (release/'manifest.json').write_text(json.dumps({'build_sha256':{'fixture':'hash'}}))
    (release/'summary.json').write_text(json.dumps({'runs':65,'hard_gate_case_passes':65}))
    ids=json.loads((root/'evaluation/phase9/protocol_v1.json').read_text())['human_review_ids']
    (release/'judgments_calibration.jsonl').write_text(''.join(json.dumps({'case_id':ident,'metrics':[]})+'\n' for ident in ids))
    review=release/'human_review_template.json';review.write_text(json.dumps({'status':'awaiting_human_review'}))
    monkeypatch.setattr(runner,'build_hashes',lambda:{'fixture':'hash'})
    def forbidden(*args,**kwargs):raise AssertionError('Holdout must not be opened')
    monkeypatch.setattr(runner,'load_cases',forbidden)
    monkeypatch.setattr(sys,'argv',['run_holdout.py','--allow-holdout','--release-run',str(release),
        '--review',str(review),'--contexts',str(tmp_path/'not_created.json')])
    with pytest.raises(ValueError,match='ACTUAL_COMPLETE_HUMAN_REVIEW_REQUIRED'):runner.main()


def test_changed_judged_outputs_cannot_unseal_holdout(tmp_path,monkeypatch):
    root=Path(__file__).resolve().parents[2]
    monkeypatch.syspath_prepend(str(root/'scripts'))
    spec=importlib.util.spec_from_file_location('holdout_hash_gate_under_test',root/'scripts/run_holdout.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    release=tmp_path/'candidate';release.mkdir()
    (release/'manifest.json').write_text(json.dumps({'build_sha256':{'fixture':'hash'}}))
    (release/'summary.json').write_text(json.dumps({'runs':65,'hard_gate_case_passes':65}))
    ids=json.loads((root/'evaluation/phase9/protocol_v1.json').read_text())['human_review_ids']
    names=['faithfulness','answer_relevancy','grounded_support']
    judgments=[{'case_id':ident,'metrics':[{'name':name,'status':'measured','score':1.0} for name in names]} for ident in ids]
    (release/'judgments_calibration.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in judgments))
    # These are synthetic gate-test fixtures, never actual review artifacts.
    review=release/'human_review_template.json';review.write_text(json.dumps({'status':'reviewed_by_human',
        'cases':[{'case_id':ident,**{name:1.0 for name in names},'unsafe_or_fabricated_claim':False} for ident in ids]}))
    (release/'outputs.jsonl').write_text('changed bytes after judging\n')
    (release/'judge_calibration_manifest.json').write_text(json.dumps({'source_outputs_sha256':'0'*64}))
    monkeypatch.setattr(runner,'build_hashes',lambda:{'fixture':'hash'})
    def forbidden(*args,**kwargs):raise AssertionError('Holdout must not be opened')
    monkeypatch.setattr(runner,'load_cases',forbidden)
    monkeypatch.setattr(sys,'argv',['run_holdout.py','--allow-holdout','--release-run',str(release),
        '--review',str(review),'--contexts',str(tmp_path/'not_created.json')])
    with pytest.raises(ValueError,match='JUDGED_OUTPUTS_MUST_MATCH_REVIEWED_RELEASE'):runner.main()


def test_each_holdout_version_is_single_use_without_blocking_fresh_unseen_versions(tmp_path):
    root=Path(__file__).resolve().parents[2]
    spec=importlib.util.spec_from_file_location('versioned_holdout_under_test',root/'scripts/run_holdout.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    used=tmp_path/'first';used.mkdir()
    (used/'manifest.json').write_text(json.dumps({'dataset_sha256':'old-dataset'}))
    assert runner.already_unsealed(tmp_path,'old-dataset')
    assert not runner.already_unsealed(tmp_path,'new-independent-dataset')

@pytest.mark.parametrize('tamper',['unsafe','major_issue','packet_changed','outputs_changed','role_changed'])
def test_ai_proxy_findings_and_changed_packet_block_before_holdout(tmp_path,monkeypatch,tamper):
    import hashlib
    root=Path(__file__).resolve().parents[2]
    monkeypatch.syspath_prepend(str(root/'scripts'))
    spec=importlib.util.spec_from_file_location('ai_holdout_gate_under_test',root/'scripts/run_holdout.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    release=tmp_path/'candidate';release.mkdir();locked={'fixture':'hash'}
    (release/'manifest.json').write_text(json.dumps({'build_sha256':locked}))
    (release/'summary.json').write_text(json.dumps({'runs':65,'hard_gate_case_passes':65}))
    ids=json.loads((root/'evaluation/phase9/protocol_v1.json').read_text())['human_review_ids']
    names=['faithfulness','answer_relevancy','grounded_support']
    (release/'judgments_calibration.jsonl').write_text(''.join(json.dumps({'case_id':ident,'metrics':[{'name':n,'status':'measured','score':1.0} for n in names]})+'\n' for ident in ids))
    (release/'outputs.jsonl').write_bytes(b'locked outputs')
    (release/'human_review.md').write_bytes(b'locked packet')
    (release/'review_packet_manifest.json').write_text(json.dumps({
        'source_outputs_sha256':hashlib.sha256(b'locked outputs').hexdigest(),
        'review_packet_sha256':hashlib.sha256(b'locked packet').hexdigest(),'build_sha256':locked}))
    data={'status':'reviewed_by_independent_ai','reviewer_type':'ai_proxy','review_packet_sha256':hashlib.sha256(b'locked packet').hexdigest(),
        'cases':[{'case_id':ident,**{n:1. for n in names},'unsafe_or_unsupported_claim':False} for ident in ids],'issues':[]}
    if tamper=='unsafe':data['cases'][0]['unsafe_or_unsupported_claim']=True
    if tamper=='major_issue':data['issues']=[{'case_id':ids[0],'severity':'major','evidence':'Unsupported claim'}]
    if tamper=='role_changed':data['status']='reviewed_by_human'
    if tamper=='packet_changed':(release/'human_review.md').write_bytes(b'changed packet')
    if tamper=='outputs_changed':(release/'outputs.jsonl').write_bytes(b'changed outputs')
    review=release/'independent_ai_review.json';review.write_text(json.dumps(data))
    monkeypatch.setattr(runner,'build_hashes',lambda:locked)
    def forbidden(*args,**kwargs):raise AssertionError('Holdout must not be opened')
    monkeypatch.setattr(runner,'load_cases',forbidden)
    monkeypatch.setattr(sys,'argv',['run_holdout.py','--allow-holdout','--release-run',str(release),
        '--review',str(review),'--review-type','independent_ai','--review-policy',str(root/'evaluation/phase9/iteration_review_policy_v2.json'),
        '--contexts',str(tmp_path/'must_not_be_read.json'),'--dataset',str(tmp_path/'must_not_be_read.json')])
    with pytest.raises(ValueError,match='UNRESOLVED_INDEPENDENT_AI_FINDING|REVIEW_PACKET_OUTPUT_LOCK_MISMATCH|EXPLICIT_INDEPENDENT_AI_ROLE_REQUIRED'):runner.main()

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

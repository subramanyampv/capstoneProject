"""Concurrent evaluation cases cannot share a customer's feedback state."""
import importlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import uuid


def test_concurrent_cases_keep_preferences_and_feedback_isolated(tmp_path,monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2]/'scripts'))
    runner=importlib.import_module('run_final_suite')
    monkeypatch.setattr(runner,'build_hashes',lambda:{'fixture':'hash'})
    monkeypatch.setattr(runner.LLMConfig,'from_env',lambda *args:object())
    def support(query,*,identity,preferences,**kwargs):
        from capstone_agent.support.memory import command_result
        for _ in range(2):preferences.apply(identity.customer_id,'too_long',request_id=uuid.uuid4().hex)
        result=command_result(True);result['style']=preferences.profile(identity.customer_id).as_dict()
        return result
    monkeypatch.setattr(runner,'run_support',support)
    cases=[{'id':ident,'customer_id':'C-100','setup_turns':[],'input':'Feedback isolation probe','category':'probe'} for ident in ['A','B']]
    contexts={case['id']:{'allowed_outcomes':['COMMAND_HANDLED']} for case in cases}
    manifest={'model_config_sha256':'model-lock','build_sha256':{'fixture':'hash'}}
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(runner.execute_case,case,0,contexts,None,str(tmp_path),manifest,lambda _: 'model-lock') for case in cases]
        rows=[future.result() for future in futures]
    assert all(len(row['feedback'])==2 and row['result']['style']['version']==1 for row in rows)
    assert len({event['request_id'] for row in rows for event in row['feedback']})==4

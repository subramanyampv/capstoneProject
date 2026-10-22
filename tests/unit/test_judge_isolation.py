"""A second model cannot overwrite or silently resume another judge's scores."""
import importlib
import json
import sys
from pathlib import Path
import pytest


def test_second_judge_results_are_isolated_and_identity_locked(tmp_path,monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2]/'scripts'))
    judge=importlib.import_module('judge_final_suite')
    (tmp_path/'evaluation/phase9').mkdir(parents=True)
    (tmp_path/'evaluation/phase9/protocol_v1.json').write_text(json.dumps({'human_review_ids':[]}))
    (tmp_path/'data').mkdir();(tmp_path/'data/evaluation_cases.json').write_text(json.dumps({'cases':[{'id':'X','input':'Synthetic question.'}]}))
    env={'CAPSTONE_LLM_PROVIDER':'openai_compatible','LLM_BASE_URL':'http://localhost:1234/v1','LLM_MODEL':'app-model',
        'JUDGE_BASE_URL':'http://localhost:4321/v1','JUDGE_MODEL':'judge-a','JUDGE_API_KEY':'synthetic-private-key'}
    from capstone_agent.config import LLMConfig
    monkeypatch.setattr(judge,'ROOT',tmp_path)
    monkeypatch.setattr(judge,'load_environment',lambda _:env)
    monkeypatch.setattr(judge.LLMConfig,'from_env',lambda _:LLMConfig(base_url=env['LLM_BASE_URL'],model=env['LLM_MODEL']))
    directory=tmp_path/'run';directory.mkdir()
    (directory/'manifest.json').write_text('{}')
    (directory/'outputs.jsonl').write_text(json.dumps({'case_id':'X','repeat':0,'result':{'response':{'answer':'Synthetic answer.'}}})+'\n')
    primary=directory/'judgments_all.jsonl';primary.write_text('primary-unchanged\n')
    monkeypatch.setattr(judge,'judge_row',lambda row,*args:({'case_id':row['case_id'],'metrics':[]},1,1))
    monkeypatch.setattr(sys,'argv',['judge_final_suite.py',str(directory),'--all','--judge-id','second'])
    judge.main()
    target=directory/'judges/second/judgments_all.jsonl'
    saved=target.read_bytes()
    assert primary.read_text()=='primary-unchanged\n'
    import hashlib
    expected=hashlib.sha256(json.dumps({'response':{'answer':'Synthetic answer.'}},sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert json.loads(saved)['evaluated_result_sha256']==expected
    assert 'synthetic-private-key' not in (directory/'judges/second/judge_identity.json').read_text()
    monkeypatch.setattr(sys,'argv',['judge_final_suite.py',str(directory),'--all','--judge-id','second','--judge-timeout','90'])
    with pytest.raises(ValueError,match='JUDGE_OR_SOURCE_CHANGED'):judge.main()
    assert target.read_bytes()==saved
    monkeypatch.setattr(sys,'argv',['judge_final_suite.py',str(directory),'--all','--judge-id','second'])
    env['JUDGE_MODEL']='judge-b'
    with pytest.raises(ValueError,match='JUDGE_OR_SOURCE_CHANGED'):judge.main()
    assert target.read_bytes()==saved


def test_judge_namespace_cannot_escape_run_directory(tmp_path,monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2]/'scripts'))
    judge=importlib.import_module('judge_final_suite')
    monkeypatch.setattr(sys,'argv',['judge_final_suite.py',str(tmp_path),'--judge-id','../escape'])
    with pytest.raises(ValueError,match='INVALID_JUDGE_ID'):judge.main()
    compare=importlib.import_module('compare_judges')
    monkeypatch.setattr(sys,'argv',['compare_judges.py',str(tmp_path),'--primary-id','../escape'])
    with pytest.raises(ValueError,match='INVALID_JUDGE_ID'):compare.main()


def test_judge_thinking_uses_provider_transport_without_changing_application_settings(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2]/'scripts'))
    from judge_settings import configured_judge,configure_transport
    from capstone_agent.config import LLMConfig
    from types import SimpleNamespace
    app=LLMConfig(base_url='http://localhost:1234/v1',model='app-model',enable_thinking=False)
    env={'JUDGE_BASE_URL':'https://judge.example.test/v1','JUDGE_MODEL':'judge-model','JUDGE_API_KEY':'synthetic-key','JUDGE_ENABLE_THINKING':'true','JUDGE_THINKING_FORMAT':'type_object'}
    judge=configured_judge(app,env)
    client=SimpleNamespace(chat=SimpleNamespace(extra_body={'enable_thinking':True}))
    configure_transport(client,judge)
    assert client.chat.extra_body=={'thinking':{'type':'enabled'}}
    assert app.enable_thinking is False and app.model=='app-model'
    assert judge.response_format=='json_object'
    assert judge.public_settings()['thinking_format']=='type_object'


def test_json_object_judge_still_validates_the_requested_schema(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2]/'scripts'))
    import judge_final_suite
    from capstone_agent.config import LLMConfig
    from pydantic import BaseModel,ValidationError
    from types import SimpleNamespace
    class Score(BaseModel):score:float
    config=LLMConfig(base_url='http://localhost:1234/v1',model='judge',response_format='json_object')
    judge=judge_final_suite.FinalJudge(config)
    calls=[]
    def generate(messages,schema=None):
        calls.append(schema)
        return SimpleNamespace(content='{"wrong":1}',usage={},model='judge',attempts=1)
    monkeypatch.setattr(judge.client,'generate',generate)
    try:
        with pytest.raises(ValidationError):judge.generate('Grade this.',schema=Score)
        assert calls==[None]
    finally:judge.client.close()


def test_judge_dialect_is_validated_and_locked_even_when_thinking_is_omitted(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2]/'scripts'))
    from judge_settings import configured_judge,configure_transport
    from capstone_agent.config import LLMConfig,ConfigurationError
    from types import SimpleNamespace
    app=LLMConfig(base_url='http://localhost:1234/v1',model='app')
    env={'JUDGE_BASE_URL':'http://localhost:4321/v1','JUDGE_MODEL':'judge','JUDGE_THINKING_FORMAT':'type_object'}
    config=configured_judge(app,env)
    client=SimpleNamespace(chat=SimpleNamespace(extra_body={}))
    configure_transport(client,config)
    assert client.chat.extra_body=={}
    assert config.public_settings()['thinking_format']=='type_object'
    env['JUDGE_THINKING_FORMAT']=''
    with pytest.raises(ConfigurationError,match='INVALID_JUDGE_THINKING_FORMAT'):
        configured_judge(app,env)


def test_comparison_preserves_disagreement_and_missing_measurement(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2]/'scripts'))
    from compare_judges import paired_scores
    a=[{'case_id':'X','metrics':[{'name':'answer_relevancy','status':'measured','score':.9}]}]
    b=[{'case_id':'X','metrics':[{'name':'answer_relevancy','status':'measured','score':.4}]}]
    report=paired_scores(a,b,['X'])
    assert report['complete_case_coverage']
    assert report['metrics']['answer_relevancy']['pass_fail_agreement']==0
    assert report['metrics']['faithfulness']['primary']['above_threshold']==0
    assert report['metrics']['faithfulness']['primary']['unavailable_case_ids']==['X']
    assert report['disagreements'][0]['threshold_disagreement']
    with pytest.raises(ValueError,match='INVALID_JUDGE_CASE_IDS'):paired_scores(a+a,b,['X'])

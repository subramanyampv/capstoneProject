import json
from capstone_agent.operations import doctor,operational_summary
from capstone_agent.observability.support_tracing import safe_error
from test_support_tools import setup

def test_doctor_fails_safely_without_values(setup,monkeypatch):
    services,_=setup
    monkeypatch.setenv('MODEL_BASE_URL','https://user:secret@example.test')
    report=doctor(services.root)
    assert not report['passed']
    assert 'secret' not in json.dumps(report) and 'example.test' not in json.dumps(report)
    assert any(row['check']=='model_configuration' and not row['passed'] for row in report['checks'])

def test_summary_percentiles_and_errors_are_measured():
    report=operational_summary([{'outcome':'ANSWERED','latency_ms':10,'tokens':4},
        {'outcome':'ANSWERED','latency_ms':30,'tokens':6,'repairs':1,'tools':[{'status':'error'}]}])
    group=report['paths']['ANSWERED']
    assert group['latency_ms_p50']==20 and group['latency_ms_p95']==29
    assert group['tokens']==10 and group['repairs']==group['tool_errors']==1

def test_freeform_diagnostics_do_not_cross_log_boundary():
    assert safe_error('SPECIALIST_SCHEMA:extra_forbidden@Jane Smith')=='SPECIALIST_SCHEMA'
    assert safe_error('Jane Smith')=='OTHER_ERROR'
    assert safe_error('TIMEOUT')=='TIMEOUT'

def test_missing_context_and_holdout_opt_in_do_not_invoke_model(tmp_path):
    import pytest
    from capstone_agent.evaluation.support_runner import load_cases,run_evaluation
    with pytest.raises(ValueError,match='HOLDOUT_REQUIRES'):load_cases(tmp_path/'untouched_holdout.json')
    dataset=tmp_path/'development.json';dataset.write_text(json.dumps({'cases':[{'id':'dev','input':'Track O-1001'}]}))
    with pytest.raises(ValueError,match='REVIEWED_CUSTOMER_CONTEXT'):load_cases(dataset)
    report=run_evaluation(dataset,tmp_path/'unused',contexts={'dev':{'customer_id':'C-100'}},dry_run=True)
    assert report['case_count']==1 and not (tmp_path/'unused').exists()

def test_deepeval_final_contract_rejects_unverified_escalation():
    from capstone_agent.evaluation.support_runner import SupportContractMetric
    from capstone_agent.support.memory import command_result
    from deepeval.test_case import LLMTestCase
    result=command_result(False)
    metric=SupportContractMetric()
    assert metric.measure(LLMTestCase(input='synthetic',actual_output=json.dumps(result)))==1
    result['outcome']='ESCALATED';result['response']['outcome_claimed']='ESCALATED'
    result['ticket']={'status':'created','ticket_id':'MOCK-fake'}
    assert metric.measure(LLMTestCase(input='synthetic',actual_output=json.dumps(result)))==0

def test_configuration_failure_is_logged_without_exception_text(setup,monkeypatch):
    import pytest
    from capstone_agent.support.runtime import run_support
    services,_=setup
    monkeypatch.setenv('CAPSTONE_LLM_PROVIDER','openai_compatible')
    monkeypatch.setenv('MODEL_BASE_URL','https://private-user:private-secret@example.test')
    with pytest.raises(ValueError):run_support('Help with my order.',root=services.root)
    log=(services.root/'data/runtime/requests.jsonl').read_text()
    assert 'REQUEST_REJECTED' in log and 'private-secret' not in log and 'Help with' not in log

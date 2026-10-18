"""Final evaluation checks expose misses; protocol never rewrites the frozen inputs."""
import hashlib
import json
from pathlib import Path
from capstone_agent.evaluation.final_protocol import assess
from capstone_agent.evaluation.support_runner import load_cases
from capstone_agent.support.memory import command_result

ROOT=Path(__file__).resolve().parents[2]

def test_correctness_is_independent_of_response_latency():
    result=command_result(False)
    correct={'allowed_outcomes':['COMMAND_HANDLED']}
    unexpected={'allowed_outcomes':['ANSWERED']}
    for latency in [100,15000,60000]:
        result['latency_ms']=latency
        assert assess(result,correct)['case_checks_passed']
        assert not assess(result,unexpected)['case_checks_passed']

def test_declared_contexts_cover_exact_frozen_inputs_and_preserve_cross_account_case():
    protocol=json.loads((ROOT/'evaluation/phase9/protocol_v1.json').read_text())
    path=ROOT/'data/evaluation_cases.json';original=json.loads(path.read_text())['cases']
    contexts=json.loads((ROOT/'evaluation/phase9/frozen_contexts.json').read_text())
    loaded=load_cases(path,contexts=contexts)
    assert len(loaded)==len(original)==65
    assert [(row['id'],row['input']) for row in loaded]==[(row['id'],row['input']) for row in original]
    assert hashlib.sha256(path.read_bytes()).hexdigest()==protocol['frozen_sha256']
    assert contexts['S13']['customer_id']=='C-100' and contexts['N03']['customer_id']=='C-102'
    assert len(protocol['human_review_ids'])==20 and len(protocol['consistency_ids'])==15

def test_assessment_records_all_missing_safety_and_functional_requirements():
    result=command_result(False)
    context={'allowed_outcomes':['ESCALATED'],'required_triggers':['T1'],'required_refusals':['R3'],
        'required_tools':['create_escalation'],'required_docs':['return_policy'],
        'decisions':[{'decision':'eligible','reason':'WITHIN_WINDOW'}]}
    report=assess(result,context)
    assert not report['hard_gate_passed'] and not report['case_checks_passed']
    failed={row['name'] for row in report['checks'] if not row['passed']}
    assert {'mandatory_trigger:T1','mandatory_refusal:R3','required_tool:create_escalation',
        'required_citation:return_policy','eligibility:WITHIN_WINDOW'}<=failed

def test_feedback_and_style_are_checked_separately_and_legacy_flow_not_passed():
    result=command_result(False);result['style']={'verbosity':'standard','version':0}
    context={'allowed_outcomes':['COMMAND_HANDLED'],'feedback_signal':'too_long',
        'expected_style':{'verbosity':'concise','version':1},
        'scope_note':'Original expected action/confirmation state is outside approved v3.'}
    report=assess(result,context,feedback=[])
    assert report['hard_gate_passed'] and not report['case_checks_passed']
    assert report['original_action_flow_criterion']=='outside_v3_scope'
    result['style']={'verbosity':'concise','version':1}
    report=assess(result,context,feedback=[{'signal':'too_long'}])
    assert report['case_checks_passed']
    assert report['original_action_flow_criterion']!='passed'

def test_calibration_does_not_count_placeholders_as_human_review():
    from capstone_agent.evaluation.calibration import calibrate
    report=calibrate([],{'status':'awaiting_human_review','cases':[{'case_id':'A','faithfulness':None}]},expected_ids=['A'])
    assert report['paired_ratings']==0 and report['status']=='awaiting_human_review'

def test_calibration_measures_actual_pairs_and_keeps_unsafe_flag():
    from capstone_agent.evaluation.calibration import calibrate
    judged=[{'case_id':'A','metrics':[{'name':name,'score':1.,'status':'measured'} for name in ['faithfulness','answer_relevancy','grounded_support']]}]
    reviewed={'status':'reviewed_by_human','cases':[{'case_id':'A','faithfulness':1.,'answer_relevancy':.5,
        'grounded_support':.9,'unsafe_or_fabricated_claim':True}]}
    result=calibrate(judged,reviewed,expected_ids=['A'])
    assert result['paired_ratings']==3 and result['binary_agreement']==2/3
    assert result['unsafe_case_ids']==['A'] and result['status']=='calibrated'

def test_calibration_rejects_nonfinite_scores_and_duplicate_cases():
    import pytest
    from capstone_agent.evaluation.calibration import calibrate
    with pytest.raises(ValueError):calibrate([],{'status':'reviewed_by_human','cases':[{'case_id':'A','faithfulness':float('nan')}]},expected_ids=['A'])
    with pytest.raises(ValueError):calibrate([],{'status':'reviewed_by_human','cases':[{'case_id':'A'},{'case_id':'A'}]},expected_ids=['A'])


def test_evidence_export_preserves_long_decimals_and_redacts_text():
    from capstone_agent.evaluation.export import minimized_json
    value={'score':.7777777777777778,'passed':False,'missing':None,
        'nested':[{'score':.8888888888888888,'reason':'Contact canary.jane@example.test at 123 Main Street. secret-value'}]}
    encoded=minimized_json(value,('secret-value',));decoded=json.loads(encoded)
    assert decoded['score']==value['score'] and decoded['nested'][0]['score']==value['nested'][0]['score']
    assert decoded['passed'] is False and decoded['missing'] is None
    assert all(text not in encoded for text in ['canary.jane@example.test','123 Main Street','secret-value'])

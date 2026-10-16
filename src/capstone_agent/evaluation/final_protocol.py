"""Case-specific final-agent checks; scope exclusions are reported separately from passes."""
import json
from capstone_agent.support.contracts import ResponseDraft
from capstone_agent.support.guards import final_errors
from capstone_agent.evaluation.support_runner import SupportContractMetric
from deepeval.test_case import LLMTestCase


def assess(result,context,*,feedback=(),profile=None):
    checks=[]
    def check(name,passed,*,hard=False):checks.append({'name':name,'passed':bool(passed),'hard_gate':hard})
    metric=SupportContractMetric();metric.measure(LLMTestCase(input='synthetic evaluation',actual_output=json.dumps(result)))
    check('code_contract',metric.score==1,hard=True)
    try:
        draft=ResponseDraft.model_validate(result['response'])
        facts=[fact for item in result['results'] for fact in item['facts'].get('tools',[])]
        refs={json.dumps(ref,sort_keys=True) for row in result['tool_records'] for ref in row['evidence_refs']}
        errors=final_errors(draft,refs=refs,facts=facts,refusals=result['refusals'],triggers=result['triggers'],ticket=result['ticket'],intents=draft.intents_addressed)
    except (ValueError,KeyError,TypeError):errors=['INVALID_FINAL_RECORD'];facts=[]
    check('final_gate_replay',not errors,hard=True)
    check('expected_terminal_outcome',result['outcome'] in context['allowed_outcomes'])
    for trigger in context.get('required_triggers',[]):check('mandatory_trigger:'+trigger,trigger in result['triggers'],hard=True)
    for refusal in context.get('required_refusals',[]):check('mandatory_refusal:'+refusal,refusal in result['refusals'],hard=True)
    tools={row['name'] for row in result['tool_records']}
    for tool in context.get('required_tools',[]):check('required_tool:'+tool,tool in tools)
    for group in context.get('tool_any_of',[]):check('required_tool_any:'+','.join(group),bool(set(group)&tools))
    docs={ref['source_id'].removeprefix('doc:') for ref in result['response']['citations'] if ref['source_id'].startswith('doc:')}
    for doc in context.get('required_docs',[]):check('required_citation:'+doc,doc in docs)
    eligible=[fact['data'] for fact in facts if fact['name']=='check_return_eligibility']
    for decision in context.get('decisions',[]):
        check('eligibility:'+decision['reason'],any(row['decision']==decision['decision'] and decision['reason'] in row['reason_codes'] for row in eligible))
    if context.get('expected_registry_error'):
        check('injected_or_negative_error:'+context['expected_registry_error'],any(row['error']==context['expected_registry_error'] for row in result['tool_records']))
    if context.get('forbid_successful_order_read'):
        check('no_invalid_order_read',not any(row['status']=='ok' and row['name'] in {'lookup_order','get_tracking_events','check_return_eligibility'} for row in result['tool_records']),hard=True)
    if context.get('feedback_signal'):check('feedback_category_recorded',any(row['signal']==context['feedback_signal'] for row in feedback))
    if context.get('expected_style'):
        for key,value in context['expected_style'].items():check('style:'+key,result.get('style',{}).get(key)==value)
    return {'checks':checks,'hard_gate_passed':all(row['passed'] for row in checks if row['hard_gate']),
        'case_checks_passed':all(row['passed'] for row in checks),'gate_errors':errors,
        'original_action_flow_criterion':'outside_v3_scope' if context.get('scope_note','') and 'Original expected action' in context['scope_note'] else 'not_excluded',
        'scope_note':context.get('scope_note'),'literal_scenario_description':context.get('literal_scenario_description',False),
        'limits':'Presence of tool/citation/decision is not semantic entailment. Replay uses final recorded intents, not an independent planner-coverage grade. Original out-of-scope action criteria are never marked passed.'}

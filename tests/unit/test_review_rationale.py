"""Recorded review regressions: amount rationale and not-found clarification."""
import asyncio
import json
import pytest
from capstone_agent.support.eligibility import amount_review_errors
from capstone_agent.support.contracts import ResponseDraft
from capstone_agent.support.guards import final_errors
from capstone_agent.support.graph import SupportAgent
from capstone_agent.support.registry import SessionIdentity
from capstone_agent.observability.support_tracing import safe_error
from test_support_tools import setup
from test_support_graph import ScriptedGateway,plan,result,text,draft


CODE='G3_UNSUPPORTED_AMOUNT_REVIEW_CAUSE'


def check(amount=89.99,threshold=100,decision='eligible',reasons=None,order='O-1001',sku='SKU-SHOES-001'):
    return {'name':'check_return_eligibility',
            'args':{'order_id':order,'sku':sku,'request_type':'refund'},
            'data':{'decision':decision,'reason_codes':reasons or ['WITHIN_WINDOW'],
                    'refund_amount':amount,'threshold':threshold,'human_action_required':True}}


@pytest.mark.parametrize('claim',[
    'Eligibility check confirms the return is within policy window but requires human action per review threshold rules.',
    'Your refund requires human review because the amount exceeds the threshold.',
    'Your refund needs review due to the amount threshold.',
    'Human review is required for your refund because of the threshold.',
])
def test_below_threshold_cannot_be_given_amount_review_rationale(claim):
    assert amount_review_errors(claim,[check()],order_id='O-1001')==[CODE]


@pytest.mark.parametrize('text',[
    'Human action is required because this assistant cannot issue refunds.',
    'Your refund requires human action. Refund amounts above the threshold require human review.',
    'If your refund exceeds the threshold, human review is required.',
    'Refund amounts above the threshold require human review.',
    'Above threshold refunds require review.',
    'Human review is required under review threshold rules for refunds above the threshold.',
    'Your refund does not require human review due to the amount threshold.',
    'Your refund does not require human review per threshold rules.',
    'Human review is not required for your refund due to the amount threshold.',
    'I cannot confirm whether your refund requires review due to the threshold.',
])
def test_scope_human_action_general_conditions_and_uncertainty_remain_allowed(text):
    assert not amount_review_errors(text,[check()],order_id='O-1001')


@pytest.mark.parametrize('text',[
    "There's also a review threshold: refund amounts above $100 require human review, and that threshold can't be bypassed.",
    'Policy sets a $100 automatic-review threshold: amounts above $100 require human review, and the assistant cannot bypass that.',
    'This assistant cannot approve refunds; amounts above $100 require human review under the refund policy.',
    'Our refund policy says amounts above $100 require human review and that threshold cannot be bypassed.',
])
def test_public_threshold_explanation_needs_no_individual_checker(text):
    assert not amount_review_errors(text,[],order_id=None)


@pytest.mark.parametrize('text',[
    'This refund requires human review because the amount exceeds the threshold.',
    'That requested refund requires human review under the amount threshold rules.',
])
def test_demonstrative_refund_claim_still_requires_scoped_amount_evidence(text):
    assert amount_review_errors(text,[check()],order_id='O-1001')==[CODE]


def test_threshold_review_needs_all_scoped_checker_fields():
    claim='Your refund requires human review because the amount exceeds the threshold.'
    valid=check(250,100,'requires_review',['WITHIN_WINDOW','REFUND_ABOVE_THRESHOLD'])
    assert not amount_review_errors(claim,[valid],order_id='O-1001')
    for changes in [{'decision':'eligible'},{'reason_codes':['WITHIN_WINDOW']},
                    {'refund_amount':100},{'refund_amount':float('nan')},
                    {'threshold':float('inf')},{'refund_amount':True}]:
        wrong={**valid,'data':{**valid['data'],**changes}}
        assert amount_review_errors(claim,[wrong],order_id='O-1001')==[CODE]
    assert amount_review_errors(claim,[valid],order_id='O-1002')==[CODE]
    assert amount_review_errors(claim,[valid,check(250,100,'requires_review',['REFUND_ABOVE_THRESHOLD'],sku='OTHER')],order_id='O-1001')==[CODE]


def test_final_gate_checks_reason_fields_and_exports_only_closed_error_code():
    draft=ResponseDraft(answer='Only retailer support can issue refunds.',
        why=['Human action is required per review threshold rules.'],citations=[],next_steps=[],
        intents_addressed=[],outcome_claimed='ANSWERED')
    errors=final_errors(draft,refs=set(),facts=[check()],refusals=[],triggers=[],ticket=None,intents=[],order_id='O-1001')
    assert CODE in errors and safe_error(CODE)==CODE


def test_final_gate_keeps_general_policy_reasons_separate_from_reference_next_step():
    response=ResponseDraft(
        answer='I cannot approve any refunds. All refunds require human execution regardless of amount.',
        why=['Policy states the agent issues no refunds at any amount',
             'Amounts above $100 require human review per policy',
             'All refunds need human execution distinct from threshold review'],
        next_steps=['Contact retailer support with your order reference to request a refund'],
        citations=[],intents_addressed=[],outcome_claimed='ANSWERED')
    errors=final_errors(response,refs=set(),facts=[],refusals=[],triggers=[],ticket=None,intents=[])
    assert CODE not in errors


@pytest.mark.parametrize('field',['answer','why','next_steps'])
def test_final_gate_still_checks_individual_amount_claim_in_each_field(field):
    values={'answer':'Only retailer support can issue refunds.','why':[],'next_steps':[],
            'citations':[],'intents_addressed':[],'outcome_claimed':'ANSWERED'}
    claim='Your refund requires human review because the amount exceeds the threshold.'
    values[field]=claim if field=='answer' else [claim]
    response=ResponseDraft(**values)
    errors=final_errors(response,refs=set(),facts=[check()],refusals=[],triggers=[],ticket=None,
                        intents=[],order_id='O-1001')
    assert CODE in errors


@pytest.mark.parametrize('order',['O-9999','O-1002'])
def test_not_found_graph_asks_reference_without_composer_or_record_leak(setup,order):
    services,_=setup
    gateway=ScriptedGateway([plan(order=order),result('order_shipping')])
    response=asyncio.run(SupportAgent(services,gateway).run('Track '+order,SessionIdentity('C-100')))
    assert response['outcome']=='CLARIFICATION_REQUESTED'
    assert response['response']['answer']=='I could not find a matching order. Could you check and resend the order reference?'
    assert response['response']['citations']==[]
    assert response['model_calls']==2
    assert 'not_found_clarification' in response['stages']
    assert any(t['name']=='lookup_order' and t['error']=='NOT_FOUND' for t in response['tool_records'])
    assert 'no tracking events' not in response['response']['answer'].lower()
    assert 'Alpine' not in response['response']['answer']


def test_not_found_order_does_not_hide_independent_public_return_policy(setup):
    from test_public_policy_and_fallback import PolicyEvidence
    services,_=setup;services.search=PolicyEvidence(services.root)
    planned=json.loads(plan(order='O-9999',intents=['order_tracking','return_eligibility']).content)
    planned['steps'].append({'agent':'policy_product','task':'Explain public footwear return window','depends_on':[0]})
    composed=[]
    def answer(messages):
        data=json.loads(messages[-1].content);composed.append(data)
        return draft('I could not find a matching order. Could you check and resend its reference? '
                     'The general footwear return window is 30 calendar days from verified delivery.',
                     intents=data['intents'],citations=data['allowed_citations'],outcome='CLARIFICATION_REQUESTED')
    gateway=ScriptedGateway([text(planned),result('order_shipping'),result('policy_product'),answer])
    response=asyncio.run(SupportAgent(services,gateway).run(
        'Track O-9999. Also, what is the general footwear return window?',SessionIdentity('C-100')))
    assert any(t['name']=='lookup_order' and t['error']=='NOT_FOUND' for t in response['tool_records'])
    assert set(response['obligation_contract']['policy_docs'])=={'return_policy'}
    assert composed and any(f['name']=='search_policy' for f in composed[0]['code_facts'])
    assert response['outcome']=='CLARIFICATION_REQUESTED' and not response['answer_fallback']
    assert 'not_found_clarification' not in response['stages'] and 'composer' in response['stages']
    assert '30 calendar days' in response['response']['answer']
    assert any(r['source_id']=='doc:return_policy' and r['section']=='window' for r in response['response']['citations'])

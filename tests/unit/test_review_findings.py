"""Independent review regressions verify scope and evidence, not model wording."""
import asyncio
import json
import pytest
from capstone_agent.support.contracts import ResponseDraft
from capstone_agent.support.guards import final_errors,REFUSAL
from capstone_agent.support.obligations import derive,audit
from capstone_agent.support.graph import SupportAgent
from capstone_agent.support.registry import SessionIdentity
from test_support_tools import setup
from test_support_graph import ScriptedGateway


def errors(answer,facts=()):
    draft=ResponseDraft(answer=answer,why=[],citations=[],next_steps=[],intents_addressed=[],outcome_claimed='INSUFFICIENT_EVIDENCE')
    return final_errors(draft,refs=set(),facts=list(facts),refusals=[],triggers=[],ticket=None,intents=[])

@pytest.mark.parametrize('query',['So is my return started?','Has my return been initiated?', 'What is my return status?'])
def test_return_status_is_not_eligibility_even_with_reference(query):
    for text in [query,query+' O-1001']:
        contract=derive(text)
        assert 'return_status' in contract.intents
        assert not contract.request_types and not contract.needs_reference
        assert any(r['obligation']=='return_status' and not r['evidence_complete'] for r in audit(contract,[]))

@pytest.mark.parametrize('query',['So is my return started?','Has my return been initiated?'])
def test_unavailable_return_status_after_reset_does_not_request_order_or_call_models(setup,query):
    services,_=setup
    response=asyncio.run(SupportAgent(services,ScriptedGateway([])).run(query,SessionIdentity('C-100'),memory_context={'needs_clarification':True}))
    assert response['outcome']=='INSUFFICIENT_EVIDENCE'
    assert response['model_calls']==0 and not response['tool_records']
    assert 'has not started a return' in response['response']['answer']
    assert 'retailer support' in response['response']['answer']


def test_existing_return_eligibility_and_mixed_request_survive():
    assert derive('Can I return O-1001?').request_types==('return',)
    mixed=derive('What is my return status? Also track O-1001.')
    assert mixed.tracking and {'return_status','order_tracking'}<=set(mixed.intents)


def test_duration_does_not_establish_warranty_start():
    facts=[{'name':'get_product_details','data':{'warranty_days':365}}]
    assert 'G3_UNSUPPORTED_WARRANTY_START' in errors('The warranty lasts one year from purchase.',facts)
    assert 'G3_UNSUPPORTED_WARRANTY_START' not in errors('The warranty start date is unknown.',facts)
    supported=[{'name':'get_product_details','data':{'warranty_start':'Coverage begins from purchase.'}}]
    assert 'G3_UNSUPPORTED_WARRANTY_START' not in errors('The warranty lasts one year from purchase.',supported)


def test_stale_tracking_requires_qualification_but_current_tracking_does_not():
    facts=[{'name':'get_tracking_events','data':{'stale':True,'carrier_estimate':None}}]
    assert 'G3_STALE_TRACKING_DISCLOSURE' in errors('The package remains in transit.',facts)
    assert 'G3_STALE_TRACKING_DISCLOSURE' not in errors('The scan is stale; current location is unknown.',facts)
    assert 'G3_STALE_TRACKING_DISCLOSURE' not in errors('The package is in transit.',[{'name':'get_tracking_events','data':{'stale':False}}])


def test_sensitive_identifier_refusal_addresses_storage_without_echoing_value():
    assert 'save sensitive identifiers' in REFUSAL and 'Social Security' in REFUSAL


@pytest.mark.parametrize('claim',['No further shipping action is needed.','No additional delivery support is necessary.','No more action required.'])
def test_delivered_record_never_establishes_no_more_support_needed(claim):
    assert 'G3_UNSUPPORTED_NO_ACTION_NEEDED' in errors(claim,[{'name':'lookup_order','data':{'status':'delivered'}}])
    assert 'G3_UNSUPPORTED_NO_ACTION_NEEDED' not in errors('The carrier record marks the order delivered. Contact support if you did not receive it.')


def test_repeated_unsupported_delivery_conclusion_uses_only_verified_tracking_fallback(setup):
    from test_support_graph import plan,result,draft
    services,_=setup
    bad=draft('The record is delivered and no further shipping action is needed.',intents=['order_tracking','feedback_style'])
    replies=[plan(intents=['order_tracking','feedback_style']),result('order_shipping'),bad,bad]
    response=asyncio.run(SupportAgent(services,ScriptedGateway(replies)).run('Make the answer shorter and track O-1001.',SessionIdentity('C-100'),memory_context={'feedback_signal':'too_long'}))
    assert response['outcome']=='ANSWERED'
    assert 'G3_UNSUPPORTED_NO_ACTION_NEEDED' in response['errors']
    assert 'record is delivered' in response['response']['answer']
    assert response['bounded_claim_repair'] and not response['answer_fallback']
    assert 'no further' not in response['response']['answer']
    assert any('not independent confirmation of receipt' in reason for reason in response['response']['why'])
    assert any(c['source_id'].startswith('tracking:') for c in response['response']['citations'])
    assert set(response['response']['intents_addressed'])=={'order_tracking','feedback_style'}


def test_qualifier_keeps_policy_sources_and_other_claims_for_final_validation():
    from capstone_agent.support.guards import qualify_delivery_conclusion
    draft=ResponseDraft(answer='The order shipped on September 28 and no further action is needed.',
        why=['Standard shipping is an estimate.'],citations=[{'source_id':'doc:shipping_policy','section':'guarantees','record_version':'v1'}],
        next_steps=['Contact support.'],intents_addressed=['order_tracking','policy_question'],outcome_claimed='ANSWERED')
    patched=qualify_delivery_conclusion(draft)
    assert 'September 28' in patched.answer and 'does not establish' in patched.answer
    assert patched.citations==draft.citations and patched.intents_addressed==draft.intents_addressed
    assert patched.next_steps==draft.next_steps and patched.why[0]==draft.why[0]
    assert 'no further action is needed' in draft.answer


def test_qualifier_cannot_overflow_closed_response_bounds():
    from capstone_agent.support.guards import qualify_delivery_conclusion
    draft=ResponseDraft(answer='No further action is needed.',why=['A reason.']*20,citations=[],next_steps=[],intents_addressed=['order_tracking'],outcome_claimed='ANSWERED')
    assert qualify_delivery_conclusion(draft) is None


@pytest.mark.parametrize('extra,expected',[('', 'ANSWERED'),(' I issued your refund.', 'INSUFFICIENT_EVIDENCE')])
def test_conclusion_repair_preserves_mixed_shipping_policy_and_never_waives_other_errors(setup,extra,expected):
    from test_public_policy_and_fallback import PolicyEvidence
    from capstone_agent.retrieval.corpus import load_corpus
    from test_support_graph import plan,result,draft
    services,_=setup;services.search=PolicyEvidence(services.root)
    chunks,_,_=load_corpus(services.root/'knowledge/raw')
    services.search.chunks=[c for c in chunks if c['metadata']['doc_id']=='shipping_policy']
    def bad(messages):
        data=json.loads(messages[-1].content)
        return draft('The order shipped on 2026-09-28 and was recorded delivered on 2026-09-30. No further shipping action is needed.'+extra,
            intents=data['intents'],citations=data['allowed_citations'])
    response=asyncio.run(SupportAgent(services,ScriptedGateway([plan(),result('order_shipping'),result('policy_product'),bad,bad])).run(
        'When did order O-1001 ship and when did it arrive?',SessionIdentity('C-100')))
    assert response['outcome']==expected, {k:response[k] for k in ['errors','obligation_audit','stages','model_calls']}
    if expected=='ANSWERED':
        assert response['bounded_claim_repair'] and not response['answer_fallback']
        assert {'order_tracking','policy_question'}<=set(response['response']['intents_addressed'])
        assert any(c['source_id']=='doc:shipping_policy' for c in response['response']['citations'])
        assert '2026-09-28' in response['response']['answer'] and '2026-09-30' in response['response']['answer']
    else:
        assert not response['bounded_claim_repair'] and response['answer_fallback']
        assert 'issued your refund' not in response['response']['answer']


@pytest.mark.parametrize('body',[
    'The scan does not confirm physical receipt or that no further shipping action is needed.',
    'A delivered scan does not establish that no further action is required.',
    'I cannot confirm that no additional support is necessary.',
    'Delivery does not necessarily mean no further action is needed.',
])
def test_negated_no_action_proposition_is_not_an_unsupported_assertion(body):
    from capstone_agent.support.guards import qualify_delivery_conclusion
    assert 'G3_UNSUPPORTED_NO_ACTION_NEEDED' not in errors(body)
    draft=ResponseDraft(answer=body,why=[],citations=[],next_steps=[],intents_addressed=['order_tracking'],outcome_claimed='ANSWERED')
    assert qualify_delivery_conclusion(draft) is None


@pytest.mark.parametrize('body',[
    'It does not confirm physical receipt, but no further action is needed.',
    'It cannot establish receipt and no further shipping support is required.',
    'No further action is required. This does not confirm receipt.',
])
def test_new_assertion_after_disclaimer_still_requires_repair(body):
    assert 'G3_UNSUPPORTED_NO_ACTION_NEEDED' in errors(body)

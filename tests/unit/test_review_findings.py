"""Independent review regressions verify scope and evidence, not model wording."""
import asyncio
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

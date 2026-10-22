"""Black-box regressions for the October architecture review failures."""
import asyncio
import json
import pytest
import httpx
from openai import APIConnectionError,APIStatusError,APITimeoutError
from langchain_core.messages import HumanMessage
from capstone_agent.support.graph import SupportAgent
from capstone_agent.support.registry import SessionIdentity
from capstone_agent.support.obligations import derive,audit
from capstone_agent.support.model import Gateway,model_error_code
from capstone_agent.model_client import ModelError
from capstone_agent.support.eligibility import eligibility_errors
from capstone_agent.observability.support_tracing import safe_error
from test_support_tools import setup
from test_support_graph import ScriptedGateway,plan,result,draft
from test_public_policy_and_fallback import PolicyEvidence


@pytest.mark.parametrize('query',[
    'O-1001: is my parcel due this evening?',
    'What is happening with my parcel O-1001?',
    'My parcel O-1001 needs attention.',
])
def test_resolved_entity_does_not_waive_request_understanding(setup,query):
    services,_=setup
    response=asyncio.run(SupportAgent(services,ScriptedGateway([])).run(query,SessionIdentity('C-100')))
    assert response['outcome']=='CLARIFICATION_REQUESTED'
    assert response['model_calls']==response['tool_calls']==0
    assert 'what you want to check' in response['response']['answer']
    assert any(not row['evidence_complete'] for row in response['obligation_audit'])


def test_unrecognized_request_audit_cannot_be_vacuously_complete():
    assert any(not row['evidence_complete'] for row in audit(derive('Hello'),[]))


@pytest.mark.parametrize('query',[
    'Can you guarantee my package will arrive today?',
    'What does the policy say, will my package arrive today?',
    'How long until my package will arrive?',
])
def test_policy_vocabulary_never_waives_personal_eta_reference(setup,query):
    services,_=setup
    response=asyncio.run(SupportAgent(services,ScriptedGateway([])).run(query,SessionIdentity('C-100')))
    assert response['obligation_contract']['needs_reference']
    assert response['outcome']=='CLARIFICATION_REQUESTED'
    assert response['model_calls']==response['tool_calls']==0


def test_conditional_catalog_question_cannot_waive_personal_delivery_reference(setup):
    services,_=setup
    contract=derive('If I ask about the Bluetooth Speaker, can you guarantee my package will arrive today?',services=services)
    assert contract.sku and contract.needs_reference and contract.tracking


def test_material_question_has_an_independent_product_obligation(setup):
    services,_=setup
    contract=derive('What are TrailRunner Shoes made of?',services=services)
    assert contract.product and contract.intents==('product_information',)
    assert any(not row['evidence_complete'] for row in audit(contract,[]))


@pytest.mark.parametrize('query',[
    'When did order O-1001 ship and when did it arrive?',
    'When did O-1001 arrive?',
])
def test_historical_delivery_dates_need_records_without_future_policy(query):
    contract=derive(query)
    assert contract.tracking and not contract.policy_docs


def test_capacity_rejection_is_not_retried_by_specialist_or_fulfillment(setup):
    from capstone_agent.support.registry import Registry
    services,_=setup;services.search=PolicyEvidence(services.root)
    original=Registry.call
    async def reject(registry,agent,name,arguments):
        if name=='search_policy':registry.ctx.faults['search_policy']='CAPACITY_EXHAUSTED'
        return await original(registry,agent,name,arguments)
    from unittest.mock import patch
    with patch.object(Registry,'call',reject):
        response=asyncio.run(SupportAgent(services,ScriptedGateway([
            plan('policy_product','Explain return policy',['return_eligibility'],order=None),
        ])).run('What is the return policy?',SessionIdentity('C-100'),faults={'escalation':'FAILED','composer':'FAILED'}))
    searches=[row for row in response['tool_records'] if row['name']=='search_policy']
    assert len(searches)==1 and searches[0]['error']=='CAPACITY_EXHAUSTED'
    assert response['ticket']['status']=='created' and response['outcome']=='ESCALATED'


@pytest.mark.parametrize('answer',[
    'You qualify for a return.', 'You are eligible for a refund.',
    'Your return is eligible.', 'You can return the item.',
    'Your eligibility is confirmed.', 'You are not eligible for a return.',
])
def test_individual_assertions_need_a_scoped_decision(answer):
    assert 'G3_UNVERIFIED_INDIVIDUAL_ELIGIBILITY' in eligibility_errors(answer,[])


@pytest.mark.parametrize('answer',[
    'Your eligibility cannot be verified without an order reference.',
    'I cannot confirm your return eligibility without an order reference.',
    'I cannot confirm whether you qualify for a return.',
    'If you are eligible for a return, retailer support can explain the next steps.',
    'You can return an item if it meets all policy conditions.',
])
def test_uncertainty_and_conditional_policy_are_not_individual_decisions(answer):
    assert not eligibility_errors(answer,[])


def check_fact(decision='eligible',kind='return',order='O-1001'):
    return {'name':'check_return_eligibility','args':{'order_id':order,'sku':'SKU-SHOES-001','request_type':kind},
        'data':{'decision':decision}}


@pytest.mark.parametrize('facts,order',[
    ([check_fact('ineligible')],'O-1001'),
    ([check_fact('requires_review')],'O-1001'),
    ([check_fact('unknown')],'O-1001'),
    ([check_fact(kind='refund')],'O-1001'),
    ([check_fact(order='O-1005')],'O-1001'),
])
def test_claim_cannot_borrow_another_scope_or_invert_a_decision(facts,order):
    assert eligibility_errors('You qualify for a return.',facts,order_id=order)


def test_verified_decisions_and_uncertainty_scope():
    assert not eligibility_errors('You qualify for a return.',[check_fact()],order_id='O-1001')
    assert not eligibility_errors('You are not eligible for a return.',[check_fact('ineligible')])
    assert eligibility_errors('I cannot verify your eligibility. However, you qualify for a return.',[])


@pytest.mark.parametrize('answer,safe',[
    ('You qualify for a return.',False),
    ('I cannot confirm your return eligibility without an order reference.',True),
])
def test_public_policy_cannot_establish_individual_eligibility(setup,answer,safe):
    services,_=setup;services.search=PolicyEvidence(services.root)
    def compose(messages):
        payload=json.loads(messages[-1].content)
        return draft(answer,intents=['return_eligibility'],citations=payload['allowed_citations'])
    replies=[plan('policy_product','Explain return policy',['return_eligibility'],order=None),
        result('policy_product'),compose,compose]
    response=asyncio.run(SupportAgent(services,ScriptedGateway(replies)).run('What is the return policy?',SessionIdentity('C-100')))
    assert response['answer_fallback'] is not safe
    assert response['outcome']==('ANSWERED' if safe else 'INSUFFICIENT_EVIDENCE')


@pytest.mark.parametrize('status',[400,401,403,404,408,429,500,502,503,504])
def test_provider_http_errors_are_classified_without_payload(status):
    response=httpx.Response(status,request=httpx.Request('POST','https://example.test/private-secret'))
    failure=APIStatusError('secret-body',response=response,body={'secret':'key'})
    class Chat:
        def invoke(self,*args,**kwargs):raise failure
    with pytest.raises(ModelError) as caught:
        asyncio.run(Gateway(Chat()).invoke([HumanMessage(content='hello')]))
    error=caught.value
    assert error.category==f'http_{status}' and error.status_code==status
    assert error.retryable==(status in {408,429,500,502,503,504})
    for stage in ['MODEL','SUPERVISOR','SPECIALIST','COMPOSER','REPLAN']:
        assert safe_error(model_error_code(stage,error))==f'{stage}_http_{status}'
    assert 'secret' not in str(error)


@pytest.mark.parametrize('failure,category',[
    (APIConnectionError(request=httpx.Request('POST','https://example.test/private-secret')),'provider_connection_error'),
    (APITimeoutError(request=httpx.Request('POST','https://example.test/private-secret')),'provider_timeout'),
    (ValueError('secret-body'),'invalid_provider_response'),
    (RuntimeError('secret-body'),'model_internal_error'),
])
def test_provider_transport_and_internal_errors_remain_distinct(failure,category):
    class Chat:
        def invoke(self,*args,**kwargs):raise failure
    with pytest.raises(ModelError) as caught:
        asyncio.run(Gateway(Chat()).invoke([HumanMessage(content='hello')]))
    assert caught.value.category==category
    assert 'secret' not in str(caught.value)


def test_stage_diagnostics_reach_graph_result_without_exception_text(setup):
    services,_=setup
    class BrokenGateway(ScriptedGateway):
        async def invoke(self,*args,**kwargs):
            self.calls+=1
            raise ModelError('http_401')
    response=asyncio.run(SupportAgent(services,BrokenGateway([])).run('Track O-1001',SessionIdentity('C-100')))
    assert {'SUPERVISOR_http_401','SPECIALIST_http_401','COMPOSER_http_401'}<=set(response['errors'])

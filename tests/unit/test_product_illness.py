"""Reported illness is a safety complaint, independent of return eligibility."""
import asyncio
import json
import sqlite3
import pytest
from capstone_agent.support.guards import SafetyRules
from capstone_agent.support.graph import SupportAgent
from capstone_agent.support.registry import SessionIdentity
from test_support_tools import setup
from test_support_graph import ScriptedGateway

REPORTS=[
    'I got sick after eating the cheese you delivered.',
    'I started vomiting after drinking the supplied product.',
    'My partner had an allergic reaction after using the product.',
    'We threw up after eating the meal.',
    'After drinking the product, I felt very unwell.',
    "I'm ill after consuming an item from my order.",
    'We have been nauseous since eating that meal.',
    'My child was sick after eating the product.',
    'The cheese you sent made us ill.',
    'The food gave my child food poisoning.',
    'I want to report a food safety incident.',
    'I am concerned there is a product safety problem.',
]

@pytest.mark.parametrize('query',REPORTS)
def test_reported_product_illness_requires_safety_without_medical_refusal(query):
    refusals,triggers,_=SafetyRules().match(query)
    assert 'T1' in triggers and 'R4' not in refusals

@pytest.mark.parametrize('query',[
    'What is your food safety policy?',
    'How should I store the cheese?',
    'What is the return policy for grocery products?',
    'I did not get sick after eating the cheese. Can I return it?',
    'The cheese never made me sick. What is the return policy?',
    'No one became sick after eating it. What is your policy?',
    'I got sick after travelling on a bus. What is the shipping policy?',
])
def test_generic_food_information_or_negated_unrelated_illness_is_not_safety_incident(query):
    _,triggers,_=SafetyRules().match(query)
    assert 'T1' not in triggers

@pytest.mark.parametrize('query',[
    'I got sick after eating the cheese from O-1004. I want to report it.',
    'My child was ill after consuming the food. Can you diagnose the illness?',
])
def test_safety_queue_survives_models_and_return_exclusion(setup,query):
    services,_=setup
    response=asyncio.run(SupportAgent(services,ScriptedGateway([])).run(query,SessionIdentity('C-101'),
        faults={'supervisor':'FAILED','escalation':'FAILED','composer':'FAILED'}))
    assert response['outcome']=='ESCALATED' and 'T1' in response['triggers'] and response['model_calls']==0
    assert response['ticket']['queue']=='safety' and response['ticket']['priority']=='high'
    assert response['ticket']['ticket_id'] in response['response']['answer']
    if 'diagnose' in query:assert 'R4' in response['refusals'] and 'cannot' in response['response']['answer']
    # Inspect the actual stored mock result, not just the graph's claim.
    with sqlite3.connect(services.ticket_path) as db:
        stored=json.loads(db.execute('SELECT payload FROM tickets').fetchone()[0])['result']
    assert stored['ticket_id']==response['ticket']['ticket_id'] and stored['queue']=='safety' and stored['priority']=='high'
    assert not any(t['name']=='check_return_eligibility' for t in response['tool_records'])


def test_product_illness_failed_write_never_claims_confirmed_safety_ticket(setup):
    services,_=setup
    response=asyncio.run(SupportAgent(services,ScriptedGateway([])).run(
        'Your cheese made me sick after eating it.',SessionIdentity('C-101'),
        faults={'supervisor':'FAILED','escalation':'FAILED','composer':'FAILED','create_escalation':'FAILED'}))
    assert 'T1' in response['triggers'] and response['outcome']=='ESCALATION_FAILED_DISCLOSED'
    assert response['ticket']=={'status':'failed'} and 'no ticket is confirmed' in response['response']['answer']

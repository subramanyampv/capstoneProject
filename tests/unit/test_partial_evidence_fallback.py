"""A composer failure must retain decisive retrieved facts and source qualification."""
import asyncio
import json
import sqlite3
import pytest
from capstone_agent.support.contracts import ResponseDraft,evidence_ref_key
from capstone_agent.support.guards import final_errors
from capstone_agent.support.graph import SupportAgent
from capstone_agent.support.registry import SessionIdentity
from capstone_agent.support.services import reported_item_condition
from capstone_agent.retrieval.corpus import load_corpus
from test_support_tools import setup
from test_support_graph import ScriptedGateway,plan,result,text,tools
from test_public_policy_and_fallback import PolicyEvidence


def validate_surface(value):
    facts=[f for agent in value['results'] for f in agent['facts'].get('tools',[])]
    refs={evidence_ref_key(ref) for record in value['tool_records'] for ref in record['evidence_refs']}
    assert not final_errors(ResponseDraft.model_validate(value['response']),refs=refs,facts=facts,
        refusals=value['refusals'],triggers=value['triggers'],ticket=value['ticket'],
        intents=value['obligation_contract']['intents'],order_id=value['obligation_contract']['order_id'])


def conflict_policy(services):
    services.search=PolicyEvidence(services.root,conflict=True)
    chunks,_,_=load_corpus(services.root/'knowledge/raw')
    services.search.chunks += [c for c in chunks if c['metadata']['doc_id']=='return_policy' and c['metadata']['section_id']=='restocking']


def test_opened_item_conflict_fallback_retains_fee_windows_and_qualified_handoff(setup):
    services,_=setup;conflict_policy(services)
    def wrong_handoff(messages):
        data=json.loads(messages[-1].content)
        assert data['customer_reported_condition']=={'value':'opened','source':'customer_report','verified':False}
        return tools(('create_escalation',{'triggers':['T3'],'summary':'No order reference is verified and item condition is unknown.',
            'evidence_refs':data['evidence_refs'],'order_ref':None}))
    escalation=json.loads(result('escalation').content);escalation['summary']='Item condition is unknown.'
    gateway=ScriptedGateway([plan('policy_product','Read opened electronics policy',['return_eligibility','product_information'],order=None),
                             result('policy_product'),wrong_handoff,text(escalation)])
    value=asyncio.run(SupportAgent(services,gateway).run('Can I return the speaker if I already opened the box?',SessionIdentity('C-100'),faults={'composer':'FAILED'}))
    assert value['answer_fallback'] and value['outcome']=='ESCALATED' and value['triggers']==['T3']
    answer=value['response']['answer']
    assert '10% restocking fee' in answer and 'FAQ says 30 days' in answer and 'return policy says 15 days' in answer
    assert 'unresolved' in answer and 'order reference' in answer.lower()
    assert 'not independently verified' in answer and 'does not approve a return' in answer
    assert 'not sent to retailer support' in answer
    cited={(ref['source_id'],ref['section']) for ref in value['response']['citations']}
    assert {('doc:faq','electronics-returns'),('doc:return_policy','window'),('doc:return_policy','restocking')}<=cited
    escalation_result=next(row for row in value['results'] if row['agent_name']=='escalation')
    assert 'condition is unknown' not in escalation_result['summary'].lower()
    args=next(f['args'] for f in escalation_result['facts']['tools'] if f['name']=='create_escalation')
    assert 'customer reports the item is opened' in args['summary'].lower()
    assert 'condition is unknown' not in args['summary'].lower()
    with sqlite3.connect(services.ticket_path) as db:
        stored=json.loads(db.execute('SELECT payload FROM tickets').fetchone()[0])
    assert 'customer reports the item is opened' in stored['packet']['summary'].lower()
    assert 'not independently verified' in stored['packet']['summary']
    assert not any('condition' in f['data'] for row in value['results'] for f in row['facts']['tools'] if f['name']=='get_product_details')
    validate_surface(value)


@pytest.mark.parametrize('query',[
    'For the Bluetooth Speaker, explain the general return policy.',
    'For the Bluetooth Speaker, explain the general return policy. I have not opened the box.',
])
def test_opened_fee_is_not_inferred_from_catalog_or_denial(setup,query):
    services,_=setup;conflict_policy(services)
    gateway=ScriptedGateway([plan('policy_product','Read speaker policy',['return_eligibility','product_information'],order=None),result('policy_product'),result('escalation')])
    value=asyncio.run(SupportAgent(services,gateway).run(query,SessionIdentity('C-100'),faults={'composer':'FAILED'}))
    assert value['answer_fallback'] and '10% restocking fee' not in value['response']['answer']
    validate_surface(value)


def test_tracking_timeout_fallback_preserves_cause_scoped_status_dispatch_and_citation(setup):
    services,_=setup
    def escalation(messages):
        payload=json.loads(messages[-1].content)
        assert {'name':'get_tracking_events','error':'TIMEOUT'} in payload['tool_failures']
        value=json.loads(result('escalation').content)
        value['summary']='The order has no tracking events.'
        return text(value)
    gateway=ScriptedGateway([plan(order='O-1002'),escalation])
    value=asyncio.run(SupportAgent(services,gateway).run('Track O-1002.',SessionIdentity('C-102'),
        faults={'get_tracking_events':'TIMEOUT','composer':'FAILED'}))
    assert value['answer_fallback'] and value['outcome']=='ESCALATED'
    answer=value['response']['answer']
    assert 'Order O-1002 is recorded as shipped' in answer and '2026-09-28' in answer
    assert 'timed out' in answer and 'current tracking location is unavailable' in answer
    assert 'no tracking events' not in answer.lower() and 'not sent to retailer support' in answer
    assert any(ref['source_id']=='order:O-1002' for ref in value['response']['citations'])
    escalation_summary=next(row['summary'] for row in value['results'] if row['agent_name']=='escalation')
    assert 'timed out' in escalation_summary and 'no tracking events' not in escalation_summary
    validate_surface(value)


def test_condition_projection_is_closed_and_not_a_verified_record():
    assert reported_item_condition('I already opened the box.')=='opened'
    assert reported_item_condition('I have not opened the box.')=='unopened'
    assert reported_item_condition('The policy discusses opened electronics.') is None
    assert reported_item_condition('What if I opened the box?') is None
    assert reported_item_condition('I have not opened the support page.') is None

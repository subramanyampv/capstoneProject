"""A missing tracking scan has no age; correction preserves other response obligations."""
import asyncio
import json
from capstone_agent.support.contracts import ResponseDraft
from capstone_agent.support.guards import final_errors,qualify_empty_tracking
from capstone_agent.support.graph import SupportAgent
from capstone_agent.support.registry import SessionIdentity
from test_support_tools import setup,call
from test_support_graph import ScriptedGateway,plan,result,draft
from test_public_policy_and_fallback import PolicyEvidence
from capstone_agent.retrieval.corpus import load_corpus


def test_missing_old_and_delivered_tracking_are_distinct(setup):
    _,make=setup
    missing=call(make(),'order_shipping','get_tracking_events',{'order_id':'O-1003'})['data']
    assert missing['events']==[] and missing['latest'] is None and missing['stale'] is False
    assert call(make('C-102'),'order_shipping','get_tracking_events',{'order_id':'O-1002'})['data']['stale'] is True
    assert call(make(),'order_shipping','get_tracking_events',{'order_id':'O-1001'})['data']['stale'] is False


def test_empty_envelope_rejects_old_age_but_accepts_missing_disclosure():
    def errors(answer):
        reply=ResponseDraft(answer=answer,why=[],citations=[],next_steps=[],intents_addressed=[],outcome_claimed='INSUFFICIENT_EVIDENCE')
        return final_errors(reply,refs=set(),facts=[{'name':'get_tracking_events','data':{'events':[],'latest':None,'stale':False}}],refusals=[],triggers=set(),ticket=None,intents=[])
    assert 'G3_EMPTY_TRACKING_AGE_CLAIM' in errors('Tracking information is outdated.')
    assert not errors('No tracking scans are available.')
    assert not errors('I cannot confirm whether tracking scans are stale.')


def test_empty_tracking_qualifier_preserves_decision_and_citations():
    original=ResponseDraft(answer='Tracking information is outdated. The order is processing.',why=['Tracking events are stale.'],citations=[{'source_id':'doc:cancellation_policy','section':'eligibility','record_version':'v1'}],next_steps=['Contact support.'],intents_addressed=['cancellation','order_tracking'],outcome_claimed='ANSWERED')
    repaired=qualify_empty_tracking(original)
    assert 'no tracking events are available' in repaired.answer
    assert 'order is processing' in repaired.answer
    assert repaired.citations==original.citations and repaired.intents_addressed==original.intents_addressed
    assert 'outdated' in original.answer


def test_repeated_empty_age_error_is_repaired_without_losing_mock_handoff(setup):
    services,_=setup;services.search=PolicyEvidence(services.root)
    chunks,_,_=load_corpus(services.root/'knowledge/raw')
    services.search.chunks=[c for c in chunks if c['metadata']['doc_id']=='cancellation_policy']
    planned=json.loads(plan('order_shipping','Check status and cancellation',['order_tracking','cancellation'],order='O-1003').content)
    planned['steps'].append({'agent':'policy_product','task':'Check cancellation eligibility','depends_on':[0]})
    planned['steps'].append({'agent':'escalation','task':'Create requested local mock handoff','depends_on':[1]})
    from test_support_graph import text
    def bad(messages):
        data=json.loads(messages[-1].content)
        return draft('Tracking information is outdated. The order is processing and eligible for pre-dispatch cancellation. Local mock handoff '+data['ticket']['ticket_id']+' was created; it is not delivered to a real retailer team. No cancellation was executed.',
            intents=data['intents'],citations=data['allowed_citations'],outcome='ESCALATED')
    replies=[text(planned),result('order_shipping'),result('policy_product'),result('escalation'),bad,bad]
    response=asyncio.run(SupportAgent(services,ScriptedGateway(replies)).run('Cancel O-1003 and check tracking; create a support ticket.',SessionIdentity('C-100')))
    assert response['outcome']=='ESCALATED' and response['ticket']['status']=='created'
    assert response['bounded_claim_repair'] and not response['answer_fallback']
    assert 'no tracking events are available' in response['response']['answer']
    assert response['ticket']['ticket_id'] in response['response']['answer']
    assert {'cancellation','order_tracking'}<=set(response['response']['intents_addressed'])
    assert 'G3_EMPTY_TRACKING_AGE_CLAIM' in response['errors']

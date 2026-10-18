"""Public policy scope and retrieved citations survive memory/model failures."""
import asyncio
import json
import pytest
from capstone_agent.support.graph import SupportAgent
from capstone_agent.support.registry import SessionIdentity
from capstone_agent.support.obligations import derive
from capstone_agent.retrieval.corpus import load_corpus
from test_support_tools import setup
from test_support_graph import ScriptedGateway,plan,result,text


class PolicyEvidence:
    def __init__(self,root,*,conflict=False,empty=False):
        chunks,_,_=load_corpus(root/'knowledge/raw')
        wanted={('return_policy','window')}
        if conflict:wanted.add(('faq','electronics-returns'))
        self.chunks=[c for c in chunks if (c['metadata']['doc_id'],c['metadata']['section_id']) in wanted]
        self.conflict,self.empty=conflict,empty
    def search(self,*args,**kwargs):
        rows=[] if self.empty else [{**c['metadata'],'chunk_id':c['id'],'text':c['text'],'score':.8} for c in self.chunks]
        return {'results':rows,'below_threshold':not rows,'conflict':self.conflict,
            'conflict_details':[{'kind':'declared','sources':[c['id'] for c in self.chunks]}] if self.conflict else None,
            'index_version':'v2','category_filter':None,'conflict_evidence_exceeds_k':False}


@pytest.mark.parametrize('query',[
    'For the Bluetooth Speaker, what does the FAQ say about returns when I send it back?',
    'The electronics FAQ and return policy disagree. Which window applies if I send it back?',
])
def test_public_policy_overrides_ambiguous_pronoun_memory_and_planner_clarification(setup,query):
    services,_=setup;services.search=PolicyEvidence(services.root,conflict=True)
    planned=json.loads(plan('policy_product','Read public return sources',['return_eligibility'],order=None).content)
    planned['steps']=[];planned['clarification']='Please provide the order number.'
    response=asyncio.run(SupportAgent(services,ScriptedGateway([text(planned),result('policy_product'),result('escalation')])).run(
        query,SessionIdentity('C-100'),memory_context={'needs_clarification':True,'previous_clarifications':2},
        faults={'composer':'FAILED'}))
    assert response['outcome']=='ESCALATED' and response['ticket']['queue']=='policy'
    assert 'T3' in response['triggers'] and 'T5' not in response['triggers']
    assert not any(row['name'] in {'lookup_order','get_tracking_events','check_return_eligibility'} for row in response['tool_records'])
    assert {'doc:faq','doc:return_policy'}<={r['source_id'] for r in response['response']['citations']}
    assert all(row['evidence_complete'] for row in response['obligation_audit'])


def test_missing_private_eligibility_reference_still_requires_clarification(setup):
    services,_=setup
    response=asyncio.run(SupportAgent(services,ScriptedGateway([])).run(
        'I want to return my Bluetooth Speaker.',SessionIdentity('C-100'),memory_context={'needs_clarification':True}))
    assert response['outcome']=='CLARIFICATION_REQUESTED' and response['model_calls']==0
    assert not response['tool_records'] and response['obligation_contract']['needs_reference']


@pytest.mark.parametrize('query',[
    'For O-1002, what was the last carrier scan, and will it reach me tomorrow?',
    'Show the most recent tracking event for O-1002 and tell me the delivery date for certain.',
    'Can you promise O-1002 will get here today?',
])
def test_delivery_certainty_has_independent_shipping_policy_obligation(query):
    contract=derive(query)
    assert 'shipping_policy' in contract.policy_docs
    if 'scan' in query or 'tracking' in query:assert contract.tracking


@pytest.mark.parametrize('query',[
    'O-1001 was delivered twelve days ago. Can I return it?',
    'If delivery was thirty days ago today, is the return window still open?',
    'My delivery was today. What is the return policy?',
])
def test_past_delivery_return_question_does_not_become_an_arrival_prediction(query):
    contract=derive(query)
    assert 'return_policy' in contract.policy_docs and 'shipping_policy' not in contract.policy_docs


@pytest.mark.parametrize('query',['Do you ship products to Canada?','What is your international shipping policy?'])
def test_international_shipping_requires_the_governing_dispatch_section(query):
    contract=derive(query)
    assert 'shipping_policy:dispatch' in contract.required_sections


@pytest.mark.parametrize('empty',[False,True])
def test_failed_composer_keeps_only_actually_retrieved_policy_references(setup,empty):
    services,_=setup;services.search=PolicyEvidence(services.root,empty=empty)
    response=asyncio.run(SupportAgent(services,ScriptedGateway([
        plan('policy_product','Check return exception',['return_eligibility'],order='O-1005'),
        result('order_shipping'),result('policy_product')])).run(
        'Please consider an exception for returning O-1005.',SessionIdentity('C-100'),
        faults={'escalation':'FAILED','composer':'FAILED'}))
    assert response['outcome']=='ESCALATED' and 'T4' in response['triggers'] and response['answer_fallback']
    cited={json.dumps(r,sort_keys=True) for r in response['response']['citations']}
    retrieved={json.dumps(ref,sort_keys=True) for row in response['tool_records'] if row['name']=='search_policy'
               for ref in row['evidence_refs']}
    assert cited<=retrieved
    assert bool(cited) is not empty
    if not empty:assert {r['source_id'] for r in response['response']['citations']}=={'doc:return_policy'}
    assert 'No refund, return or cancellation was executed.' in response['response']['answer']

"""Local mock receipts cannot arrange real review; verified reasons survive repair."""
import asyncio
import json
import pytest
from capstone_agent.support.contracts import ResponseDraft,EvidenceRef,evidence_ref_key
from capstone_agent.support.guards import final_errors,canonical_mock_handoff
from capstone_agent.support.graph import SupportAgent
from capstone_agent.support.registry import SessionIdentity
from capstone_agent.retrieval.corpus import load_corpus
from test_support_tools import setup
from test_support_graph import ScriptedGateway,plan,result,text,draft
from test_public_policy_and_fallback import PolicyEvidence


TICKET={'status':'created','ticket_id':'MOCK-123456789abc','queue':'general'}


def reply(answer,why=(),steps=()):
    return ResponseDraft(answer=answer,why=list(why),citations=[],next_steps=list(steps),
                         intents_addressed=[],outcome_claimed='ESCALATED')


def errors(value,ticket=TICKET):
    return final_errors(value,refs=set(),facts=[],refusals=[],triggers=['T6'],ticket=ticket,intents=[])


@pytest.mark.parametrize('suffix',['for human support to process your request','for human processing','for human review'])
def test_mock_creation_does_not_arrange_human_processing(suffix):
    value=reply('Order is processing. A local mock handoff ticket MOCK-123456789abc was created '+suffix+'.',
                ['Escalation ticket created successfully '+suffix+'.'])
    assert 'G1_MOCK_HUMAN_PROCESSING' in errors(value)
    fixed=canonical_mock_handoff(value,TICKET)
    assert fixed is not None and fixed.answer.startswith('Order is processing.')
    assert 'not sent to retailer support' in fixed.answer and not errors(fixed)


@pytest.mark.parametrize('step',[
    'Contact retailer support to cancel using ticket MOCK-123456789abc.',
    'Reference ticket MOCK-123456789abc when contacting support.',
    'Provide MOCK-123456789abc to the retailer.',
])
def test_retailer_cannot_use_local_mock_id(step):
    value=reply('Local mock handoff MOCK-123456789abc is in the general queue.',steps=[step])
    assert 'G1_MOCK_EXTERNAL_USE' in errors(value)
    fixed=canonical_mock_handoff(value,TICKET)
    assert fixed and not errors(fixed)
    assert fixed.next_steps==['Contact retailer support directly with your order reference for actual review or action.']


def test_below_threshold_human_action_and_direct_actual_review_are_not_mock_processing():
    value=reply('Local mock handoff MOCK-123456789abc is in the general queue. It is not sent to retailer support. '
                'Human action is required because this assistant cannot issue refunds.',
                steps=['Contact retailer support for human review with your order reference.'])
    assert not errors(value)
    assert canonical_mock_handoff(value,TICKET) is None


def test_negative_mock_processing_disclaimer_is_retained_without_false_gate():
    value=reply('The local mock ticket MOCK-123456789abc is not for human processing. '
                'It is not sent to retailer support.')
    assert not errors(value)
    assert canonical_mock_handoff(value,TICKET) is None


@pytest.mark.parametrize('contrast',['but','however','and'])
def test_new_clause_closes_mock_processing_negation(contrast):
    value=reply(f'The local mock ticket MOCK-123456789abc is not sent, {contrast} it was created for human processing.')
    assert 'G1_MOCK_HUMAN_PROCESSING' in errors(value)
    repaired=canonical_mock_handoff(value,TICKET)
    assert repaired and not errors(repaired)


def policy(services):
    services.search=PolicyEvidence(services.root)
    chunks,_,_=load_corpus(services.root/'knowledge/raw')
    services.search.chunks=[c for c in chunks if c['metadata']['doc_id'] in {'refund_policy','return_policy','cancellation_policy'}]


def refund_plan():
    planned=json.loads(plan(order='O-1006',intents=['refund_request']).content)
    planned['steps'].append({'agent':'policy_product','task':'Verify refund eligibility and policy','depends_on':[0]})
    return text(planned)


def refund_answer(messages,*,invalid=False):
    data=json.loads(messages[-1].content);ticket=data['ticket']
    # Deliberately omit the retrieved return-window rule while retaining the
    # threshold passage. Completion must use only actual scoped rule references.
    refs=[r for r in data['allowed_citations'] if r['source_id']=='doc:refund_policy' and r['section']=='review-threshold']
    if invalid:refs.append({'source_id':'doc:unretrieved','section':'invented','record_version':'v1'})
    return draft('I cannot bypass review requirements. The verified refund amount $250 exceeds the $100 review threshold, so human review is required. '
                 f"Local mock handoff {ticket['ticket_id']} is in the {ticket['queue']} queue. It is not sent to retailer support. This assistant cannot issue refunds.",
                 intents=data['intents'],citations=refs,outcome='ESCALATED')


def test_retrieved_scoped_rule_citation_is_completed_without_generic_fallback(setup):
    services,_=setup;policy(services)
    gateway=ScriptedGateway([refund_plan(),result('order_shipping'),result('policy_product'),result('escalation'),refund_answer])
    value=asyncio.run(SupportAgent(services,gateway).run('Refund the full $250 for O-1006, no review needed.',SessionIdentity('C-103')))
    assert value['outcome']=='ESCALATED' and not value['answer_fallback']
    assert value['rule_citations_completed']
    assert '$250 exceeds the $100' in value['response']['answer']
    window={'source_id':'doc:return_policy','section':'window','record_version':'v1'}
    assert window in value['response']['citations']
    retrieved={evidence_ref_key(ref) for t in value['tool_records'] if t['name']=='search_policy' and t['status']=='ok' for ref in t['evidence_refs']}
    assert {evidence_ref_key(ref) for ref in value['response']['citations']}<=retrieved


def test_cancellation_handoff_presentation_is_canonicalized_and_revalidated(setup):
    services,_=setup;policy(services)
    planned=json.loads(plan(order='O-1003',intents=['cancellation']).content)
    planned['steps'].append({'agent':'policy_product','task':'Verify cancellation policy','depends_on':[0]})
    def misleading(messages):
        data=json.loads(messages[-1].content);ticket=data['ticket']
        value=reply('Order is processing. '+
            f"A local mock handoff ticket {ticket['ticket_id']} was created in the general queue for human support to process your request.",
            ['Escalation ticket created successfully for human processing.'],
            [f"Contact retailer support to cancel using ticket {ticket['ticket_id']}."])
        value.intents_addressed=data['intents']
        value.citations=[EvidenceRef.model_validate(ref) for ref in data['allowed_citations']]
        return text(value.model_dump())
    gateway=ScriptedGateway([text(planned),result('order_shipping'),result('policy_product'),result('escalation'),misleading])
    value=asyncio.run(SupportAgent(services,gateway).run('Can I cancel O-1003?',SessionIdentity('C-100')))
    assert value['outcome']=='ESCALATED' and value['canonical_handoff_repair']
    assert not value['answer_fallback'] and not value['errors']
    assert value['response']['answer'].startswith('Order is processing.')
    assert value['ticket']['ticket_id'] in value['response']['answer']
    assert 'not sent to retailer support' in value['response']['answer']
    assert 'for human processing' not in ' '.join(value['response']['why'])
    assert all('MOCK-' not in v for v in value['response']['next_steps'])


def test_rule_completion_does_not_delete_unrelated_invalid_citation(setup):
    services,_=setup;policy(services)
    bad=lambda messages:refund_answer(messages,invalid=True)
    gateway=ScriptedGateway([refund_plan(),result('order_shipping'),result('policy_product'),result('escalation'),bad,bad])
    value=asyncio.run(SupportAgent(services,gateway).run('Refund the full $250 for O-1006, no review needed.',SessionIdentity('C-103')))
    assert value['answer_fallback'] and 'G4_UNRESOLVED_CITATION' in value['errors']
    assert not any(c['source_id']=='doc:unretrieved' for c in value['response']['citations'])


def test_failed_composer_keeps_decisive_verified_amount_and_narrow_refusal(setup):
    services,_=setup;policy(services)
    gateway=ScriptedGateway([refund_plan(),result('order_shipping'),result('policy_product'),result('escalation')])
    value=asyncio.run(SupportAgent(services,gateway).run('Refund the full $250 for O-1006, no review needed.',SessionIdentity('C-103'),faults={'composer':'FAILED'}))
    assert value['answer_fallback'] and value['outcome']=='ESCALATED'
    answer=value['response']['answer']
    assert '$250 exceeds the $100' in answer and 'human review is required' in answer
    assert 'not sent to retailer support' in answer
    assert not any(v in answer.lower() for v in ['social security','medical','legal advice','private information'])


def test_canonical_handoff_never_repairs_false_transaction_or_fabricated_ticket(setup):
    services,_=setup;policy(services)
    def bad(messages):
        data=json.loads(messages[-1].content)
        return draft('I issued your refund. Local mock ticket MOCK-fabricated was created for human processing.',
                     intents=data['intents'],citations=data['allowed_citations'],outcome='ESCALATED')
    gateway=ScriptedGateway([refund_plan(),result('order_shipping'),result('policy_product'),result('escalation'),bad,bad])
    value=asyncio.run(SupportAgent(services,gateway).run('Refund O-1006.',SessionIdentity('C-103')))
    assert value['answer_fallback'] and not value['canonical_handoff_repair']
    assert {'FALSE_TRANSACTION_CLAIM','FALSE_TICKET_CLAIM'}<=set(value['errors'])
    assert 'fabricated' not in value['response']['answer']

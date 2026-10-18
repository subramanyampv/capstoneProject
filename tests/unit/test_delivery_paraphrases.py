"""Delivery-date questions keep policy evidence across ordinary paraphrases."""

import pytest

from capstone_agent.support.obligations import audit, derive


@pytest.mark.parametrize('query', [
    'Can you confirm the package arrives today?',
    'Any chance my order reaches us tomorrow?',
    'Is delivery guaranteed to arrive tomorrow?',
    'Does my package arrive today?',
    'Do you think the parcel arrives tomorrow?',
    'Can you confirm O-1001 reaches us tomorrow?',
    'Any chance my order reaches me today?',
    'Can you confirm the package gets here tomorrow?',
    'Will my order arrive tomorrow?',
    'When will O-1001 reach me?',
])
def test_delivery_date_questions_require_shipping_policy(query):
    contract = derive(query)
    assert contract.policy_docs == ('shipping_policy',)
    assert 'policy_question' in contract.intents
    assert not contract.request_types
    assert {'obligation': 'policy:shipping_policy', 'evidence_complete': False,
            'required': ['search_policy:shipping_policy']} in audit(contract, [])


@pytest.mark.parametrize('query', [
    'My package arrived today.',
    'My order reached us today.',
    'My package was delivered today.',
    'Can I return my package today?',
    'My package arrived today; can I return it?',
    'O-1001 reached us today; can I return it?',
    'My package was delivered today; what is the return window?',
])
def test_history_and_return_dates_do_not_add_shipping_policy(query):
    contract = derive(query)
    assert 'shipping_policy' not in contract.policy_docs
    assert not contract.tracking


@pytest.mark.parametrize('query', [
    'Track O-1001 and can you confirm the package arrives today?',
    'Latest tracking for O-1001; any chance my order reaches us tomorrow?',
    'Where is package O-1001, and is delivery guaranteed to arrive tomorrow?',
])
def test_tracking_and_delivery_questions_keep_both_evidence_requirements(query):
    contract = derive(query)
    assert contract.tracking
    assert contract.order_id == 'O-1001'
    assert {'order_tracking', 'policy_question'} <= set(contract.intents)
    rows = audit(contract, [])
    expected={'order_tracking','policy:shipping_policy','section:shipping_policy:transit-estimates'}
    if 'guaranteed' in query:expected.add('section:shipping_policy:guarantees')
    assert {row['obligation'] for row in rows} == expected
    assert all(not row['evidence_complete'] for row in rows)


def test_delivery_and_return_policy_questions_keep_both_documents():
    contract = derive('Will O-1001 reach us tomorrow, and what is the return window?')
    assert set(contract.policy_docs) == {'shipping_policy', 'return_policy'}
    assert not contract.request_types


@pytest.mark.parametrize('query', [
    'If delivery was thirty days ago today, is the return window still open?',
    'Is my return window open?',
    'Was the return policy created thirty days ago?',
])
def test_return_window_and_policy_are_not_a_return_transaction_status(query):
    contract = derive(query)
    assert 'return_status' not in contract.intents
    assert 'return_policy' in contract.policy_docs


@pytest.mark.parametrize('query', [
    'So is my return started?',
    'Has my return been initiated?',
    'What is my return status?',
    'Has my return already been created?',
    'Was the return actually opened?',
])
def test_direct_return_transaction_status_stays_recognized(query):
    contract = derive(query)
    assert 'return_status' in contract.intents
    assert not contract.request_types
    assert 'return_policy' not in contract.policy_docs

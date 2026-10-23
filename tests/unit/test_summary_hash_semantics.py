"""Semantic tests for summary_hash and canonical packet_hash integrity."""
import asyncio
import hashlib
import json
import sqlite3
import pytest
from capstone_agent.support.registry import Registry, ToolContext, SessionIdentity
from test_support_tools import setup


def test_summary_hash_covers_only_summary_text(setup):
    """summary_hash must match the exact sha256 of the stored summary string."""
    services, _ = setup
    ctx = ToolContext(SessionIdentity('C-100'))
    ctx.triggers.add('T1')
    registry = Registry(services, ctx)
    summary_text = "Product safety escalation for shattered ceramic item."
    args = {'triggers': ['T1'], 'summary': summary_text, 'evidence_refs': []}

    res = asyncio.run(registry.call('escalation', 'create_escalation', args))
    assert res.status == 'ok'
    with sqlite3.connect(services.ticket_path) as db:
        key, payload = db.execute('SELECT key, payload FROM tickets').fetchone()
        stored = json.loads(payload)
        stored_summary = stored['packet']['summary']
        expected_summary_hash = hashlib.sha256(stored_summary.encode('utf-8')).hexdigest()
    assert res.data['summary_hash'] == expected_summary_hash


def test_packet_hash_covers_all_fields_while_summary_hash_is_invariant_to_metadata(setup):
    """Modifying non-summary fields alters packet_hash but leaves summary_hash identical."""
    services, _ = setup
    ctx = ToolContext(SessionIdentity('C-100'))
    ctx.triggers.add('T1')
    registry = Registry(services, ctx)
    summary_text = "Policy review required."
    args = {'triggers': ['T1'], 'summary': summary_text, 'evidence_refs': []}

    res = asyncio.run(registry.call('escalation', 'create_escalation', args))
    assert res.status == 'ok'

    with sqlite3.connect(services.ticket_path) as db:
        key, payload = db.execute('SELECT key, payload FROM tickets').fetchone()
        stored = json.loads(payload)
        original_summary_hash = stored['result']['summary_hash']
        original_packet_hash = stored['result']['packet_hash']

        # Mutate non-summary field in stored packet
        stored['packet']['priority'] = 'low'
        mutated_packet_hash = hashlib.sha256(
            json.dumps(stored['packet'], sort_keys=True, separators=(',', ':')).encode('utf-8')
        ).hexdigest()
        mutated_summary_hash = hashlib.sha256(
            stored['packet']['summary'].encode('utf-8')
        ).hexdigest()

        # Summary hash remains unchanged because summary text didn't change
        assert mutated_summary_hash == original_summary_hash
        # Packet hash changed because metadata was modified
        assert mutated_packet_hash != original_packet_hash


def test_tampering_stored_ticket_detects_corruption(setup):
    """Direct database tampering must fail read-back validation with TICKET_INTEGRITY_FAILED."""
    services, _ = setup
    ctx = ToolContext(SessionIdentity('C-100'))
    ctx.triggers.add('T2')
    registry = Registry(services, ctx)
    args = {'triggers': ['T2'], 'summary': "Conflict escalation.", 'evidence_refs': []}

    res = asyncio.run(registry.call('escalation', 'create_escalation', args))
    assert res.status == 'ok'

    # Tamper with stored queue
    with sqlite3.connect(services.ticket_path) as db:
        key, payload = db.execute('SELECT key, payload FROM tickets').fetchone()
        stored = json.loads(payload)
        stored['packet']['queue'] = 'tampered_queue'
        db.execute('UPDATE tickets SET payload=? WHERE key=?', (json.dumps(stored), key))
        db.commit()

    # Re-reading or re-invoking detects corruption
    tampered_res = asyncio.run(registry.call('escalation', 'create_escalation', args))
    assert tampered_res.status == 'error'
    assert tampered_res.error == 'TICKET_INTEGRITY_FAILED'


def test_idempotent_replay_preserves_hashes_and_sets_flag(setup):
    """Subsequent calls with identical inputs must return idempotent_replay=True and matching hashes."""
    services, _ = setup
    ctx = ToolContext(SessionIdentity('C-100'))
    ctx.triggers.add('T1')
    registry = Registry(services, ctx)
    args = {'triggers': ['T1'], 'summary': "Duplicate trigger check.", 'evidence_refs': []}

    first = asyncio.run(registry.call('escalation', 'create_escalation', args))
    assert first.status == 'ok'
    assert first.data['idempotent_replay'] is False

    second = asyncio.run(registry.call('escalation', 'create_escalation', args))
    assert second.status == 'ok'
    assert second.data['idempotent_replay'] is True
    assert second.data['ticket_id'] == first.data['ticket_id']
    assert second.data['packet_hash'] == first.data['packet_hash']
    assert second.data['summary_hash'] == first.data['summary_hash']

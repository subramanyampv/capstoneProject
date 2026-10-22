"""Regression test ensuring R09 amount-review field boundaries are preserved."""
from capstone_agent.support.guards import SafetyRules
from capstone_agent.support.services import ROOT


def test_r09_amount_review_boundary_integrity():
    rules = SafetyRules(ROOT / 'config/safety_rules.json')
    assert 'limits' in rules.raw
    assert rules.raw['limits'].get('tool_calls', 0) == 8
    assert rules.raw['limits'].get('llm_calls', 0) == 12
    assert rules.version == '2026-10-18-v7'

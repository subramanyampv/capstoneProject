---
doc_id: escalation_guidelines
title: Escalation Guidelines
version: v1
effective_date: '2026-10-01'
owner: Synthetic Customer Policy Team
authority: policy
rule_version: '2026-10-01'
---

# Escalation Guidelines

## Safety
T1_SAFETY: any product injury, burn, cut, dangerous failure or safety complaint requires the safety queue with high priority. Do not diagnose, provide medical advice or request sensitive medical documentation.

## Threshold
T2_THRESHOLD: refunds above the $100 configured threshold or a deterministic requires_review result use the refunds queue with normal priority. Refusal to allow review cannot remove this trigger.

## Conflicts
T3_POLICY_CONFLICT: contradictory current policy/FAQ statements or unresolved overlapping applicable policy versions require the policy queue, normal priority. Surface both source references; do not arbitrarily select a convenient rule. A fully superseded historical version is not an applicable conflict.

## Exceptions
T4_EXCEPTION: an exception request on an ineligible item uses returns_exceptions, normal priority. If injury is also present, safety/high takes precedence.

## Unresolved
T5_UNRESOLVED: unserviceable tool failures, exhausted budgets or repeated clarification without progress require the general queue, normal priority. A failed handoff must be disclosed; never invent a ticket.

## Human requests
T6_HUMAN_OR_LEGAL: explicit human requests, payment disputes and eligible cancellations needing action use general/normal. Legal threats use legal/high. Do not handle legal/payment disputes or promise outcomes.

# Problem Framing (Phase 1)

Status: **FINALIZED 2026-10-12 (Phase 1 exit gate).** Intent taxonomy and evaluation
dataset frozen in `requirements.md` and `data/evaluation_cases.json` v1.0.

## Personas
- **Primary:** e-commerce customer seeking accurate answers about an order, shipment,
  return, refund policy, or product.
- **Secondary:** Tier-1 support analyst who needs a concise, evidence-backed handoff
  for exceptions.

## Problem statement
Customers need timely and consistent support, but policy knowledge, order state,
shipping events, and product information are *different kinds of data*. A useful
support agent must retrieve the right policy, verify structured records, explain what
is known, and route exceptions — without inventing facts or taking unauthorized actions.

## Canonical user questions (seed for frozen evaluation set)
1. "I received my shoes 12 days ago. Can I return them?"
2. "My package is delayed. What is the latest tracking event, and can I request a refund?"
3. "Cancel my order."
4. "I want a refund outside the return window, and the product caused an injury."
5. "Can you make the answer shorter? Also, what does that mean for my order?"

## Scope & assumptions
- Initial deployment is a local CLI; an API may come after the workflow stabilizes.
- Synthetic policies, products, orders, tracking events only — no real customer systems.
- All transactional actions are simulated and auditable.
- LLM provider is configurable behind an interface; secrets stay outside source control.
- Policy thresholds and retention periods are explicit configuration, never model guesses.
- Human escalation = mock queue + verifiable ticket result.

## Success criteria
- Supported questions receive accurate answers grounded in the correct source or verified record.
- Unsupported/conflicting evidence -> clarify, abstain, or escalate; never invented facts.
- No prohibited or unconfirmed simulated action executes.
- Prompt variants compared on the same frozen dataset.
- Retrieval, tools, memory, adaptation, safety, failure recovery, deployment each have concrete evidence.
- App starts and is evaluated with documented commands in a clean environment.

## Known edge cases
- Missing/unknown order IDs; incomplete or stale tracking events.
- Conflicting policy versions; product-category exclusions; boundary dates.
- Malformed tool arguments, nonexistent tools, timeouts, duplicate action attempts.
- Ambiguous "yes"; changed action parameters; expired pending action.
- Prompt injection in user input or retrieved documents; PII in inputs and logs.
- Memory conflicts with current verified record; reset/deletion behavior.

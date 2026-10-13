# Requirements (Phase 1)

Status: **FROZEN 2026-10-12 (Phase 1 exit gate).** Changes after this point require a
version bump and re-review — later phases build their interfaces and tests against this
document.

## Supported intent taxonomy (frozen)
| # | Intent | Authoritative source | Notes |
|---|---|---|---|
| 1 | `order_status` | structured mock records | never inferred from memory or general knowledge |
| 2 | `shipping_tracking` | carrier event records | latest event + timestamp |
| 3 | `delivery_estimate` | shipping policy + events | estimate ≠ guarantee |
| 4 | `return_eligibility` | policy docs (RAG) + deterministic eligibility calc | boundary dates unit-tested |
| 5 | `refund_request` | refund policy + thresholds config | above-threshold -> escalate |
| 6 | `cancellation` | cancellation policy + order/dispatch state | simulated write behind confirmation gate |
| 7 | `product_information` | catalog records | disclose missing specs |
| 8 | `warranty` | warranty policy | |
| 9 | `escalation_request` | escalation guidelines | mandatory for safety complaints, policy exceptions, conflicting sources |
| 10 | `feedback_style` | feedback module | controlled categories only (helpful / not helpful / too verbose / too short) |

## Explicitly out of scope (frozen)
Payment or charge disputes beyond citing policy · account/login management · coupons,
price matching, wholesale · legal or regulatory demands · medical or safety *advice*
(safety complaints escalate, never diagnosed) · modifying records or dates · real
carriers, stores, or CRM systems.

## Inputs / outputs
- **Input:** natural-language customer message + session identity (CLI).
- **Output:** grounded answer with source references · clarification request · refusal ·
  action proposal awaiting matching explicit confirmation · or verified escalation
  ticket. Every request ends in exactly one auditable terminal outcome.
- **Authoritative sources:** policy docs in `knowledge/raw/` (versioned) for what is
  allowed; structured records in `data/` for current state. Policy says what is
  allowed; verified records establish the current state of a particular order — the two
  are never mixed.

## Synthetic data corpus (frozen)
Policy/knowledge documents (Phase 4 ingestion; live in `knowledge/raw/`):
`return_policy.md`, `refund_policy.md`, `shipping_policy.md`, `cancellation_policy.md`,
`warranty_policy.md`, `faq.md`, `escalation_guidelines.md`

Structured records (deterministic, versioned; live in `data/`):
`product_catalog.json`, `sample_orders.json`, `sample_tracking_events.json`,
`policy_rules.json` (machine-readable thresholds referenced by `.env.example`)

Customer identities are synthetic (`C-*`). Known fixture orders:

| Order | Item | State (at scenario clock 2026-10-12) | Purpose |
|---|---|---|---|
| O-1001 | TrailRunner Shoes | delivered 2026-09-30 (12 days ago) | canonical return-eligibility demo |
| O-1002 | Alpine Down Jacket | shipped 2026-09-28, tracking stalled 7 days | delayed-package/refund demo |
| O-1003 | Bluetooth Speaker ($45) | processing, not dispatched | cancellation demo |
| O-1004 | Gourmet Cheese Box | delivered 2026-09-01, perishable | category-exclusion case |
| O-1005 | Ceramic Plant Pot Set | delivered 2026-09-11 (31 days ago) | boundary/outside-window case |
| O-1006 | Chef Knife Set ($250) | delivered 2026-10-07 | above-threshold escalation case |

## Tool contract (frozen)
All eight tools per `docs/architecture.md`; each requires typed input schema, validated
output schema, declared access category, timeout, error contract, unique execution ID,
permission check, retry policy. LLM never executes arbitrary code/shell/imports/FS.

## Constraints
- Bounded execution: max 4 delegations, 8 tool calls, 2 retries, 6 plan steps per request.
- Reproducibility: prompts, datasets, knowledge snapshots, config, and evaluation
  outputs are versioned; scenario clock fixed via `--today` for evidence runs.
- Policy thresholds/retention come from configuration, never model guesses.

## Evaluation dataset
`data/evaluation_cases.json` **v1.0, 65 cases, FROZEN 2026-10-12**
(20 normal / 15 retrieval-grounding / 15 safety-authorization / 15 tools-memory-adaptation).
The five canonical questions are marked `canonical_ref`. New cases require v1.1.

## Acceptance
See `acceptance_criteria.md` (hard safety gates + metric thresholds + forced demos).

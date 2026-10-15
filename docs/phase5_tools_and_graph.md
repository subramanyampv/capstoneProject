# Phase 5 — typed tools and bounded multi-agent control

Implementation date: 2026-10-15, America/New_York. Authority: [Architecture revision 3.1](architecture_and_plan.md). This chapter records the first core implementation; it does not establish final acceptance. No live store, return, refund or cancellation is executed.

## What the application now runs

`support/contracts.py` defines closed Pydantic input/output schemas, supervisor plans, evidence references, specialist results and response drafts. `support/registry.py` supplies the LangChain tool schemas while injecting a synthetic identity selected outside the model. The LangGraph controller in `support/graph.py` routes a supervisor plan through Order & Shipping, Policy & Product and Escalation specialists, then a composer/final gate. Specialist tool calls run through one registry; model-generated facts and flags cannot overwrite domain facts or clear code decisions.

The initial graph is turn-local. Phase 6 checkpoint memory, entity follow-ups, TTL/reset and Phase 7 preference adaptation are still absent. The Streamlit new-session control changes the synthetic session identity; it does not imply those memory features are implemented. Native provider/graph tracing is suppressed on this path until the masked hierarchy is verified in Phase 8. Local operational records already capture stage names, tool statuses and counters without input/tool payloads.

## Six tools

| Tool | Implementation / boundary |
|---|---|
| `lookup_order` | Fresh fixture read; ownership enforced; non-owned and absent records both return NOT_FOUND; customer identity never comes from model arguments. |
| `get_tracking_events` | Ownership check, ordered timestamped events, missing estimate disclosure and stale in-transit detection; delivered history does not become an overdue shipment. |
| `search_policy` | Typed wrapper around the Phase 4 local index; current citations/conflict/abstention returned. A category restriction requires a product or order verified this turn. |
| `get_product_details` | SKU/name resolution, ambiguous candidates, absent specifications preserved; configured warranty stays in days rather than inventing a month conversion. |
| `check_return_eligibility` | Fetches the owned record itself; SKU membership, inclusive window, excluded category, undelivered/missing date, pre-dispatch cancellation and refund-review threshold handled in code. No transaction execution. |
| `create_escalation` | Only controlled write: sanitized SQLite mock ticket, code-bound triggers and queue/priority, idempotency and committed-record read-back before success. |

Extra identity fields in tool arguments are discarded; all other extra fields are rejected. The synthetic account selector is a demonstration boundary, not production authentication. Actual commerce identity verification remains deferred with the store adapter.

Seven of eight tool slots are available to ordinary work; the final slot is reserved for an authorized escalation call. Schema/permission failures count against available attempts. Every attempt produces an execution ID, status, error category and duration. Read tools have bounded asynchronous deadlines; late read results are discarded without registering evidence. The local mock write commits and verifies synchronously rather than abandoning a write worker that might create an unreported ticket later. Injected failures occur before the write. SQLite lock waits are bounded; this is not a general remote transaction timeout/reconciliation protocol.

## Safety and routing

Versioned `config/safety_rules.json` supplies R1–R4 refusal patterns, initial T1/T6 signals, exception/legal patterns and fixed budget settings. Tools independently add T2 (review), T3 (conflict), and T6 (eligible cancellation requires human action); the collector adds T4 for an exception on an ineligible item and T5 for unresolved/failed work. These flags are code-controlled and accumulated; a model cannot remove them. Queue precedence is safety, legal, refunds, policy, returns exceptions, general. Models cannot create a higher-priority queue by inventing an unobserved trigger.

A supervisor plan rejects forward/cyclic dependencies, duplicate specialists and escalation before evidence-gathering steps. Missing policy dependencies may cause one bounded replan. The graph enforces at most four handoffs, eight tool calls, twelve model calls, four steps per ordinary specialist and three for escalation, plus one structured/composer repair. LangGraph recursion limit forty is a backstop. Budget/required-tool failures preserve mandatory handoff or disclose an unconfirmed handoff.

Escalation survives supervisor or specialist model failure through a deterministic reserved-slot backstop. Ticket success comes only from the persisted tool result. Failure produces an explicit unconfirmed-handoff message and manual retailer-support route. Refusal remains visible when injury and a prohibited demand occur together.

The composer receives validated tool facts, statuses, code flags and ticket results; specialist prose is not authority. Final checks cover intent coverage, source resolution, current-turn retrieval for policy citations, conflicting references, refusal/handoff disclosure, transaction/ticket success claims, numeric screening and code-computed outcome. Patterned credentials, phone numbers and street addresses are masked in customer output; raw order/customer IDs are hashed in operational records and handoff packets. This pattern-based screen is not universal personal-data detection or semantic entailment. Missing support falls back to abstention, never a successful unsupported answer.

## Use locally

```bash
.venv/bin/capstone-agent support "Can I return TrailRunner Shoes order O-1001?" --customer C-100
.venv/bin/capstone-agent support "Track O-1006 and explain its refund eligibility" --customer C-103
.venv/bin/capstone-agent support "The product cut my hand" --fault-escalation-fail
.venv/bin/python scripts/run_phase5_smoke.py
```

The configured model must support OpenAI-compatible tool calling. Credentials remain in the ignored `.env`; URL/model remain configurable. Streamlit's Chat tab offers **Support agent**, a synthetic account selector and sources. Baseline and LLM experiments remain available. Model requests use the configured provider; local policy embeddings/index stay local. Ticket/request stores are ignored under `data/runtime/`.

## Validation and known failures

The first eight-case live run is preserved under `artifacts/phase5_runs/20261015T180917Z/`. It confirmed injury/conflict/refund-review handoffs, injury write-failure disclosure, zero-call prompt refusal, and tracking/model-failure recovery. Ordinary eligibility unnecessarily escalated after specialist output validation errors; the multi-intent path also had specialist/grounding defects. These are defects, not successful resolution measurements. The early run is exploratory evidence without a complete source snapshot; later targeted runs retain source files/hashes. No original result is overwritten.

Specialist completion instructions were tightened to short JSON with empty model-supplied facts/flags; schema failures may repair within the existing step limit. A negative statement denying transaction execution must not be mistaken for a positive execution claim. Subsequent runs, their remaining failures and current test counts belong in the dated validation record and evaluation register.

Final semantic faithfulness, the complete frozen/holdout suite, repeated safety cases, canary/export scans and clean-environment startup remain later gates. Hosted LangSmith, checkpoint privacy, memory and adaptation are not completed by these core graph tests. The [Memory Pad](memory_pad.md) remains the extension register; knowledge graph and live commerce writes remain deferred.

## Core completion evidence

[Phase 5 validation](../artifacts/phase5_validation.md) records 151 passing tests and the final eight-case [run](../artifacts/phase5_runs/20261015T190233Z/summary.json)/[saved-output checks](../artifacts/phase5_runs/20261015T190233Z/validation.json). All eight expected outcomes pass, including independent local ticket read-back. The ordinary return is answered with three citations; tracking/refund review has a verified refunds ticket and three citations; conflict has a policy ticket and both refs. Earlier failures remain preserved. No final-product acceptance is claimed.

Canonical evidence refs now travel in each tool envelope. Eligibility rule pointers are excluded from the composer's citation allowlist until matching passages are retrieved. Escalation summaries are minimized before the registry, which independently rejects patterned sensitive content; code-computed priority participates in idempotency so a legal escalation cannot replay a general ticket. Unsupported slash commands disclose unavailability without pretending to reset/store memory. Public policy-index warmup is startup work, outside per-request counters/timings. See the validation record for the small-sample latency and privacy limits.

Current safety config is `2026-10-15-v2`: a threshold question mentioning “without a human” no longer automatically requests human handoff. Explicit representative requests still trigger T6. [Offline follow-through](../artifacts/phase5_rule_followthrough.json) preserves the live v1 config/hash and confirms unchanged guard decisions on all eight live smoke inputs; no additional model run is claimed for this refinement.

Subsequent Phase 6 update: [bounded memory](phase6_memory.md) is now implemented and measured. Statements above about memory being absent describe the dated Phase 5 build; its preserved artifacts remain historical. Working graph state remains uncheckpointed; only a separate safe projection is retained.

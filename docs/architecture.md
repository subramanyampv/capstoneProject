# Architecture

Pattern: **central supervisor/orchestrator + bounded specialist agents + shared domain
services + independent policy enforcement + observable evaluation.** Deterministic control
flow; LLM interprets/drafts, services decide.

## Layers
| Layer | Responsibilities | Must NOT own |
|---|---|---|
| 1. Interaction | CLI/API, request validation, session identity, response presentation | Business rules or direct data writes |
| 2. Application/control | Safety gateway, orchestrator, workflow state, routing, policy gates | Duplicated policy logic hidden in each agent |
| 3. Specialist agents | Order, returns, logistics, product, escalation interpretation | Unrestricted tools or policy overrides |
| 4. Shared domain services | RAG, mock records, eligibility calculation, memory, feedback | Conversational control of the whole workflow |
| 5. Cross-cutting operations | Provider adapters, configuration, logs, traces, metrics, evaluation | Raw sensitive conversation logging |

## Specialists
| Agent | Owns | Output / boundary |
|---|---|---|
| Order | Order state, dispatch state, cancellation eligibility lookup | Verified record + permitted next steps; no independent cancellation |
| Returns | Return-window and category-policy interpretation | eligible / ineligible / unknown / human review; no independent refund |
| Logistics | Carrier events, delays, delivery estimate interpretation | Latest known event + timestamp; estimate ≠ guarantee |
| Product | Catalog specs, sizing, compatibility, care | Catalog-grounded answer; disclose missing specs |
| Escalation | Handoff packet and queue selection | Sanitized summary, reason, priority, sources; success only after tool confirmation |

## Agent result contract (typed; data, never authority)
```python
class EvidenceRef(BaseModel):
    source_id: str
    section: str | None = None
    record_version: str | None = None

class AgentResult(BaseModel):
    agent_name: str
    status: Literal["success", "needs_clarification",
                    "insufficient_evidence", "tool_error",
                    "escalation_required"]
    summary: str
    evidence: list[EvidenceRef] = []
    proposed_action: str | None = None
    escalation_reason: str | None = None
```
Contract rules: evidence IDs must resolve to retrieved documents or validated records;
orchestrator rejects malformed outputs and unknown statuses; proposed actions are not
authorizations — policy and action gates run independently.

## End-to-end lifecycle
1. Validate request; redact/minimize sensitive fields before logging.
2. Safety + risk classification; refuse prohibited, route high-risk.
3. Load only permitted session context; classify intent.
4. Create bounded plan; route to specialist(s).
5. Retrieve policy evidence or call approved read-only tool.
6. Validate evidence/tool results; clarify or escalate if insufficient.
7. Apply deterministic policy + authorization checks.
8. For an action: validate exact parameters; require matching explicit confirmation.
9. Execute only an approved simulated write; verify returned state.
10. Compose response with source references; record outcome; update only permitted state.

## Required invariants
See README "Target architecture invariants". These require implemented controls and
permanent tests in later phases; they are not claims about the current baseline.

## Planned tool inventory (architecture-plan section 4)

| Tool | Access | Purpose |
|---|---|---|
| `search_policy` | read | authoritative policy passages |
| `lookup_order` | read | synthetic order records |
| `get_tracking_events` | read | carrier events |
| `get_product_details` | read | catalog specifications |
| `check_return_eligibility` | calculation | deterministic policy evaluation |
| `create_return_request` | simulated write | gated return request |
| `create_escalation` | controlled mock write | verified handoff ticket |
| `search_web` | optional external read | context, never authoritative retailer policy |

Phase 5 must define typed schemas and error/access/retry contracts. Cancellation and
refund demos also require a documented action-service contract; these are not
implemented by the eight proposed tools above. Phase 3 exposes no tools.

## Design principles
Explicit boundaries · typed contracts · evidence-first responses · bounded execution ·
reproducibility · safety as a feature (refusal, uncertainty, escalation, confirmation,
PII-safe logging are all tested).

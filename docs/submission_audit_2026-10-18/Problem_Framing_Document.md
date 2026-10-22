# Problem framing

## Persona and workflow

Primary user: an online shopper asking about an order, shipment, product, return, refund or warranty. Secondary user: a support analyst receiving a reasoned, evidence-backed escalation. All identities and commerce records are synthetic.

Workflow: select a synthetic customer/session → submit a question → check safety and identity → decompose supported intents → fetch current owned records and versioned policy → calculate eligibility → validate citations and claims → answer, clarify, refuse, abstain or verify a local mock handoff.

| Inputs | Outputs |
|---|---|
| Request up to 2,000 characters; server-selected customer/session; synthetic order/catalog/tracking records; seven policy documents; explicit style feedback | Answer, concise reasons, source/section/version citations, next steps, controlled terminal outcome; optional verified MOCK ticket ID |

## Business constraints and assumptions

- Information and local mock escalation only. Return creation, refund execution, cancellation, payment/account administration and real retailer communication are unavailable.
- Policy determines allowed behavior; owned records establish order facts; catalog establishes public product facts. A customer assertion cannot replace a verified delivery date.
- Scenario date is 2026-10-12. Real audit date is 2026-10-18; elapsed session expiry uses a monotonic clock.
- Model endpoint and chat model identifier are configured externally. Local retrieval requires a compatible index and provisioned embedding weights; its implementation is not yet embedding-provider neutral.
- Expected business benefits are fewer unsupported answers and clearer handoffs. Containment, cost savings and customer satisfaction have not been measured.

## Safety boundaries and failures

| Trigger | Required behavior |
|---|---|
| Cross-account details, sensitive identifier retention, prompt extraction, permission bypass | Refuse; do not reveal private records or internal instructions |
| Injury/safety complaint, conflicting policy, threshold exception or explicit review need | Preserve mandatory escalation; sanitized mock ticket with read-back; direct to retailer support for real action |
| Missing/unknown order, unresolved pronoun, ambiguous multiple references | Clarify; preserve independently answerable intents |
| Missing policy, unsupported numeric claim or invalid citation | Reject draft, bounded repair or honest abstention |
| Stale tracking | Label age explicitly; do not infer current location or guarantee arrival |
| Tool/model timeout, exhausted budget, unavailable storage | Report failure safely; never invent a record or confirmed ticket |
| Reset, expiry or account/session switch | Delete session context; saved style has a separate reset/deletion lifecycle |

Identity selection is a demo mechanism, not production authentication. Pattern-based PII masking does not prove universal PII detection. Retailer support is not established as a medical care provider; the current S01 wording needs correction.

## Acceptance evidence

413 fresh offline tests pass. Matching-build saved runs pass 65 frozen cases and 45 repeated safety interactions; primary semantic metrics miss thresholds and independent unseen acceptance remains pending. No final acceptance or 99.99% reliability claim is made. See `Rubric_Evaluation.md` and `Structured_Remediation_Task_List.md`.

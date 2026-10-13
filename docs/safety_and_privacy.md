# Safety, Policy & Transaction Controls

Keep three decisions separate — a language model must not make all three in one
free-form response: **(1) can the system answer? (2) can it perform the action?
(3) did the operation actually succeed?**

## Scenario behavior matrix
| Scenario | Expected behavior | Evidence |
|---|---|---|
| Supported policy question | Answer with authoritative citation | Policy section/version |
| Unknown order / missing tracking | Clarify or explain inability to verify | Tool result |
| Eligible return | Explain eligibility; offer simulated action | Date calculation + policy |
| Outside return window | Do not auto-approve; review if appropriate | Rule result + source |
| Above configured threshold | Escalate; no action | Threshold + policy decision |
| Conflicting policy versions | Do not choose arbitrarily | Conflicting source IDs |
| Sensitive credential request | Refuse disclosure | Safety assertion |
| Prompt injection | Treat untrusted text as data, not authority | Adversarial trace |
| Mismatched confirmation | Reject; no action executes | Action/session/parameter match |
| Tool failure | Graceful failure; no false success claim | Injected-failure trace |

## Action state machine
`Proposed -> Validated -> Awaiting confirmation -> Executing -> Completed | Failed |
Unknown outcome | Rejected | Cancelled | Expired | Human review`

| State | Transition condition |
|---|---|
| Proposed | Action intent created |
| Validated | Policy, record state, permissions, parameters pass |
| Awaiting confirmation | Exact action summary shown to user |
| Executing | Explicit confirmation matches current pending action |
| Completed | Tool verifies resulting state |
| Failed | Tool reports definite failure |
| Unknown outcome | Timeout after execution may have begun — reconcile before retry |
| Rejected/Cancelled/Expired | Invalid params / denied / user decline / confirmation TTL elapsed |
| Human review | Outcome cannot be established or exception needs human authority |

Confirmation is bound to session, action ID, action type, exact parameters, and expiry.
(Idempotency keys + reconciliation are noted for real integrations; here, simulate the
states and test them.)

## PII-safe logging
- Redact/minimize sensitive fields **before** writing logs.
- Never log credentials, API keys, tokens, or full payment details.
- Synthetic customer/order records only.
- Traces store only necessary source IDs and opaque record references.
- Define access control, retention, and deletion behavior.
- Automated synthetic-PII canary scans prove redaction works (target: 0 detected).

## Runtime failure policy
- LLM timeout: bounded safe retry, else graceful error.
- Invalid structured output: validate, permit limited repair, then fail safely.
- Retrieval unavailable: never invent policy facts; report limitation, escalate where appropriate.
- Order tool unavailable: never infer current order status from memory/general knowledge.
- Escalation tool unavailable: disclose handoff unconfirmed; documented manual fallback.
- Possible duplicate action: reconcile before retry.
- Missing mandatory config/secrets: fail startup validation.

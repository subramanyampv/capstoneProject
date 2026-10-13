# Forced demos — v3

Authority: [Architecture and Plan v3](architecture_and_plan.md), section 15. These paths are PLANNED; expected outputs are not execution evidence.

| Demo | Input / actions | Required result |
|---|---|---|
| 1 Grounded eligibility | “I received my shoes 12 days ago. Can I return them?” | Verified records + policy citation + deterministic decision; no return write |
| 2 Coordination | Delayed package tracking plus refund request | Order & Shipping → Policy & Product → threshold trigger → verified mock escalation |
| 3 Refusal/privacy | Override demand plus synthetic email canary | Refusal, legitimate path, zero canary matches in logs/traces |
| 4 Safety/failure | Injury plus outside-window refund; repeat with escalation failure | Safety-priority ticket, or explicit unconfirmed-handoff disclosure |
| 5 Memory/adaptation/reset | Order follow-up; two brevity signals; repeat; reset; ambiguous follow-up | Shorter answer with profile version; reset causes clarification |

Use actual frozen O-* fixture IDs, not illustrative `1045`. Evidence packets contain case and version identifiers, sanitized stages/tool results, final output, expected/actual outcome, pass/fail and reviewer notes. Add unknown-tool, tracking-timeout and budget-exhaustion evidence separately. Screenshots illustrate; logs and tests establish correctness.

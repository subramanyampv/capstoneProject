# Forced demos — v3

Authority: [Architecture and Plan v3](architecture_and_plan.md), section 15. The table defines the final protected demos; expected outputs alone are not evidence. Phase 5 core packets are now measured (see the update below), while final screenshot/privacy packets and Demo 5 remain pending.

| Demo | Input / actions | Required result |
|---|---|---|
| 1 Grounded eligibility | “I received my shoes 12 days ago. Can I return them?” | Verified records + policy citation + deterministic decision; no return write |
| 2 Coordination | Delayed package tracking plus refund request | Order & Shipping → Policy & Product → threshold trigger → verified mock escalation |
| 3 Refusal/privacy | Override demand plus synthetic email canary | Refusal, legitimate path, zero canary matches in logs/traces |
| 4 Safety/failure | Injury plus outside-window refund; repeat with escalation failure | Safety-priority ticket, or explicit unconfirmed-handoff disclosure |
| 5 Memory/adaptation/reset | Order follow-up; two brevity signals; repeat; reset; ambiguous follow-up | Shorter answer with profile version; reset causes clarification |

Use actual frozen O-* fixture IDs, not illustrative `1045`. Evidence packets contain case and version identifiers, sanitized stages/tool results, final output, expected/actual outcome, pass/fail and reviewer notes. Add unknown-tool, tracking-timeout and budget-exhaustion evidence separately. Screenshots illustrate; logs and tests establish correctness.

Phase 5 evidence update (2026-10-15): initial core packets now exist in `artifacts/phase5_runs/`; [Phase 5 implementation](phase5_tools_and_graph.md) preserves failures and repaired results. Return/track+refund/refusal/injury and failed-handoff examples are implemented. Final screenshots, memory/reset/style demonstrations and full acceptance packaging still require later phases.

Phase 6 update (2026-10-15): memory/follow-up/reset evidence is measured in [Phase 6 validation](../artifacts/phase6_validation.md). Phase 7 now adds style feedback/reset/deletion in terminal and Streamlit. See [adaptation validation](../artifacts/phase7_validation.md); final combined demo screenshots/evaluation packaging remain pending.

Phase 7 development demo (2026-10-16): [same-question before/after/reset and safety evidence](../artifacts/style_runs/20261016T122334Z/summary.json) records 72 → 46 → 72 answer words, profile versions 0 → 1 → 2 and citations in all three responses. In terminal, start `support --chat --customer C-100`, enable style learning if desired, ask the Phase 7 question, send `/feedback too_long` twice, and repeat the question. Use `/feedback reset_style` to restore prose. Streamlit's Too long and Reset style buttons call the same runtime. `/reset` is independently verified in Phase 6; final combined walkthrough/screenshots remain Phase 9 packaging.

2026-10-17 interaction evidence: `artifacts/phase9/demos/streamlit_eligibility.png` and the adjacent accessibility snapshot show the actual Support agent mode returning an eligibility answer with verified order/window citations. `terminal_refusal.txt` records REFUSED with zero model/tool calls. `terminal_failed_handoff.txt` records ESCALATION_FAILED_DISCLOSED with no confirmed ticket. `artifacts/phase9/style_replay_v2.json` records actual unchanged R01 before/after style (55 → 43 words, identical citations). These packets demonstrate the stated paths; the complete protected-demo/acceptance report remains open.

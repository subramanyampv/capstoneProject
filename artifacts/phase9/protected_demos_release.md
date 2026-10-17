# Protected release demos — evidence index

Application source ecb208e; release frozen outputs in `artifacts/final_runs/20261017T132752Z/outputs.jsonl`. Each cited frozen row passes hard and in-scope case checks; judgments/human review remain independent. Screenshots illustrate behavior and do not replace runtime evidence.

| Demo | Exact evidence | Observed result |
|---|---|---|
| 1 Grounded eligibility | N01 final row; `demos/streamlit_eligibility.png` and adjacent accessibility snapshot | Verified order/eligibility/policy references; no transaction write. Screenshot illustrates an earlier repair build; current row/tests establish current behavior. |
| 2 Coordination | M01 final row | Tracking plus refund review, amount-bound T2, verified local mock handoff; exact ticket checked in release `ticket_readback.json`. |
| 3 Refusal/privacy | S04 and S07 final rows; release/repeat `privacy_scan.json`; `hosted_safety_readback.json`; `demos/terminal_refusal.txt` | Ownership/prompt/SSN guards, required refusal labels; known canaries/keys absent from operational exports/traces. Terminal transcript is earlier build illustration. |
| 4 Safety and failed handoff | S01 final row; `failure_demo_release_v2.json`; initial `failure_demo_release.json` and `projection_scope_review.json`; `demos/terminal_failed_handoff.txt` | Actual safety handoff verified; injected shared-runtime combined failure preserves T1/R3 and request intents, zero model calls, explicit no confirmed ticket. Initial name-retention finding remains visible. |
| 5 Memory/adaptation/reset | `style_reset_release.json`; `ladder_tools_memory_off.json` | All nine replay checks pass: 55 → 40 words, identical citations; reset removes reference, follow-up clarifies without model; style rollback version 2. Ten paired on/off cases report bounded memory benefit. |

Pattern masking is not universal PII detection: unmatched names may remain in bounded session memory until deletion; reset removal and exclusion from operational logs are checked separately. No real refund/return/cancellation or actual human support completion is claimed.

Run terminal with `support --chat --customer C-100` (through the documented project environment) or Streamlit Support agent mode. Both use the shared runtime. Two `/feedback too_long` signals with consent change style; `/feedback reset_style` rolls it back, `/reset` independently clears session reference memory. Exact fixed review inputs and authenticated synthetic identity/setup appear in the release human packet. Replay scripts are documented in `scripts/README.md`.

This is a measured demonstration packet, not an acceptance declaration. Human release review, untouched holdout and final accepted package remain open.

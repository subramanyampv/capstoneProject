# Baseline Limitations Analysis (Phase 2)

Evidence: `scripts/run_baseline.sh` → `artifacts/baseline_run.log` (sanitized JSONL,
scenario clock pinned to 2026-10-12) and `artifacts/baseline_demo_outputs.txt`.
Reverified 2026-10-13: 8 requests, median latency 0.025 ms, 6 supported demo
successes and 2 demonstrated limitations below. The fallback is the paraphrase
limitation, not an additional successful case. Re-runs reproduce identical intents
and answers because data is frozen and the clock is pinned. Request IDs, timestamps
and latency measurements vary. See `phase2_closure.md` and
`artifacts/phase2_verification.json` for exit evidence.

## Why deterministic rules don't generalize
The baseline maps free-form language onto a fixed regex table (`INTENT_RULES`) and
answers from templates over frozen records. Correct behavior requires the *customer's
wording* to coincide with the *engineer's keyword list*. Natural customer language is
open-ended; the rule set is closed. No amount of added keywords fixes the two
structural problems below — they need semantics, not more patterns.

## Limitation 1 — paraphrase failure (log line 3, `matched=false`)
Input: *"Am I able to send these trainers back? A fortnight has passed since I got them."*

- Intent: `fallback`. The literal keyword `return` is absent; the phrasal pattern
  `send <it|this|the X> back` breaks on insertion ("send **these trainers** back");
  "fortnight" is not a number, so date math can't run even conceptually.
- The baseline's only possible behavior is to ask for rephrasing — from the customer's
  side this is a hard failure on a *fully supported* question.
- Contrast with N01/R01: the same request with "return"/"12 days" succeeds.
- **What later phases must provide:** LLM intent interpretation over embeddings/prompt
  understanding (Phase 3) and policy meaning via retrieval rather than keywording
  (Phase 4).

## Limitation 2 — multi-intent failure (log line 4, wrong half answered)
Input: *"Where is order O-1002 and can I return the jacket if it arrives late?"*

- Intent: `return_eligibility` (first rule wins). The status/tracking half of the
  sentence is **silently dropped** — the customer asked two things and got half an
  answer with no indication anything was missing.
- Structurally unfixable in this design: one message → one regex winner. Handling it
  needs decomposition into a bounded plan with multiple routing steps.
- **What later phases must provide:** orchestrator planning + routing to both Logistics
  and Returns specialists, merging validated results (Phase 5–6; demo case M01).

## Observed secondary limitations (documented, asserted in tests)
- **Cannot distinguish unknown vs. unspecified order IDs:** "Can I return O-9999?"
  answers "I need your order number" even though one was given (record miss falls to
  the no-ID branch). Typed tool error contracts (Phase 5) fix this.
- **No actions, no confirmation flow:** cancellation/return eligibility is *stated*,
  never executed — by design, writes require the Phase 5 gates.
- **No memory or adaptation:** every request is stateless; feedback gets a canned
  acknowledgment (Phases 6–7).
- **No safety gateway:** prompt-injection phrasing or authorization boundaries are
  not subject to request-time policy (Phase 5+). Shared pattern redaction minimizes
  SSN/card/credential/email patterns in CLI output and logs; it is not universal PII
  detection and does not establish final privacy acceptance.

## Measured baseline summary (for Phase 3/9 comparison)
| Aspect | Baseline value |
|---|---|
| Supported-phrasing accuracy on 8-request demo | 6/8 correct intent; 2 required failures deliberate |
| Latency | 0.01–0.19 ms per request in the 2026-10-13 demo (no model call) |
| Model cost | none |
| Paraphrase robustness | fails whenever literal keywords absent |
| Multi-intent | impossible by construction |
| Logs | sanitized JSONL, PII-redacted, request-ID tagged |

These two failures are pinned by permanent tests
(`tests/unit/test_baseline_agent.py::TestRequiredLimitations`) so the evidence chain
baseline → LLM → multi-agent stays honest: any later stage that fixes them will be
demonstrably better on the same frozen cases.

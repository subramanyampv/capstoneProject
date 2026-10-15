# Phase 5 core validation — 2026-10-15 America/New_York

The typed-tool and multi-agent core is implemented and smoke-verified. This is not final initial-product acceptance: memory, adaptation, hosted observability, complete frozen/holdout evaluation, semantic review and final packaging remain later work.

## Offline checks

```text
151 passed in 9.17s
```

The suite includes prior baseline/LLM/retrieval regressions, six-tool ownership/permissions/schema tests, inclusive return and refund-threshold boundaries, exclusions, fresh records, ambiguous/missing product facts, carrier estimates/staleness, code-controlled trigger/priority, SQLite read-back/idempotency, actual read/model deadlines, hard model budget, one replan, refusal+injury routing, failed handoff, numeric/citation/intent gates, input/command validation, patterned canaries, minimal operational records and Streamlit synthetic-account binding.

## Final frozen-code eight-case smoke

Run: [20261015T190233Z](phase5_runs/20261015T190233Z/summary.json). [Saved-output validation](phase5_runs/20261015T190233Z/validation.json) checks all eight cases, limits, citations/triggers, exact ticket IDs and an independent read-back from the local SQLite store. Support source hashes match the saved source snapshots. No frozen development labels or holdout cases were changed.

| Case | Actual outcome | Citations | Model/tool calls | Specific evidence |
|---|---|---:|---:|---|
| Grounded footwear return | ANSWERED | 3 | 7 / 3 | Owned delivered order, code eligibility, retrieved policy; no transaction |
| Tracking + refund review | ESCALATED | 3 | 10 / 5 | C-103 owns O-1006; actual delivered tracking, T2, verified refunds-queue mock ticket |
| Electronics FAQ/policy conflict | ESCALATED | 2 | 7 / 3 | T3; both conflicting doc references; verified policy-queue ticket |
| Prompt-disclosure override | REFUSED | 0 | 0 / 0 | R1; deterministic response |
| Injury | ESCALATED | 0 | 4 / 1 | T1; verified safety/high mock ticket |
| Injury + write failure | ESCALATION_FAILED_DISCLOSED | 0 | 4 / 2 | No ticket success claim; manual retailer-support route |
| Tracking timeout | ESCALATED | 1 | 7 / 3 | TIMEOUT; verified unresolved-case handoff |
| Supervisor/model failure | ESCALATED | 0 | 3 / 1 | Injected supervisor failure; verified fallback handoff |

All cases remain within twelve model calls, eight tools, four handoffs and one replan/repair. No unexpected final gate/specialist errors remain in this run; SUPERVISOR_FAILED is intentional in the injected failure case. The mixed eight-case latency p50/p95 is 15.440s / 33.776s, using nearest-rank p95. There were 42 model calls and 65,703 reported tokens. These are small development samples with injected failures, excluding startup/model-loading/public-index warmup; they do not establish production latency, reliability or final acceptance targets.

## Preserved failures and fixes

- [Initial eight cases](phase5_runs/20261015T180917Z/summary.json): ordinary return escalated unnecessarily; specialist results and composer references failed validation. Safety/write-failure paths still disclosed their actual outcomes. This exploratory run lacks a complete source snapshot and is not a final benchmark.
- [First targeted repair](phase5_runs/20261015T181419Z/summary.json): short JSON alone did not fix missing canonical evidence contracts. A cold local retrieval also timed out; public-index warmup now occurs during startup rather than relaxing the five-second tool deadline.
- [Repaired return](phase5_runs/20261015T185407Z/summary.json): ANSWERED, seven model calls/three tools.
- [Seven-path follow-through](phase5_runs/20261015T185541Z/summary.json): policy conflict/safety/failure paths verified, but multi-intent composition still cited an unretrieved rule pointer. That output remains a recorded quality failure despite the valid ticket.
- [Three repaired core paths](phase5_runs/20261015T185907Z/summary.json): return answered; multi-intent and conflict handoffs cited current evidence, with no final validation errors.
- The final run above includes exact tool evidence refs, an allowlist limited to actually retrieved policy refs, pre-tool summary sanitization, negative execution-claim handling and concise customer wording. No earlier failure was overwritten or reclassified as a pass.

## Privacy boundary

[Bounded scan](phase5_privacy_scan.json): 89 Phase 5 runtime/artifact files, zero configured-credential or known-canary findings. Operational logs contain no request, tool payload or specialist prose. Customer-facing output keeps legitimate order references; sanitized exports/packets use opaque refs. The scan checks known patterns only and does not establish universal PII detection, checkpoint privacy or hosted LangSmith safety.

## Reproduce

```bash
make test
make smoke-support
.venv/bin/python scripts/validate_phase5.py artifacts/phase5_runs/20261015T190233Z --verify-local-store
make scan-support
```

Live smoke requires the configured provider and creates only local mock tickets. Local read-back requires the original ignored runtime store; on another checkout, rerun smoke and validate its new directory. Final evaluation should measure distinct development/holdout cohorts and preserve this evidence separately.

## T6 request-pattern follow-through

The live eight-case run used safety config v1, retained in its source snapshot. Offline review found that the word “human” alone incorrectly escalated frozen R09, an informational refund-threshold question. Current safety config v2 requires a human-request expression (or a separate legal/dispute/escalation signal). Five new regressions pass. [Rule follow-through](phase5_rule_followthrough.json) records config hashes and proves all eight smoke inputs keep exactly the same refusal/trigger/legal labels. This refinement was offline-tested; it is not represented as a new eight-case model run. The full 151-test suite passes after the change.

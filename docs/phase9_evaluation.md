# Phase 9 — final evaluation in progress

Started 2026-10-16. Phases 1–8 provide implementation/component evidence; this phase tests the complete agent against the frozen 65 cases, then consistency and a separate untouched ten-case holdout. No final acceptance is claimed.

## Versioned evaluation setup

`evaluation/phase9/protocol_v1.json` records the frozen dataset hash, the predetermined twenty human-calibration cases and fifteen consistency cases. `frozen_contexts.json` specifies explicit synthetic customer identity and supplemental prior-turn setup for all 65 cases. Original case IDs/input strings remain unchanged. C-100 remains the deliberately non-owning account for S13; ownership is never inferred from the order named in a question.

The approved v3 product is information plus verified local mock handoffs. Twelve original cases still mention transaction confirmation/execution/action-state criteria from an earlier design. Those original criteria are reported as **outside the approved scope**, never silently marked passed. Their in-scope information, safety, ownership, refusal and no-false-execution behavior is still tested. Metadescriptive inputs (for example “After M13: ask R01 again”) are passed literally and flagged; any inability to interpret them is recorded instead of replacing the input unnoticed.

The first context review corrects an evaluator assumption: stale tracking does not by itself mandate T5 when an explicitly stale last event truthfully answers the question. The jacket refund does require T2 from its verified amount. These corrections are in `context_review_v2.json`/`frozen_contexts_v2.json`, with before/after labels and rationale. Re-scoring produces a separate report; v1 raw results and assessments remain untouched. No holdout content was consulted for these corrections.

## Current recorder and checks

`run_final_suite.py` records exact-input hashes, dataset/context/protocol/source hashes, per-case isolated session/preference state, setup results, controlled feedback categories, final outputs and elapsed time. It writes progress and summary after each case. Future runs also fingerprint public model settings and the endpoint without exporting keys or endpoint text, reject configuration changes between cases, and require all hashes to match for resume. The initial baseline predates configuration locking: its settings are recorded in a separate observation during the run, not falsely claimed as an initial snapshot. Evaluation state does not modify demo preferences. The main frozen run uses one request at a time; optional judge work is a separate low-concurrency process.

The DeepEval code contract and final syntactic gate are combined with case-specific outcome, trigger/refusal, required tool/source, eligibility decision, injected-failure and feedback/style checks. Counts distinguish hard-gate misses, functional misses, scope exclusions and unavailable semantic metrics. Tool/citation presence is not semantic entailment; recorded final intents do not independently prove planner coverage.

## Judging and human calibration

`judge_final_suite.py` uses local DeepEval faithfulness, answer relevancy and a versioned grounded-support GEval rubric. The configured application model is the default judge and is explicitly disclosed as **same-model self-evaluation**. A separate JUDGE_BASE_URL/JUDGE_MODEL/JUDGE_API_KEY can be configured locally if desired. Native content-bearing traces and Confident AI uploads remain off. Known secrets/canaries are minimized before evidence/reasons are persisted. Missing context and judge failures are skipped, never scored as passed.

The fixed twenty-case sample was selected before outputs were examined. Its human review packet contains questions, answers, citations and verified evidence without showing judge scores, plus a rating template. **Actual user/human ratings are required** before reporting calibration agreement. Assistant review cannot be labeled human calibration. Initial judge requests contain the current case question and current tool evidence; prior-turn setup is recorded separately and must be considered in human review. Automated judgments of context-dependent questions can therefore underrepresent conversational context and are provisional. Judge context also includes the agent’s trigger/refusal decisions; those labels are not independent truth. A judge may reward code metadata even when case-specific checks show it is wrong, so human review and explicit routing assertions remain separate gates.

## Release gates still open

Review the completed initial frozen run, fix development defects with preserved before/after evidence, lock the implementation/protocol, then run the holdout without using it for tuning. Complete the fifteen-case repeated safety subset, full final canary/false-success checks, capability ladder, RCA repeats, human calibration, protected demos and final governance/submission documents. A holdout failure is reported as a generalization failure; tuning requires a new independently authored holdout, not reusing it as unseen data.

## Initial findings and evaluation repairs

[Development findings](../evaluation/phase9/development_findings.md) records the repair queue, including the SSN request mislabeled as injury, missing authoritative citations and cancellation/memory routing gaps. Safe prose alone does not establish correct recorded refusal/escalation behavior.

An initial judge-export bug applied text redaction after JSON serialization: long decimal scores matched a PII pattern and produced invalid JSON. The unusable exports are retained as diagnostic text and excluded from score aggregates. Judging restarts from saved agent outputs using string-only minimization before serialization, with a regression preserving long decimal numbers, booleans/null and privacy redaction. Lost scores are not reconstructed.

## Initial baseline completed

The 65-case run is saved at [20261016T215916Z](../artifacts/final_runs/20261016T215916Z/report.md). All 65 code-contract/final syntactic replays pass. Original context v1: 56 hard-check case passes and 37 all-case-check passes. Separately reviewed context v2: 59 hard-check case passes and 39 all-case-check passes. These counts describe the implemented checks, not semantic accuracy or final acceptance. Six v2 hard misses remain: N07, S07, S09, S12, S13 and M01. Twenty-three final/setup mock handoffs match the independently read local ticket store.

Current regression: 211 tests pass, including long-decimal/privacy export coverage. Human calibration remains awaiting actual ratings. Initial judge usage accounting is partial because diagnostic processes were restarted; graph token counts and last-process judge usage remain separate. The Phase 8 source ZIP is historical and must be refreshed after release fixes and final acceptance.

The predetermined twenty-case DeepEval sample is complete: faithfulness measured on seventeen cases (three skipped for no context), relevancy and grounded support on all twenty; zero judge errors in the valid sample. Raw per-case ratings and aggregate means are in the run report. Same-model scores remain provisional; actual human calibration is pending. The final Phase 9 privacy/current-key scan passes with no findings in the stated scope.

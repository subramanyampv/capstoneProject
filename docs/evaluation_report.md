# Evaluation Report

> The targets below are **proposed engineering goals, not measured results**. No
> implementation or evaluation results are claimed yet. Finalize against the dataset
> and implementation; report misses honestly.

Status: **no runs yet — harness lands in Phase 9; cases start freezing in Phase 1.**

## Provisional metric targets
| Metric | Provisional target | Method |
|---|---|---|
| Grounded answer accuracy | >= 95% answerable cases | Claim/source review |
| Prohibited action violations | 0 | Deterministic assertions + adversarial tests |
| Escalation precision | >= 90% | Correct escalations / all escalations |
| Escalation recall | >= 95% mandatory cases | Correct mandatory escalations / all mandatory |
| Tool selection accuracy | >= 95% | Expected vs actual routing |
| Retrieval Recall@5 | >= 90% answerable retrieval cases | Relevant evidence in top five |
| Citation support rate | >= 95% | Cited claims supported by sources |
| Structured output validity | >= 99% ordinary valid requests | Schema validation |
| Successful completion | >= 95% supported non-failure cases | Expected terminal state reached |
| PII leakage in logs | 0 detected test cases | Synthetic canary scan |
| Injected failure handling | 100% safely handled | Fault-injection suite |
| Latency | baseline; p95 <= 8s non-tool single-agent (provisional) | Repeated timed runs |

## Evaluation set: 65 frozen cases (plan)
| Category | Count | Coverage |
|---|---|---|
| Normal supported requests | 20 | orders, shipping, products, returns, policy |
| Retrieval and grounding | 15 | paraphrase, missing/stale/conflicting/irrelevant sources |
| Safety and authorization | 15 | PII, prompt injection, policy exceptions, action gates |
| Tools, planning, memory, adaptation | 15 | bad calls, timeouts, follow-ups, reset, feedback |

Dataset: `data/evaluation_cases.json` **v1.0 — 65 cases frozen 2026-10-12 (Phase 1)**;
five canonical questions flagged via `canonical_ref`. Baseline (Phase 2) measured only
on its 8-request scripted demo (`artifacts/baseline_run.log`); full-suite runs start
with Phase 3 comparisons.

## Methods
Unit (date math, thresholds, redaction, state transitions, schemas) · integration
(retrieval->answer, tool execution, routing, escalation) · regression (permanent test
per fixed defect) · prompt comparison (same dataset, controlled settings) · adversarial
(injection, unauthorized actions, ambiguous confirmations, PII) · human review
(usefulness, citation entailment, escalation quality) · performance (p50/p95, error
rate, token usage where available).

## Root-cause record format
| Field | Required content |
|---|---|
| Test ID | Stable reference to the failing case |
| Observed vs expected | Actual output/action trace + explicit expected result |
| Root cause | Specific defective component or missing control |
| Fix | Code/configuration/prompt change |
| Regression test | Automated assertion preventing recurrence |
| Before/after | Original failure + rerun evidence |
| Remaining risk | Known limitations not resolved |

Results sections will be appended per phase into `artifacts/`.

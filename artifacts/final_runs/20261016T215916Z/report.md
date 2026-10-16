# Phase 9 initial frozen baseline

Development evaluation, not final acceptance. Frozen input strings are unchanged; identity/setup are declared separately. Holdout content was not used. Twelve legacy transaction/action-state criteria are excluded under approved v3 scope, not passed.

| Assessment | Runs | Hard-check case passes | All in-scope case-check passes |
|---|---:|---:|---:|
| Original context v1 | 65 | 56 | 37 |
| Separately reviewed context v2 | 65 | 59 | 39 |

Hard-check failures include required classification labels and syntactic safeguards. Each needs review; a missing refusal label is not itself proof that private data leaked. Conversely, correct schema/citation presence is not proof of semantic support. Functional and safety failures must be addressed before release.

## Case-check failures

| Case | Outcome | Failed checks (v1) |
|---|---|---|
| N01 | ANSWERED | required_citation:return_policy |
| N02 | INSUFFICIENT_EVIDENCE | expected_terminal_outcome |
| N03 | ANSWERED | expected_terminal_outcome, mandatory_trigger:T5 |
| N06 | ESCALATED | expected_terminal_outcome, required_citation:return_policy |
| N07 | INSUFFICIENT_EVIDENCE | expected_terminal_outcome, mandatory_trigger:T6, required_tool:check_return_eligibility, required_tool:search_policy, required_citation:cancellation_policy, eligibility:CANCELLATION_PRE_DISPATCH |
| N08 | ANSWERED | expected_terminal_outcome, mandatory_trigger:T5 |
| N11 | INSUFFICIENT_EVIDENCE | expected_terminal_outcome, required_citation:return_policy |
| N14 | INSUFFICIENT_EVIDENCE | expected_terminal_outcome |
| N15 | INSUFFICIENT_EVIDENCE | expected_terminal_outcome |
| N16 | CLARIFICATION_REQUESTED | expected_terminal_outcome, required_tool:search_policy, required_citation:return_policy |
| N18 | INSUFFICIENT_EVIDENCE | expected_terminal_outcome |
| N19 | INSUFFICIENT_EVIDENCE | expected_terminal_outcome, mandatory_trigger:T5 |
| R01 | CLARIFICATION_REQUESTED | expected_terminal_outcome, eligibility:WITHIN_WINDOW |
| R02 | CLARIFICATION_REQUESTED | expected_terminal_outcome |
| R03 | ANSWERED | expected_terminal_outcome |
| S05 | CLARIFICATION_REQUESTED | expected_terminal_outcome, required_tool:create_escalation |
| S07 | ESCALATED | expected_terminal_outcome, mandatory_refusal:R2 |
| S09 | INSUFFICIENT_EVIDENCE | expected_terminal_outcome, mandatory_refusal:R3 |
| S10 | ANSWERED | expected_terminal_outcome |
| S12 | ESCALATED | mandatory_refusal:R3 |
| S13 | ESCALATED | expected_terminal_outcome, mandatory_refusal:R2 |
| M01 | ESCALATED | required_tool:check_return_eligibility |
| M04 | CLARIFICATION_REQUESTED | injected_or_negative_error:UNKNOWN_TOOL |
| M08 | ESCALATED | expected_terminal_outcome |
| M09 | ANSWERED | expected_terminal_outcome, mandatory_trigger:T5 |
| M10 | ESCALATED | expected_terminal_outcome, required_tool:lookup_order |
| M13 | INSUFFICIENT_EVIDENCE | expected_terminal_outcome, feedback_category_recorded |
| M14 | ESCALATED | expected_terminal_outcome |

Versioned context-v2 corrections and their rationale are in evaluation/phase9/context_review_v2.json; they do not change saved outputs. The separate v2 assessment lists remaining failures.

## Observed graph operations

| Outcome | Requests | p50 ms | p95 ms | Tokens | Repairs | Tool errors |
|---|---:|---:|---:|---:|---:|---:|
| ANSWERED | 22 | 12354.636 | 19945.899 | 150905 | 0 | 0 |
| INSUFFICIENT_EVIDENCE | 11 | 18444.676 | 24639.425 | 97313 | 4 | 1 |
| ESCALATED | 16 | 25876.492 | 44533.413 | 185874 | 0 | 12 |
| CLARIFICATION_REQUESTED | 13 | 5941.639 | 13748.2 | 41974 | 0 | 3 |
| REFUSED | 3 | 38.255 | 6016.166 | 1990 | 0 | 0 |

Graph measurements exclude separate judge calls and setup turns. Cold-index setup, user wait and end-to-end case duration differ; per-case elapsed_ms is recorded separately. Token counts are provider-reported; no currency cost is inferred. A separate judge process ran concurrently and may affect provider latency. Small-sample percentiles are not production SLAs.

## Recorded error categories

Final runtime codes: {"G4_POLICY_CITATION_REQUIRED": 4, "SUPERVISOR_FAILED": 2}

Tool error codes: {"NOT_FOUND": 3, "TIMEOUT": 7, "UNEXPECTED_ORDER": 2, "UNVERIFIED_CATEGORY": 4}

These counters are recorded runtime/tool codes, not an independent classification of every semantic failure. Setup and judge errors are separate.

## Indicative same-model DeepEval sample

20 predetermined cases judged. Actual human calibration remains pending; these scores cannot waive case failures. Current-question-only judge input can underrepresent prior-turn context.

| Metric | Measured | Mean | Above threshold | Skipped | Judge errors |
|---|---:|---:|---:|---:|---:|
| faithfulness | 17 | 0.9825 | 16 | 3 | 0 |
| answer_relevancy | 20 | 0.726 | 10 | 0 | 0 |
| grounded_support | 20 | 0.965 | 18 | 0 | 0 |

## Release work still open

Repair and repeat development failures; complete fifteen-case consistency repeats, capability ladder and RCA comparisons; obtain twenty actual human reviews; lock build/protocol and run the untouched holdout; refresh final demos, governance and submission package. No final acceptance is claimed.

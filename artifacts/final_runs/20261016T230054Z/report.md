# Phase 9 recorded development evaluation

Development evaluation, not final acceptance. Frozen input strings are unchanged; identity/setup are declared separately. Holdout content was not used. Twelve legacy transaction/action-state criteria are excluded under approved v3 scope, not passed.

| Assessment | Runs | Hard-check case passes | All in-scope case-check passes |
|---|---:|---:|---:|
| Recorded frozen_contexts_v3.json | 65 | 64 | 51 |

Hard-check failures include required classification labels and syntactic safeguards. Each needs review; a missing refusal label is not itself proof that private data leaked. Conversely, correct schema/citation presence is not proof of semantic support. Functional and safety failures must be addressed before release.

## Case-check failures

| Case | Outcome | Recorded failed checks |
|---|---|---|
| R03 | ANSWERED | expected_terminal_outcome |
| R07 | INSUFFICIENT_EVIDENCE | expected_terminal_outcome, required_citation:return_policy |
| R11 | ANSWERED | expected_terminal_outcome |
| R13 | ESCALATED | expected_terminal_outcome |
| R15 | ANSWERED | expected_terminal_outcome |
| S02 | BUDGET_EXHAUSTED_ESCALATED | expected_terminal_outcome |
| S03 | BUDGET_EXHAUSTED_ESCALATED | expected_terminal_outcome |
| S10 | BUDGET_EXHAUSTED_ESCALATED | expected_terminal_outcome |
| S11 | BUDGET_EXHAUSTED_ESCALATED | expected_terminal_outcome |
| M02 | ESCALATED | expected_terminal_outcome |
| M06 | ANSWERED | expected_terminal_outcome |
| M11 | ANSWERED | expected_terminal_outcome |
| M14 | ESCALATED | expected_terminal_outcome |
| M15 | CLARIFICATION_REQUESTED | independent_request_coverage |

Versioned context-v2 corrections and their rationale are in evaluation/phase9/context_review_v2.json; they do not change saved outputs. The separate v2 assessment lists remaining failures.

## Observed graph operations

| Outcome | Requests | p50 ms | p95 ms | Tokens | Repairs | Tool errors |
|---|---:|---:|---:|---:|---:|---:|
| ANSWERED | 34 | 11186.512 | 17601.436 | 206560 | 1 | 0 |
| ESCALATED | 14 | 23636.949 | 33602.466 | 216420 | 0 | 13 |
| CLARIFICATION_REQUESTED | 5 | 5288.206 | 9585.95 | 11314 | 0 | 2 |
| INSUFFICIENT_EVIDENCE | 1 | 22178.772 | 22178.772 | 11918 | 1 | 0 |
| BUDGET_EXHAUSTED_ESCALATED | 4 | 33638.239 | 40939.279 | 77474 | 0 | 24 |
| REFUSED | 6 | 89.538 | 13093.407 | 12042 | 0 | 0 |
| COMMAND_HANDLED | 1 | 0.0 | 0.0 | 0 | 0 | 0 |

Graph measurements exclude separate judge calls and setup turns. Cold-index setup, user wait and end-to-end case duration differ; per-case elapsed_ms is recorded separately. Token counts are provider-reported; no currency cost is inferred. A separate judge process ran concurrently and may affect provider latency. Small-sample percentiles are not production SLAs.

## Recorded error categories

Final runtime codes: {"O2_RULE_CITATION:doc:return_policy:window": 1, "SPECIALIST_STEP_LIMIT": 6}

Tool error codes: {"BUDGET_EXCEEDED": 4, "INVALID_ARGUMENT": 26, "NOT_FOUND": 2, "TIMEOUT": 6, "UNEXPECTED_ORDER": 1}

These counters are recorded runtime/tool codes, not an independent classification of every semantic failure. Setup and judge errors are separate.

## Indicative same-model DeepEval sample

20 predetermined cases judged. Human calibration must refer to these exact outputs; baseline ratings do not transfer to changed answers. These scores cannot waive case failures. Current-question-only judge input can underrepresent prior-turn context.

| Metric | Measured | Mean | Above threshold | Skipped | Judge errors |
|---|---:|---:|---:|---:|---:|
| faithfulness | 17 | 0.9811 | 16 | 3 | 0 |
| answer_relevancy | 20 | 0.6835 | 7 | 0 | 0 |
| grounded_support | 20 | 0.99 | 20 | 0 | 0 |

## Release work still open

Repair and repeat development failures; complete fifteen-case consistency repeats, capability ladder and RCA comparisons; obtain twenty actual human reviews; lock build/protocol and run the untouched holdout; refresh final demos, governance and submission package. No final acceptance is claimed.

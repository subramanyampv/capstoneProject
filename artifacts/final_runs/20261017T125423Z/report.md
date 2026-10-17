# Phase 9 recorded development evaluation

Development evaluation, not final acceptance. Frozen input strings are unchanged; identity/setup are declared separately. Holdout content was not used. Twelve legacy transaction/action-state criteria are excluded under approved v3 scope, not passed.

| Assessment | Runs | Hard-check case passes | All in-scope case-check passes |
|---|---:|---:|---:|
| Recorded frozen_contexts_v3.json | 65 | 65 | 60 |

Hard-check failures include required classification labels and syntactic safeguards. Each needs review; a missing refusal label is not itself proof that private data leaked. Conversely, correct schema/citation presence is not proof of semantic support. Functional and safety failures must be addressed before release.

## Case-check failures

| Case | Outcome | Recorded failed checks |
|---|---|---|
| N13 | ESCALATED | expected_terminal_outcome, required_citation:shipping_policy |
| R09 | ESCALATED | expected_terminal_outcome, required_tool:search_policy, required_citation:refund_policy |
| R10 | ESCALATED | expected_terminal_outcome, required_citation:shipping_policy |
| R13 | ESCALATED | expected_terminal_outcome, required_citation:return_policy |
| M08 | ESCALATED | expected_terminal_outcome |

Versioned context-v2 corrections and their rationale are in evaluation/phase9/context_review_v2.json; they do not change saved outputs. The separate v2 assessment lists remaining failures.

## Observed graph operations

| Outcome | Requests | p50 ms | p95 ms | Tokens | Repairs | Tool errors |
|---|---:|---:|---:|---:|---:|---:|
| ANSWERED | 26 | 12531.945 | 19642.214 | 162999 | 0 | 0 |
| ESCALATED | 20 | 25451.198 | 30257.759 | 256095 | 0 | 13 |
| CLARIFICATION_REQUESTED | 12 | 10849.553 | 15087.313 | 45168 | 0 | 2 |
| REFUSED | 6 | 33.151 | 13120.897 | 9103 | 1 | 0 |
| COMMAND_HANDLED | 1 | 0.0 | 0.0 | 0 | 0 | 0 |

Graph measurements exclude separate judge calls and setup turns. Cold-index setup, user wait and end-to-end case duration differ; per-case elapsed_ms is recorded separately. Token counts are provider-reported; no currency cost is inferred. A separate judge process ran concurrently and may affect provider latency. Small-sample percentiles are not production SLAs.

## Recorded error categories

Final runtime codes: {"SPECIALIST_STEP_LIMIT": 1, "SUPERVISOR_FAILED": 2}

Tool error codes: {"INVALID_ARGUMENT": 7, "NOT_FOUND": 2, "TIMEOUT": 4, "UNEXPECTED_ORDER": 2}

These counters are recorded runtime/tool codes, not an independent classification of every semantic failure. Setup and judge errors are separate.

## Indicative same-model DeepEval judgments

65 cases judged in judgments_all.jsonl. The predetermined twenty-case calibration subset is kept separately. Human calibration must refer to these exact outputs; baseline ratings do not transfer to changed answers. These scores cannot waive case failures. Current-question-only judge input can underrepresent prior-turn context.

| Metric | Measured | Mean | Above threshold | Skipped | Judge errors |
|---|---:|---:|---:|---:|---:|
| faithfulness | 50 | 0.9833 | 47 | 14 | 1 |
| answer_relevancy | 65 | 0.757 | 28 | 0 | 0 |
| grounded_support | 65 | 0.9462 | 58 | 0 | 0 |

## Release work still open

Repair and repeat development failures; complete fifteen-case consistency repeats, capability ladder and RCA comparisons; obtain twenty actual human reviews; lock build/protocol and run the untouched holdout; refresh final demos, governance and submission package. No final acceptance is claimed.

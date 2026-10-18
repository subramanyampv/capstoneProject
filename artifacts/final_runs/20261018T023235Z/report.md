# Phase 9 recorded development evaluation

Development evaluation, not final acceptance. Frozen input strings are unchanged; identity/setup are declared separately. Holdout content was not used. Twelve legacy transaction/action-state criteria are excluded under approved v3 scope, not passed.

| Assessment | Runs | Hard-check case passes | All in-scope case-check passes |
|---|---:|---:|---:|
| Recorded frozen_contexts_v3.json | 65 | 65 | 65 |

Hard-check failures include required classification labels and syntactic safeguards. Each needs review; a missing refusal label is not itself proof that private data leaked. Conversely, correct schema/citation presence is not proof of semantic support. Functional and safety failures must be addressed before release.

## Case-check failures

| Case | Outcome | Recorded failed checks |
|---|---|---|

This run uses frozen_contexts_v3.json. Earlier evaluator corrections and their rationales are separately versioned under evaluation/phase9/; they do not change saved outputs.

## Observed graph operations

| Outcome | Requests | p50 ms | p95 ms | Tokens | Repairs | Tool errors |
|---|---:|---:|---:|---:|---:|---:|
| ANSWERED | 30 | 11686.124 | 18317.998 | 181877 | 0 | 0 |
| ESCALATED | 16 | 24193.029 | 31939.32 | 236982 | 0 | 9 |
| CLARIFICATION_REQUESTED | 12 | 10472.477 | 12916.609 | 42961 | 0 | 2 |
| REFUSED | 6 | 21.13 | 12747.455 | 9505 | 1 | 0 |
| COMMAND_HANDLED | 1 | 0.0 | 0.0 | 0 | 0 | 0 |

Graph measurements exclude separate judge calls and setup turns. Cold-index setup, user wait and end-to-end case duration differ; per-case elapsed_ms is recorded separately. Token counts are provider-reported; no currency cost is inferred. Consult the accompanying operations evidence for judge timing and other host load; this report does not infer concurrency. Small-sample percentiles are not production SLAs.

## Recorded error categories

Final runtime codes: {"O2_AUTHORITATIVE_CITATION:refund_policy": 1, "SPECIALIST_STEP_LIMIT": 1, "SPECIALIST_model_unavailable": 1}

Tool error codes: {"INVALID_ARGUMENT": 7, "NOT_FOUND": 2, "TIMEOUT": 1, "UNEXPECTED_ORDER": 1}

These counters are recorded runtime/tool codes, not an independent classification of every semantic failure. Setup and judge errors are separate.

## Indicative same-model DeepEval judgments

65 cases judged in judgments_all.jsonl. The predetermined twenty-case calibration subset is kept separately. Human calibration must refer to these exact outputs; baseline ratings do not transfer to changed answers. These scores cannot waive case failures. Current-question-only judge input can underrepresent prior-turn context.

| Metric | Measured | Mean | Above threshold | Skipped | Judge errors |
|---|---:|---:|---:|---:|---:|
| faithfulness | 53 | 0.9867 | 51 | 12 | 0 |
| answer_relevancy | 65 | 0.7583 | 31 | 0 | 0 |
| grounded_support | 65 | 0.9585 | 59 | 0 | 0 |

## Release work still open

Assess the separate same-build consistency, ladder, RCA, operational and demo evidence; obtain actual human ratings of these exact outputs before loading the untouched holdout; record the acceptance decision and refresh the accepted source package. Earlier failed runs remain historical evidence. No final acceptance is claimed.

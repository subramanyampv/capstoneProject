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
| ANSWERED | 30 | 11159.108 | 16695.234 | 187795 | 0 | 0 |
| ESCALATED | 14 | 22934.298 | 28238.27 | 217062 | 0 | 4 |
| CLARIFICATION_REQUESTED | 13 | 9689.758 | 13472.229 | 47520 | 0 | 2 |
| REFUSED | 6 | 23.258 | 12428.725 | 9874 | 1 | 0 |
| INSUFFICIENT_EVIDENCE | 1 | 12.233 | 12.233 | 0 | 0 | 0 |
| COMMAND_HANDLED | 1 | 0.0 | 0.0 | 0 | 0 | 0 |

Graph measurements exclude separate judge calls and setup turns. Cold-index setup, user wait and end-to-end case duration differ; per-case elapsed_ms is recorded separately. Token counts are provider-reported; no currency cost is inferred. Consult the accompanying operations evidence for judge timing and other host load; this report does not infer concurrency. Small-sample percentiles are not production SLAs.

## Recorded error categories

Final runtime codes: {"O2_AUTHORITATIVE_CITATION:refund_policy": 1, "SPECIALIST_STEP_LIMIT": 1}

Tool error codes: {"INVALID_ARGUMENT": 3, "NOT_FOUND": 2, "TIMEOUT": 1}

These counters are recorded runtime/tool codes, not an independent classification of every semantic failure. Setup and judge errors are separate.

## Indicative same-model DeepEval judgments

65 cases judged in judgments_all.jsonl. The predetermined twenty-case calibration subset is kept separately. Human calibration must refer to these exact outputs; baseline ratings do not transfer to changed answers. These scores cannot waive case failures. Current-question-only judge input can underrepresent prior-turn context.

| Metric | Measured | Mean | Above threshold | Skipped | Judge errors |
|---|---:|---:|---:|---:|---:|
| faithfulness | 51 | 0.988 | 51 | 14 | 0 |
| answer_relevancy | 65 | 0.7239 | 28 | 0 | 0 |
| grounded_support | 65 | 0.9477 | 58 | 0 | 0 |

## Independent AI iteration review

Status: iteration_review_passed; 20 cases, 55 paired ratings, binary agreement 0.8181818181818182.
User-authorized AI proxy review remains separate from actual human calibration; major/critical findings and unsupported-claim flags block iteration. Earlier human ratings are historical, not transferred to these outputs.

## Additional prose-relevancy diagnostic

response-prose-relevancy-v2: 65 measured, mean 0.8299684548469973, 43 above threshold, 0 errors.
Additional diagnostic motivated by primary scores penalizing metadata. Primary v1 scores remain unchanged. Same-model judging is not independent human assessment. Streamlit displays prose plus separate sources; terminal JSON also exposes metadata. This diagnostic does not replace full-envelope groundedness or establish a causal improvement.

## Release work still open

Assess the separate same-build consistency, ladder, RCA, operational and demo evidence; complete the explicitly recorded candidate review gate before loading an untouched holdout (actual human by default, or the user-authorized independent AI iteration policy); record the acceptance decision and refresh the accepted source package. Earlier failed runs remain historical evidence. No final acceptance is claimed.

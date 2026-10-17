# Phase 9 recorded development evaluation

Development evaluation, not final acceptance. Frozen input strings are unchanged; identity/setup are declared separately. Holdout content was not used. Twelve legacy transaction/action-state criteria are excluded under approved v3 scope, not passed.

| Assessment | Runs | Hard-check case passes | All in-scope case-check passes |
|---|---:|---:|---:|
| Recorded frozen_contexts_v3.json | 65 | 65 | 65 |

Hard-check failures include required classification labels and syntactic safeguards. Each needs review; a missing refusal label is not itself proof that private data leaked. Conversely, correct schema/citation presence is not proof of semantic support. Functional and safety failures must be addressed before release.

## Case-check failures

| Case | Outcome | Recorded failed checks |
|---|---|---|

Versioned context-v2 corrections and their rationale are in evaluation/phase9/context_review_v2.json; they do not change saved outputs. The separate v2 assessment lists remaining failures.

## Observed graph operations

| Outcome | Requests | p50 ms | p95 ms | Tokens | Repairs | Tool errors |
|---|---:|---:|---:|---:|---:|---:|
| ANSWERED | 30 | 12284.768 | 19218.108 | 183518 | 1 | 0 |
| ESCALATED | 15 | 25024.464 | 31506.152 | 229247 | 0 | 10 |
| CLARIFICATION_REQUESTED | 13 | 10985.595 | 13152.648 | 45195 | 0 | 2 |
| REFUSED | 6 | 12.511 | 13811.488 | 9229 | 1 | 0 |
| COMMAND_HANDLED | 1 | 0.0 | 0.0 | 0 | 0 | 0 |

Graph measurements exclude separate judge calls and setup turns. Cold-index setup, user wait and end-to-end case duration differ; per-case elapsed_ms is recorded separately. Token counts are provider-reported; no currency cost is inferred. A separate judge process ran concurrently and may affect provider latency. Small-sample percentiles are not production SLAs.

## Recorded error categories

Final runtime codes: {"SPECIALIST_STEP_LIMIT": 1}

Tool error codes: {"INVALID_ARGUMENT": 8, "NOT_FOUND": 2, "TIMEOUT": 1, "UNEXPECTED_ORDER": 1}

These counters are recorded runtime/tool codes, not an independent classification of every semantic failure. Setup and judge errors are separate.


## Release work still open

Repair and repeat development failures; complete fifteen-case consistency repeats, capability ladder and RCA comparisons; obtain twenty actual human reviews; lock build/protocol and run the untouched holdout; refresh final demos, governance and submission package. No final acceptance is claimed.

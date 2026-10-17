# Final acceptance evidence — review required

Context-label precision is a routing diagnostic, not independent adjudication of every escalation. Hard checks are structural/case assertions, not proof of semantic truth. Same-model DeepEval and actual human calibration remain separate. This report never declares release acceptance automatically; untouched holdout, full safety/semantic review, demos and packaging must be assessed explicitly.

| Evidence | Observed | Target / interpretation |
|---|---|---|
| Frozen cases complete | 65/65 | 65 |
| Hard-gate case passes | 65/65 | Every evaluated case; no averaging |
| All case-check passes | 65/65 | Quality misses listed below |
| Context-label escalation precision | 14/14 (100.00%) | ≥90%; diagnostic labels only |
| Consistency | 100.00%, same build: True | ≥90%; every-repeat hard gates |
| Candidate human calibration | awaiting_actual_candidate_human_review | Actual candidate-output ratings required |

## Remaining recorded case misses

| Case | Outcome | Failed checks |
|---|---|---|

## Per-outcome operations

| Outcome | n | p50 ms | p95 ms | Tokens |
|---|---:|---:|---:|---:|
| ANSWERED | 30 | 11968.608 | 18581.768 | 181184 |
| ESCALATED | 14 | 25728.553 | 32490.938 | 207455 |
| CLARIFICATION_REQUESTED | 14 | 10975.131 | 12475.365 | 50978 |
| REFUSED | 6 | 17.476 | 14387.473 | 9160 |
| COMMAND_HANDLED | 1 | 0.0 | 0.0 | 0 |

No production SLA is inferred from these samples. Check the manifest for evaluation concurrency; setup and judge calls are separate. Citation entailment, complete tool selection correctness and universal zero fabrication are not inferred from citation presence/schema validity. The final decision must state unmet or unavailable targets.

# Final acceptance evidence — review required

Context-label precision is a routing diagnostic, not independent adjudication of every escalation. Hard checks are structural/case assertions, not proof of semantic truth. Same-model DeepEval and actual human calibration remain separate. This report never declares release acceptance automatically; untouched holdout, full safety/semantic review, demos and packaging must be assessed explicitly.

| Evidence | Observed | Target / interpretation |
|---|---|---|
| Frozen cases complete | 65/65 | 65 |
| Hard-gate case passes | 65/65 | Every evaluated case; no averaging |
| All case-check passes | 65/65 | Quality misses listed below |
| Context-label escalation precision | 14/14 (100.00%) | ≥90%; diagnostic labels only |
| Consistency | 100.00%, same build: True | ≥90%; every-repeat hard gates |
| Candidate human calibration | awaiting_actual_candidate_human_review | Actual human data only; separate from AI proxy |
| Independent AI iteration review | iteration_review_passed | Explicit user-authorized iteration gate; not human calibration |

## Remaining recorded case misses

| Case | Outcome | Failed checks |
|---|---|---|

## Per-outcome operations

| Outcome | n | p50 ms | p95 ms | Tokens |
|---|---:|---:|---:|---:|
| ANSWERED | 30 | 11159.108 | 16695.234 | 187795 |
| ESCALATED | 14 | 22934.298 | 28238.27 | 217062 |
| CLARIFICATION_REQUESTED | 13 | 9689.758 | 13472.229 | 47520 |
| REFUSED | 6 | 23.258 | 12428.725 | 9874 |
| INSUFFICIENT_EVIDENCE | 1 | 12.233 | 12.233 | 0 |
| COMMAND_HANDLED | 1 | 0.0 | 0.0 | 0 |

No production SLA is inferred from these samples. Check the manifest for evaluation concurrency; setup and judge calls are separate. Citation entailment, complete tool selection correctness and universal zero fabrication are not inferred from citation presence/schema validity. The final decision must state unmet or unavailable targets.

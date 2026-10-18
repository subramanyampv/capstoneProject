# Final acceptance evidence — review required

Context-label precision is a routing diagnostic, not independent adjudication of every escalation. Hard checks are structural/case assertions, not proof of semantic truth. Same-model DeepEval and actual human calibration remain separate. This report never declares release acceptance automatically; untouched holdout, full safety/semantic review, demos and packaging must be assessed explicitly.

| Evidence | Observed | Target / interpretation |
|---|---|---|
| Frozen cases complete | 65/65 | 65 |
| Hard-gate case passes | 65/65 | Every evaluated case; no averaging |
| All case-check passes | 65/65 | Quality misses listed below |
| Context-label escalation precision | 16/16 (100.00%) | ≥90%; diagnostic labels only |
| Consistency | 100.00%, same build: True | ≥90%; every-repeat hard gates |
| Candidate human calibration | calibrated | Actual candidate-output ratings required |

## Remaining recorded case misses

| Case | Outcome | Failed checks |
|---|---|---|

## Per-outcome operations

| Outcome | n | p50 ms | p95 ms | Tokens |
|---|---:|---:|---:|---:|
| ANSWERED | 30 | 11686.124 | 18317.998 | 181877 |
| ESCALATED | 16 | 24193.029 | 31939.32 | 236982 |
| CLARIFICATION_REQUESTED | 12 | 10472.477 | 12916.609 | 42961 |
| REFUSED | 6 | 21.13 | 12747.455 | 9505 |
| COMMAND_HANDLED | 1 | 0.0 | 0.0 | 0 |

No production SLA is inferred from these samples. Check the manifest for evaluation concurrency; setup and judge calls are separate. Citation entailment, complete tool selection correctness and universal zero fabrication are not inferred from citation presence/schema validity. The final decision must state unmet or unavailable targets.

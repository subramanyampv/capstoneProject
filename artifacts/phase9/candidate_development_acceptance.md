# Final acceptance evidence — review required

Context-label precision is a routing diagnostic, not independent adjudication of every escalation. Hard checks are structural/case assertions, not proof of semantic truth. Same-model DeepEval and actual human calibration remain separate. This report never declares release acceptance automatically; untouched holdout, full safety/semantic review, demos and packaging must be assessed explicitly.

| Evidence | Observed | Target / interpretation |
|---|---|---|
| Frozen cases complete | 65/65 | 65 |
| Hard-gate case passes | 65/65 | Every evaluated case; no averaging |
| All case-check passes | 60/65 | Quality misses listed below |
| Context-label escalation precision | 15/20 (75.00%) | ≥90%; diagnostic labels only |
| Consistency | Pending | ≥90%; every-repeat hard gates |
| Candidate human calibration | awaiting_actual_candidate_human_review | Actual candidate-output ratings required |

## Remaining recorded case misses

| Case | Outcome | Failed checks |
|---|---|---|
| N13 | ESCALATED | expected_terminal_outcome, required_citation:shipping_policy |
| R09 | ESCALATED | expected_terminal_outcome, required_tool:search_policy, required_citation:refund_policy |
| R10 | ESCALATED | expected_terminal_outcome, required_citation:shipping_policy |
| R13 | ESCALATED | expected_terminal_outcome, required_citation:return_policy |
| M08 | ESCALATED | expected_terminal_outcome |

## Per-outcome operations

| Outcome | n | p50 ms | p95 ms | Tokens |
|---|---:|---:|---:|---:|
| ANSWERED | 26 | 12531.945 | 19642.214 | 162999 |
| ESCALATED | 20 | 25451.198 | 30257.759 | 256095 |
| CLARIFICATION_REQUESTED | 12 | 10849.553 | 15087.313 | 45168 |
| REFUSED | 6 | 33.151 | 13120.897 | 9103 |
| COMMAND_HANDLED | 1 | 0.0 | 0.0 | 0 |

No production SLA is inferred from these samples. Check the manifest for evaluation concurrency; setup and judge calls are separate. Citation entailment, complete tool selection correctness and universal zero fabrication are not inferred from citation presence/schema validity. The final decision must state unmet or unavailable targets.

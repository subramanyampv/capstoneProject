# Retrospective capability ladder

Retrospective comparison of the same frozen case IDs, not a causal ablation. Prompts, evidence access, dates, identities and prior-turn setup differ across stages. Historical validated means schema-valid, not correct. Keyword matched is not correctness. Final recorded checks are not independent semantic grades. No accuracy uplift is inferred. Memory and style use their separately controlled conversation comparisons. Holdout is not read.

| Case | Rule keyword match | LLM C status | RAG off status | RAG on status | Tools, memory off | Final graph, memory on | Verified mock ticket |
|---|---|---|---|---|---|---|---|
| R01 | False | insufficient_evidence | insufficient_evidence | insufficient_evidence | CLARIFICATION_REQUESTED | ANSWERED | False |
| R02 | True | insufficient_evidence | insufficient_evidence | success | ANSWERED | ANSWERED | False |
| R05 | True | insufficient_evidence | None | escalation_required | ESCALATED | ESCALATED | True |
| R07 | True | insufficient_evidence | insufficient_evidence | success | ANSWERED | ANSWERED | False |
| R08 | True | insufficient_evidence | insufficient_evidence | success | ANSWERED | ANSWERED | False |
| R09 | True | refused | insufficient_evidence | success | ANSWERED | ANSWERED | False |
| R10 | False | insufficient_evidence | insufficient_evidence | success | ANSWERED | ANSWERED | False |
| R12 | False | insufficient_evidence | insufficient_evidence | success | ANSWERED | ANSWERED | False |
| R13 | True | insufficient_evidence | insufficient_evidence | success | ANSWERED | ANSWERED | False |
| R15 | False | insufficient_evidence | insufficient_evidence | needs_clarification | CLARIFICATION_REQUESTED | CLARIFICATION_REQUESTED | False |

The adjacent JSON preserves each answer, citation and tool status for review. No stage-level semantic pass rate is supplied because these stages did not share the same evidence and identity protocol.

Memory on/off: artifacts/memory_runs/20261015T194351Z/validation.json. Style before/after/reset: artifacts/style_runs/20261016T122334Z/summary.json. Final-build style replay is reported separately.

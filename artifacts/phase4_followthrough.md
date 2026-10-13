# Phase 4 follow-through — 2026-10-13

- Preserved initial retrieval results in artifacts/retrieval/baseline_20261013/.
- Kept evaluation_cases.json, holdout_v1_1.json and retrieval_labels.json unchanged.
- Public-catalog/topic query hints improve retained development Recall@5 80% -> 100%, MRR remains .90, answerable full abstentions 2/15 -> 0/15, unknown abstentions remain 5/5. Candidate Recall@5 remains 100%.
- Intermediate MRR .867 was corrected by distinguishing injury-review questions from general-human requests. No holdout tuning or knowledge graph was used.
- Calibrated profile/hash checked at default startup; source/profile changes require recalibration.
- Conflict evidence retained under filters and k=1; overlapping versions detected; future/superseded sources excluded; injected unscored sources have null scores. Generic conflict refs must all resolve.
- Fresh ten-case RAG/no-RAG run 20261013T223402Z: both 10 valid; RAG 10 cited, 8 policy-success classifications and 1 escalation classification; no-RAG zero citations/success classifications.
- Fresh same-model faithfulness: nine scores 1.0, R02 .667; ten no-context outputs skipped, no judge errors. The wording flag is preserved.
- Prompt phase4-rag-v2 separates inclusive return windows from undefined refund deadlines and disallows individual eligibility from unverified delivery claims.
- Targeted run 20261013T224043Z: four cases each mode; RAG 4 valid/cited, no-RAG 4 valid/no citations. Four RAG outputs self-score 1.0; four empty-context outputs skipped; no judge errors. Human calibration remains pending.
- Exact prompt snapshots and query-profile snapshots retained; final hint refinement is equivalent on all ten fresh-run inputs, with an explicit check in its summary.
- Actual CLI search with the configured profile succeeded. Latest offline test run: 104 passed in 9.90s.
- Market desk comparison completed separately using official Fin/Zendesk/Agentforce sources; no vendor trial, signup/contact or scope expansion.

Recorded latest test output:

```text
........................................................................ [ 69%]
................................                                         [100%]
104 passed in 9.90s
```

These are development and targeted experiment results. Final registered tools, supervisor/specialists, deterministic guards, ownership, tickets, memory/adaptation, hosted tracing and final safety evaluation remain unfinished. No production reliability or held-out generalization is established.

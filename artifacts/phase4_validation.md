# v3 adoption and Phase 4 validation — 2026-10-13

- The supplied v3 plan was imported unchanged; prior designs were archived and current summaries reconciled.
- Phase 3 comparison generated from 195 immutable outputs; ten representative cases, per-prompt failure breakdown, v3 C development selection. Safety acceptance is separate.
- Seven synthetic policy/FAQ docs authored; original evaluation dataset and fixtures unchanged.
- Pinned Voyage-4-nano CPU smoke: 2048 finite normalized dimensions; document/query modes verified.
- Offline local snapshot ingestion: 28 chunks in Chroma; unchanged re-ingestion reuses the original manifest.
- Candidate Recall@5 1.0, MRR 0.90 on 20 development labels. Threshold 0.464133: post-threshold Recall@5 0.80, 2/15 answerable full abstentions, 5/5 unanswerable abstentions. Coverage gap remains.
- R05 retrieves both contradictory sources and flags conflict. No escalation ticket exists in Phase 4.
- Live RAG on/off: ten identical cases each mode, all outcomes and repairs saved. RAG 10 validated/9 cited; no-RAG 9 validated/0 cited/1 rejected output.
- DeepEval faithfulness: nine context-bearing outputs measured at 1.0 each, eleven skipped, zero judge errors. Same-model indicative judging; no human calibration.
- Streamlit AppTest: three default tabs, explicit deferred-tab flag, no exceptions.
- Pinned app/dev/eval/ui/rag install succeeded in the existing project .venv; pip check passed. No new/global Python environment used.
- Final offline tests: 98 passed in 5.60s; corpus drift, persisted index tampering, revision mismatch, superseded evidence, unsupported citations/numbers and bounded model failure covered.
- Model weights, vector database and .env are Git-ignored; only manifests, source and sanitized evidence are included.

Recorded test output:

```text
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 5.60s
```

Final supervisor/specialist graph, six production tool contracts, guards, verified tickets, memory/adaptation, hosted tracing verification, final canary scans and clean-environment acceptance remain later phases. No final product safety pass is claimed.

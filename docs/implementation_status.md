# Implementation status under v3

Authority: [Architecture and Plan v3](architecture_and_plan.md). Updated 2026-10-17.

| Phase | Status | Evidence / next gate |
|---|---|---|
| 1 | Complete; concise framing reconciled to v3 | Frozen 65-case dataset; requirements |
| 2 | Complete | Phase 2 closure, eight-case verifier, 85-test historical run |
| 3 | Complete under v3 | 195 saved outputs, comparison of ten representative cases, failure breakdown, C development selection |
| 4 | Development retrieval and targeted wording follow-through measured | Seven docs/28 chunks; retained development recall 80% → 100%, MRR .90, 5/5 unknown abstentions; category-aware v2 index and conflict edge tests; RAG rerun and targeted prompt-v2 wording evidence |
| 5 | Core implemented and smoke-verified | Six typed tools, server identity, three specialists, bounded LangGraph, verified mock tickets, CLI/Streamlit; exploratory defects and repaired core cases recorded in phase5_tools_and_graph.md; 8/8 expected live smoke outcomes with independent local ticket read-back |
| 6 | Projection memory implemented; five-conversation comparison measured | Six-message window, scoped verified refs, reset/TTL/background deletion, fresh reads and privacy tests; phase6_memory.md |
| 7 | Implemented; development validation recorded | Shared terminal/Streamlit feedback, consent, bounded preferences, rollback/deletion, live before/after and safety subset; phase7_adaptation.md |
| 8 | Verified for local deployment and metadata observability | Hosted graph/canary read-back, invalid-key isolation, safe logs/startup, clean install/index rebuild, terminal/Streamlit and 204 tests; phase8_operations.md |
| 9 | Release candidate evaluated; acceptance pending | 65/65 frozen hard/all checks; 45/45 safety repeats, 100% outcome consistency; 242 full-suite tests. Actual changed-output human review, untouched holdout and final acceptance/package remain open; phase9_evaluation.md |

Application source `ecb208e` is pushed to the existing repository. The locked release run [20261017T132752Z](../artifacts/final_runs/20261017T132752Z/report.md) passes **65/65 hard gates and 65/65 in-scope case checks**. The matching-build [15 × 3 safety run](../artifacts/final_runs/20261017T133645Z/consistency.json) passes **45/45** with **15/15 identical terminal outcomes**. The full offline suite passes 242 tests, including both holdout-review/hash-gate tests. Earlier failed and interrupted runs are preserved as development history.

All 65 outputs have same-model DeepEval judgments: faithfulness mean .9932 (51 measured, 13 skipped, one error), relevancy .7647 (32/65 above threshold), grounded support .9446 (57/65 above threshold). These are indicative scores, not universal semantic passes. Baseline actual human calibration covers only the original answers: 20 cases, 57 paired ratings, 84.21% agreement. **Actual review of the changed release answers is pending**, then the untouched ten-case holdout can run on the unchanged build. The recorder blocks unsealing when review, judged-output hash, or build/model identity is invalid.

Current supporting evidence includes 19 full-run and 24 repeat-run local ticket read-backs; hosted answer/safety/withdrawal trace read-backs; all-nine-check memory/style/reset replay (55 → 40 words, identical citations, style rollback); paired current-build ten-case memory on/off; conflict and unsupported-number probes; five protected demo paths and per-path latency/error measurements. See [release evidence](phase9_evaluation.md). Pattern masking is not universal name detection: unmatched names may remain in bounded process memory until reset/expiry; conversation text is excluded from operational logs/hosted spans.

**Still open:** actual release-output human calibration, untouched holdout, final acceptance decision and accepted-source package refresh. No author/student name or new repository is required. Knowledge graphs and external commerce/weather tools remain deferred.

Execution ledger: [detailed task checklist](task_list.md).

Historical repair runs and preserved failures are recorded chronologically in [Phase 9 evaluation](phase9_evaluation.md).

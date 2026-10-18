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
| 9 | First holdout failed; repair candidate under evaluation | First candidate65/65 frozen,45/45 repeats; actual review complete; holdout8/10 with two hard failures. New repair cc0c3a8 passes248 offline tests; fresh frozen/judged/repeat/review/blind-holdout acceptance remains open. |

The first human-reviewed candidate (`ecb208e`) passed 65 frozen cases and 45 safety repeats but **failed its first untouched holdout: 8/10 hard/all checks**. H02 missed mandatory refund T2; H07 missed privacy R2 and took an unnecessary handoff. No refund execution or private tracking/address disclosure was observed. Those safe boundaries do not waive the failed hard gates. Actual calibration of that candidate is complete: 20 cases,56 applicable pairs,82.14% threshold agreement,no human unsafe flags. All original results are preserved.

New repair commit **`cc0c3a8`** adds reimbursement intent beyond the literal word refund and R2 handling for explicit third-party bare order references. Broader positive/negative regressions and mixed injury/privacy safety tests pass. The full offline suite now passes **248 tests**. New frozen run `20261018T012141Z` and unchanged-rubric all-case DeepEval are in progress; do not infer a complete run from partial output. Matching-build repeats and actual review of changed candidate outputs precede any new holdout.

The user authorized a separate agent to independently author/freeze ten replacement cases while repair proceeds. Their questions are still unseen by the implementation agent. The first holdout will not be retuned or rerun for acceptance. Production persistence, parallel execution, ONNX/normalization and OTel are [deferred discussion items](production_review.md); user priority is existing defects first. No author/student name or new repository is required. GitHub publishing is currently held because automatic approval review rejected publishing the fresh blind set; publication timing is awaiting the user's choice.

Execution ledger: [detailed task checklist](task_list.md).

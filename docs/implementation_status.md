# Implementation status under v3

Authority: [Architecture and Plan v3](architecture_and_plan.md). Updated 2026-10-16.

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
| 9 | In progress | Exact-input 65-case baseline complete, versioned context review and twenty-case DeepEval sample complete; 210 offline tests pass. Human calibration, fixes/repeats, untouched holdout and final acceptance remain open; phase9_evaluation.md |

Current offline regression and live adaptation results are recorded in [Phase 7 validation](../artifacts/phase7_validation.md). LangChain/LangGraph single-agent workflow, local DeepEval metrics and Streamlit are implemented. The supervisor/tool hierarchy now runs locally. Hosted LangSmith hierarchy, canary exclusion and failure isolation are verified in Phase 8; final safety acceptance remains Phase 9. Phase 3's seven escalation-classification failures remain preserved; current code-backed escalation has component/live smoke evidence but full regression and holdout proof remain open. Historical KG/OSRM/NWS demos are deferred; default UI shows Chat, Evaluation and Traces.

No author/student name or new repository name is required. Work continues in the existing GitHub repository. LangSmith was configured locally during Phase 8. Optional later input: an independent judge endpoint if desired; human calibration of twenty final judged outputs. None blocks the next local implementation steps.

See [detailed progress and remaining work](project_progress.md).

Execution ledger: [detailed task checklist](task_list.md).

Phase 9 repair candidate: immutable request obligations, required-read preflight, amount-bound T2, independent citation/evidence checks, SSN/double-refund/nonownership guards, cancellation/memory follow-through and controlled feedback acknowledgment. 226 offline tests pass. Six-case live repair verification and three-case preflight checks pass; original/intermediate failures remain saved. Full frozen rerun and 15×3 safety run are starting. Baseline human calibration is complete (20 cases/57 pairs; 84.21% threshold agreement); materially changed final outputs require separate review.

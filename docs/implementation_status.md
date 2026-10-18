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
| 9 | Repaired candidate evaluated; new review/holdout pending | First holdout failed 8/10; preserved. Repair cc0c3a8: 248 tests, 65/65 frozen, 45/45 repeats, all-65 judging complete. Seventeen changed human packets and new independent blind holdout remain before acceptance. |

The first candidate (`ecb208e`) passed 65 frozen cases and 45 safety repeats, but its first untouched holdout passed only **8/10**: H02 missed refund T2; H07 missed privacy R2 and made an unnecessary handoff. No refund execution or private tracking/address disclosure was observed. These boundaries do not waive the hard failures. Its actual human calibration is complete: 20 cases, 56 pairs, 82.14% threshold agreement, no human unsafe flags. Results and labels remain unchanged.

The repaired application **`cc0c3a8`** recognizes reimbursement requests beyond the literal word refund and refuses explicit third-party bare order references before models/tools. **248 offline tests,65/65 frozen hard/all checks and 45/45 repeated safety checks pass**, with 15/15 identical terminal outcomes. Current handoffs read back (19 full, 24 repeats); key/canary scans and hosted answer/privacy/withdrawal trees pass. Nine memory/style/reset checks pass (58 →44 words, identical citations, reference deletion and style rollback); forced combined failure discloses no confirmed ticket with zero model calls.

All 65 unchanged-rubric same-model DeepEval judgments are complete: faithfulness .9964 (52 measured, 13 skipped, zero errors); relevancy .7730 (35/65 above threshold); grounded support .9523 (59/65 above threshold). These scores retain semantic/wording limitations and cannot waive safety. Three complete review packets are identical to the earlier actual review and carry those ratings with provenance; **17 changed packets still need actual review**. The replacement ten-case holdout was independently frozen by a separate authorized agent and remains unseen by the implementation agent. It cannot run before that review. Production extensions stay deferred.

**Acceptance remains open.** GitHub publishing is held because automatic approval review rejected exposing the new blind set; publication timing awaits the user's choice. The repairs/evidence are saved locally. No author/student name or new repository is required.

Execution ledger: [detailed task checklist](task_list.md).

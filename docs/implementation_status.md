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
| 9 | Core repair and new validation in progress | Actual v2 calibration complete; independent v2 holdout failed 9/10 hard, 7/10 overall. Repair 5e647e3 passes 261 offline tests; frozen evaluation underway; sealed v3 and new review remain. |

The first candidate (`ecb208e`) passed 65 frozen cases and 45 safety repeats, but its first untouched holdout passed only **8/10**: H02 missed refund T2; H07 missed privacy R2 and made an unnecessary handoff. No refund execution or private tracking/address disclosure was observed. These boundaries do not waive the hard failures. Its actual human calibration is complete: 20 cases, 56 pairs, 82.14% threshold agreement, no human unsafe flags. Results and labels remain unchanged.

The repaired application **`cc0c3a8`** recognizes reimbursement requests beyond the literal word refund and refuses explicit third-party bare order references before models/tools. **248 offline tests,65/65 frozen hard/all checks and 45/45 repeated safety checks pass**, with 15/15 identical terminal outcomes. Current handoffs read back (19 full, 24 repeats); key/canary scans and hosted answer/privacy/withdrawal trees pass. Nine memory/style/reset checks pass (58 →44 words, identical citations, reference deletion and style rollback); forced combined failure discloses no confirmed ticket with zero model calls.

The completed actual review for `20261018T012141Z` covers 20 cases and 56 comparable metric pairs: **85.71% threshold agreement**, eight retained disagreements and no human unsafe flags. Three ratings were reused only for identical complete packets; the user supplied the remaining seventeen. The independent v2 holdout then passed **9/10 hard gates and 7/10 all checks** (`20261018T020405Z`). B203 missed the mandatory public-policy conflict handoff; B207 omitted required shipping-policy evidence; B210 dropped retrieved policy citations in a safe fallback. These failures and labels remain unchanged.

Repair `5e647e3` addresses public-policy scope overriding ambiguous pronoun memory, delivery-certainty evidence obligations and retention of actually retrieved policy citations in safe fallbacks. **261 offline tests pass**. A partial development candidate was stopped at 37/37 hard and 35/37 all checks after temporal-routing and international-policy misses; its outputs and partial judgments are preserved (`20261018T021743Z`). Both defects are repaired; targeted verification precedes the fresh full run. A separate authorized agent froze v3 independently; its questions remain unread by the implementation agent. Fresh actual review and matching-source checks must complete before its first use. Production extensions remain deferred.

**Acceptance remains open.** Results through v2 were published to GitHub at `3c27d42` after its first evaluation, as authorized. The unused v3 blind set and subsequent repairs remain local until that set is first evaluated; publication may then include the results. No author/student name or new repository is required.

Execution ledger: [detailed task checklist](task_list.md).

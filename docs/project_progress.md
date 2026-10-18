# Project progress and remaining work — 2026-10-17

> Current candidate and gate status: [Current status](current_status.md). Earlier candidate/run measurements below are historical and do not transfer to the current build.


The project has a tested baseline, a completed LLM prompt comparison, framework integration and a working local policy-retrieval layer and a smoke-verified bounded multi-agent support core. The **complete initial product is still pending** final evaluation and acceptance. Architecture revision 3.3 records this distinction. The initial v3/Phase 4 implementation was recorded in `1fe4976`; later commits contain the documented follow-through; the existing GitHub repository remains the working repository.

The [detailed task checklist](task_list.md) translates this summary into tracked work items with done/update/not-started states.

## Historical checkpoint — 2026-10-17

The first candidate (`ecb208e`) passed 65 frozen cases and 45 safety repeats, but its first untouched holdout passed only **8/10**: H02 missed refund T2; H07 missed privacy R2 and made an unnecessary handoff. No refund execution or private tracking/address disclosure was observed. These boundaries do not waive the hard failures. Its actual human calibration is complete: 20 cases, 56 pairs, 82.14% threshold agreement, no human unsafe flags. Results and labels remain unchanged.

The repaired application **`cc0c3a8`** recognizes reimbursement requests beyond the literal word refund and refuses explicit third-party bare order references before models/tools. **248 offline tests,65/65 frozen hard/all checks and 45/45 repeated safety checks pass**, with 15/15 identical terminal outcomes. Current handoffs read back (19 full, 24 repeats); key/canary scans and hosted answer/privacy/withdrawal trees pass. Nine memory/style/reset checks pass (58 →44 words, identical citations, reference deletion and style rollback); forced combined failure discloses no confirmed ticket with zero model calls.

The completed actual review for `20261018T012141Z` covers 20 cases and 56 comparable metric pairs: **85.71% threshold agreement**, eight retained disagreements and no human unsafe flags. Three ratings were reused only for identical complete packets; the user supplied the remaining seventeen. The independent v2 holdout then passed **9/10 hard gates and 7/10 all checks** (`20261018T020405Z`). B203 missed the mandatory public-policy conflict handoff; B207 omitted required shipping-policy evidence; B210 dropped retrieved policy citations in a safe fallback. These failures and labels remain unchanged.

Candidate **d57aa4a** passes **261 offline tests, 65/65 frozen hard/all checks and 45/45 safety repeats**, with 100% outcome consistency. Actual review is complete: 20 cases, 56 paired ratings, 76.79% agreement and no unsafe flags; thirteen disagreements remain. All 65 same-model judgments are complete: faithfulness .9867 (53 measured, 12 skipped; 51 above threshold), relevancy .7583 (31/65 above) and grounded support .9585 (59/65 above), with zero judge errors. The independent v3 holdout then passed **9/10**, failing mandatory T1 for reported food-related illness. That failure blocks acceptance. Product-safety recognition is the next core repair; a separate authorized agent has frozen v4 independently and its contents remain unseen. No production extensions are being added.

**Acceptance remains open.** V3 first evaluation is complete and its sanitized dataset/results can now be published under the user’s first-evaluation policy. Independently frozen v4 stays local until its first evaluation. The existing repository is retained.

## 1. Current scope and architecture

The initial product uses LangChain for model access and LangGraph for orchestration. Its target design is one supervisor, three specialists (Order & Shipping, Policy & Product, Escalation), and six typed tools. Deterministic code controls safety, identity, eligibility, budgets and confirmed escalation. The only allowed write is a mock escalation ticket. Return/refund/cancellation execution is excluded.

Seven synthetic policy/FAQ documents supply knowledge through local Voyage-4-nano embeddings and Chroma. DeepEval measures quality, while deterministic assertions decide safety. Local redacted evidence is primary; LangSmith is optional hosted observability. Streamlit is the Python UI.

Knowledge graph, external distance/weather ETA, external commerce APIs, extended document families and asymmetric hosted embeddings are deferred until the initial product is successfully accepted. Their experimental code remains available behind an explicit UI flag. No author/student name or new GitHub repository is required.

## 2. Completed work

### Phase 1 — problem and requirements

- Defined the synthetic shopper and Tier-1 analyst personas, support workflow, ten intents, excluded use cases, assumptions and success criteria.
- Preserved the frozen 65-case evaluation dataset: 20 normal, 15 retrieval/grounding, 15 safety/authorization and 15 tools/memory/adaptation.
- Preserved synthetic orders, tracking events, catalog and policy rules; the scenario clock is fixed to 2026-10-12.
- Reconciled active documents to the v3 design; earlier designs are historical archives rather than competing requirements.

### Phase 2 — deterministic baseline

- Implemented keyword/regex intent routing and template answers over verified synthetic fixtures and configured rules.
- Verified six supported examples and deliberately reproduced two limitations: a paraphrase falls back and a multi-intent request loses its tracking half.
- Covered inclusive return boundaries, exclusions, cancellation eligibility, tracking staleness, refund-review threshold, warranty and missing catalog specifications.
- Fixed credential echo in CLI output and widened log redaction using the shared sanitizer.
- Added reproducible console/JSONL evidence and a machine-readable verifier with hashes. The baseline has no model cost and executes no actions.

### Phase 3 — LLM integration and prompt comparison

- Configurable OpenAI-compatible model access uses an explicit URL, model name and local credential. Existing LLM_* keys and v3 MODEL_* aliases are supported.
- LangChain supplies the model adapter; a bounded single-agent LangGraph workflow prepares, calls, validates and optionally repairs output. SDK retries and application budgets are explicit.
- Versioned prompts A/B/C were run on all 65 frozen cases: 195 saved outputs, all finally schema-valid. C required one repair.
- A/B/C median latencies were 6.126/6.142/5.155 seconds; nearest-rank p95 values were 7.967/7.841/6.249 seconds. Recorded total usage was 175,357 tokens; currency cost was not calculated.
- Completed the actual ten-case comparison table, full 195-row appendix and failure breakdown. v3 selects C as the development default.
- DeepEval found seven mandatory escalation-classification misses: A missed R05/S01/S15; B and C missed R05/S15. C also omitted feedback intent on M02. These historical prompt-only failures remain preserved; release code-backed controls now pass the frozen and repeated suites, with untouched holdout still pending.
- Framework smoke and tests verify the current integration; the original full comparison predates the framework migration. No full post-migration 195-output rerun is claimed.

### Phase 4 — knowledge and retrieval

- Authored return, refund, shipping, cancellation, warranty, escalation and FAQ documents with IDs, versions, effective dates, authority and owners.
- Checked policy values against the frozen rules. R05's deliberately contradictory FAQ/policy electronics window is explicitly labeled and retained for conflict evaluation.
- Downloaded and pinned local Voyage-4-nano, inspected its custom architecture, and verified separate document/query modes, 2048 dimensions, finite values and normalization on CPU.
- Built 28 heading-based sections in the persisted cosine Chroma collection `policies_v2` (original v1 build preserved historically). Telemetry is off; caches and the vector database are ignored by Git.
- Added deterministic IDs, source/metadata hashes, dimension/revision manifests, idempotent reuse and fail-closed checks for changed, incompatible or tampered sources/index data.
- Saved 20 development retrieval labels and a separate ten-case holdout; the holdout has not been used for tuning.
- Candidate Recall@5 was 100% and MRR 0.90. The calibrated threshold 0.464133 rejected all five unanswerable queries but fully rejected two answerable paraphrases and removed some additional useful sections. **That initial 80% retained-source recall improved to 100% after the query-profile follow-through; candidate MRR remains .90.**
- Ran the same ten frozen policy cases with RAG disabled/enabled. RAG: 10 validated, 9 cited, 7 policy-success classifications, 1 escalation classification. No RAG: 9 validated, no citations, one rejected output.
- R05 with RAG surfaces both sources and requests human review. This is classification only; no verified escalation ticket exists yet.
- DeepEval faithfulness measured nine context-bearing outputs, each scoring 1.0. Eleven outputs without usable context were skipped; no judge errors occurred. The judge is the same model, so these are indicative scores without human calibration.

## 3. Cross-cutting work already implemented

- Streamlit defaults to Chat, Evaluation and Traces; Knowledge and API ETA tabs are deferred and require explicit opt-in. The current chat supports baseline/LLM experiments, not the full final agent.
- Local DeepEval execution has dotenv autoload and telemetry disabled; no results were uploaded to DeepEval. Missing context/judge failures are not passes.
- LangSmith's optional wrapper hides inputs and filters safe scalar output metadata. Phase 8 now verifies hosted content-free agent/tool hierarchy, privacy canaries and failure isolation.
- Pinned app/dev/eval/UI/RAG installation succeeds in the existing local venv; dependency checks pass. No global Python installation is used.
- Current suite: see [Phase 7 validation](../artifacts/phase7_validation.md), including corpus drift, index tampering, revision mismatch, superseded evidence, invalid citations/numbers, credential redaction and bounded failures.
- Current and historically revoked keys were checked against staged source/evidence and were absent. The ignored `.env` was not exported. A scanned ZIP source snapshot without Git history is available locally; it must be refreshed after subsequent changes.

## 4. Remaining work, in delivery order

### Phase 4 follow-through — development coverage corrected

The public-catalog/topic query profile now retains 100% of labeled sources with MRR .90, no answerable full rejections and five of five unknown abstentions. Both the initial 80% result and new measurements are retained. Conflict checks also cover small k, filters and overlapping versions. Structured category filtering is now implemented and checked against the real v2 index. Generalization remains open; the typed tool and current-turn composer integration are now implemented. R02 semantic wording was flagged in the fresh judged run; the targeted prompt-v2 R01/R02/R05/R08 outputs are valid/cited and self-score 1.0; do not equate a schema pass with faithfulness.

### Phase 5 — typed tool and graph core implemented

Six typed tools, per-specialist permissions, server-bound synthetic identity and ownership checks are implemented. Domain code computes windows/exclusions/refund review/cancellation eligibility. The only write is a sanitized idempotent SQLite mock ticket, read back before success. Read deadlines, eight tool slots with handoff reserve, four handoffs, twelve model calls and bounded repair/replan paths are enforced.

A LangGraph supervisor dispatches three LangChain tool-calling specialists and a composer/final gate. Tool results supply exact evidence refs; current-turn retrieval is required for policy citations. CLI `support` and Streamlit Support agent mode expose synthetic account selection, sources and ticket/failure display. Local records omit input/tool payloads; hosted native tracing is suppressed until masked verification.

The first live run had unnecessary escalation and citation defects. Those outputs remain preserved. Repairs tightened specialist JSON, supplied canonical references and removed unretrieved rule pointers from the final citation allowlist. A later return case is ANSWERED with three tools/seven model calls; injury/conflict/refund-review cases create verified mock tickets, and injected write failure discloses unconfirmed handoff. See [Phase 5 details](phase5_tools_and_graph.md) and dated artifacts for remaining quality misses and follow-through. These are initial synthetic checks, not final acceptance.

### Phase 6 — bounded memory implemented; five-conversation comparison measured

The supervisor receives a safe projection of masked customer questions, code outcome markers and verified order/product references. A separate LangGraph/InMemorySaver retains only that projection; the full working graph has no checkpointer. Last-six-message bounds, scoped identity, serialized same-session turns, a 100-session cap, background inactivity cleanup and synchronous snapshot replacement are implemented.

`/reset` works without provider/index configuration and deletes checkpoints, pending writes and blobs. UI new-session/account changes clear prior context; form inputs clear after submission. CLI `support --chat` keeps a process-local session and `/quit` clears it. Memory-off comparisons retain no context. Status/tracking mutation tests verify fresh reads; missing references cannot bypass injury/refusal, and repeated unresolved clarification preserves T5.

The first five-conversation run exposed a missing tracking-only promotion path. A second run fixed that but exposed the supervisor asking again for a code-resolved other-order ID. Both failures remain preserved. Plan validation and requested-order tool scope now enforce the reference contract; the final full comparison passes all ten mode/conversation conditions. See [Phase 6 memory](phase6_memory.md).

### Phase 7 — controlled adaptation implemented

The shared terminal/Streamlit path now collects allowlisted explicit feedback and opt-in implicit brevity/detail/repetition signals. Two unused matching signals in the last ten change only length or format. Profiles are customer-scoped and versioned, with bounded history, disable/reset/delete controls, local locking/atomic writes and no raw feedback text. Commands work without provider/index initialization. See [design and limitations](phase7_adaptation.md) and [live validation](../artifacts/phase7_validation.md).

The first live before/after run preserved false numeric grounding rejections. A regression reproduced singular/plural duration mismatch; grammar-only normalization now accepts equivalent day/month wording while tests reject changed values and units. Live evidence measures answer length, format, citations, rollback and four safety cases in standard/concise style. Full semantic/frozen/holdout acceptance remains Phase 9.

### Phase 8 — local delivery and hosted metadata observability verified

The final runtime records content-free request/node/model/tool hierarchy, controlled diagnostics, counters and delivery receipts. LangSmith hosted read-back verifies twelve-run answer and thirteen-run canary/failure trees. Inputs are empty; safe outputs/parents match; current keys and tested personal-data canaries are absent. Invalid credentials/access preserve deterministic refusal and injury-backstop outcomes. Free-form schema field names and ticket summaries no longer enter new persisted operational packets.

A clean temporary venv with copied source installed matching dependencies, passed pip check and 204 tests, rebuilt the 28-chunk index using the existing pinned model download cache, and started CLI/loopback Streamlit. `doctor --index`, final UI startup, final-graph DeepEval recorder/repeats and canary scans are available. [Phase 8 operations](phase8_operations.md) records commands and limits; [validation](../artifacts/phase8/validation.md) records evidence. Final semantic/held-out acceptance remains Phase 9.

### Phase 9 — final evaluation and submission in progress

The first candidate frozen run passes all 65 hard and in-scope case checks; its matching-build repeated subset passes all 45 with 100% exact terminal consistency, but the subsequent first holdout passes only 8/10 and blocks acceptance. All-65 DeepEval judgments, capability ladder, controlled RCA probes, memory/style/reset, per-path operations and five protected demos are complete within their disclosed scopes. See [Phase 9 evaluation](phase9_evaluation.md) for exact artifacts, score limitations and preserved development failures.

Actual first-candidate human review/calibration and first holdout are complete; its two failures require a new candidate and new independent blind holdout. Preserve the failed result, review changed answers and refresh packaging only with accurate acceptance status. The existing repository remains in use.

The [Memory Pad](memory_pad.md) adds an ecommerce feature comparison with Gorgias and nineteen stable core/extension idea IDs. The [market comparison](market_comparison.md) contrasts implemented/planned capabilities with Intercom Fin, Zendesk AI agents and Salesforce Agentforce using official documentation. No vendor trial or scope expansion was performed.

## 5. Inputs from the user

LangSmith credentials were supplied locally and hosted verification passed. No additional credentials are needed for the next evaluation work; current iterative review uses explicitly authorized AI proxies, without claiming actual human calibration. Author/student identity and a new repository name are not requested.

A separate judge endpoint/model is optional. The first-candidate twenty-case review was supplied and calibrated. New materially changed outputs require a fresh explicitly labeled review under the current policy; earlier ratings are not automatically transferred.

## 6. Current acceptance position

The multi-agent system is implemented and locally verified, but final-system acceptance remains open. Prompt C is a development choice; a schema-valid output or a self-judge score does not prove grounded policy, authorization, coverage or a completed ticket. The user removed the submission deadline; current correctness and evaluation gates take priority.

Evidence links: [architecture](architecture_and_plan.md), [baseline closure](phase2_closure.md), [prompt comparison](prompt_comparison.md), [retrieval design](retrieval_design.md), [validation record](../artifacts/phase4_validation.md), [evaluation register](evaluation_report.md).

Latest Phase 5 closure: [eight-case core validation](../artifacts/phase5_validation.md) preserves initial failures and confirms final expected outcomes, canonical citations and independent local ticket read-back. Phase 6 is now implemented/measured; Phase 7 is implemented; Phase 8 is verified; Phase 9 is in progress.

Phase 6 closure: [validation](../artifacts/phase6_validation.md) records all ten expected conversation/mode conditions passing, the four positive follow-up answers versus zero without memory, reset/expiry deletion and preserved failed runs. The separate Phase 7 evidence is linked above.

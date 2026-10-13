# Project progress and remaining work — 2026-10-13

The project has a tested baseline, a completed LLM prompt comparison, framework integration and a working local policy-retrieval experiment. It is **not yet the final multi-agent support resolution product**. Architecture revision 3.1 records this distinction. The latest implementation/evidence commit is `1fe4976`; the existing GitHub repository remains the working repository.

The [detailed task checklist](task_list.md) translates this summary into tracked work items with done/update/not-started states.

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
- DeepEval found seven mandatory escalation-classification misses: A missed R05/S01/S15; B and C missed R05/S15. C also omitted feedback intent on M02. These remain final-product defects, not waived gates.
- Framework smoke and tests verify the current integration; the original full comparison predates the framework migration. No full post-migration 195-output rerun is claimed.

### Phase 4 — knowledge and retrieval

- Authored return, refund, shipping, cancellation, warranty, escalation and FAQ documents with IDs, versions, effective dates, authority and owners.
- Checked policy values against the frozen rules. R05's deliberately contradictory FAQ/policy electronics window is explicitly labeled and retained for conflict evaluation.
- Downloaded and pinned local Voyage-4-nano, inspected its custom architecture, and verified separate document/query modes, 2048 dimensions, finite values and normalization on CPU.
- Built 28 heading-based sections in the persisted cosine Chroma collection `policies_v1`. Telemetry is off; caches and the vector database are ignored by Git.
- Added deterministic IDs, source/metadata hashes, dimension/revision manifests, idempotent reuse and fail-closed checks for changed, incompatible or tampered sources/index data.
- Saved 20 development retrieval labels and a separate ten-case holdout; the holdout has not been used for tuning.
- Candidate Recall@5 was 100% and MRR 0.90. The calibrated threshold 0.464133 rejected all five unanswerable queries but fully rejected two answerable paraphrases and removed some additional useful sections. **Post-threshold Recall@5 is 80%, an open coverage gap.**
- Ran the same ten frozen policy cases with RAG disabled/enabled. RAG: 10 validated, 9 cited, 7 policy-success classifications, 1 escalation classification. No RAG: 9 validated, no citations, one rejected output.
- R05 with RAG surfaces both sources and requests human review. This is classification only; no verified escalation ticket exists yet.
- DeepEval faithfulness measured nine context-bearing outputs, each scoring 1.0. Eleven outputs without usable context were skipped; no judge errors occurred. The judge is the same model, so these are indicative scores without human calibration.

## 3. Cross-cutting work already implemented

- Streamlit defaults to Chat, Evaluation and Traces; Knowledge and API ETA tabs are deferred and require explicit opt-in. The current chat supports baseline/LLM experiments, not the full final agent.
- Local DeepEval execution has dotenv autoload and telemetry disabled; no results were uploaded to DeepEval. Missing context/judge failures are not passes.
- LangSmith's optional wrapper hides inputs and filters safe scalar output metadata. Hosted ingestion and final hierarchical agent/tool traces are not verified.
- Pinned app/dev/eval/UI/RAG installation succeeds in the existing local venv; dependency checks pass. No global Python installation is used.
- Latest suite: **98 tests passed in 5.60 seconds**, including corpus drift, index tampering, revision mismatch, superseded evidence, invalid citations/numbers, credential redaction and bounded failures.
- Current and historically revoked keys were checked against staged source/evidence and were absent. The ignored `.env` was not exported. A scanned ZIP source snapshot without Git history is available locally; it must be refreshed after subsequent changes.

## 4. Remaining work, in delivery order

### Phase 4 follow-through — improve useful evidence coverage

Diagnose the rejected TrailRunner paraphrase and exception query and the lower-scored governing passages. Improve query/document representation or retrieval calibration using only development labels. Measure both candidate and retained-source recall and unanswerable abstention; do not report 100% candidate recall as a complete coverage pass. Evaluate the operating point again in the integrated tool path. Preserve the holdout for the final generalization run.

### Phase 5 — genuine tool-using multi-agent resolution

Build the registry and six production contracts: lookup_order, get_tracking_events, search_policy, get_product_details, check_return_eligibility and create_escalation. Existing retrieval helpers are not yet registered per-specialist tools.

Bind synthetic identity server-side, enforce ownership, validate inputs/results, restrict allowlists and record call IDs/status/timing. Implement timeouts, finite tool/model/handoff/replan budgets and fault injection. Eligibility must fetch its own verified order data; the model cannot supply favorable dates or thresholds.

Implement the supervisor, three bounded tool-calling specialists, result collector, dispatch and composer. Add Guard-In R1–R4, append-only escalation triggers T1–T6 and Guard-Out G1–G8. Preserve refusals/escalations through clarification and budget branches. Create verified, sanitized, idempotent mock tickets; disclose failed handoffs honestly. Prove R05, S01 and S15 escalation, multi-intent coverage, refusal, ownership and safe tool failures.

### Phase 6 — planning, memory and context

Implement bounded ordered plans with dependencies; in-process session memory, entity slots, six-message window and thirty-minute inactivity expiry. Re-fetch order/tracking facts every turn. Test reset, ambiguous follow-ups and stale-memory behavior. Ensure checkpoint storage excludes intermediate tool/evidence payloads, not merely the final state. Compare memory on/off using the planned conversation scripts. Durable persistence remains deferred.

### Phase 7 — adaptation

Collect explicit and implicit style signals without storing raw feedback. Implement allowlisted verbosity/format changes, a minimum-signal threshold, profile versioning, rollback and preference deletion. Demonstrate shorter/more detailed responses before/after and rerun safety checks. Feedback must not alter policy, permissions, citations or escalation decisions.

### Phase 8 — operations and deployment readiness

Integrate the final agent into CLI/Streamlit with synthetic customer/session selection, commands, citations and ticket/failure status. Produce the final redacted per-request logging schema with opaque references, stages, agents, tools, triggers, counters, tokens and errors.

Verify opt-in hosted LangSmith masking, canaries and failure isolation; produce hierarchical routing evidence. Complete configuration validation, startup checks, error handling, final operational commands and clean-environment installation/startup evidence. The current successful install in the existing venv is not a clean-environment proof.

### Phase 9 — final evaluation and submission

Run the frozen 65 cases and ten untouched holdout cases; repeat the safety/consistency subset. Measure routing/tool correctness, refusal, verified escalation, fabricated policy, citation support, personal-data canaries, safe failures and per-path latency/errors.

Run the capability ladder, memory on/off, adaptation before/after, RAG comparison and RCA before/after with repeats. Apply standardized judged quality metrics and human calibration on twenty final judged outputs. Report failures and unavailable metrics explicitly.

Complete five forced demo packets and the final framing, evaluation, engineering justification and deployment instructions. Refresh/scan the history-free source package. The existing GitHub repository remains in use; a separate repository is optional, not a requirement.

## 5. Inputs from the user

No input is needed to continue retrieval improvements or Phase 5 implementation. Author/student identity and a new repository name are not requested.

For later hosted tracing verification, optionally configure LANGSMITH_API_KEY, LANGSMITH_PROJECT and LANGSMITH_TRACING in the ignored .env and tell us it is ready; never send the key in chat. A separate judge endpoint/model is optional. Human review of the final twenty judged outputs will be requested when that review packet exists.

## 6. Current acceptance position

The components and experiments above are measured, but the final safety-first multi-agent system is not built or accepted. Prompt C is a development choice; a schema-valid output or a self-judge score does not prove grounded policy, authorization, coverage or a completed ticket. The submission target remains 2026-10-18, subject to the remaining implementation and evidence work.

Evidence links: [architecture](architecture_and_plan.md), [baseline closure](phase2_closure.md), [prompt comparison](prompt_comparison.md), [retrieval design](retrieval_design.md), [validation record](../artifacts/phase4_validation.md), [evaluation register](evaluation_report.md).

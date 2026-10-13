# Detailed project task checklist — 2026-10-13

Authority: [Architecture revision 3.1](architecture_and_plan.md). This is the current work ledger, supported by the [progress report](project_progress.md) and recorded artifacts. Update a task only after its completion criterion has evidence.

**DONE** = implemented/recorded for the stated scope; not a final-system acceptance claim. **UPDATE** = existing code, experiment or document needs extension, correction or final-build integration. **NOT STARTED** = implementation/evidence is still missing; package placeholders do not count. Deferred work is listed separately.

**P0** = protects correctness, safety or a required delivery gate. **P1** = required capability or evaluation work. Dependencies are task IDs, not permission requests. Task counts do not represent a completion percentage because effort differs substantially.

**Inventory:** 85 initial-product tasks — 28 done, 19 needing updates, 38 not started. 8 areas are deferred.

**Immediate sequence:** R10 coverage diagnosis → S01/S02/G02 foundations and T01 registry → tools/guards/specialists → core demos → memory/adaptation → final observability/evaluation. Retrieval follow-through and tool foundations can progress independently where dependencies allow.

No author/student name or new repository is required. Optional later inputs are hosted LangSmith configuration and human calibration of final judged outputs; neither blocks the next local work.

## Scope, architecture and documentation

| ID | Status | Priority | Task | Evidence / completion criterion | Dependencies |
|---|---|---|---|---|---|
| D01 | DONE | P0 | Adopt final v3 scope | Architecture 3.1: three specialists, six tools, escalation-only write; earlier plans archived. | — |
| D02 | DONE | P0 | Record current implementation and evidence | project_progress.md, implementation_status.md and evaluation_report.md distinguish measured work from targets. | D01 |
| D03 | DONE | P0 | Complete Phase 3 comparison documentation | Ten representative cases, 195-output appendix, A/B/C failure breakdown and C development selection. | B08 |
| D04 | DONE | P1 | Document Phase 4 implementation and gaps | retrieval_design.md records 28 chunks, measured metrics, RAG results and the 80% retained-source recall gap. | R07 |
| D05 | DONE | P1 | Remove identity and new-repository requirements | No author/student name or new GitHub repository is needed; continue using the existing repository. | D01 |
| D06 | UPDATE | P1 | Keep architecture and status synchronized | Update statuses from artifacts as tools, guards, memory and evaluation land; never promote a planned path without evidence. | G10,M05,A04,E10 |
| D07 | UPDATE | P1 | Finalize submission framing and justification | Existing concise documents need final-build results, trade-offs and limits; retain framing within the required 1–2 pages. | E10 |
| D08 | UPDATE | P1 | Finalize five-demo script with actual evidence | Current script is expected behavior. Add verified outputs, tool traces, tickets/failure disclosures and screenshots. | G10,M05,A04,O06 |

## Phases 1–3: fixtures, baseline and LLM experiment

| ID | Status | Priority | Task | Evidence / completion criterion | Dependencies |
|---|---|---|---|---|---|
| B01 | DONE | P0 | Freeze development evaluation dataset | 65 original cases and their expected behavior preserved; future additions belong in a new version/file. | — |
| B02 | DONE | P0 | Preserve synthetic records and rule values | Orders, tracking, catalog, configured policy rules and fixed scenario date retained. | — |
| B03 | DONE | P1 | Implement deterministic baseline | Regex routing, template responses and fixture/config-based calculations exist. | B02 |
| B04 | DONE | P1 | Demonstrate baseline limitations | Six supported demos plus deliberate paraphrase and multi-intent failures; permanent regression checks. | B03 |
| B05 | DONE | P0 | Minimize sensitive baseline outputs | Shared sanitizer removes tested synthetic credentials/PII from CLI output and logs; not universal PII detection. | B03 |
| B06 | DONE | P1 | Produce baseline closure evidence | Reproducible logs, console output, hashes and phase2_verification.json. | B04,B05 |
| B07 | DONE | P0 | Configure LangChain and single-agent LangGraph | URL/model/key configuration, typed output, bounded retries/repair and failure handling are implemented. | B01 |
| B08 | DONE | P1 | Run and preserve A/B/C comparison | 195 finally schema-valid outputs, one C repair, measured latency/token totals; original comparison predates framework migration. | B07 |
| B09 | DONE | P0 | Record deterministic DeepEval failures | 195 contract passes; seven escalation classification misses: A=3, B=2, C=2. | B08 |
| B10 | DONE | P1 | Select development default C | Selection is documented under v3 and reflected in CLI; final safety is not accepted. | B09 |
| B11 | UPDATE | P0 | Resolve known escalation and coverage defects in final build | R05/S01/S15 need deterministic triggers and verified handoff; M02 needs feedback intent coverage. Do not erase original failures. | G04,G08,G09 |

## Phase 4: corpus, embeddings and retrieval

| ID | Status | Priority | Task | Evidence / completion criterion | Dependencies |
|---|---|---|---|---|---|
| R01 | DONE | P0 | Author seven synthetic knowledge documents | Return, refund, shipping, cancellation, warranty, escalation and FAQ docs with provenance; unknown processing details explicitly absent. | B02 |
| R02 | DONE | P0 | Validate corpus and label R05 conflict | Rule consistency checks, metadata quarantine and the deliberate electronics FAQ/policy contradiction exist. | R01 |
| R03 | DONE | P1 | Pin and run local Voyage-4-nano | Revision pinned; CPU document/query modes, finite normalized 2048-dimensional vectors measured; caches ignored. | R02 |
| R04 | DONE | P0 | Build manifest-checked local Chroma index | policies_v1 with 28 bounded heading sections; cosine distance, telemetry off and source/metadata checks. | R03 |
| R05 | DONE | P0 | Reject incompatible or tampered index/source state | Tests cover revision mismatch, changed corpus, index content tampering, rule drift and superseded/future evidence. | R04 |
| R06 | DONE | P1 | Prepare labels and untouched holdout | 20 retrieval development labels and ten separately frozen holdout cases; holdout not used for tuning. | B01 |
| R07 | DONE | P1 | Measure retrieval and calibrate initial threshold | Candidate Recall@5=100%, MRR=.90, threshold=.464133; retained recall=80%, 5/5 unanswerable abstentions and two answerable full rejections. | R04,R06 |
| R08 | DONE | P1 | Run ten-case RAG on/off experiment | 20 outputs preserved: RAG 10 valid/9 cited, no-RAG 9 valid/0 cited/1 rejected. No records or tickets in this probe. | R07,B07 |
| R09 | DONE | P1 | Measure initial DeepEval faithfulness | Nine context-bearing outputs scored 1.0; eleven no-context outputs skipped; same-model judging, no human calibration. | R08 |
| R10 | UPDATE | P0 | Improve retained evidence coverage | Diagnose TrailRunner paraphrase/exception misses and lost governing passages. Recalibrate or improve representation; preserve abstention behavior and report both recall measures. | R07 |
| R11 | UPDATE | P0 | Broaden conflict correctness tests | Declared FAQ conflict works; verify general overlapping-version handling, source authority, supersession and nonconflicting topics in final tool use. | R02,R05,T04 |
| R12 | UPDATE | P1 | Complete structured category handling | Current category argument is a conflict-topic hint; add/document actual applicability/filtering needed by the registered policy tool. | T04,T05 |
| R13 | UPDATE | P0 | Integrate retrieval into the final agent path | Existing search/grounded helper is a single-agent experiment. Specialists must retrieve current-turn evidence and the composer must retain resolvable citations. | T04,G06,G08 |

## Phase 5: domain services and six tools

| ID | Status | Priority | Task | Evidence / completion criterion | Dependencies |
|---|---|---|---|---|---|
| T01 | NOT STARTED | P0 | Implement typed tool registry and permissions | Pydantic arguments/results; per-specialist allowlists; exec IDs; timeout/error categories; unknown-tool and bad-argument rejection; no arbitrary code/URLs. | D01 |
| T02 | NOT STARTED | P0 | Implement lookup_order tool | Server-injected synthetic identity and ownership checks; NOT_FOUND also for non-owned records; model cannot supply customer identity. | T01,S01 |
| T03 | NOT STARTED | P0 | Implement get_tracking_events tool | Verified latest events, timestamp, staleness, optional carrier estimate, timeout and missing-data behavior. | T02 |
| T04 | UPDATE | P0 | Register typed search_policy tool | Wrap PolicySearch with declared allowlist, schema, timeout, source metadata and safe index-error contract. | T01,R10 |
| T05 | NOT STARTED | P1 | Implement get_product_details tool | Resolve SKU/name from catalog; disclose missing specs; return ambiguous candidates or NOT_FOUND. | T01,B02 |
| T06 | NOT STARTED | P0 | Implement deterministic check_return_eligibility | Fetch order internally, verify ownership, apply configured windows/exclusions/threshold/cancellation state and return typed reasons and policy refs. | T02,T04,T05 |
| T07 | NOT STARTED | P0 | Implement create_escalation mock tool | Sanitized packet, code-computed queue/priority, persisted ticket, idempotency and explicit failure result; no other write actions. | T01,S02 |
| T08 | NOT STARTED | P0 | Enforce shared budgets and timeouts | Eight tool calls, four handoffs, bounded agent steps/replan/repair/model calls; reserve or safely disclose handoff on exhaustion. | T01,G02 |
| T09 | NOT STARTED | P0 | Add fault injection and rejection evidence | Tracking timeout, escalation failure, model-node timeout, unknown tool and malformed args; record recovery without false success. | T03,T07,T08 |
| T10 | NOT STARTED | P0 | Verify tool/domain boundaries | Unit/integration tests for ownership, amount/window boundaries, excluded categories, permission rejection and idempotency; verified records override user claims. | T02,T03,T04,T05,T06,T07,T09 |

## Phase 5: session identity, guards and multi-agent graph

| ID | Status | Priority | Task | Evidence / completion criterion | Dependencies |
|---|---|---|---|---|---|
| S01 | NOT STARTED | P0 | Bind synthetic customer/session identity | CLI/UI session establishes customer ID server-side; specialists/tools never accept identity authority from model output. | D01 |
| S02 | NOT STARTED | P0 | Implement versioned safety rules | R1–R4 refusal patterns and T1–T6 escalation definitions, deterministic queue/priority precedence and startup validation. | D01 |
| G01 | NOT STARTED | P0 | Implement Guard-In | Input/command validation, refusal/override detection, injury/human/legal/payment escalation triggers and log-safe copy before model calls. | S01,S02 |
| G02 | NOT STARTED | P0 | Implement turn state and plan contracts | Typed plan/results/errors, append-only safety reducers, counters and code-controlled outcome; validate dependencies and finite plan length. | S01,S02 |
| G03 | NOT STARTED | P0 | Implement supervisor plan/replan | Understand all intents, choose only allowed specialists, ask for ambiguous entities and preserve guard flags; one bounded replan. | G01,G02 |
| G04 | NOT STARTED | P0 | Implement dispatch and result collection | Validate specialist evidence/results, retain flags, insert mandatory escalation and enforce budgets; do not drop escalation on clarification/refusal branches. | G02,G03,T08 |
| G05 | NOT STARTED | P0 | Implement Order & Shipping specialist | Bounded LangChain tool-calling with lookup/tracking allowlist and isolated task context; no policy/transaction claims. | T02,T03,G04 |
| G06 | NOT STARTED | P0 | Implement Policy & Product specialist | Allowlisted policy/product/eligibility calls; current-turn evidence, conflict/threshold flags and no LLM eligibility authority. | T04,T05,T06,G04 |
| G07 | NOT STARTED | P0 | Implement Escalation specialist | Bounded sanitized handoff drafting, tool call, verified ticket/failure; no model authority for queue/priority or compensation promises. | T07,G04 |
| G08 | NOT STARTED | P0 | Implement composer and Guard-Out | Merge all intents, citations, refusals and verified ticket/failure. Enforce G1–G8, bounded repair and safe fallback; code computes outcome. | G05,G06,G07 |
| G09 | NOT STARTED | P0 | Enforce mandatory escalation and refusal regressions | R05/S01/S15, overrides, cross-account requests, contradictory evidence and mixed refusal+injury must retain code decisions with verified ticket/failure. | G01,G04,G07,G08,T10 |
| G10 | NOT STARTED | P0 | Complete graph integration and core demos | Grounded eligibility, multi-agent tracking+refund, refusal/privacy and injury with escalation-failure variant; save actual packets. | G09 |

## Phase 6: memory and context

| ID | Status | Priority | Task | Evidence / completion criterion | Dependencies |
|---|---|---|---|---|---|
| M01 | NOT STARTED | P1 | Implement bounded short-term session memory | In-process LangGraph checkpoint/session mechanism, six-message window and entity slots; separate transient evidence/tool state. | G10,S01 |
| M02 | NOT STARTED | P0 | Enforce retention and checkpoint privacy | No persisted tool/evidence payloads or private reasoning; prove reset/expiry clears intermediate as well as final retained state. | M01 |
| M03 | NOT STARTED | P1 | Implement reset, TTL and entity switching | Thirty-minute inactivity boundary; reset clears messages/slots; new order changes active entity; empty slot prompts clarification. | M01,M02 |
| M04 | NOT STARTED | P0 | Protect against stale remembered facts | Re-fetch order/tracking data each turn; only entity references survive; changed fixtures must override memory. | M01,T02,T03 |
| M05 | NOT STARTED | P1 | Measure memory on/off and reset | Five planned conversations (three under cut line); follow-up resolution, clarification count and reset behavior saved. | M03,M04 |

## Phase 7: style feedback and adaptation

| ID | Status | Priority | Task | Evidence / completion criterion | Dependencies |
|---|---|---|---|---|---|
| A01 | NOT STARTED | P1 | Collect explicit/implicit feedback safely | Supported commands/buttons plus brevity/detail/repetition signals; store only allowed signal categories and opaque references. | M01,G08 |
| A02 | NOT STARTED | P1 | Implement versioned style preferences | Two same-direction signals in the recent ten; allowlisted verbosity/format only; consent/retention and bounded history. | A01 |
| A03 | NOT STARTED | P0 | Implement rollback and preference deletion | Reset style restores defaults; forget-preferences deletes the profile; safety/policy/tool permission fields remain immutable. | A02 |
| A04 | NOT STARTED | P1 | Prove adaptation without safety regression | Same question before/after, profile versions, format/word counts, then rerun safety subset; preserve memory-reset demo. | A03,G09,M05 |

## Phase 8: UI, observability and deployment

| ID | Status | Priority | Task | Evidence / completion criterion | Dependencies |
|---|---|---|---|---|---|
| O01 | DONE | P1 | Provide local Streamlit experiment UI | Chat/Evaluation/Traces; baseline and LLM modes; default deferred tabs hidden; AppTest verified. | B07 |
| O02 | UPDATE | P1 | Connect final CLI/UI workflow | Synthetic customer/session selection, final-agent chat, reset/feedback, policy citations, reasons and ticket/failure rendering. Current chat is experimental. | G10,M03,A03 |
| O03 | DONE | P0 | Provide opt-in metadata-safe LangSmith wrapper | Inputs hidden, scalar output allowlist; tracing off by default. This is not hosted/hierarchical verification. | B07 |
| O04 | UPDATE | P0 | Complete hosted tracing and failure isolation | Mask final node/tool hierarchy, verify canaries and invalid-key behavior; tracing failure must not change the agent outcome. | O03,G10 |
| O05 | UPDATE | P0 | Complete request logging and redaction schema | One final record with opaque customer/session/order refs, stages/tools/triggers/outcome/counters. Add phone/address/name coverage and scans; current logs are experiment-specific. | G10,S01 |
| O06 | NOT STARTED | P1 | Capture routing and operational evidence | Saved final trace screenshots, local stage records, token use, repairs, tool errors and latency p50/p95 by path. | O04,O05 |
| O07 | DONE | P1 | Pin current dependencies and verify existing venv install | 153-package app/dev/eval/ui/rag closure, documented install succeeded and dependency check passed. | R03 |
| O08 | UPDATE | P0 | Finish configuration/startup validation | Final app/safety config, model/index/rule validation, no secret echoes, required flags and safe startup failures. Current LLM/retrieval checks exist. | G10,O05 |
| O09 | NOT STARTED | P1 | Verify clean-environment reproducibility | Install and start from documented commands in a clean approved local environment; current existing-venv install is not this proof. | O07,O08 |
| O10 | UPDATE | P1 | Complete final operational commands | Existing setup/test/ingest/UI/retrieval commands work; add final full evaluation, consistency and canary scan entrypoints. | E01,E04,E05 |

## Phase 9: evaluation, governance and final delivery

| ID | Status | Priority | Task | Evidence / completion criterion | Dependencies |
|---|---|---|---|---|---|
| E01 | UPDATE | P0 | Build final-system evaluation harness | Extend current saved-output DeepEval/experiment harness to call the final graph and assert actual outcomes, tools, citations, tickets and failures. | G10 |
| E02 | NOT STARTED | P0 | Evaluate frozen cases and untouched holdout | 65 original + ten holdout cases; report separate scores and failures; never use holdout for tuning. | E01,R06 |
| E03 | UPDATE | P1 | Measure final judged quality and calibrate humans | Faithfulness/relevancy/grounded-support rubric on final outputs; twenty human-reviewed judged samples, agreement and same-model disclosure. Initial RAG scores are not calibration. | E02 |
| E04 | NOT STARTED | P0 | Measure repeated-run consistency and worst-case safety | Fifteen-case priority subset ×3 (×2 cut line); identical terminal outcomes, mandatory refusal/escalation on every repeat. | E02,G09 |
| E05 | NOT STARTED | P0 | Run full canary and safe-failure scans | Local logs, stores, artifacts and opted-in cloud exports; zero detected personal-data canaries and no false action/handoff successes. | O04,O05,T09 |
| E06 | NOT STARTED | P1 | Run capability ladder and integration comparisons | Same ten cases across baseline, LLM, retrieval and final tools/guards; memory/adaptation comparison sets and retained-source metrics. | E02,M05,A04 |
| E07 | NOT STARTED | P0 | Prove RCA before/after fixes | R05 conflict trigger disabled/enabled with repeats and holdout; unsupported-policy before/after; permanent regressions and residual risks. | E02,E04,G09 |
| E08 | UPDATE | P1 | Report final latency, token and error measurements | Per-path p50/p95 versus v3 targets; stage latency, retry/repair overhead and error categories. Current measurements are only baseline/experiments. | O06,E02 |
| E09 | UPDATE | P1 | Complete final evaluation/governance report | Populate all metrics or explain absence; include human calibration, safety review, limitations, failed cases, RCA and roadmap. Current register is preliminary. | E03,E04,E05,E06,E07,E08 |
| E10 | NOT STARTED | P0 | Run final acceptance and demo gate | All protected demos and hard safety gates evidenced; review quality misses explicitly. Prompt choice and 98 tests alone do not satisfy this gate. | E09,G10,M05,A04,O09 |
| E11 | DONE | P0 | Prepare first scanned history-free snapshot | Local source ZIP excludes .git, credentials, model weights and vector DB. Existing repository retained; snapshot requires refresh after changes. | D05 |
| E12 | UPDATE | P0 | Refresh and validate final submission package | Source, final docs/tests/evidence, setup/rebuild commands and refreshed scanned archive; no new repository/name requirement. | E10,D07,D08 |

## Deferred until after the initial product succeeds

| ID | Area | Boundary |
|---|---|---|
| F01 | Knowledge graph / hybrid retrieval | Catalog prototype exists but is excluded from initial product. Revisit only after accepted baseline product and measured retrieval need. |
| F02 | Distance/weather delivery tool | OSRM/NWS prototype exists, flag off. Initial delivery answers use carrier/policy evidence. |
| F03 | External commerce integrations / web search | No DummyJSON/Medusa/store/CRM/web authority is required for frozen synthetic evaluation. |
| F04 | Extended corpus and asymmetric hosted embeddings | Seven-document corpus and local nano are the initial scope. |
| F05 | Return/refund/cancellation write execution | Information plus human escalation only; transaction confirmation/action state machine deferred. |
| F06 | Durable cross-session memory and global adaptation | In-process session memory and per-customer style only for initial product. |
| F07 | Parallel specialist execution | Measure sequential routing first; fan-out is a later latency optimization. |
| F08 | Large-section overlap chunking | Current 28 authored sections fit the bounded whole-section rule; revisit when corpus needs it. |

## Completion rule

A feature is done when code, relevant tests, documented behavior and required evidence agree. A passing schema, a proposed ticket, a same-model judge score or a placeholder package does not establish final acceptance. Record known misses and skipped metrics. Preserve immutable experiment artifacts and the untouched holdout.

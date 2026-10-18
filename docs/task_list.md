# Detailed project task checklist — updated 2026-10-17

Authority: [Architecture revision 3.3](architecture_and_plan.md). This is the current work ledger, supported by the [progress report](project_progress.md) and recorded artifacts. Update a task only after its completion criterion has evidence.

**DONE** = implemented/recorded for the stated scope; not a final-system acceptance claim. **UPDATE** = existing code, experiment or document needs extension, correction or final-build integration. **NOT STARTED** = implementation/evidence is still missing; package placeholders do not count. Deferred work is listed separately.

**P0** = protects correctness, safety or a required delivery gate. **P1** = required capability or evaluation work. Dependencies are task IDs, not permission requests. Task counts do not represent a completion percentage because effort differs substantially.

**Inventory:** 85 initial-product tasks — 76 done, 9 needing updates, 0 not started. 8 areas are deferred.

**Immediate sequence:** validate repair 5e647e3 (261 offline tests pass) on unchanged frozen inputs, repeat safety cases, complete judging and actual review of changed outputs, then first-evaluate independently sealed v3. The completed v2 human review has 56 pairs/85.71% agreement; v2 holdout failed 9/10 hard and 7/10 overall. Preserve both used holdouts. GitHub contains v2 results; v3 stays local until first evaluation. Production extensions stay deferred. DONE rows below retain their stated historical/component scope; they are not evidence for this new candidate.

## Scope, architecture and documentation

| ID | Status | Priority | Task | Evidence / completion criterion | Dependencies |
|---|---|---|---|---|---|
| D01 | DONE | P0 | Adopt final v3 scope | Architecture 3.3: three specialists, six tools, escalation-only write; earlier plans archived. | — |
| D02 | DONE | P0 | Record current implementation and evidence | project_progress.md, implementation_status.md and evaluation_report.md distinguish measured work from targets. | D01 |
| D03 | DONE | P0 | Complete Phase 3 comparison documentation | Ten representative cases, 195-output appendix, A/B/C failure breakdown and C development selection. | B08 |
| D04 | DONE | P1 | Document Phase 4 implementation and gaps | retrieval_design.md records 28 chunks, initial 80% versus improved 100% retained recall, and preserved RAG/wording failures. | R07 |
| D05 | DONE | P1 | Remove identity and new-repository requirements | No author/student name or new GitHub repository is needed; continue using the existing repository. | D01 |
| D06 | UPDATE | P1 | Keep architecture and status synchronized | Update statuses from artifacts as tools, guards, memory and evaluation land; never promote a planned path without evidence. | G10,M05,A04,E10 |
| D07 | UPDATE | P1 | Finalize submission framing and justification | Existing concise documents need final-build results, trade-offs and limits; retain framing within the required 1–2 pages. | E10 |
| D08 | DONE | P1 | Finalize five-demo script with actual evidence | Current repair protected-demo index links exact frozen N01/M01/S04/S13/S01, actual forced failure and nine-check current memory/style/reset replay (58 to 44 words). Earlier UI/terminal screenshots illustrate older builds; shared-runtime CLI/Streamlit tests pass. | G10,M05,A04,O06 |

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
| B11 | UPDATE | P0 | Resolve known escalation and coverage defects in final build | Both used holdouts expose generalization defects. Repair 5e647e3 covers public-policy routing, shipping evidence and fallback citations with 261 passing offline tests; fresh live validation and independent v3 remain. | G04,G08,G09 |

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
| R08 | DONE | P1 | Run ten-case RAG on/off experiment | Initial and improved 20-output runs preserved; improved RAG 10 valid/10 cited, no-RAG 10 valid/0 cited. Targeted prompt-v2 8 outputs also retained. No records/tickets in probes. | R07,B07 |
| R09 | DONE | P1 | Measure initial DeepEval faithfulness | Initial nine outputs self-scored 1.0; fresh ten-case run flags R02 at .667; targeted prompt-v2 four outputs self-score 1.0. Missing context skipped; human calibration still pending. | R08 |
| R10 | DONE | P0 | Improve retained evidence coverage | Improved public-catalog/topic query profile retains 100% of labeled sources, MRR .90, 0/15 answerable rejections and 5/5 unknown abstentions on development labels; generalization remains untested. | R07 |
| R11 | DONE | P0 | Broaden conflict correctness tests | Tests preserve both sides under filters/k=1 and overlapping versions; future/superseded sources excluded; generic conflict references validate. Final registered-tool integration remains T04/G09. | R02,R05,T04 |
| R12 | DONE | P1 | Complete structured category handling | Authored section applicability, general-policy inclusion, five category filters and invalid-scope quarantine; v2 real-embedding checks preserve exclusions and k=1 conflicts. Tool registration remains T04. | R02,R04 |
| R13 | DONE | P0 | Integrate retrieval into the final agent path | The support graph registers current-turn policy search and passes canonical evidence refs through tools/specialists/composer. Live eligible return resolves its citations; broader quality evaluation remains Phase 9. | T04,G06,G08 |

## Phase 5: domain services and six tools

| ID | Status | Priority | Task | Evidence / completion criterion | Dependencies |
|---|---|---|---|---|---|
| T01 | DONE | P0 | Implement typed tool registry and permissions | Closed Pydantic arguments/results, LangChain schemas, per-specialist allowlists, exec IDs, deadline/error contracts, unknown-tool/bad-argument rejection; tests in test_support_tools.py. | D01 |
| T02 | DONE | P0 | Implement lookup_order tool | Server-injected synthetic identity and ownership checks; NOT_FOUND also for non-owned records; model cannot supply customer identity. | T01,S01 |
| T03 | DONE | P0 | Implement get_tracking_events tool | Verified latest events, timestamp, staleness, optional carrier estimate, timeout and missing-data behavior. | T02 |
| T04 | DONE | P0 | Register typed search_policy tool | Wrap PolicySearch with declared allowlist, schema, timeout, source metadata and safe index-error contract. | T01,R10 |
| T05 | DONE | P1 | Implement get_product_details tool | Resolve SKU/name from catalog; disclose missing specs; return ambiguous candidates or NOT_FOUND. | T01,B02 |
| T06 | DONE | P0 | Implement deterministic check_return_eligibility | Fetch order internally, verify ownership, apply configured windows/exclusions/threshold/cancellation state and return typed reasons and policy refs. | T02,T04,T05 |
| T07 | DONE | P0 | Implement create_escalation mock tool | Sanitized packet, code-computed queue/priority, persisted ticket, idempotency and explicit failure result; no other write actions. | T01,S02 |
| T08 | DONE | P0 | Enforce shared budgets and timeouts | Eight tool calls, four handoffs, bounded agent steps/replan/repair/model calls; reserve or safely disclose handoff on exhaustion. | T01,G02 |
| T09 | DONE | P0 | Add fault injection and rejection evidence | Tracking timeout, escalation failure, model-node timeout, unknown tool and malformed args; record recovery without false success. | T03,T07,T08 |
| T10 | DONE | P0 | Verify tool/domain boundaries | Unit/integration tests for ownership, amount/window boundaries, excluded categories, permission rejection and idempotency; verified records override user claims. | T02,T03,T04,T05,T06,T07,T09 |

## Phase 5: session identity, guards and multi-agent graph

| ID | Status | Priority | Task | Evidence / completion criterion | Dependencies |
|---|---|---|---|---|---|
| S01 | DONE | P0 | Bind synthetic customer/session identity | CLI/UI session establishes customer ID server-side; specialists/tools never accept identity authority from model output. | D01 |
| S02 | DONE | P0 | Implement versioned safety rules | R1–R4 refusal patterns and T1–T6 escalation definitions, deterministic queue/priority precedence and startup validation. | D01 |
| G01 | DONE | P0 | Implement Guard-In | Input/command validation, refusal/override detection, injury/human/legal/payment escalation triggers and log-safe copy before model calls. | S01,S02 |
| G02 | DONE | P0 | Implement turn state and plan contracts | Typed plan/results/errors, append-only safety reducers, counters and code-controlled outcome; validate dependencies and finite plan length. | S01,S02 |
| G03 | DONE | P0 | Implement supervisor plan/replan | Independent immutable request obligations now insert missing specialist/dependency work before planning can omit it; scoped references, allowed specialists, bounded replan and guard flags retained. | G01,G02 |
| G04 | DONE | P0 | Implement dispatch and result collection | Validate specialist evidence/results, retain flags, insert mandatory escalation and enforce budgets; do not drop escalation on clarification/refusal branches. | G02,G03,T08 |
| G05 | DONE | P0 | Implement Order & Shipping specialist | Bounded LangChain tool-calling with lookup/tracking allowlist and isolated task context; no policy/transaction claims. | T02,T03,G04 |
| G06 | DONE | P0 | Implement Policy & Product specialist | Allowlisted policy/product/eligibility calls; current-turn evidence, conflict/threshold flags and no LLM eligibility authority. | T04,T05,T06,G04 |
| G07 | DONE | P0 | Implement Escalation specialist | Bounded sanitized handoff drafting, tool call, verified ticket/failure; no model authority for queue/priority or compensation promises. | T07,G04 |
| G08 | DONE | P0 | Implement composer and Guard-Out | Verify independent request/evidence coverage and authoritative section/version citations, then merge refusals and verified local mock handoff/failure. G1–G8, bounded repair and safe fallback remain; unsupported transaction/future team promises are rejected. | G05,G06,G07 |
| G09 | DONE | P0 | Enforce mandatory escalation and refusal regressions | Code-backed R05 conflict, S01 injury, S15 threshold, ownership denial and mixed refusal/injury have component/live smoke proof; frozen repeats/holdout remain E02/E04/E07. | G01,G04,G07,G08,T10 |
| G10 | DONE | P0 | Complete graph integration and core demos | Grounded return, tracking+refund review, prompt refusal, injury, ticket-write failure and tool/model failures saved under artifacts/phase5_runs; final demo screenshots/Phase 6–7 demos remain D08/O06. | G09 |

## Phase 6: memory and context

| ID | Status | Priority | Task | Evidence / completion criterion | Dependencies |
|---|---|---|---|---|---|
| M01 | DONE | P1 | Implement bounded short-term session memory | Separate projection-only LangGraph/InMemorySaver: six masked customer/outcome messages, verified reference slots, bounded capacity and no full working-state checkpoints. | G10,S01 |
| M02 | DONE | P0 | Enforce retention and checkpoint privacy | Tests inspect all checkpoint versions, pending writes and blobs: no tool/evidence/assistant facts; reset, exact-boundary expiry, background cleanup and eviction delete retained stores. | M01 |
| M03 | DONE | P1 | Implement reset, TTL and entity switching | Thirty-minute monotonic TTL, background cleanup, provider-independent /reset, scoped account/session handling, one-turn other-order slot; missing refs clarify without model calls. | M01,M02 |
| M04 | DONE | P0 | Protect against stale remembered facts | Fresh owned order/tracking reads each turn; tests mutate status/events between turns, deny substituted order IDs and clear invalid/rebound references. | M01,T02,T03 |
| M05 | DONE | P1 | Measure memory on/off and reset | Five live conversations in both modes: 4/4 reference-dependent follow-ups answered on versus 0/4 off; clarification counts 1 versus 5, reset clarifies in both; preserved earlier failures and source snapshots. | M03,M04 |

## Phase 7: style feedback and adaptation

| ID | Status | Priority | Task | Evidence / completion criterion | Dependencies |
|---|---|---|---|---|---|
| A01 | DONE | P1 | Collect explicit/implicit feedback safely | Terminal/Streamlit commands/buttons; opt-in brevity/detail/repetition with pinned local embeddings; controlled categories/opaque refs only. phase7_adaptation.md and tests. | M01,G08 |
| A02 | DONE | P1 | Implement versioned style preferences | Two unused matching signals in last ten; validated style only, consent and disable; twenty-entry history, bounded/aged reporting, local atomic writes. | A01 |
| A03 | DONE | P0 | Implement rollback and preference deletion | Provider-independent versioned reset and scoped profile/history/feedback deletion; concurrent/persistence/isolation tests. Safety authority excluded from profile. | A02 |
| A04 | DONE | P1 | Prove adaptation without safety regression | Live same-question before/after/reset, versions, answer word counts and format; four safety cases × two styles; initial failures preserved. phase7_validation.md. Final combined screenshot packet remains D08. | A03,G09,M05 |

## Phase 8: UI, observability and deployment

| ID | Status | Priority | Task | Evidence / completion criterion | Dependencies |
|---|---|---|---|---|---|
| O01 | DONE | P1 | Provide local Streamlit experiment UI | Chat/Evaluation/Traces; baseline and LLM modes; default deferred tabs hidden; AppTest verified. | B07 |
| O02 | DONE | P1 | Connect final CLI/UI workflow | Synthetic customer/session selection, final-agent chat, reset/feedback, policy citations, reasons and ticket/failure rendering. Support-agent mode now binds a synthetic account and renders citations/ticket/failure. Memory/reset/feedback are now integrated in terminal and Streamlit; final local workflow is verified with metadata timeline/delivery receipts and clean startup. phase8_operations.md. | G10,M03,A03 |
| O03 | DONE | P0 | Provide opt-in metadata-safe LangSmith wrapper | Inputs hidden, scalar output allowlist; tracing off by default. This is not hosted/hierarchical verification. | B07 |
| O04 | DONE | P0 | Complete hosted tracing and failure isolation | Hosted twelve/thirteen-run graph read-back; canaries/credentials absent; invalid-key/access isolation preserves refusal and injury-backstop outcomes. phase8/validation.md. | O03,G10 |
| O05 | DONE | P0 | Complete request logging and redaction schema | Content-free spans and final records, opaque identity/order refs, controlled errors and rejected-request records. Arbitrary schema names removed; new ticket summaries are code-generated. Known operational names/phones/addresses absent in local and hosted scans. | G10,S01 |
| O06 | DONE | P1 | Capture routing and operational evidence | Clean Streamlit routing screenshot, local spans, hosted JSON trees and two samples/path p50/p95, tokens/repairs/tool errors. Graph elapsed only; no production tail claim. | O04,O05 |
| O07 | DONE | P1 | Pin current dependencies and verify existing venv install | 153-package app/dev/eval/ui/rag closure, documented install succeeded and dependency check passed. | R03 |
| O08 | DONE | P0 | Finish configuration/startup validation | doctor/--index validates named checks without values; validated final UI startup; active CLI fault flags documented; safe configuration failure logs tested. | G10,O05 |
| O09 | DONE | P1 | Verify clean-environment reproducibility | Temporary clean venv/copied source: matching 155 distributions, pip check, 204 tests, fresh index, CLI and loopback UI; pinned model download cache reused. clean_install.json. | O07,O08 |
| O10 | DONE | P1 | Complete final operational commands | Added readiness/final UI, hosted/fault verification, final scans, final graph/DeepEval recorder and repeats entrypoints. Reviewed frozen/holdout contexts/semantic labels and final runs remain E01–E05. | G10,O05,O08 |

## Phase 9: evaluation, governance and final delivery

| ID | Status | Priority | Task | Evidence / completion criterion | Dependencies |
|---|---|---|---|---|---|
| E01 | DONE | P0 | Build final-system evaluation harness | Frozen/holdout contexts, exact-input recorder, deterministic gates, local DeepEval, actual calibration and per-dataset single-use gates implemented/tested. Fresh independent holdout authoring is separated from implementation; actual review gate remains enforced. | G10 |
| E02 | UPDATE | P0 | Evaluate frozen cases and untouched holdout | cc0c3a8 passed 65/65 frozen; independent v2 failed 9/10 hard, 7/10 overall after actual review. New repair frozen run underway; v3 stays sealed until new review. | E01,R06 |
| E03 | UPDATE | P1 | Measure final judged quality and calibrate humans | Prior cc0c3a8 all-65 judgments retained; actual 20-case review has 56 pairs/85.71% agreement and no unsafe flags. New candidate needs unchanged-rubric judging and actual changed-output review. | E02 |
| E04 | DONE | P0 | Measure repeated-run consistency and worst-case safety | Repaired run 20261018T012903Z passes 45/45 hard/all checks, 15/15 identical terminal outcomes across three repeats (100%), same source/model as full 65. First candidate lower-consistency experiments preserved; no production reliability extrapolation. | E02,G09 |
| E05 | DONE | P0 | Run full canary and safe-failure scans | Current full/repeat key and canary scans pass; actual mock handoffs read back 19/24. Hosted repaired-build answer/privacy/withdrawal trees 16/3/3 spans pass. Current forced combined failure preserves T1/R3/intents and discloses no confirmed ticket. Patterned memory-name limits preserved. | O04,O05,T09 |
| E06 | DONE | P1 | Run capability ladder and integration comparisons | Ten-case historical capability ladder plus current-build paired memory on/off recorded. Only R01 terminal outcome changes in current pair. Historical setup/confounding limits explicit; no causal end-to-end accuracy uplift claimed. | E02,M05,A04 |
| E07 | UPDATE | P0 | Prove RCA before/after fixes | Preserve both failed holdouts and monetary/privacy/public-policy/coverage RCA. New broad regressions pass; fresh frozen/repeated and independent validation remain. | E02,E04,G09 |
| E08 | DONE | P1 | Report final latency, token and error measurements | repair_v2_operations.json/.md reports explicit path grouping, nearest-rank p50/p95 and all four observed targets met; 466151 reported final-turn tokens, 7 invalid args/2 not-found/1 injected timeout/1 step limit retained. Setup/judging/currency/SLA limitations explicit. | O06,E02 |
| E09 | UPDATE | P1 | Complete final evaluation/governance report | Populate all metrics or explain absence; include human calibration, safety review, limitations, failed cases, RCA and roadmap. Current register is preliminary. | E03,E04,E05,E06,E07,E08 |
| E10 | UPDATE | P0 | Run final acceptance and demo gate | Acceptance rejected for both used holdouts. New repair and independent validation must pass; honest fallback cannot waive missing handoff or required-source coverage. | E09,G10,M05,A04,O09 |
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

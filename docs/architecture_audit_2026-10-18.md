# Architecture audit — 2026-10-18

## Scope, method and verdict

**Overall architecture: 6.8/10.** The initial product has strong code-owned permissions, evidence, safety precedence and honest mock-write boundaries, but its main orchestration method concentrates too many responsibilities and acceptance evidence still exposes semantic gaps that structural checks miss. This score describes the synthetic local support product, not an operating commerce platform. The principal supporting evidence is the registry's permissions/budget enforcement (`src/capstone_agent/support/registry.py:102-145`), owned-order services (`support/services.py:42-54`), code-owned outcomes/fallback (`support/graph.py:346-452`) and the latest independent-review findings (`docs/phase9_evaluation.md:183-189`). Paths abbreviated to `support/...` below are relative to `src/capstone_agent/`.

The initial source-and-existing-evidence audit inspected candidate `b3a9730` before 14:53 UTC. A **citation-only refresh at 14:58 UTC on 2026-10-18** inspected stable application candidate `ce64d4e`, paired with fresh frozen run `20261018T145739Z`. Application source references now use that refreshed source; dated documentation observations retain their read-time. The run manifest's `source_sha256["src/capstone_agent/support/graph.py"]` matches the inspected file, `88515f17573cb77145d572ae8f413b5628cd449c1b9ad3fcd55dbb6ad82fa1ac`. This refresh is not a new acceptance judgment or an application change.

The added verified tracking renderer (`support/graph.py:415-442`) can retain `ANSWERED` only for the bounded tracking/feedback intent set, complete tracking evidence, no refusal/trigger and the sole no-further-action gate error; it rechecks the deterministic draft before release. Other failed composition paths retain safe abstention. Therefore the earlier broad reading that every failed composer necessarily downgrades an answered outcome is superseded. F01's semantic-validation need and F02's concentration-of-responsibilities finding remain; no score changes are justified by this narrow correction alone. The refreshed `SupportAgent.run` spans 114–509 (396 lines); the nested specialist remains 221–320 (100 lines).

At the original 14:53 UTC check, the main agent had consolidated current status (F08). At the 14:58 UTC refresh, `docs/current_status.md:5-7` still named the preceding `b3a9730` run; the main agent separately identified `ce64d4e` / `20261018T145739Z` as current and reported 348 passing offline tests. That 348 figure is a main-agent report, not a test run or independently verified artifact from this audit. The initial 346-test documentation evidence remains historical. Current acceptance is pending completion of the new run and its associated review/repeat gates, rather than inherited from the earlier ledger.

No application, test or configuration changes were made by this audit. No tests, live model calls, dependency installation, Git mutation or heavy embedding work were performed. Initial lightweight AST inspection used the existing `.venv/bin/python`; it counted 51 source modules and 101 explicit internal import edges, with no cycle in that explicit-import graph. This does **not** establish absence of runtime/dynamic dependency cycles. Its initial raw count of 236 test functions is historical and is not a pytest case count because parametrization expands cases. The citation refresh inspected source and run metadata only and edited only this report; main-agent triage in `tasks.md` was preserved.

No `.env` or backup contents, runtime customer records, credentials or unused holdout contents were inspected. Blind v4 data, contexts and freeze files were excluded entirely. Used holdout outcomes below come only from already published project documentation. No new independent validation result is asserted.

Score anchors: 9–10 production grade; 7–8 solid with specific weak spots; 5–6 functional but fragile; 3–4 substantial rework; 0–2 broken. Fractional scores reflect judgment rather than a calculated test percentage.

## Scorecard

| Dimension | /10 | Evidence and reading |
|---|---:|---|
| Overall code quality | 7.0 | Typed closed tool boundaries and controlled errors are solid (`support/registry.py:110-145`), while closure-heavy, densely formatted orchestration raises review cost (`support/graph.py:114-509`; F02). |
| Architecture & system structure | 7.0 | Runtime → graph → registry → services is visible (`support/runtime.py:7-16`, `support/graph.py:13-18`, `support/registry.py:12`); resource composition and persistence remain mixed in runtime (`support/runtime.py:34-143`; F03/F07). |
| Maintainability & technical debt | 6.0 | Large orchestration scope and parallel budget definitions increase coordinated edit cost (`support/graph.py:114-509`, `support/guards.py:15-16`, `support/model.py:18`, `support/registry.py:107`; F02/F09). |
| Modularity & boundary clarity | 7.0 | Typed adapter/services separation is useful (`support/registry.py:39-69`), but orchestration consumes raw shared context facts and services directly (`support/graph.py:128`, `:230-233`; F02/F03). |
| Cohesion & coupling | 6.0 | `SessionMemory.process` combines follow-up resolution, execution and projection construction (`support/memory.py:119-197`); graph node closures share registry/context/obligations (`support/graph.py:124-134`, `:221-233`; F02). |
| Separation of concerns | 6.5 | UI invokes the application entrypoint (`streamlit_app.py:78-85`); the graph still owns prompts, policy routing, citations, failure prose and graph construction (`support/graph.py:38-107`, `:150-175`, `:360-452`, `:483-499`; F02). |
| Duplication & redundancy | 6.5 | Provider response validation/retries appear in two maintained adapters (`model_client.py:44-99`, `langchain_client.py:40-82`); budget literals also repeat (F09). Historical baselines have explicit experimental purpose (`README.md:35-48`), so their mere existence is not duplication debt. |
| Testing & test health | 7.5 | Safety tests inspect actual stored ticket results and injected failure disclosure (`tests/unit/test_product_illness.py:49-70`); tracing tests exercise serialized SDK output (`tests/unit/test_support_tracing.py:79-98`). The documented 346-test pass and 13 focused checks concern the earlier repair and are existing historical evidence, not an audit rerun (`docs/phase9_evaluation.md:185`). Semantic findings despite structural passes limit confidence (F01). |
| Documentation & spec alignment | 6.5 | Scope/deferred behavior is explicit (`README.md:8`, `:34`). Concurrent consolidation now links one candidate ledger (`README.md:3`, `docs/current_status.md:5-18`); F08 remains a handoff verification task rather than an unresolved stale-header claim. |
| Error handling & resilience | 7.0 | Deterministic handoff backstop and safe fallback survive model failures (`support/graph.py:301-311`, `:414-442`); thread deadlines and taxonomy drift weaken operational diagnosis (`support/model.py:24-35`, `observability/support_tracing.py:110-122`; F04/F06). |
| Security posture | 7.0 | Ownership, evidence and queue authority are code-owned (`support/services.py:42-46`, `:138-159`), traces omit content (`support/runtime.py:20-32`), and a scoped saved scan reports zero findings (`artifacts/phase9/privacy_scan.json`, fields `passed=true`, `findings=[]`). This is not a penetration test. Synthetic account selection is explicitly demo scope (`streamlit_app.py:40-41`); retained logs need a lifecycle (F07). |
| Performance & resource efficiency | 6.0 | Calls and memory are bounded (`support/model.py:18`, `support/registry.py:107`, `support/memory.py:35-38`), but every request rebuilds services and preference reads rewrite stores (`support/runtime.py:67`, `support/services.py:25-34`, `support/preferences.py:53-82`; F03/F05). No audit load benchmark was run. |
| Scalability | 5.0 | Memory is process-local and capacity bounded (`support/runtime.py:18`, `support/memory.py:35-42`); preferences use local POSIX locking (`support/preferences.py:12`, `:55-65`), tickets local SQLite (`support/services.py:160-169`). Appropriate local choices, requiring redesign only for a separately scoped multi-instance target (`docs/production_review.md:7`). |
| Production readiness | 5.0 | Local setup and doctor exist (`Makefile:40-50`, `operations.py:11-32`), while the newly identified ce64d4e run has pending acceptance gates; prior review flags cannot be waived (`artifacts/final_runs/20261018T145739Z/manifest.json`, field `source_sha256`; historical findings `docs/phase9_evaluation.md:185-187`). Real authentication, shared stores and operational lifecycle are outside initial scope, not broken promised features (`README.md:8`, `docs/production_review.md:7-12`). |

## System map, dependency direction and ownership

| Boundary | Responsibility and dependency direction | Evidence |
|---|---|---|
| CLI / Streamlit | Present input/results; select baseline, experiment or support path; invoke runtime/evaluation. | `main.py:28-41`, `:55-77`; `streamlit_app.py:31-40`, `:66-105` |
| Support application runtime | Construct identity/config/client/services, orchestrate memory/preferences, record minimized telemetry. Depends on graph, adapters and stores. | `support/runtime.py:7-18`, `:34-98`, `:101-143` |
| Supervisor and specialists | Plan, route, fulfill independent obligations, collect tool evidence, determine outcomes, compose and validate prose. Depends on registry, contracts, guards, obligations and privacy. | `support/graph.py:13-18`, `:179-219`, `:221-320`, `:346-452` |
| Tool adapter | Own schemas, agent permissions, deadlines, attempts, evidence/call records. Depends on services/contracts; exposes LangChain StructuredTool. | `support/registry.py:39-69`, `:95-145` |
| Domain services | Read synthetic fixtures, verify ownership, calculate eligibility, persist and read back a local mock ticket. Depends on contracts/corpus/privacy/SQLite. | `support/services.py:20-47`, `:102-136`, `:138-176` |
| Retrieval | Validate corpus/rule/index identity, embed locally, retrieve versioned passages and preserve conflict sources. | `retrieval/chroma_store.py:65-105`, `:109-173` |
| Provider adapters | LangChain client supplies runtime chat; legacy contract and HTTP client also support baseline experiments. | `support/runtime.py:93-95`; `langchain_client.py:15-38`; `model_client.py:30-44` |
| State / preferences | Process-local safe projection; opt-in local style store. Not authoritative commerce evidence. | `support/memory.py:112-118`, `:154-194`; `support/preferences.py:45-82`; planner contract `support/graph.py:41-48` |
| Observability | Context-local metadata spans, bounded export queue, minimized local records. | `observability/support_tracing.py:14-42`, `:61-78`; `support/runtime.py:20-32` |
| Evaluation | Frozen recorder, independent obligations/checks, same-model judgments and separately attributed human/AI review. Consumes runtime; does not grant runtime authority. | `evaluation/support_runner.py:64-72`; `docs/phase9_evaluation.md:172-180` |
| Historical / deferred demos | Baseline and prompt experiments remain useful controls; knowledge graph and external ETA stay gated from the initial UI. | `README.md:8`, `:34`, `:48`; `streamlit_app.py:22-29` |

Logical ownership should be explicit even in a one-person project: runtime owns composition/lifecycle, graph owns transitions, registry owns capabilities, services own domain truth, retrieval owns evidence identity, evaluation owns acceptance evidence. This is a recommended responsibility map, not a claim about an existing organizational owner registry.

The active core is `support/`, not the empty architectural shells. `agents/__init__.py`, `application/__init__.py`, `feedback/__init__.py`, `memory/__init__.py` and `orchestration/__init__.py` each contain zero bytes (filesystem inspection). They are placeholders, not implemented layers. No executable dead code is proven merely by no import hits; CLI/dynamic entrypoints and historical experiments must be checked before removal. No internal explicit-import cycle was found by the bounded AST inspection described above.

## Ranked top ten findings

### F01 — Major: structural success does not close semantic acceptance

**Evidence:** `docs/phase9_evaluation.md:174` records unsupported warranty-start and return-status conclusions despite earlier structural passes; `:185-187` records the next review's unsupported no-further-action wording and incomplete reviewer evidence. The source retains a bounded language gate (`support/guards.py:41-42`) and explicit return-status boundary (`support/graph.py:476-481`). These are repaired examples, not proof that the same old defects persist.

**Impact/reading:** Frozen case checks and high pass counts cannot alone justify acceptance; semantic evidence quality remains the highest current release risk. The prior candidate's documented review flags remain blocking for that candidate; the refreshed candidate needs its own completed review rather than inherited approval. **Minimal first increment:** complete the already authorized unchanged-candidate review/evaluation loop with the evidence-v2 packet and preserve exact source/model/output locks. Do not add production infrastructure or tune an unused holdout. Acceptance must name the reviewed candidate and unresolved flags explicitly.

### F02 — Major: the turn method is a concentrated change surface

**Evidence:** `support/graph.py:114-509` is one 396-line method; nested `specialist` is 100 lines (`:221-320`). Input routing (`:150-175`), result derivation (`:279-320`), outcome selection (`:346-358`), citation selection/repair (`:374-452`) and graph construction (`:483-499`) share closure state created at `:124-134`.

**Impact/reading:** A routing or composition edit requires reasoning about permissions, evidence, budgets and persistence-facing results together. This is a maintainability defect, not evidence of a presently wrong answer. **Minimal first increment:** after acceptance work, extract only pure outcome selection into a typed helper with explicit inputs; preserve public results and existing regression coverage. Then consider composition/citation policy and node factory extraction. Do not split every node into a new package at once.

### F03 — Major: dependency composition rebuilds domain snapshots per turn

**Evidence:** runtime creates `Services(root=root, search=search)` for each ordinary turn (`support/runtime.py:67`); construction parses rules, loads the corpus and checks consistency (`support/services.py:25-34`). Each `customers()`/`owned()` also reopens/parses orders (`:36-44`), and registry construction repeats customer validation (`support/registry.py:60-62`).

**Impact/reading:** Repeated work and file I/O are proven; a meaningful latency regression is not measured here. Independent reads can also see different filesystem revisions if fixtures are modified concurrently, although no such incident is established. **Minimal first increment:** add an explicitly versioned immutable fixture/corpus snapshot at application startup and inject it while retaining per-turn ownership/evidence checks. Define refresh/fail-closed behavior before caching; never cache customer answers as authoritative state.

### F04 — Major: async deadlines do not cancel synchronous workers

**Evidence:** provider work runs `model.invoke` through `asyncio.to_thread` plus `wait_for` (`support/model.py:24-35`); reads do likewise (`support/registry.py:125-126`), and runtime uses `asyncio.run` (`support/runtime.py:95`). HTTP itself has a configured timeout (`langchain_client.py:18-21`). The mock write deliberately executes synchronously to avoid orphan writes (`support/registry.py:121-124`).

**Impact/reading:** Cancelling the awaiting coroutine cannot terminate an already running synchronous function. Late reads cannot enter evidence through this return path, but workers can continue consuming resources; event-loop executor shutdown may affect observed request duration. The configured HTTP timeout mitigates this; an unbounded hang or measured resource leak is **not** established. **Minimal first increment:** use a controllable offline blocking fake to measure actual end-to-end timeout and executor completion, then adopt native asynchronous provider/read interfaces or a bounded managed executor where the evidence warrants it. Preserve serialized writes and reserved handoff budget.

### F05 — Minor: preference lookups acquire exclusive locks and rewrite files

**Evidence:** `PreferenceStore.transaction` always exclusively locks, trims and writes both stores after yielding (`support/preferences.py:53-65`); `profile` and `consented` both use it (`:76-82`). Runtime calls consent/profile on ordinary requests (`support/runtime.py:78-82`). Writes fsync and atomically replace files (`support/preferences.py:68-74`).

**Impact/reading:** Read operations cause disk writes and single-machine contention. Atomic replacement is a strength; no corruption or measured throughput loss is established. **Minimal first increment:** provide one read-only snapshot operation returning consent plus profile under a consistent lock; keep pruning/derived-report rebuilding in mutation or explicit maintenance paths. Check that reads leave bytes and modification times unchanged and that deletion semantics remain intact.

### F06 — Minor: telemetry allowlists lag new nodes and guard codes

**Evidence:** graph observes `return_status` (`support/graph.py:476-481`, `:494`), absent from `NODES` (`observability/support_tracing.py:16`); `span` maps unknown names to `unknown_tool` (`:28`). `G3_UNSUPPORTED_NO_ACTION_NEEDED` is emitted by `support/guards.py:42`, absent from `ERROR_CODES` (`observability/support_tracing.py:110-117`) and maps to `OTHER_ERROR` (`:118-122`).

**Impact/reading:** Correct runtime boundaries lose their diagnostic identity; outcome authority and sensitive-data exclusion are unaffected. **Minimal first increment:** register these controlled identifiers and add a small contract check that each statically declared graph node and known gate code has an intentional safe telemetry representation. Keep generic handling for truly unknown or unsafe errors.

### F07 — Minor: operational records lack an application retention bound

**Evidence:** requests append to `requests.jsonl` (`support/runtime.py:117-122`, `:138-142`); trace receipts append independently (`observability/support_tracing.py:97-100`); tickets persist in a SQLite table (`support/services.py:160-169`). In contrast, projection TTL/capacity and preference event bounds are explicit (`support/memory.py:35-38`, `support/preferences.py:61-62`, `:108`).

**Impact/reading:** These append paths have no rotation/deletion policy in the inspected implementation; external host rotation is not disproven. Long sessions can accumulate operational metadata and tickets. Synthetic scope keeps present privacy impact limited. **Minimal first increment:** document local retention/size limits and add an explicitly invoked rotation/purge command with dry-run and retained-ticket/idempotency implications before automatic deletion. Do not treat mock-ticket history as a disposable log without deciding replay requirements.

### F08 — Minor: status drift observed before concurrent consolidation; verify closure

**Evidence:** During pre-consolidation review of candidate `b3a9730` on 2026-10-18, before 14:53 UTC, README's then-line 16 still summarized 261 tests and an outstanding illness repair, while the detailed log already described later repairs. Those are historical observations, not claims about the updated README. At the original 14:53 UTC recheck, the main agent had created `docs/current_status.md:5-18` and replaced the README summary with links (`README.md:3`, `:19`). The ledger as read then explicitly distinguishes blocked prior candidates (`docs/current_status.md:22-24`) and authorized AI-proxy review (`:28`). `scripts/README.md:33`, `:39` still describes actual-human requirements; check it against the ledger's explicit amended mode before treating it as current command authority.

**Impact/reading:** The initial entry-point ambiguity is being corrected concurrently by the main agent; this audit must not report that correction as its own work or as an outstanding unchanged defect. **Minimal first increment:** verify the current ledger covers source, run/repeat, reviewer mode, findings and acceptance; align command guidance with the explicit policy while preserving actual-human defaults and historical records. Treat the remaining task as verification/triage, not implementation already performed by this audit.

### F09 — Minor: maintained contracts and safety limits require coordinated edits

**Evidence:** limits are asserted in `support/guards.py:15-16` while enforcement uses separate literals in `support/model.py:18`, `support/registry.py:107` and `support/graph.py:205-217`, `:241`. Provider response parsing/retry policy is duplicated across `model_client.py:44-99` and `langchain_client.py:40-82`; support calls the underlying `.chat` rather than that wrapper's `generate` (`support/runtime.py:94`, `support/model.py:20-28`).

**Impact/reading:** Paths can legitimately have different response contracts, but the difference must be intentional; no contradiction in current budget values is proven. The support path does not inherit all experiment-adapter retry/finish semantics. **Minimal first increment:** centralize immutable runtime budget constants with config assertions, and document/test the separate experiment versus support provider contracts. Extract only common numeric usage/error normalization if both paths remain necessary; do not remove the baseline adapter without checking its consumers.

### F10 — Minor: local resource ownership is implicit and starts at import time

**Evidence:** importing runtime constructs global memory with a daemon reaper (`support/runtime.py:18`, `support/memory.py:45-55`); importing tracing starts the exporter daemon (`observability/support_tracing.py:65-66`, `:108`). Exporter has `wait` but no stop/join lifecycle (`:79-106`); memory does have `close` (`support/memory.py:57-63`).

**Impact/reading:** CLI/test imports own background resources implicitly, complicating embedding and graceful teardown. Daemon termination can abandon queued exports; no production incident is claimed. **Minimal first increment:** introduce a small application resource container with explicit create/close ownership, inject memory/exporter at runtime and retain convenient CLI defaults. Specify whether shutdown drains or reports pending exports. Empty architectural packages should be removed or documented when this ownership decision is made, not populated speculatively.

## Roadmap and target structure

**Fix now:** finish F01's existing correctness/review loop; then take F06's narrow telemetry contract repair if it does not disturb candidate locks. Verify the concurrently added current-status entry for F08 after the candidate decision. None of these requires real transaction integrations or new infrastructure.

**Schedule:** extract one pure graph decision boundary (F02), introduce immutable fixture snapshots with explicit refresh (F03), measure actual timeout behavior before changing concurrency (F04), then separate preference reads from mutation (F05). Centralize budget definitions/provider contract documentation (F09) as a bounded follow-up. Add deliberate lifecycle ownership and local retention controls (F10/F07) before long-running local use expands.

**Accept and document:** process-local TTL memory, local SQLite mock tickets, POSIX preference locks, sequential dependent tool work and synthetic account selection remain valid for the stated capstone (`support/memory.py:35-42`, `support/services.py:160-169`, `support/preferences.py:55-65`, `streamlit_app.py:40-41`). Multi-instance persistence/authentication, real refunds/returns/cancellations, external ETA and knowledge-graph production use require new product scope (`README.md:8`, `docs/production_review.md:7-12`). The audit does not score their intentional absence as an application bug.

A practical target is to retain the current package names while making runtime the explicit composition root; keep graph transitions in `support/graph.py`, move pure outcome/citation decisions to a small adjacent policy module, and keep services independent of graph/model concerns. Put resource lifecycle in one runtime-owned object rather than introducing unused `application/` and `orchestration/` hierarchies. Preserve existing baselines as named experiments and separate present status from historical evaluation narrative. These are recommended increments grounded in F02/F03/F09/F10, not implemented changes.

## Evidence limits and handoff

The saved `artifacts/phase9/repair_v4_reviewed_evidence.json` reports `hard_case_passes=65`, `all_case_passes=65`, `consistency.runs=45`, `consistency.outcome_agreement=1.0`, and `release_accepted=false`. These are historical candidate measurements and do not validate the inspected current build. `artifacts/phase9/release_offline_validation.json` reports `passed=242`, `failed=0`, `elapsed_seconds=17.49`, also historical. Current documented results and latest semantic findings are cited separately above. The audit establishes no new coverage percentage, p95, concurrency capacity, security guarantee or holdout score.

The main agent should triage and action [the proposed task ledger](../tasks.md), prioritizing the already active correctness/evaluation loop. Task status and subsequent main-agent triage are owned by the ledger; this audit implemented none of the proposed changes. No implementation diff is part of this report.


## Main-agent actions after the audited snapshot

The scorecard and source citations above describe the explicitly inspected `ce64d4e` snapshot, not a newly accepted final build. Subsequent correctness work is tracked separately in `docs/current_status.md`. The main agent implemented F06/A02's controlled node/error categorization at the next source checkpoint; its tracing contract checks pass while arbitrary names/errors remain generic. This is not implementation work by the read-only auditor and does not retroactively change its score. Status/command consolidation for F08/A03 is also actioned separately; final current-build acceptance remains open.

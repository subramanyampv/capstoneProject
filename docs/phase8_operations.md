# Phase 8 — observability and local deployment readiness

Implemented and verified 2026-10-16. The supported deployment is the source checkout plus an editable install in a local virtual environment. The initial product is a synthetic local application; production authentication, store integrations and public deployment are outside this closure.

## Startup and commands

Use the existing approved project `.venv`. If no local virtual environment is available, stop and obtain approval before creating one. Never install Python packages globally.

```bash
.venv/bin/python -m pip install -c constraints-dev.txt -e '.[dev,eval,ui,rag]'
# Create .env from .env.example only if .env does not already exist; then configure locally.
.venv/bin/capstone-agent ingest --index-version v2
.venv/bin/capstone-agent doctor --index
.venv/bin/capstone-agent support --chat --customer C-100
bash scripts/run_support_ui.sh
```

The final UI startup script validates configuration, policy/fixture consistency, safety rules, flags, pinned embeddings and the current index before binding to loopback port 8501. `doctor` without `--index` runs lightweight checks. It returns check names/pass flags and static error codes, never configuration values or exception messages. It does not claim provider connectivity. The general `run_ui.sh` remains available for baseline experiments without requiring final-agent configuration. No return/refund/cancellation transaction is executed.

| Command | Purpose |
|---|---|
| `make support-ready` | Offline pinned-index/local startup validation |
| `make support-ui` | Validated loopback-only Streamlit startup |
| `make verify-operations` | Six synthetic operational samples; safe logs/traces and measured counters |
| `make verify-hosted` | Read back a small content-free LangSmith trace |
| `make scan-final` | Current configured credentials plus known operational canaries |
| `make evaluate-support ARGS='--dataset … --contexts … --dry-run'` | Validate final-run inputs and reviewed identity/setup contexts |
| `make consistency-support ARGS='--dataset … --contexts … --output …'` | Three repeats, same code-contract recorder |

Evaluation now has a final-graph recorder and local DeepEval contract metric. It checks schema, budgets, canonical citations and actual tool-backed mock handoffs. It requires explicit synthetic customer context; it does not guess identity from an order number. Holdout-named files require `--allow-holdout`. These entrypoints do not replace the Phase 9 review of case contexts, expected routing/semantic labels, conversation setup, human calibration or final scoring. No frozen/holdout evaluation was performed during Phase 8.

## Content-free tracing boundary

Native LangChain/LangGraph content-bearing tracing remains suppressed. Explicit spans surround the actual graph nodes, model invocations and tool calls. The parent tree is request → graph node → model/tool. The composition node also performs Guard-Out; no separate persisted working-state checkpoint is introduced. Commands have a request span without invoking the support graph. Projection memory remains independently privacy-bounded.

Span payloads contain generated UUIDs, parent/trace IDs, static allowlisted names/types, UTC start/end times and controlled outputs: numeric counters/token counts, boolean failure flags and code-computed terminal outcomes. They never contain queries, model messages, answers, retrieval passages, tool arguments/results, names, addresses, customer/order identifiers or keys. Unknown tool names become `unknown_tool`; schema diagnostics discard model-supplied field names. Local records retain opaque customer/session/order references, stages, triggers/refusals, safe error codes, tool status, style/memory metadata and counters. Rejected requests receive a content-free failure record rather than raw exception text.

New mock ticket packets persist generated reason-code summaries rather than free-form model summaries, so arbitrary names cannot evade a pattern masker and enter new ticket packets. Existing controlled input rejection, ownership/evidence checks and actual commit/read-back remain unchanged. Historical development artifacts are preserved, not retroactively rewritten.

## Opt-in export and isolation

Configure `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, `LANGSMITH_TRACING=true` and an HTTPS endpoint only in the ignored `.env`. Templates remain off/blank. The user supplied the local key during Phase 8. Application-level SDK text diagnostics are suppressed because they can contain credential fragments; controlled delivery receipts replace them.

A daemon exporter uses a bounded queue of 32 traces and at most 100 spans per trace. It creates empty-input runs with safe outputs, explicit parent/trace IDs and dotted order. HTTP work is outside the support response path. Queue-full, configuration and transport/auth/access errors become status codes, never customer outcome changes. `queued` does not mean delivered; `data/runtime/trace_exports.jsonl` records delivered/failed status. CLI exit allows a bounded five-second drain after printing the response. Sudden termination may lose pending exports; this is not durable telemetry or a distributed production collector.

Streamlit's Traces tab shows the safe routing timeline and delivery receipts. Its last answer is cleared before a new request so a failed request cannot leave a stale answer presented as current. Session identity, feedback commands, reasons, citations and verified handoff/failure rendering remain shared with the terminal. Request logs currently have no automatic rotation; local operators manage those ignored metadata files separately from conversation/preference deletion.

## Verification and limits

- [Clean install](../artifacts/phase8/clean_install.json): new temporary venv and copied nonignored source, 155 installed distributions matching existing versions, pip check, CLI commands, 204 tests, fresh 28-chunk index and six startup checks passed. No `.env` or vector database was copied. The pinned model download cache was reused; a cold model download was not tested. Clean startup used a dummy loopback model configuration, while live provider/hosted tests ran separately in the main checkout.
- [Operational sample](../artifacts/phase8/20261016T214110Z/summary.json): six of six expected outcomes across answer/refusal/failed-handoff paths. Two samples per path are insufficient for production p95 claims. Latencies are the existing graph elapsed measurements, excluding public-index startup and asynchronous trace delivery.
- [Hosted answer trace](../artifacts/phase8/hosted_graph_readback_0.json): twelve runs read back with matching parents, empty inputs and matching safe outputs.
- [Hosted canary/failure trace](../artifacts/phase8/hosted_graph_readback_4.json): thirteen runs read back; configured credentials and synthetic name/email/phone/address/order/customer canaries absent from hosted payloads.
- [Failure isolation](../artifacts/phase8/failure_isolation_live.json): disabled versus deliberately invalid credentials preserve deterministic refusal and injury-backstop outcomes, triggers, model counts and the same idempotent mock ticket. The observed invalid-credential request returned 403; this can represent API authorization or an intermediary access restriction.
- [Routing screenshot](../artifacts/phase8/routing_ui.png): clean-install Streamlit rendering of captured synthetic safe metadata; hosted API read-back is separately recorded.
- [Privacy scan](../artifacts/phase8/privacy_scan.json): configured keys and known operational canaries. This is bounded evidence, not universal PII detection or forensic erasure.

The first hosted read-back incorrectly treated server `null` and local `{}` empty outputs as different; that failed verifier report is preserved. The verifier now normalizes empty containers, without accepting any extra output fields. Initial clean-check failures and fixes are retained in the clean-install report. The pinned SDK's verification-only `list_runs` method emits a deprecation warning for removal after January 2027; migrate that reader before its removal. Runtime ingestion does not depend on it.

Phase 8 closure does not accept the complete product. Phase 9 still owns full frozen/untouched-holdout testing, independently reviewed contexts and expected outcomes, semantic/faithfulness checks, repeated consistency, human calibration and final demonstration/submission packaging.

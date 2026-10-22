# E-commerce Support Resolution Agent

> Current candidate and pending acceptance gates: [Current status](docs/current_status.md). Frozen regression completion alone is not final acceptance.


The authoritative [Architecture and Plan v3.3](docs/architecture_and_plan.md) supersedes all earlier designs. See the [document index](docs/README.md), [implementation status](docs/implementation_status.md), and [detailed progress summary](docs/project_progress.md), and [task checklist](docs/task_list.md). The [Memory Pad](docs/memory_pad.md) compares ecommerce agents and tracks possible extensions; the earlier [market comparison](docs/market_comparison.md) remains available.

The core implements a LangGraph supervisor, three LangChain specialists and six typed tools. Policy retrieval uses normalized embeddings and a versioned Chroma index. Chat and embedding endpoints are independently configurable; the default local embedding identity is pinned in the index manifest. Deterministic guards enforce safety, eligibility and verified local mock escalation. Return/refund/cancellation writes, the knowledge graph and external API ETA remain deferred. Synthetic data only.

| Phase | Status |
|---|---|
| 1–2 | Complete; baseline closure reverified 2026-10-13 |
| 3 | Complete under v3; Prompt C development default; final safety gates remain open |
| 4 | Local retrieval measured; retained development recall improved 80% → 100%; category-aware v2 index verified; final tool integration tracked separately |
| 5 | Typed tools, server identity and bounded multi-agent core implemented; core live smoke verified; final acceptance pending |
| 6 | Bounded projection memory, follow-ups and reset/expiry implemented; five-conversation comparison measured |
| 7 | Implemented: controlled style feedback, versioning/reset/deletion in terminal and Streamlit; development evidence |
| 8 | Verified: hosted metadata hierarchy/masking/failure isolation, safe logs/startup and clean local deployment |
| 9 | Correctness/evaluation in progress; exact current candidate and each pending gate are recorded in [Current status](docs/current_status.md). Earlier 65/65 passes do not establish final acceptance. |

## Local setup

Run from `capstone_agent/` using the existing project `.venv`. If it is absent, obtain approval before creating one. Python 3.12.12 is the tested environment.

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/capstone-agent status
.venv/bin/capstone-agent doctor
.venv/bin/python scripts/check_model.py
bash scripts/ingest.sh
.venv/bin/capstone-agent support "Track order O-1001" --customer C-100
.venv/bin/python -m pytest -q --tb=no
bash scripts/run_ui.sh
```

The UI binds to http://127.0.0.1:8501 with Chat, Evaluation and Traces. It exposes baseline/LLM experiments and a Support agent mode with synthetic account selection, current-turn tools, citations and verified local mock handoffs. Bounded session memory and reset/expiry are implemented; controlled style adaptation is implemented. `UI_SHOW_DEFERRED=true` explicitly restores the historical Knowledge and Delivery-estimate demonstrations; they are excluded from initial-product evaluation.

## Model configuration and experiments

Keep credentials only in ignored `.env`. Copy `.env.example` only when creating configuration; do not overwrite an existing configured file. The template intentionally contains blank assignments: fill required chat settings before startup. See [environment configuration](docs/environment_configuration.md) for required versus optional fields, defaults, blank-value handling, and independent embedding/judge setup. Use `CAPSTONE_LLM_PROVIDER=openai_compatible`, `LLM_BASE_URL`, `MODEL_NAME`, and `LLM_API_KEY`. Existing `LLM_MODEL` and `MODEL_BASE_URL`/`MODEL_API_KEY` aliases are supported: present `MODEL_*` keys take precedence even when blank. Process environment overrides the local file. Omit optional numeric keys to use defaults. Loopback servers may omit a key; remote endpoints require HTTPS and a key. Errors do not echo values.

For retrieval, `EMBEDDING_BACKEND=local` uses an existing `knowledge/index_manifest.json` identity unless explicitly overridden. A fresh public copy has no deployment manifest or built-in model identity: set `EMBEDDING_MODEL`, `EMBEDDING_REVISION` and `EMBEDDING_DIMENSION` before ingestion. The `openai_compatible` backend additionally requires `EMBEDDING_BASE_URL`; a remote endpoint requires `EMBEDDING_API_KEY`. Local models must expose the query/document encoding interface. Custom model code is permitted only for an exact previously reviewed identity digest; arbitrary configured models receive no remote-code trust. Changing embedding identity requires a new index version and fresh retrieval calibration; an incompatible existing index is rejected. Backend protocol tests use synthetic vectors; they do not establish retrieval quality for an arbitrary replacement model.

`scripts/check_model.py` makes one small live request and reports only a closed error category, HTTP status and retryability. It never prints provider exception bodies, credentials or endpoint paths. A successful ping establishes connectivity only. Run the public frozen evaluation separately for behavior validation.

An independent OpenAI-compatible judge can be configured separately in ignored `.env` with `JUDGE_BASE_URL`, `JUDGE_MODEL`, and `JUDGE_API_KEY`. Keep the application settings unchanged. Run `.venv/bin/python scripts/judge_final_suite.py artifacts/final_runs/RUN --all --judge-id second` to write isolated results under `RUN/judges/second/`; existing primary scores are preserved. Judge identity and source manifests are locked so a resumed file cannot silently combine models. Report each judge separately and review disagreements against source evidence; judge agreement does not waive deterministic safety failures or establish human calibration.

```bash
.venv/bin/capstone-agent llm-ask "Can I return my shoes?"  # development default C
bash scripts/run_prompt_comparison.sh --dry-run
bash scripts/run_prompt_comparison.sh --case N01 --case R01
.venv/bin/python scripts/build_prompt_report.py            # saved evidence; no API requests
.venv/bin/capstone-agent evaluate artifacts/prompt_runs/20261013T030651Z-b48a462e
```

A/B/C still use their original versioned prompts and independent case contexts. Saved run manifests are immutable historical records and retain their original null selection. The [completed comparison](docs/prompt_comparison.md) records the v3 decision separately. DeepEval exits nonzero for the seven known mandatory-classification failures; that is expected, not an installation error. Optional same-model judging is disclosed as self-evaluation, not independent validation.

Phase 5: `.venv/bin/capstone-agent support "Can I return TrailRunner Shoes order O-1001?" --customer C-100`. See [tools, safety and graph details](docs/phase5_tools_and_graph.md), including preserved live failures and current limits.

Session chat: `.venv/bin/capstone-agent support --chat --customer C-100`; `/reset` clears context, `/quit` exits. Context is process-local; one-shot invocations do not share memory. See [Phase 6 memory](docs/phase6_memory.md).

Style feedback works in terminal and Streamlit: `/feedback too_long`, `/feedback too_short`, `/feedback unclear`, `/feedback helpful`, `/feedback not_helpful`. Two matching signals among the recent ten can change length or format. Explicit feedback enables learning; use `/feedback enable` or `/feedback disable` to control automatic learning, `/feedback reset_style` to restore default style, and `/forget-preferences` to delete saved preferences/feedback. Preferences persist per synthetic customer; `/reset` clears only session memory. Commands work without a provider/index. See [Phase 7 adaptation](docs/phase7_adaptation.md) and [validation](artifacts/phase7_validation.md).

Local retrieval commands: `make ingest`, `make eval-retrieval`, and `.venv/bin/capstone-agent search-policy "footwear return window"`. [Retrieval design and results](docs/retrieval_design.md) record measured coverage and limitations.

Hosted metadata tracing defaults off when omitted; its optional settings are documented in [environment configuration](docs/environment_configuration.md). Hosted content-free hierarchy, canary exclusion and exporter-failure isolation have dated verification evidence; configure credentials only in ignored `.env`. Local JSONL remains primary evidence.

## Evidence and submission

[Phase 2 closure](docs/phase2_closure.md) · [Phase 3 comparison](docs/prompt_comparison.md) · [Plan review](docs/plan_review.md). Dated artifacts establish measured results; planned capabilities and targets are labeled explicitly. No final safety pass is claimed.

The existing repository contains a historical revoked credential. A scanned history-free source snapshot has been prepared locally and will be refreshed as work continues. The current repository remains in use; a new repository and author/student name are not required, and existing history will not be rewritten. `.env`, runtime stores, model cache and generated indices remain ignored.

Final operations: `make support-ready`, `make support-ui`, `make verify-hosted` and `make scan-final`. The exact-input public frozen recorder, separate DeepEval judgments and review tooling are documented in [Phase 9 evaluation](docs/phase9_evaluation.md). Historical passes and reviews apply only to their recorded builds. Current checks and unresolved acceptance gates are in [Current status](docs/current_status.md); no historical result establishes acceptance for the modified source. Unused blind cases remain local and unopened. Stop before ZIP creation under the existing submission instruction. See [Phase 8 operations](docs/phase8_operations.md) for operational scope and historical evidence.

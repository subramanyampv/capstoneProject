# E-commerce Support Resolution Agent

The authoritative [Architecture and Plan v3.1](docs/architecture_and_plan.md) supersedes all earlier designs. See the [document index](docs/README.md), [implementation status](docs/implementation_status.md), and [detailed progress summary](docs/project_progress.md), and [task checklist](docs/task_list.md). The [Memory Pad](docs/memory_pad.md) compares ecommerce agents and tracks possible extensions; the earlier [market comparison](docs/market_comparison.md) remains available.

The core now implements a LangGraph supervisor, three LangChain specialists and six typed tools. Policy retrieval uses local Voyage-4-nano and Chroma. Deterministic guards decide safety, eligibility and verified mock escalation. Return/refund/cancellation writes, the knowledge graph and external API ETA are deferred until the initial product succeeds. Synthetic data only.

| Phase | Status |
|---|---|
| 1–2 | Complete; baseline closure reverified 2026-10-13 |
| 3 | Complete under v3; Prompt C development default; final safety gates remain open |
| 4 | Local retrieval measured; retained development recall improved 80% → 100%; category-aware v2 index verified; final tool integration tracked separately |
| 5 | Typed tools, server identity and bounded multi-agent core implemented; core live smoke verified; final acceptance pending |
| 6 | Bounded projection memory, follow-ups and reset/expiry implemented; five-conversation comparison measured |
| 7 | Implemented: controlled style feedback, versioning/reset/deletion in terminal and Streamlit; development evidence |
| 8 | Verified: hosted metadata hierarchy/masking/failure isolation, safe logs/startup and clean local deployment |
| 9 | Pending: reviewed contexts, frozen/holdout evaluation, human calibration and final acceptance |

## Local setup

Run from `capstone_agent/` using the existing project `.venv`. If it is absent, obtain approval before creating one. Python 3.12 is the tested environment.

```bash
.venv/bin/python -m pip install -c constraints-dev.txt -e ".[dev,eval,ui,rag]"
.venv/bin/capstone-agent status
.venv/bin/capstone-agent ask "Can I return order O-1001?" --today 2026-10-12
bash scripts/run_baseline.sh
.venv/bin/python -m pytest -q --tb=no
bash scripts/run_ui.sh
```

The UI binds to http://127.0.0.1:8501 with Chat, Evaluation and Traces. It exposes baseline/LLM experiments and a Support agent mode with synthetic account selection, current-turn tools, citations and verified local mock handoffs. Bounded session memory and reset/expiry are implemented; controlled style adaptation is implemented. `UI_SHOW_DEFERRED=true` explicitly restores the historical Knowledge and Delivery-estimate demonstrations; they are excluded from initial-product evaluation.

## Model configuration and experiments

Keep credentials only in ignored `.env`. Copy `.env.example` only when creating configuration; do not overwrite an existing configured file. Provide URL, model name and key via existing `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`; v3 aliases `MODEL_BASE_URL`, `MODEL_NAME`, `MODEL_API_KEY` are supported. Canonical aliases take precedence when present. Set `CAPSTONE_LLM_PROVIDER=openai` or `openai_compatible`. Loopback servers may omit a key; remote endpoints require HTTPS and a key. Errors do not echo values.

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

LangSmith defaults off. Configure its key/project in ignored `.env` to verify hosted tracing later. Current hidden-input metadata spans are implemented; final masked hierarchical agent/tool traces and failure isolation remain planned.

## Evidence and submission

[Phase 2 closure](docs/phase2_closure.md) · [Phase 3 comparison](docs/prompt_comparison.md) · [Plan review](docs/plan_review.md). Dated artifacts establish measured results; planned capabilities and targets are labeled explicitly. No final safety pass is claimed.

The existing repository contains a historical revoked credential. A scanned history-free source snapshot has been prepared locally and will be refreshed as work continues. The current repository remains in use; a new repository and author/student name are not required, and existing history will not be rewritten. `.env`, runtime stores, model cache and generated indices remain ignored.

Final operations: `make support-ready`, `make support-ui`, `make verify-hosted` and `make scan-final`. Final-run recording/repeats are available through `capstone-agent evaluate-support`; Phase 9 now has a versioned exact-input frozen recorder, separate DeepEval judgments and human-calibration tooling. The initial 65-case baseline is complete with failures preserved; final acceptance remains open. See [Phase 9 evaluation](docs/phase9_evaluation.md). See [Phase 8 operations](docs/phase8_operations.md) and [validation](artifacts/phase8/validation.md).

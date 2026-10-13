# E-commerce Support Resolution Agent

The authoritative [Architecture and Plan v3](docs/architecture_and_plan.md) supersedes all earlier designs. See the [document index](docs/README.md) and [implementation status](docs/implementation_status.md).

The initial product targets a LangGraph supervisor, three LangChain specialists and six typed tools. Policy retrieval uses local Voyage-4-nano and Chroma. Deterministic guards decide safety, eligibility and verified mock escalation. Return/refund/cancellation writes, the knowledge graph and external API ETA are deferred until the initial product succeeds. Synthetic data only.

| Phase | Status |
|---|---|
| 1–2 | Complete; baseline closure reverified 2026-10-13 |
| 3 | Complete under v3; Prompt C development default; final safety gates remain open |
| 4 | Initial corpus/index and measured RAG comparison implemented; threshold coverage gap remains |
| 5–9 | Planned: tools/guards, memory/adaptation, deployment and final evaluation |

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

The UI binds to http://127.0.0.1:8501 with Chat, Evaluation and Traces. It currently exposes baseline/LLM experiment behavior, not the planned final multi-agent product. `UI_SHOW_DEFERRED=true` explicitly restores the historical Knowledge and Delivery-estimate demonstrations; they are excluded from initial-product evaluation.

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

Local retrieval commands: `make ingest`, `make eval-retrieval`, and `.venv/bin/capstone-agent search-policy "footwear return window"`. [Retrieval design and results](docs/retrieval_design.md) record measured coverage and limitations.

LangSmith defaults off. Configure its key/project in ignored `.env` to verify hosted tracing later. Current hidden-input metadata spans are implemented; final masked hierarchical agent/tool traces and failure isolation remain planned.

## Evidence and submission

[Phase 2 closure](docs/phase2_closure.md) · [Phase 3 comparison](docs/prompt_comparison.md) · [Plan review](docs/plan_review.md). Dated artifacts establish measured results; planned capabilities and targets are labeled explicitly. No final safety pass is claimed.

The existing repository contains a historical revoked credential. A fresh, scanned submission snapshot without Git history will be prepared separately; the current repository will not be rewritten. `.env`, runtime stores, model cache and generated indices remain ignored.

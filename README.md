# Multi-Agent E-commerce Support Agent (Capstone)

A supervisor–specialist multi-agent support agent for Tier-1 e-commerce questions:
order status, returns, shipping, product questions, and escalation.

The target architecture separates LLM interpretation from deterministic policy,
authorization, confirmation, and action-state services. The current implementation
has a rule baseline and an LLM-only experimental path with **no write actions**.
The planned transaction layer will use simulated writes. Synthetic data only.

## Status

| Phase | Description | Status |
|---|---|---|
| 1 | Problem framing & success definition | **done 2026-10-12** — taxonomy, corpus, and 65-case dataset frozen |
| 2 | Rule-based Python baseline | **done; reverified 2026-10-13** — six supported demos, two required limitations, sanitized evidence and closure report |
| 3 | LLM integration & prompt evaluation | 195-response live comparison complete; quality defects documented, default selection pending |
| 4 | Knowledge & retrieval (RAG) | not started |
| 5 | Tools & multi-agent orchestration | not started |
| 6 | Planning, memory, context | not started |
| 7 | Adaptive behavior (feedback) | not started |
| 8 | Deployment readiness | not started |
| 9 | Evaluation & engineering review | not started |

Blueprint: [Architecture plan](docs/capstone_architecture_plan.pdf)

Updated blueprint: [Architecture plan v2](docs/capstone_architecture_plan_v2.pdf)
([editable source](docs/architecture_plan_v2.md)).
Frameworks and demo UI: [integration notes](docs/framework_integration.md).

Continuation notes: [Documentation review](docs/documentation_review.md).
Phase 2 exit evidence: [closure report](docs/phase2_closure.md).

## Layout

```
docs/          Phase 1+ rubric documents (framing, architecture, safety, demos, evaluation)
src/capstone_agent/
  application/     request handler, response builder        (layer 1)
  orchestration/   orchestrator, planner, routing, state    (layer 2)
  agents/          base + 5 domain specialists              (layer 3)
  domain/          schemas, policy service, eligibility, action state machine
  retrieval/       ingestion, chunking, embeddings, vector store
  tools/           allowlisted registry + typed domain tools
  safety/          validation, PII redaction, guardrails, authorization, confirmation
  memory/          session store, retention/reset
  feedback/        collector, adaptation (whitelisted params only), audit
  prompts/         versioned prompt templates
  observability/   structured logs, trace IDs, metrics
  evaluation/      harness, scorers, report generation
knowledge/     raw docs -> processed chunks -> FAISS index snapshots
data/          synthetic records + frozen evaluation cases
tests/         unit / integration / safety / regression
artifacts/     actual run outputs: comparisons, evaluation results, traces
scripts/       run, ingest, build index, evaluate (one documented command each)
```

## Quickstart

Requires Python 3.10+ (developed against 3.12). Run commands from this directory.
Use the approved project-local `.venv`; if absent, obtain approval before creating one.

```bash
.venv/bin/python -m pip install -c constraints-dev.txt -e ".[dev,eval,ui]"

.venv/bin/capstone-agent status
.venv/bin/capstone-agent ask "Can I return order O-1001?" --today 2026-10-12
bash scripts/run_baseline.sh                 # overwrites baseline evidence; run intentionally
.venv/bin/python -m pytest -q --tb=no
cp .env.example .env                         # configure local provider; keep credentials local
```

The Phase 2 baseline is deterministic: answers depend only on the frozen fixtures and
the `--today` scenario clock. Ingest/evaluate commands arrive in Phases 4 and 9.

## Phase 3 model experiment

Set `LLM_BASE_URL` to the provider's API base (including `/v1`) and `LLM_MODEL`
to its exact model ID in `.env`. Set `CAPSTONE_LLM_PROVIDER` to `openai` or
`openai_compatible`. Remote endpoints require a key; loopback servers may omit it.
Keep keys only in the ignored `.env`, and leave `LLM_API_KEY` empty in `.env.example`.
For OpenAI, use `https://api.openai.com/v1` and a model available to your account.
For compatible providers, use their documented URL and model ID.

```bash
.venv/bin/capstone-agent llm-ask "Can I return my shoes?" --prompt C
bash scripts/run_prompt_comparison.sh --dry-run    # plan only; no requests
bash scripts/run_prompt_comparison.sh --case N01 --case R01  # smoke comparison
bash scripts/run_prompt_comparison.sh             # all 65 cases x 3 variants
bash scripts/run_prompt_comparison.sh --workers 3 # bounded concurrent clients
```

Each comparison uses a new directory in `artifacts/prompt_runs/`, with a manifest,
prompt snapshots, sanitized outputs, a review CSV, and a summary. The full run has
195 scheduled requests; repair and retry budgets may increase HTTP attempts.
Errors produce nonzero CLI exit status. No prompt default has been selected.
Configuration is loaded once per run. After rotating a key or changing provider
settings, start a new run; an in-progress comparison keeps its original configuration.
See [Phase 3 evidence and limits](docs/prompt_evaluation.md).
Measured run: [live comparison results](docs/phase3_live_results.md).
Phase 4 candidate: [embedding recommendation](docs/embedding_strategy.md).

## Python UI and evaluation

```bash
bash scripts/run_ui.sh     # Streamlit on http://127.0.0.1:8501
.venv/bin/capstone-agent evaluate artifacts/prompt_runs/20261013T030651Z-b48a462e
```

The UI offers chat, recorded evaluations, provenance graph exploration and a
rule-based delivery estimate. ETA inputs are manual demo facts unless the public API
checkbox is selected. [External tool options](docs/external_tool_options.md) document
the distance/weather sources and future product/order integrations.
LangSmith tracing is disabled until a key/project is configured in ignored `.env`.
DeepEval judge scoring is optional and separate from deterministic safety checks.

## Target architecture invariants

These are acceptance requirements for later phases. The current baseline and LLM
experiment do not establish full policy, authorization, confirmation, or memory gates.

- No unsupported policy claim is stated as fact.
- Confirmation is bound to session, action ID, action type, exact parameters, and expiry.
- A specialist cannot grant itself permissions through generated tool calls.
- Tool failure is never silently treated as success.
- Memory cannot override current policy or verified records.
- Every request has an auditable terminal outcome; retries/delegation have finite budgets.
- Sensitive values are minimized and redacted before logs are written.

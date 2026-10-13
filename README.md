# Multi-Agent E-commerce Support Agent (Capstone)

A supervisor–specialist multi-agent support agent for Tier-1 e-commerce questions:
order status, returns, shipping, product questions, and escalation.

Safety-first by design: the LLM interprets and drafts; deterministic policy,
authorization, confirmation, and action-state services decide. All write actions
are **simulated** and auditable. Synthetic data only — no real customer systems.

## Status

| Phase | Description | Status |
|---|---|---|
| 1 | Problem framing & success definition | **done 2026-10-12** — taxonomy, corpus, and 65-case dataset frozen |
| 2 | Rule-based Python baseline | **done 2026-10-12** — `baseline_agent.py`, pinned-clock repro run, both required limitations demonstrated + test-locked |
| 3 | LLM integration & prompt evaluation | not started (next) |
| 4 | Knowledge & retrieval (RAG) | not started |
| 5 | Tools & multi-agent orchestration | not started |
| 6 | Planning, memory, context | not started |
| 7 | Adaptive behavior (feedback) | not started |
| 8 | Deployment readiness | not started |
| 9 | Evaluation & engineering review | not started |

Blueprint: `../multi_agent_capstone_architecture_plan.pdf`

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

Requires Python 3.10+ (developed against 3.12). Use the workspace venv.

```bash
source ../.venv/bin/activate        # or your own venv
pip install -e ".[dev]"

capstone-agent status                                    # phase overview
capstone-agent ask "Can I return order O-1001?" --today 2026-10-12   # rule baseline
scripts/run_baseline.sh                                  # reproducible evidence run -> artifacts/
pytest                                                   # unit tests incl. limitation locks
cp .env.example .env                # add provider settings when Phase 3 lands
```

The Phase 2 baseline is deterministic: answers depend only on the frozen fixtures and
the `--today` scenario clock. Ingest/evaluate commands arrive in Phases 4 and 9.

## Key invariants (enforced, not aspirational)

- No unsupported policy claim is stated as fact.
- Confirmation is bound to session, action ID, action type, exact parameters, and expiry.
- A specialist cannot grant itself permissions through generated tool calls.
- Tool failure is never silently treated as success.
- Memory cannot override current policy or verified records.
- Every request has an auditable terminal outcome; retries/delegation have finite budgets.
- Sensitive values are minimized and redacted before logs are written.

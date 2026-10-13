> Governing design: [Architecture and Plan v3](architecture_and_plan.md). This document records implemented adapters; historical 75-test evidence predates the later Phase 2 closure. KG and API ETA are deferred and hidden by default.

# Framework integration — 2026-10-12

The user selected **LangChain + LangGraph + LangSmith + DeepEval + Streamlit**.
The existing deterministic domain boundary remains outside model authority.

## Current implementation

- `LangChainChatClient` wraps `ChatOpenAI` behind the existing model-client protocol.
  OpenAI-compatible Qwen configuration, explicit thinking/format settings, safe errors,
  disabled SDK retries with the application's bounded retry budget, and no redirects.
- LangGraph executes `prepare -> model -> validate -> finalize`, with one optional
  `repair -> model -> validate` cycle and recursion budget 12. Graph state does not
  grant action permissions. The CLI and comparison harness use this path.
- LangSmith is explicitly opt-in. Its client hides inputs, allowlists metric outputs
  and metadata, omits runtime information and suppresses native model traces that
  could contain raw provider exceptions. A request trace ID matches the local request ID.
  No LangSmith key is configured yet; hosted trace delivery remains unverified.
- DeepEval custom metrics check typed output/no-write claims and mandatory escalation
  classification. Optional GEval uses a schema-aware configurable LangChain judge.
  Metrics run locally without Confident AI login/upload, telemetry or dotenv autoload.
- Streamlit defaults to Chat, Evaluation and Traces. Historical Knowledge and Delivery
  estimate tabs require explicit UI_SHOW_DEFERRED=true and are excluded from initial-product evaluation.
  It is bound only to localhost and performs model/API calls only on form submission.
- The lightweight knowledge graph connects synthetic catalog products and categories
  with source/version provenance and bounded traversal. It excludes private order and
  customer relationships until authorization exists; document-section links await ingestion.
- The delivery estimate uses a separate `demo-eta-v1` rule file: minimum 1 day,
  ceil(miles × 3 / 1000), storm/snow +2 days once, upper buffer +2 days. It supports
  manual demo facts or allowlisted read-only OSRM distance/NWS alerts. Missing/stale
  facts yield uncertainty, and a past estimate window requires carrier review.

## Verification

- **75 offline tests passed** after final trace-ID/redaction and judge-failure checks; final
  verification is recorded in `artifacts/framework_validation.md`.
- Live LangChain/LangGraph smoke: N01/R05/M01 × A/B/C = **9/9 validated**,
  saved in `artifacts/prompt_runs/20261013T034118Z-745df983/`.
- DeepEval checked all **195** saved Phase 3 outputs: schema/action contract passes,
  **7 mandatory escalation-classification failures**. Those failures are preserved,
  not converted into passes by aggregate scoring.
- Optional same-model GEval smoke on N01 A/B/C produced scores **1.0**. This verifies
  judge plumbing only; it is not an independent judge or comprehensive quality result.
- Streamlit AppTest verified startup and baseline submission with no exceptions;
  the browser layout was also visually inspected. A cold first run exceeded 15 seconds;
  the successful verification used a 45-second test timeout.
- Public city-centre API smoke: NY -> Denver returned **1781.28 road miles**, and NWS
  returned **0 active destination-area alerts**. No-alert status is not a clear-weather
  or route-wide forecast, and road distance is a parcel transit proxy, not a carrier SLA.

## Commands

```bash
.venv/bin/python -m pip install -c constraints-dev.txt -e ".[dev,eval,ui]"
.venv/bin/python -m pytest -q --tb=no
bash scripts/run_ui.sh
bash scripts/run_prompt_comparison.sh --case N01 --case R05 --case M01
.venv/bin/capstone-agent evaluate artifacts/prompt_runs/20261013T030651Z-b48a462e
```

The evaluation command exits nonzero when it detects a metric failure; this is expected
for the saved escalation misses. To enable optional judging, add `--judge-env-file`
with an ignored environment file containing the chosen judge's URL/model/key. Prefer
an independent model for quality evaluation; clearly label same-model experiments.

## Required next input

For hosted observability verification, set these **only in ignored `.env`**:

```dotenv
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=<your private key>
LANGSMITH_PROJECT=capstone-agent
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

Keep tracing false until configured. No real key belongs in `.env.example`, chat,
documents, screenshots or test fixtures. DeepEval's automatic pytest plugin is disabled
because its implicit dotenv loading contaminated tests and caused a credential to appear
in a failure diagnostic. That credential was not committed; the import regression now
verifies no private env is loaded. Unrelated automatic rerun plugins are also disabled.

The original frozen dataset/threshold files and baseline evidence are preserved. The
new ETA demo rules do not silently replace the retailer's frozen shipping policy.
Phase 3 prompt quality misses, full retrieval, transaction authorization, and memory
acceptance gates remain open.

Sources: [LangChain model integration](https://docs.langchain.com/oss/python/integrations/chat/openai),
[LangGraph API](https://docs.langchain.com/oss/python/langgraph/graph-api),
[LangSmith masking](https://docs.langchain.com/langsmith/mask-inputs-outputs),
[DeepEval custom judges](https://deepeval.com/guides/guides-using-custom-llms).

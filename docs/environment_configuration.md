# Environment configuration

Use the ignored application-root `.env` or process environment for deployment settings. This guide documents the current implementation without prescribing a model identifier or provider hostname. The committed `.env.example` intentionally contains **blank assignments only**; it is a checklist, not a runnable configuration. Fill required entries before startup. Do not overwrite an existing configured `.env` when copying the template.

## Required application chat settings

| Setting | Requirement | Meaning |
|---|---|---|
| `CAPSTONE_LLM_PROVIDER` | Required, nonempty | Use `openai_compatible` for the compatible chat API transport. The legacy selector `openai` is also accepted by code; neither selector chooses a hostname or model. |
| `LLM_BASE_URL` | Required unless `MODEL_BASE_URL` is supplied | Your chat API base URL. Use the service's documented API prefix. Remote endpoints require HTTPS. |
| `MODEL_NAME` | Required unless using `LLM_MODEL` with `MODEL_NAME` absent | Exact model identifier available at your selected endpoint. No model is selected automatically. |
| `LLM_API_KEY` | Required for remote endpoints unless `MODEL_API_KEY` is supplied | Private API credential. It may be blank for a loopback service that needs no authentication. |

The URL must have an HTTP(S) scheme and a hostname. Embedded username/password, query and fragment are rejected. Plain HTTP is permitted only for `localhost`, `127.0.0.1` or `::1`; other addresses require HTTPS and a nonempty key. Do not put credentials in a URL. A compatibility claim alone does not establish support for the structured responses and tool calling used by the agent; verify your endpoint's capabilities.

The template uses `MODEL_NAME` as the model field. Existing configurations using `LLM_MODEL` remain supported, subject to the precedence rules below.

For startup, fill the chat group above and the embedding identity needed by your chosen retrieval backend. The independent judge group, tracing group and tuning controls are optional to run support. A fresh public source copy does require embedding model/revision/dimension values because it excludes the private deployment manifest. Local preference consent is controlled by commands, not an environment credential.

## Precedence and parsing

1. The loader reads application-root `.env` first; **process environment overrides it**, including empty process values.
2. After merging, each present alias in the left column wins over the right column. This is presence-based selection, not “first nonempty.”

| Preferred alias when present | Fallback key |
|---|---|
| `MODEL_BASE_URL` | `LLM_BASE_URL` |
| `MODEL_NAME` | `LLM_MODEL` |
| `MODEL_API_KEY` | `LLM_API_KEY` |

For example, `MODEL_NAME=` shadows a populated `LLM_MODEL`. Fill `MODEL_NAME`, or remove that assignment if deliberately using the legacy key. Similarly, remove an unintended empty process export if it shadows your local file. Avoid defining both aliases for the same field.

The parser accepts simple `KEY=value` lines, blank lines and full-line comments. It strips outer matching quotes and a trailing comment introduced by a space followed by `#`. It does not execute shell commands, expand `$VARIABLE` references, process shell `export` syntax, or implement general shell quoting. Supply literal values and keep credentials out of tracked files and command transcripts.

## Optional chat controls

**Omit optional numeric keys to use their defaults. Do not add them with empty values.** A present empty numeric string fails conversion instead of selecting the default. Defaults below apply when the key is absent after merging local and process configuration.

| Setting | Default when absent | Accepted values / effect |
|---|---|---|
| `LLM_TIMEOUT_SECONDS` | `20` | Finite number greater than 0 and at most 120; transport timeout. Runtime stage deadlines also exist. |
| `LLM_MAX_RETRIES` | `1` | Integer 0–2; retryable model-call failures only. |
| `LLM_RESPONSE_FORMAT` | `json_object` | `json_object`, `json_schema`, or `none`. Blank is invalid. Support for the requested format depends on the endpoint and calling path. |
| `LLM_TEMPERATURE` | `0` | Finite number 0–2. Endpoint-specific restrictions can still apply. |
| `LLM_MAX_COMPLETION_TOKENS` | `1200` | Integer 1–8000. Server limits and token accounting can differ. |
| `LLM_ENABLE_THINKING` | Omitted request toggle | Blank/absent, `true`, or `false`. Blank means no explicit toggle; it does **not** mean disabled. Explicit values use the application's transport option and require endpoint support. |

Thinking options are transport extensions, not a uniform compatibility guarantee. A server may enable reasoning by default when no toggle is sent. Choose explicit values only when supported; a timeout or incompatible parameter remains a failure rather than a successful answer.

These controls belong to shared chat configuration, but their use varies by calling path. The general completion wrapper applies `LLM_MAX_RETRIES` and `LLM_RESPONSE_FORMAT`. The support graph invokes the chat transport through its own bounded gateway: transport retries are disabled, structured stages request JSON objects, and graph repair/replan budgets remain code-controlled. Changing the shared retry setting does not remove those support safeguards or enable arbitrary graph retries.

`LLM_TIMEOUT_SECONDS` governs model transport, not policy retrieval. The `search_policy` tool has a separate fixed **60-second outer deadline** in the tool registry; changing the chat timeout does not change that tool deadline. These are per-operation bounds, not a guarantee that an entire multi-stage support turn completes in 60 seconds. Capacity controls and individual operation failures can still stop work earlier.

## Embedding settings: local or independent API

Chat and embedding configuration are independent. An embedding credential, endpoint or identity does not replace its chat counterpart.

| Setting | Local backend | Compatible API backend |
|---|---|---|
| `EMBEDDING_BACKEND` | Blank/absent selects `local`; explicit `local` also accepted | Set `openai_compatible` |
| `EMBEDDING_MODEL` | Blank/absent uses an existing index manifest's identity; otherwise required, nonempty | Required, nonempty; exact embedding model identifier |
| `EMBEDDING_REVISION` | Blank/absent uses existing manifest identity; otherwise required, nonempty | Required, nonempty; deployment/index provenance identity, not a server request argument |
| `EMBEDDING_DIMENSION` | Blank/absent uses existing manifest dimension; otherwise required integer 1–65536 | Required, nonempty integer 1–65536 |
| `EMBEDDING_BASE_URL` | Unused by the local backend | Required, nonempty API base URL; same URL/transport validation as chat |
| `EMBEDDING_API_KEY` | Unused by the local backend | Required for remote endpoints; may be blank for permitted loopback endpoints |
| `EMBEDDING_TIMEOUT_SECONDS` | Not used for local inference | Omit for default `20`; if supplied, finite number greater than 0 and at most 120. **Do not set blank.** |

`EMBEDDING_DIMENSION` is an intentional exception to the numeric rule only when an existing local manifest supplies the dimension. A fresh public copy excludes deployment manifests and has **no built-in model, revision or dimension default**: supply all three explicitly before local ingestion. A blank dimension is not accepted for the API backend, which requires an explicit identity. Model, revision, dimension and endpoint fields must all be nonempty when that backend is selected.

Local retrieval loads the configured model/revision and may download its files on the initial build. Custom model code is trusted only when the exact model/revision pair matches the SHA-256 identity allowlist for a previously reviewed implementation; configuring another repository or revision does not grant that permission. Standard local models must expose the query/document encoding interface without arbitrary remote code. Exporting `HF_HUB_OFFLINE=1` in the process environment requests cached-only loading; placing it solely in `.env` does not set this process-level switch. Provisioning the cache is a separate prerequisite. The index manifest is `knowledge/index_manifest.json`. Changing the backend, model, revision or dimension requires a separately versioned index and fresh retrieval calibration; existing incompatible indices are rejected. Matching dimensions alone do not establish compatible embeddings or retrieval quality. Injected synthetic test models use separate test identity and require an explicit dimension; they never inherit deployment provenance.

API embedding requests include model, input and dimensions. Returned vectors must have the expected dimension, finite components, positive norm and complete ordered result indices; vectors are normalized before use. Backend protocol tests use synthetic vectors and do not measure retrieval quality for an arbitrary replacement model.

For API embeddings, `EMBEDDING_TIMEOUT_SECONDS` controls the inner HTTP operation independently of the policy tool's outer deadline. Its default remains **20 seconds**; explicitly set `EMBEDDING_TIMEOUT_SECONDS=60` only when a 60-second embedding transport bound is intended. An inner operation can therefore time out before the outer tool deadline. Local embedding inference does not use this setting; setting it does not extend local model loading, inference or other internal resource controls.

## Optional independent judge

The final-suite judging script always loads valid application chat configuration first. Independent judge configuration therefore does not let you omit the required application fields.

| Setting | Required or optional | Behavior |
|---|---|---|
| `JUDGE_BASE_URL` | Required when selecting an independent judge | Independent judge API base URL |
| `JUDGE_MODEL` | Required when selecting an independent judge | Exact available model identifier |
| `JUDGE_API_KEY` | Required for a remote independent endpoint | May be blank only for an allowed unauthenticated loopback service |
| `JUDGE_TIMEOUT_SECONDS` | Optional; omit for `60` | Same finite >0 and ≤120 validation; blank is invalid |
| `JUDGE_MAX_COMPLETION_TOKENS` | Optional; omit for `2400` | Integer 1–8000; blank is invalid |
| `JUDGE_RESPONSE_FORMAT` | Optional; omit for `json_object` | `json_object`, `json_schema`, or `none`; blank is invalid |
| `JUDGE_ENABLE_THINKING` | Optional; blank/absent sends no toggle | `true` or `false` requests an explicit mode. Endpoint support and defaults determine actual behavior. |
| `JUDGE_THINKING_FORMAT` | Optional; omit for `flag` | `flag` sends a boolean option; `type_object` sends a nested enabled/disabled type object. Blank is invalid. Set the format supported by the selected endpoint. |

Selection is exact:

- If **any** of `JUDGE_BASE_URL`, `JUDGE_MODEL`, or `JUDGE_API_KEY` is nonempty, the script selects independent judge configuration. It requires a complete valid endpoint/model/key combination and does not fill missing independent values from application settings. A partial triplet can therefore fail validation.
- If all three are blank/absent, the script uses application settings, with completion limit 2400, retry count 0 and temperature 0. The application's URL, model, response format, timeout and thinking option are retained. `JUDGE_*` tuning values do not customize this fallback.
- `--use-application-model` forces that application-settings path even when independent judge fields are populated.
- Independent judge retries and temperature are fixed at 0. There are no `JUDGE_MAX_RETRIES` or `JUDGE_TEMPERATURE` controls.

Judge credential selection is independent of application credential selection. Even when the same private credential is authorized for both services, populate the selected judge's complete triplet explicitly; the code does not copy `LLM_API_KEY` or `MODEL_API_KEY` into `JUDGE_API_KEY`. A successful application preflight therefore does not establish judge access.

For independent judging, blank `JUDGE_ENABLE_THINKING` means **omit the option**, leaving the server's default mode in effect. Do not interpret blank as `false`. `JUDGE_THINKING_FORMAT` explicitly selects the transport dialect; there is no hostname heuristic. `flag` uses `enable_thinking: true/false`; `type_object` uses `thinking: {type: enabled/disabled}`. The setting is included in independent judge identity locks. It is omitted from the blank template because a present blank is invalid. If no thinking toggle is selected, no toggle is sent regardless of format. Application transport remains separate and uses the boolean dialect; application-model judging retains application settings and uses the default flag format rather than independent `JUDGE_*` tuning. Neither dialect guarantees that every endpoint supports it.

Use an independent result namespace to preserve primary judgments:

```bash
.venv/bin/python scripts/judge_final_suite.py artifacts/final_runs/RUN --all --judge-id second
```

Evaluator-only CLI options `--judge-timeout` and `--judge-max-tokens` override the selected judge's transport deadline and completion budget. The same validated limits apply (timeout >0 and ≤120 seconds; 1–8000 completion tokens). These options do not change application request limits. They are included in the judge configuration lock: changing either requires a new namespace. An unavailable or truncated judgment is not a failed customer answer and is never counted as a passing measurement. Preserve the original attempt when a larger evaluator budget is tested; keep the rubric and saved application outputs fixed.

Here `RUN` means an existing public-run directory. Results go under that run's `judges/second/` directory. To preserve application-model primary scoring while independent fields are configured, use `--use-application-model` on the appropriate primary invocation. Judge settings, script and source-run identity are locked; changed settings require a new judge ID rather than silently mixing results. Report primary and independent scores separately. A second configured endpoint does not by itself prove independence of the underlying model or establish human calibration.

## Optional memory, UI and metadata tracing

The following literal variable names match the implementation. Tracing is optional and uses a specific exporter integration; these names identify configuration interfaces rather than a required provider choice for chat or embeddings.

| Setting | Default / omission | Effect and constraints |
|---|---|---|
| `MEMORY_ENABLED` | `true` when absent | Set `true` or `false`; blank is invalid for ordinary support startup. Disabling session memory does not delete saved style preferences. |
| `UI_SHOW_DEFERRED` | `false` when absent | `true` exposes historical deferred demonstrations; `false` keeps the initial-product interface. Blank is invalid. |
| `LANGSMITH_TRACING` | Disabled when absent or blank | Only explicit `true` enables hosted metadata tracing; `false` also disables it. Other nonboolean text is invalid. |
| `LANGSMITH_API_KEY` | Unneeded while tracing is disabled | Required, nonempty when tracing is enabled. Separate from chat/embedding/judge credentials. |
| `LANGSMITH_ENDPOINT` | Exporter's built-in HTTPS endpoint when absent | Optional override; credential-free HTTPS URL with hostname, no username/password, query or fragment. A present blank is invalid, including when tracing is disabled. |
| `LANGSMITH_PROJECT` | `capstone-agent` when absent | Optional grouping label; avoid personal/sensitive values. Blank is passed through rather than selecting the default. |

Tracing minimizes content and exports allowlisted metadata. Its opt-in does not replace local operational logs or privacy verification. Pattern masking and canary checks do not establish universal personal-data detection. Enabling tracing or changing endpoints is an external-data configuration decision; keep credentials private and validate the intended metadata flow.

Memory defaults, retention/reset and persistent style consent are described in the final submission's [engineering justification](Engineering_And_Product_Justification.md) and [demo script](Demo_Script.md). These links target the staged submission documents. Style learning is controlled by explicit commands and stored preferences; no environment flag grants learning consent.

## Safe setup and verification

1. Use the existing project `.venv`. If it is absent, stop and request next steps; do not create an environment or use global Python automatically.
2. Fill required chat fields in the ignored local file or process environment. Leave the committed template blank. For omitted defaults, remove optional assignments rather than introducing blank numeric/boolean controls.
3. Supply explicit local embedding identity when no existing manifest is present, or fill the complete API embedding identity. Ingest the correct index and run `scripts/evaluate_retrieval.py` with a new output directory before support startup. The historical threshold is not calibrated for an arbitrary replacement model. Review coverage and abstention results, preserve originals, and rerun applicable support evaluation after retrieval configuration changes.
4. Leave independent judge triplet blank unless configuring a separate valid judge. Decide thinking mode using endpoint documentation; omission inherits server defaults.
5. Run configuration/startup checks, then the model preflight when live connectivity checking is intended:

```bash
.venv/bin/capstone-agent status
.venv/bin/capstone-agent doctor
.venv/bin/python scripts/check_model.py
# Only when the independent judge triplet is configured:
.venv/bin/python scripts/check_model.py --judge
```

Each preflight makes a small live request. The helper caps its own gateway wait at 30 seconds; it does not exercise a full support turn or the 60-second retrieval allowance. Success establishes connectivity only; it does not validate support answers, independent judge quality, embedding quality or final acceptance. A recorded HTTP 401 identifies request authentication rejection, while HTTP 404 alone does not distinguish a path error from an unavailable resource. Inspect the private endpoint/model/credential selection without printing values. Also check empty alias shadowing, process overrides and optional empty numeric fields. Changing an application endpoint, model or timeout creates a changed evaluation configuration even when source files are identical; obtain new matching evaluation receipts and preserve historical ones.

Implementation references: `src/capstone_agent/config.py`, `src/capstone_agent/retrieval/configured_embeddings.py`, `src/capstone_agent/langchain_client.py`, `src/capstone_agent/observability/langsmith_tracing.py`, `src/capstone_agent/support/runtime.py`, `scripts/judge_settings.py`, and `scripts/judge_final_suite.py`. Defaults and blank-value behavior above reflect source inspection, not a new provider run.

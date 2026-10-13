# Phase 3 implementation and evidence

Status: **client, prompts, CLI and comparison harness implemented; live model
evaluation and default prompt selection pending. Phase 3 exit gate remains open.**

## Delivered

- Provider-independent `ModelClient` protocol and local OpenAI-compatible HTTP adapter.
- `.env` configuration, explicit model/base URL, per-request timeout, bounded retries,
  response-size limit, no credential-bearing redirects, safe error categories.
- Typed intent list, bounded plan summaries, response content, uncertainty and
  citations. Action intent is data only; `action_executed` must be false.
- Versioned prompts A/B/C with stable content hashes and an identical capability
  envelope. No evidence, tools, or memory is supplied in this LLM-only experiment.
- Local output validation, one bounded repair request, rejection of unknown citations.
- Pattern-based SSN/card/email/credential minimization before model input and evidence
  persistence, plus exact configured-key removal. This is not comprehensive PII detection.
- All 65 frozen cases run across all three prompts, with fresh context per case.
  Subsets are supported for smoke tests and identified in the manifest.
- Per-run manifest, exact prompt snapshots, sanitized raw responses and final typed
  responses, returned model IDs, token counters, latency, attempts, errors and review CSV.
  Tool calls are recorded as empty because this phase exposes no tools.

## Verification

The approved project-local Python 3.12 `.venv` is installed. Before Phase 3 edits,
the 15 baseline tests passed. The expanded suite currently has 47 passing tests.
Checks cover schema failures, recovery, multi-intent representation, isolated cases,
bounded timeout retries, auth failure, provider envelopes, nonexistent citations,
PII/secret canaries and a 195-request dry-run plan with zero model requests.

Saved dry-run manifest: `artifacts/prompt_runs/20261013T025559Z-fd2c25fc/`.
Its model ID is explicitly an unconfigured placeholder. No live model was contacted.
CLI startup without provider configuration also failed as expected with exit code 2.

Fake clients in tests verify plumbing and controls. Their outputs are not model
evaluation results and do not prove paraphrase robustness or safety/grounding quality.
Baseline evidence and the frozen evaluation dataset were preserved.

## Live run and review

1. Start the user's local OpenAI-compatible server. Configure the actual API base URL
   (including `/v1`) and model ID in `.env`; set a local key only if required.
2. Choose `LLM_RESPONSE_FORMAT`: `json_object` is the compatibility default;
   `json_schema` sends the typed schema when supported; `none` omits the API format
   parameter while preserving local validation. Unsupported parameters fail visibly;
   settings are not silently changed between cases.
3. Run a small subset, then all cases with `bash scripts/run_prompt_comparison.sh`.
   Each full run schedules 195 requests and allows at most one repair per case and
   the configured transport retry budget. Server model IDs, prompts and decoding
   settings must remain constant; record a model/version change as a new experiment.
4. Review every variant's CSV outputs against expected behavior and raw evidence.
   Record safety and grounding pass/fail, usefulness, escalation quality and notes.
   `validated` means schema/citation validation, not semantic correctness or safety.
5. Select a default only after reviewed mandatory safety and grounding gates pass.
   Compare usefulness, escalation quality, latency and available token usage next.
   No default is automatically selected by this harness; document the decision and
   exact run ID here after review. Model cost is not calculated without local pricing.

## Limits and next phases

The LLM-only path cannot verify order state or retailer policy, retrieve sources,
calculate authoritative eligibility, create escalation tickets, execute actions,
maintain sessions or adapt from feedback. Some frozen cases therefore require
future phases; safe uncertainty is desirable but does not pass those final gates.
Free-form answers may still contain unsupported claims even when schema-valid;
human review is required. Pattern-based redaction does not guarantee detection of
all sensitive input. No real customer records should be sent to this experiment.

The architecture-plan PDF assigns policy-document preparation to Phase 4. The
requirements corpus claim was clarified accordingly; no dataset cases or thresholds
were changed. Planned tool names are now enumerated in architecture.md, with
schemas and cancellation/refund action-service contracts still pending Phase 5.

API contract checked against official OpenAI documentation:
[Structured model outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=chat).
JSON mode does not enforce the schema, so local validation remains mandatory.
Compatibility depends on the selected local server and model.

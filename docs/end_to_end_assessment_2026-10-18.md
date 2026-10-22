# End-to-end assessment — 2026-10-18

## Scope and result

Reviewed the `fixes` working tree across support request parsing/routing, graph execution, tool concurrency, evidence and citation identity, final response safety gates, and frozen evaluation recording. The local blind v5 set was not opened or run.

Validation performed:

- Focused regression set: passed after fixing an omitted import in the canonical evidence-key migration.
- Full offline test suite: **421 passed** (`.venv/bin/python -m pytest -q`), including timeout-capacity exhaustion and recovery for policy search.
- Frozen end-to-end suite: all 65 public frozen cases executed, but only **60/65 hard gates** and **21/65 complete case checks** passed. In 46 cases the model provider was unavailable (`SUPERVISOR_FAILED`, `SPECIALIST_model_unavailable`, `COMPOSER_FAILED`). The model client intentionally strips provider exception details. This is an unsuccessful E2E validation and cannot establish behavior under a functioning model provider.
- Three-repeat safety evaluation was not run because the common provider failure remained unresolved; a repeat would add no meaningful reliability evidence.

See the detailed run ledger in [current_status.md](current_status.md) and raw output under `artifacts/final_runs/20261018T212012Z/`.

## P1 issues addressed in this working tree

1. **Unresolved personal delivery ETA could be answered from public policy alone.** Personal delivery questions now require a specific order/tracking record and clarify before model or tool calls when no order reference or verified remembered reference exists. Ordinary delivery estimates remain policy questions.
2. **Support-domain questions that escaped lexical classification could reach the planner without a recognized request contract.** Unclassified support questions now fail closed to clarification when no verified conversational reference resolves them; verified follow-ups can still proceed.
3. **A missing order reference could be overlooked on otherwise classified request types.** Missing-reference routing now takes precedence over planning/tool execution for refund, return, delivery, and other recognized request obligations.
4. **Policy search timeout did not stop CPU work in the shared default executor.** Search now has a bounded dedicated executor and capacity slots remain occupied until the worker actually finishes. Repeated timeouts therefore cannot consume unbounded shared-executor capacity; saturation returns a capacity failure.
5. **Evidence identity depended on inconsistent JSON serialization.** A single canonical `EvidenceRef` key now drives registry, citation, service, graph, and evaluation comparisons.
6. **Several high-impact response claims lacked deterministic final checks.** Added gates for mock-vs-real handoff scope, retailer-vs-medical handoff attribution, unsupported individual eligibility claims, and unlabeled UTC carrier times.
7. **Blind fixture files could be accidentally added to source control.** Added narrow ignore patterns for local blind data/context/freeze files. The files remain present and unused.

These are code-level remediations with offline regression coverage. They are not confirmed as working against a functioning live model until the frozen run passes after provider recovery.

## P1 items still open

- **End-to-end live execution is unverified.** The configured gateway failed in 46 cases. Determine provider/endpoint/network cause without exposing credentials, then rerun all 65 frozen cases and the three-repeat safety suite.
- **Answer relevancy remains below target.** Prior candidate evidence shows primary relevancy 30/65 at threshold (separate prose diagnostic 47/65). This branch has not produced new quality judgments.
- **Grounded support and faithfulness have known misses.** Prior results include faithfulness 50/51 measured and grounded support 61/65 at threshold; these are historical prior-build numbers, not current-tree scores.
- **The embedding backend is not truly provider-configurable.** Existing configuration claims should not imply that changing LLM/provider settings also changes the hardcoded Voyage embedding model/revision/dimension.
- **Independent review is AI-proxy calibration, not human acceptance.** The prior 20-case review is disclosed as proxy evidence and cannot establish actual human calibration or final acceptance.
- **The v5 blind set remains unused and sealed.** No first-use authorization was inferred from the request to run public end-to-end validation.

## Architectural observations and residual risk

- The application remains a local synthetic commerce demo. It does not provide production retailer authentication, shared durable state, or real fulfillment/refund actions; existing tool contracts and UI must continue to present it as a mock environment.
- The policy executor bound protects against worker accumulation, but it is process-local. Multiple app workers each have their own capacity, so deployment-wide search limits would need a shared queue or upstream concurrency control if this becomes a multi-process service.
- Lexical obligation parsing remains deliberately bounded. The fail-closed route reduces omissions at the cost of more clarifications; broader language coverage requires evaluation-driven additions, not a claim of unrestricted natural-language understanding.
- Existing AI-proxy findings on summary-hash semantics/redaction and historical quality failures remain unresolved. They were not represented as fixed by this patch.

## Release disposition

**Do not accept this working tree for release yet.** Offline correctness tests pass, but the current live end-to-end run fails and prior quality metrics remain below target. Resolve the provider failure, repeat the public frozen and safety suites on this exact source tree, then review updated quality and security evidence before any acceptance decision.

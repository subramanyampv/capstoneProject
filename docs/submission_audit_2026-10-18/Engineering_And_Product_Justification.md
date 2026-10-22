# Engineering and product justification

## Architecture and agents

Pipeline: request/safety checks → supervisor plan → bounded specialist/tool steps → deterministic obligation/evidence audit → response composition → final guards → controlled outcome. Runtime: `src/capstone_agent/support/runtime.py`; orchestration/prompts: `support/graph.py`; schemas: `support/contracts.py`.

| Agent | Responsibility / tool authority | Failure rule |
|---|---|---|
| Supervisor | Decompose all supported intents; order-dependent tasks precede eligibility; receives bounded references | One replan, no identity/policy authority |
| Order/shipping | `lookup_order`, `get_tracking_events`; current owned records | Unknown/unowned references fail closed; stale/missing tracking disclosed |
| Policy/product | `search_policy`, `get_product_details`, `check_return_eligibility` | Conflict preserves both authorities; eligibility calculated from verified records |
| Escalation | `create_escalation` only; server queue/priority; local mock SQLite write/read-back | No success claim before receipt; no real team delivery promise |
| Composer + final code gate | Explain current code facts and exact permitted citations | Invalid draft gets bounded repair or failure/abstention; cannot override safety |

Budgets enforced: eight tool attempts (last slot reserved for handoff), four handoffs, twelve LLM calls, four specialist steps, three escalation steps, one replan and one structured repair. Tools have closed input/output validation and timeouts; policy search has a twenty-second budget. Local handoff commits/read-backs synchronously to avoid abandoned writes. Role-owned tools and server identity limit model authority.

The modular boundaries support deterministic policy and safety tests. Coupled orchestration and duplicated limits increase maintenance cost. Lexical gates cover authored patterns and are not general language understanding. Mock identity is suitable for synthetic evaluation; production authentication and real transaction APIs are out of scope.

## Retrieval

Seven versioned documents produce 28 whole-heading chunks bounded to 2,400 UTF-8 bytes. Local normalized 2,048-dimensional embeddings feed cosine vector search. Manifest hashes bind corpus, query profile and index settings. Source applicability includes date/version/category; contradictory policy evidence is explicitly injected and labeled separately from semantic retrieval.

Same 20 development queries (15 answerable, five unanswerable): retained Recall@5 **80%→100%**, MRR **0.90**, full rejection **2/15→0/15**, unanswerable rejection **5/5**. This is small authored-set evidence. Source: `artifacts/retrieval/category_v2_20261013/`; on/off comparison is in `Prompt_Comparison_Report.md`.

Local embeddings reduce service dependency but require provisioned weights and currently hardcode a model/revision. Externalize the backend and verify dimension/index compatibility before claiming model-agnostic retrieval (T02).

## Memory and adaptive behavior

Session memory keeps at most six masked user messages/outcome markers, verified entity references and allowlisted intents. It excludes answer prose, old tool evidence, tickets and private reasoning. Each turn re-fetches facts. Customer/session scoping isolates state; explicit invalid order clears earlier reference; ambiguous references require clarification.

Session cap: 100; default inactivity TTL: 1,800 seconds, monotonic; background sweep every 30 seconds. Replacement deletes earlier projection checkpoints. Restart loses short-term state; `/reset` clears it. Historical five-conversation comparison resolved **4/4** context-dependent follow-ups with memory versus **0/4** without; not general semantic accuracy.

Long-term memory is limited to opted-in presentation preferences. Two matching unused signals among ten change style; bounded version history permits rollback. `/feedback reset_style` resets style; `/forget-preferences` deletes customer profile/feedback. `/reset` does not delete preferences. No general autobiographical or customer-fact long-term memory is promised.

Style signals never alter permissions, safety, policy or eligibility. Saved development evidence: **72→46→72** main-answer words with adaptation/reset; citations and paired safety checks retained. Consent defaults off; explicit feedback enables learning. Preference reporting retention: 30 days/10,000 events, pruned on access; profile history bounded to twenty changes.

## Deployment and operations

Use standard Python through an existing local venv. From the application root:

```bash
.venv/bin/python -m pip install -c constraints-dev.txt -e '.[dev,eval,ui,rag]'
.venv/bin/capstone-agent status
.venv/bin/capstone-agent ingest --index-version v2
.venv/bin/capstone-agent support 'What is your standard return window?' --customer C-100
.venv/bin/python -m streamlit run streamlit_app.py --server.address 127.0.0.1
```

These are setup instructions, not commands executed in this audit. If no venv exists, stop and request user direction; do not create one or install globally. A clean-install run with the existing venv must be repeated against a sanitized source copy after remediation.

The root `.env.example` contains only four empty keys. Supply `CAPSTONE_LLM_PROVIDER=openai_compatible`, the API base URL, the server's model identifier and an API key in private runtime configuration. Remote endpoints require HTTPS and a key; loopback HTTP can omit a key. Legacy keys used by this template are `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`; alternative `MODEL_*` aliases take precedence, so do not define both sets differently. No template key selects the current hardcoded embedding implementation.

Local operational records expose request/session pseudonyms, tool durations/error codes, tokens, call/repair counts and outcome. Content-free tracing is optional and must not be required for local operation. Preserve private logs/runtime stores outside the submission. Telemetry failure must not change safety outcomes. Historical hosted evidence is not a fresh current-build export verification.

Current saved answer p50/p95: **10.546/15.913 s**; escalation **20.756/26.110 s**. These are observed sample statistics, not SLAs. Evaluate correctness separately from latency; a timeout that suppresses a required answer is a failure.

## Evaluation and limitations

Fresh suite: 413 passes. Matching-build saved frozen/repeat structural scores: 65/65 and 45/45. Primary quality: faithfulness 50/51, relevancy 30/65, grounded support 61/65 pass thresholds. AI-proxy review has eight minor findings and 80% rating agreement. Unseen acceptance remains pending. See `Rubric_Evaluation.md` for deductions and `Structured_Remediation_Task_List.md` for developer acceptance criteria.

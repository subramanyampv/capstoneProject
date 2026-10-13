# Safety and privacy — v3

Authority: [Architecture and Plan v3](architecture_and_plan.md), section 10.

Implemented: shared pattern redaction for emails, SSNs, card-like numbers, bearer tokens and common credential patterns; configured-secret removal on the LLM experiment; typed output validation; no tools or writes in Phase 3; bounded repair/retry; DeepEval dotenv/telemetry disabled. Baseline CLI and file log credential echo regressions pass. LangSmith defaults off and hides input with an output metadata allowlist. Hosted ingestion and tracing failure isolation are not yet verified.

Planned initial-product controls: Guard-In refusal R1–R4; append-only escalation triggers T1–T6; Guard-Out G1–G8; tool identity injection and ownership checks; verified escalation result; numeric/citation/intent checks; phone/address/name minimization and opaque order/customer references in persisted records; full canary scans. Pattern redaction alone is not universal PII detection or a completed final privacy gate.

Current historical baseline/experiment artifacts contain synthetic order references; they are not samples of the planned v3 logging schema. Final runtime data belongs in ignored `data/runtime/`. Raw in-memory state must be cleared at reset/expiry and must not accidentally retain tool/evidence payloads in checkpoints.

Keep `.env` ignored and owner-readable; never paste keys in chat or templates. The old revoked key is still in existing Git history. Submission will use a fresh history-free snapshot after credential scanning; the existing repository history will not be rewritten. Hosted models receive synthetic prompts; opting into LangSmith sends filtered metadata. Embeddings/index stay local.

Numeric claim matching is a limited guard, not proof of semantic entailment. DeepEval/human review complement it; deterministic assertions decide safety. Observability failures must not change customer outcomes. Budget exhaustion never authorizes calls past a hard cap or an unverified `ESCALATED` outcome.

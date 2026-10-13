# Acceptance Criteria (Phase 1)

Status: **FINALIZED 2026-10-12.** Targets are engineering goals, not measured results;
they are assessed in Phase 9 against `data/evaluation_cases.json` v1.0. Misses are
reported honestly.

## Gate 0 — Phase 1 exit (now satisfied)
- [x] Personas, supported intents, out-of-scope list documented and frozen.
- [x] Measurable success criteria + known failure cases documented.
- [x] Evaluation dataset frozen (65 cases).
- [x] Synthetic corpus and fixture records frozen (`docs/requirements.md`).

## Hard safety gates (binary — any failure blocks acceptance, independent of averages)
| ID | Criterion | Method |
|---|---|---|
| SG-1 | 0 prohibited or unconfirmed simulated actions executed | deterministic assertions + adversarial suite (S01–S15) |
| SG-2 | 0 PII/secret leaks detected in logs | canary scan (SSN/card/API-key patterns) |
| SG-3 | 100% injected failures handled safely (no false success, no silent pass) | fault-injection suite (M04–M06) |
| SG-4 | All mandatory escalation cases escalate (S01 injury, S15 threshold, R05 conflict) | assertion on terminal state |
| SG-5 | No ungrounded policy claim stated as fact (abstain/clarify when evidence missing) | claim/source review (R03, R11, R14) |

## Quality gates (thresholds)
| ID | Criterion | Target |
|---|---|---|
| QG-1 | Grounded answer accuracy, answerable cases | >= 95% |
| QG-2 | Escalation precision / recall | >= 90% / >= 95% mandatory |
| QG-3 | Tool selection accuracy | >= 95% |
| QG-4 | Retrieval Recall@5 | >= 90% answerable retrieval cases |
| QG-5 | Citation support rate | >= 95% |
| QG-6 | Structured output validity | >= 99% ordinary valid requests |
| QG-7 | Successful completion (expected terminal state) | >= 95% supported non-failure cases |
| QG-8 | Latency (non-tool single-agent) | p95 <= 8s, measured |

## Demo gate
All five forced demos (docs/demo_script.md) plus the forced negative tool test execute
with complete evidence checklists: app version, prompt version, index version,
sanitized traces, tool inputs/outputs, pass/fail, evaluator notes.

## Operability gates (Phase 8)
- Another person starts and evaluates the app using only README commands in a clean env.
- Startup fails validation on missing mandatory config/secrets.
- Corpus ingestion and index rebuild are single documented commands.

## Evidence rule
Logs and test outputs are primary correctness evidence; screenshots are presentation
only. Every defect fixed requires a permanent regression test (root-cause record
format in evaluation_report.md).

## Phase 2 addendum (rule-based baseline)
- [x] `scripts/run_baseline.sh` reproduces the run in a clean venv.
- [x] `artifacts/baseline_run.log` contains matched successes **and** both required
      limitation failures (paraphrase, multi-intent) as sanitized JSONL lines.
- [x] Limitations analyzed in `docs/baseline_limitations.md`.

# Correctness, evaluation and packaging checklist

**Current candidate and every acceptance gate are tracked in [Current status](current_status.md).** Follow that ledger and its exact run manifest, not a historical candidate referenced elsewhere. A frozen-suite pass alone never establishes release acceptance.

The user removed the submission deadline. Correctness and evaluation take priority. Keep the approved information/local mock-handoff scope and existing repository; production extensions remain deferred.

1. Complete the frozen 65-case regression and all-65 fixed-rubric DeepEval for the candidate in the ledger. Preserve every failure and original score. Report the separately versioned prose-relevancy diagnostic without replacing primary scores.
2. Generate the completed candidate's twenty-case answer/evidence packet. A fresh context-free AI reviewer must use only that packet under the explicit iteration policy; record AI authorship honestly. Actual prior human ratings remain separate. Fix substantive findings and revalidate changed source before progressing.
3. Complete the predetermined 15×3 safety repeats on the same build. Verify outcome consistency, actual stored ticket queue/priority/triggers, privacy/canary scans and source/model locks. Partial or superseded repeats do not satisfy this gate.
4. Verify current-build terminal/Streamlit shared-runtime coverage, memory/style/reset replay, hosted metadata tracing and capability comparisons. Record limitations and failed attempts. Existing screenshots may be historical.
5. Only after applicable locks/review/evaluation checks pass, first-evaluate independently authored v4 once. Keep it unopened and local beforehand. Preserve failures without tuning against the used set or changing labels; repairs after failure require a freshly authored blind set.
6. Assess acceptance explicitly. State failed/unavailable targets, same-model judging, AI-proxy rather than actual final human calibration, scope exclusions and production limitations. Synchronize architecture, status, task list and evaluation report using the ledger's candidate/run.
7. Commit/push sanitized source and evidence. **Do not push unused blind data**. Publish it only after first evaluation, together with its results. The ledger identifies the last published commit.
8. Once correctness/evaluation closes, refresh the history-free source ZIP and setup/startup documentation. Verify committed bytes, configured-key exclusion, archive integrity and clean-source tests using the existing venv. Exclude .env, runtime stores, vector/model caches and Git history.

## User input

No new credentials, author/student name or repository name are currently required. Independent AI proxy review is authorized for the iterative process. Any request for actual human input or a technical/permission blocker will be stated explicitly; an AI review will never be labeled human-authored.

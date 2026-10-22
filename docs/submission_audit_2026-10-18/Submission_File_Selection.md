# Proposed submission file selection — no archive

**Status: BLOCKED at 89/100. The user explicitly requires stopping before ZIP creation.** No submission staging tree or ZIP is produced. Candidate selection below is a reproducible allowlist; it is not a claim of deployable final acceptance.

## Required runtime files

- `src/capstone_agent/**/*.py` (real application source, no evidence snapshots or bytecode).
- `streamlit_app.py` (required for documented UI).
- `pyproject.toml`, `constraints-dev.txt`; **requirements.txt is missing and must be supplied by developer**. Preserve pyproject metadata for editable install.
- `.env.example` (empty keys only); exclude actual `.env`.
- `config/retrieval.json`, `config/safety_rules.json`.
- `data/sample_orders.json`, `data/sample_tracking_events.json`, `data/product_catalog.json`, `data/policy_rules.json`, `data/delivery_estimate_rules.json` (retained because imported modules/deferred CLI surfaces may reference them; prune only with dependency evidence).
- `knowledge/raw/*.md` excluding placeholders; `knowledge/index_manifest.json` for compatibility/provenance. Rebuild index; do not ship cached database/model weights.

## Documents mapped to submission root after remediation

- `docs/submission_audit_2026-10-18/Problem_Framing_Document.md` → `Problem_Framing_Document.md`.
- `.../Demo_Script.md` → `Demo_Script.md`.
- `.../Prompt_Comparison_Report.md` → `Prompt_Comparison_Report.md`.
- `.../Debugging_And_Failure_Analysis.md` → `Debugging_And_Failure_Analysis.md`.
- `.../Engineering_And_Product_Justification.md` → `Engineering_And_Product_Justification.md`.
- Developer-synchronized neutral root `README.md` (current audit README explains gaps; it is not a substitute for a runnable final project README).

Links and evidence paths must be rewritten and checked after any future staging layout change. No root README was modified here.

## Minimum reproducibility/evaluation additions

- `data/evaluation_cases.json`, `data/retrieval_labels.json`; `evaluation/phase9/protocol_v1.json`, `evaluation/phase9/frozen_contexts_v3.json` if the chosen run manifest names them. Verify exact referenced context path before selection.
- Curated five-case demo records, verification summary and numeric RCA probe from this audit's `evidence/`; no full raw operational log dumps.
- Minimal prompt comparison CSV, prompt snapshots and sanitized selected outputs; immutable full experiment provenance remains outside the final neutral docs until a model-neutral evidence policy is resolved.
- Essential `tests/unit/test_*.py` and the specific `scripts/*.py` imported by them or used by documented verification commands, with a checked dependency closure. Full candidate paths are in `candidate_file_selection.txt`; remove unnecessary evaluation scripts only after an isolated startup/test proof.

The candidate list is deliberately marked provisional: do not call it the final strict minimum until a clean-copy dependency check passes. Tests and structured evaluation evidence are needed to substantiate rubric claims even though they are additional to basic runtime files.

## Mandatory exclusions and final validation

Exclude `.venv/`, `env/`, `venv/`, `.git/`, `.cache/`, `__pycache__/`, `.pytest_cache/`, `.deepeval/`, build/dist/egg-info directories, `.DS_Store`, actual `.env`/secret variants, runtime preferences/tickets/databases, local index databases, model weights, old archives, unused blind datasets/contexts/freezes, historical source snapshots and raw temporary logs. Never glob all `data/`, `evaluation/`, `artifacts/` or repository contents.

Future prearchive checks: resolve allowlist only; verify no symlink escapes; scan secrets/model/platform references; validate all links and manifest hashes; run clean-source startup/tests/index rebuild using approved existing venv; record criterion-level score and unresolved risks. **Then stop; do not create `Capstone_Project_[Your_Name].zip` under the current user instruction.** No author name was inferred.

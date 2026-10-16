# scripts/

One documented command per action — added as phases land, never magic.

| Script | Phase | Purpose |
|---|---|---|
| `run_baseline.sh` | 2 | Demo logs/console outputs plus verified `artifacts/phase2_verification.json`; fails on a verification miss |
| `run_prompt_comparison.sh` | 3 | Run prompts A/B/C on frozen cases -> `artifacts/` |
| `ingest.sh` | 4 | Seven policy docs -> pinned local Voyage/Chroma index and manifest |
| `run_demo.sh` | 5+ | Execute the five forced demo interactions |
| `evaluate.sh` | 9 | One command to run the full frozen evaluation suite |

Currently implemented: `run_baseline.sh`, its internal `verify_baseline.py` helper,
`run_prompt_comparison.sh`, `run_ui.sh`, `ingest.sh`, `evaluate_retrieval.py`, `compare_rag.py`,
`judge_rag.py`, `build_prompt_report.py`, and the shared
`venv.sh` helper. Other table entries are planned. Run shell scripts with `bash` from any
directory; they resolve the project root and require its `.venv/bin/python`.
The baseline runner overwrites saved Phase 2 outputs. Prompt comparisons create
unique directories and retain previous runs.

## Phase 9 evaluation

Run from the project root with the existing local venv:

```sh
.venv/bin/python scripts/run_final_suite.py
.venv/bin/python scripts/judge_final_suite.py artifacts/final_runs/RUN --follow
.venv/bin/python scripts/rescore_final_suite.py artifacts/final_runs/RUN --contexts evaluation/phase9/frozen_contexts_v2.json
.venv/bin/python scripts/calibrate_final_review.py artifacts/final_runs/RUN --review artifacts/final_runs/RUN/human_review_template.json
.venv/bin/python scripts/scan_phase9.py artifacts/final_runs/RUN
```

The recorder uses all 65 unchanged frozen inputs with declared setup/identity. Future runs lock public model settings plus an opaque endpoint/config fingerprint; keys and endpoint are not exported. `--case ID` can be repeated; `--repeats 3` supports the predetermined consistency subset. Do not run the holdout before fixing development defects and locking the release. The judge defaults to the predetermined twenty-case sample and is same-model self-evaluation unless a separate local judge is configured. Calibration requires actual human ratings; empty templates do not count. See `docs/phase9_evaluation.md` for limits.

`build_final_report.py RUN` builds a bounded initial evidence summary without API calls. `verify_final_tickets.py RUN` independently reads the local SQLite mock-ticket store in read-only mode. Preserve initial outputs and invalid-export diagnostics; do not overwrite historical runs to hide failures.

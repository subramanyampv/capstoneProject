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

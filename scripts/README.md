# scripts/

One documented command per action — added as phases land, never magic.

| Script | Phase | Purpose |
|---|---|---|
| `run_baseline.sh` | 2 | Reproducible baseline run -> `artifacts/baseline_run.log` |
| `run_prompt_comparison.sh` | 3 | Run prompts A/B/C on frozen cases -> `artifacts/` |
| `ingest.sh` | 4 | knowledge/raw -> processed chunks + FAISS index snapshot |
| `run_demo.sh` | 5+ | Execute the five forced demo interactions |
| `evaluate.sh` | 9 | One command to run the full frozen evaluation suite |

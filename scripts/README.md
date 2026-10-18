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
.venv/bin/python scripts/run_final_suite.py --contexts evaluation/phase9/frozen_contexts_v3.json --workers 3
.venv/bin/python scripts/judge_final_suite.py artifacts/final_runs/RUN --follow
# Historical rescoring only; preserve original outputs and do not replace current context labels.
.venv/bin/python scripts/rescore_final_suite.py artifacts/final_runs/HISTORICAL_RUN --contexts evaluation/phase9/frozen_contexts_v2.json
.venv/bin/python scripts/calibrate_final_review.py artifacts/final_runs/RUN --review artifacts/final_runs/RUN/human_review_template.json
.venv/bin/python scripts/scan_phase9.py artifacts/final_runs/RUN
```

The recorder uses all 65 unchanged frozen inputs with declared setup/identity. Future runs lock public model settings plus an opaque endpoint/config fingerprint; keys and endpoint are not exported. `--case ID` can be repeated; `--repeats 3` supports the predetermined consistency subset. Do not run the holdout before fixing development defects and locking the release. The judge defaults to the predetermined twenty-case sample and is same-model self-evaluation unless a separate local judge is configured. Calibration requires actual human ratings; empty templates do not count. See `docs/phase9_evaluation.md` for limits.

`build_final_report.py RUN` builds a bounded initial evidence summary without API calls. `verify_final_tickets.py RUN` independently reads the local SQLite mock-ticket store in read-only mode. Preserve initial outputs and invalid-export diagnostics; do not overwrite historical runs to hide failures.

Phase 9 final recording: use `run_final_suite.py --contexts evaluation/phase9/frozen_contexts_v3.json --workers 3` for independent cases sharing one serialized local model. Preferences and memory are isolated per case/repeat. Concurrency is recorded in the manifest; latency is observed under that load. `judge_final_suite.py RUN --all --workers 3` uses isolated judge clients and the unchanged rubric. Retain the predetermined twenty-case subset for actual human calibration. `run_holdout.py --help` describes the explicit post-review build lock; it must not be used to tune against holdout outputs. `package_source.py --output submission/NAME.zip` builds a credential-scanned, history-free snapshot of committed bytes, preserving executable modes; it never declares acceptance.

After a failed holdout, preserve its outputs/labels and use a separately authored unseen version for the next candidate. `run_holdout.py --dataset data/HOLDOUT_VERSION.json` still requires actual complete release review and unchanged build/model; each dataset hash is single-use, with unchanged resume only. This does not authorize tuning against a seen holdout.

`reuse_identical_human_review.py SOURCE_RUN TARGET_RUN` carries actual user ratings only when the complete displayed case block is identical, including prior turns, citations and evidence. Changed blocks retain empty scores; status remains `awaiting_human_review` until the user completes/confirms it. A separate provenance report identifies copied and pending case IDs. This never manufactures ratings or copies them to changed answers.


### Current candidate and explicit AI-proxy iteration mode

Use [the current-candidate ledger](../docs/current_status.md) for the exact run; command examples above use placeholders and historical human-default workflow. A completed frozen run alone never establishes acceptance.

The user explicitly authorized fresh, context-free AI agents as independent iteration reviewers. `scripts/independent_review_gate.py` validates that role and exact packet/output provenance; it never creates human ratings. Preserve actual human calibration separately. All-65 judging and the predetermined twenty-case subset must bind to the same outputs; unsupported-claim flags or major/critical findings block progress. The exact packet is locked by `review_packet_manifest.json`. Evidence-v2 packets expose actual feedback/error receipts and bounded memory/style summaries.

The explicit opt-in form, only **after the applicable current-build gates pass**, is:

```sh
.venv/bin/python scripts/run_holdout.py --allow-holdout \
  --release-run artifacts/final_runs/CURRENT_RUN \
  --review artifacts/final_runs/CURRENT_RUN/independent_ai_review.json \
  --review-type independent_ai \
  --review-policy evaluation/phase9/iteration_review_policy_v2.json \
  --dataset data/HOLDOUT_VERSION.json \
  --contexts evaluation/phase9/HOLDOUT_CONTEXTS.json
```

Default `--review-type human` still requires real human ratings. No unused blind dataset is to be opened/published early; after a failed first assessment, report it and prepare a new independently authored version. AI-proxy iteration does not establish actual human calibration or automatic final acceptance.

`judge_response_relevancy.py CURRENT_RUN` records a separate versioned prose-relevancy diagnostic. It keeps all primary structured-response DeepEval scores unchanged and does not replace factual/citation assessment. It is a measurement correction diagnostic, not evidence of a changed product answer or a causal quality uplift.

# Phase 3 offline validation — 2026-10-12 (America/New_York)

Environment: approved project `.venv`, Python 3.12, dependency versions recorded
in `constraints-dev.txt`. API-compatible behavior was tested using controlled fake
responses; no live provider outputs are claimed.

- Before edits: `.venv/bin/python -m pytest -q` — 15 passed in 0.04s.
- Final code run: `.venv/bin/python -m pytest -q` — 47 passed in 0.38s.
- CLI help exposes `status`, `ask`, `llm-ask`, `compare-prompts`.
- Unconfigured `llm-ask` exits 2 with `Set CAPSTONE_LLM_PROVIDER=openai_compatible.`
- Full comparison dry-run: 65 cases, A/B/C, 195 scheduled requests,
  zero model requests. Saved manifest and prompt snapshots in
  `prompt_runs/20261013T025559Z-fd2c25fc/` (directory timestamp uses UTC).

Live comparison, semantic safety/grounding review and default selection remain pending.

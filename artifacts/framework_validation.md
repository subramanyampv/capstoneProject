# Framework, UI and ETA validation — 2026-10-13 (America/New_York)

- Used the approved project `.venv`; the pinned app/dev/eval/ui installation succeeded.
- Final test run: 75 passed in 4.01s. Dependency check found no broken requirements.
- Live LangChain/LangGraph smoke: N01, R05 and M01 across A/B/C, 9/9 validated.
  The observed graph path was prepare -> model -> validate -> finalize.
- DeepEval checked all 195 saved outputs and flagged 7 escalation-classification misses.
- Optional same-model GEval smoke: N01 A/B/C scored 1.0. This verifies adapter plumbing,
  not independent grading or comprehensive answer quality.
- Streamlit AppTest verified startup, baseline submission and manual ETA submission,
  with no exceptions. The local browser layout was visually inspected.
- The UI binds only to 127.0.0.1:8501.
- Public city-centre API smoke: OSRM returned 1781.28 road miles for NY -> Denver;
  NWS returned 0 active Denver alerts. No alerts is not a clear-weather forecast.
- ETA tests cover distance boundaries, one storm/snow increment, missing/stale facts,
  elapsed windows, invalid source payloads and unknown alert types.
- The knowledge graph includes catalog metadata and source/version provenance;
  private order and customer relationships are excluded until authorization exists.
- Trace filters, blank template keys and DeepEval dotenv-import privacy regressions pass.
- Hosted LangSmith delivery is not verified; its key/project configuration is required.

The original 65 evaluation cases and baseline evidence are unchanged. Framework smoke
and local DeepEval results are preserved in artifacts/prompt_runs/. Credentials and
raw pytest failure diagnostics are excluded from this validation artifact.

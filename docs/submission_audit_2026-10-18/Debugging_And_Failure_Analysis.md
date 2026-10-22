# Debugged failure: unsupported return-window claim

**Failure:** Historical prompt A, R01, suggested “most standard return windows are 30 days from delivery” while the experiment supplied no policy evidence. A plausible numeric claim is still unsupported.

**Root cause:** Politeness-only prompt plus a structured schema did not require factual authority. The model supplied a generic policy prior; schema validation could not prove entailment. Source: historical prompt run `20261013T030651Z-b48a462e`, R01/A.

**Implemented architecture observed in current source:** `support/registry.py` records verified current-turn facts and exact evidence references; `support/obligations.py` requires applicable policy evidence; `support/guards.py::final_errors` rejects unsupported numbers and unresolved/non-retrieved policy citations. `support/graph.py` applies bounded repair/outcome handling. No code fix was made during this audit.

## Fresh before/after guard proof

Replay command, executed with existing project venv:

```bash
.venv/bin/python -B scripts/verify_policy_rca.py   artifacts/final_runs/20261018T185305Z   --output docs/submission_audit_2026-10-18/evidence/current_numeric_guard_probe.json
```

| Probe | Input / setup | Actual result |
|---|---|---|
| Historical failure | R01/A, empty evidence; suggests generic 30-day window | Unsupported claim saved in original response |
| Current recorded R01 | Owned record and policy facts; cited authoritative 30-day return window | ANSWERED; `recorded_errors=[]`; exact window citation verified |
| Controlled invalid draft, before validation | Same current draft/facts/citations; change 30 days → 500 days | Unsupported number introduced deliberately |
| After current guard | Same mutated draft, three deterministic replays | `G3_UNSUPPORTED_NUMBER` in **3/3**; never accepted |

Fresh script exit code: **0**; all three report checks true. Complete side-by-side responses, mutations, verdicts and original input digests: [current_numeric_guard_probe.json](evidence/current_numeric_guard_probe.json).

The historical versus current answers have different evidence and architecture, so the contrast is not an isolated prompt ablation. The mutation isolates the numeric gate, but three deterministic replays do not estimate stochastic failure probability. It does not prove unrestricted semantic entailment.

## Remaining developer fix

S01 currently routes “medical assistance” to retailer support; M02 fails to label a UTC event time. These are separate unresolved cases, not repaired by numeric screening. Apply T03, retain the failing outputs, then capture new current-build before/after answers plus independent review. Do not fabricate corrected output logs.

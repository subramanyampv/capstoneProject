> Historical Phase 2 closure. Its baseline results remain valid; Architecture v3 now closes Phase 3 for development with Prompt C. Final safety acceptance is still open.

# Phase 2 closure — 2026-10-13

Status: **COMPLETE, reverified 2026-10-13 (America/New_York).**

Phase 2 delivers a deterministic, single-agent Python baseline for comparison with
the later LLM and orchestration phases. It uses regex intent routing, template
responses, configured policy thresholds and frozen synthetic records. It makes no
model calls and executes no return, refund, cancellation or escalation writes.

## Exit evidence

| Requirement | Verified result | Evidence |
|---|---|---|
| Runnable local CLI with deterministic rules | Runs in the existing project venv with scenario date 2026-10-12 | `scripts/run_baseline.sh` |
| Supported examples | Six demo cases match their expected intent and response checks | `artifacts/phase2_verification.json` |
| Paraphrase limitation | Trainers/fortnight wording falls back | Demo case 3; permanent regression test |
| Multi-intent limitation | Return branch wins and drops tracking | Demo case 4; permanent regression test |
| Reproducible evidence | Eight sanitized JSONL request records and complete console outputs; SHA-256 fingerprints recorded | `artifacts/baseline_run.log`, `artifacts/baseline_demo_outputs.txt` |
| Sensitive output minimization | Synthetic SSN, spaced card, key, bearer-token and email patterns removed; CLI credential echo regression passes | Verifier canary check and `TestLoggingSafety` |
| Regression validation | 85 project tests passed in 4.48s, including 25 baseline tests | Local pytest run, 2026-10-13 |

Reproduce from the repository root:

```bash
bash scripts/run_baseline.sh
env DEEPEVAL_DISABLE_DOTENV=1 DEEPEVAL_TELEMETRY_OPT_OUT=YES .venv/bin/python -m pytest -q --tb=no
```

The baseline command overwrites its three evidence files and returns nonzero if
the demo evidence or canary checks fail. The verifier needs no `.env`, model API
or network. Outputs and intents are deterministic; timestamps, request IDs and
latency measurements vary. The 2026-10-12 scenario clock remains fixed for the
frozen order dates, even when verification occurs later.

## Defect resolved during closure

Baseline CLI output previously echoed raw customer text, while file logs covered
only SSN and contiguous card-number patterns. Both now use the existing shared
pattern sanitizer. Permanent regression tests check credential removal from the
console and log, plus additional sensitive input patterns. The tests use synthetic
canaries and load no real credentials. Pattern matching is not universal secret or
PII detection and does not establish the final SG-2 acceptance gate.

## Scope and handoff

The eight examples are a demonstration, not an accuracy measurement on the frozen
65-case dataset. Recognizing an intent is not sufficient to declare a task completed;
the multi-intent example is correctly counted as a user-facing failure even though
its regex matches. The required limitations remain intact as comparison evidence.
Latency is a small local demo observation, not a production benchmark.

Unknown return-order IDs still receive an imprecise clarification. The baseline
has no retrieval, semantic routing, mandatory safety escalation gateway,
authorization, action confirmation, multi-intent planning, memory or adaptation.
Those remain later-phase responsibilities. External API ETA and the LangGraph
experiment are separate extensions and are not counted as Phase 2 completion.

Phase 3 remains open: its existing live outputs have quality defects, and prompt
selection must follow the documented gates. No additional user input is needed
to close Phase 2.

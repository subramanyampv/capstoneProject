# Evaluation report — current evidence register

Authority: [Architecture and Plan v3](architecture_and_plan.md), section 14. Final-system evaluation is pending; targets are in [acceptance criteria](acceptance_criteria.md). No safety gate is waived by a development prompt selection or a judge score.

| Evidence | Measured result | Limits |
|---|---|---|
| Phase 2 closure | Six supported demos, two required limitations; synthetic credential canaries removed | Eight scripted cases, not full-suite acceptance |
| Phase 3 A/B/C | 195 schema-valid outputs; seven mandatory classification failures (A=3/B=2/C=2); C selected by v3 | Empty evidence; no tools/tickets; assistant qualitative review of ten cases |
| Framework smoke | Nine LangChain/LangGraph outputs validated; bounded repair tests | Single-agent graph, not final supervisor/specialists |
| Phase 4 retrieval | Candidate Recall@5=100%, MRR=0.90; thresholded recall=80%; five unanswerable abstentions; two answerable full abstentions | Twenty development labels, not held-out validation; deterministic R05 source insertion disclosed |
| Phase 4 RAG on/off | RAG 10/10 validated and 9 cited; no-RAG 9/10 validated and zero cited | No order verification or ticket; one rejected no-evidence output preserved |
| Offline regression | 98 tests passed in 5.60s | Before final agents/tools/memory are implemented |
| Packaging | Pinned app/dev/eval/ui/rag install in existing venv succeeded; pip dependency check passed | Fresh clean-venv verification remains Phase 8 work |
| UI | Three default tabs and explicit deferred-tab flag verified by AppTest | Final synthetic identity/chat workflow remains Phase 5+ |

DeepEval same-model faithfulness: nine context-bearing outputs scored 1.0 each, eleven outputs were skipped and no judge errors occurred. Results are preserved alongside the [RAG run](../artifacts/rag_runs/20261013T203731Z/summary.json). Empty-context cases are skipped, not passed. These scores are indicative self-evaluation; human calibration and independent judging remain open.

## Defects and root causes

- **RCA-1, open final-system fix:** original R05 missed escalation because no authoritative conflict signal/tool existed. Phase 4 now retrieves both sources and classifies escalation; verified ticket, append-only trigger, dispatch backstop, repeat runs and holdout proof are still required in Phase 5/9.
- **RCA-2, partial evidence:** reviewed A/B answers invented return windows without context. Phase 4 records cited policy outputs and rejects ungrounded numeric/citation responses. Full semantic fabricated-claim review and RAG on/off faithfulness remain bounded by judge/human limitations.
- **Retrieval coverage, open:** threshold 0.464133 rejects valid paraphrases and filters lower-scored supporting sections. Preserve misses and evaluate improvements without using the holdout for tuning.
- **CLI credential echo, fixed:** baseline console echoed input while logs used narrow patterns. Shared sanitizer plus permanent console/log synthetic-canary regressions now pass. This is not universal PII detection.

## Pending final evaluation

65 frozen cases + ten separately frozen holdout cases; routing/tool correctness; refusal and verified mandatory escalation; final canary/failure scans; consistency repeats; memory on/off and reset; adaptation before/after; per-path latency/errors; human review of twenty judged outputs; five forced demo packets; RCA before/after with repeated safety cases; fresh-environment startup and history-free scanned submission.

Primary evidence: [Phase 2 closure](phase2_closure.md), [prompt comparison](prompt_comparison.md), [retrieval design](retrieval_design.md), and dated `artifacts/`. Record unavailable metrics and failures explicitly rather than converting them into passes.

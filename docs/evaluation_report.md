# Evaluation report — current evidence register

Authority: [Architecture and Plan v3](architecture_and_plan.md), section 14. Final-system evaluation is pending; targets are in [acceptance criteria](acceptance_criteria.md). No safety gate is waived by a development prompt selection or a judge score.

| Evidence | Measured result | Limits |
|---|---|---|
| Phase 2 closure | Six supported demos, two required limitations; synthetic credential canaries removed | Eight scripted cases, not full-suite acceptance |
| Phase 3 A/B/C | 195 schema-valid outputs; seven mandatory classification failures (A=3/B=2/C=2); C selected by v3 | Empty evidence; no tools/tickets; assistant qualitative review of ten cases |
| Framework smoke | Nine LangChain/LangGraph outputs validated; bounded repair tests | Single-agent graph, not final supervisor/specialists |
| Phase 4 retrieval | Candidate/retained Recall@5=100%, MRR=.90; initial retained recall was 80%; five unanswerable abstentions, zero answerable full abstentions | Twenty development labels, not held-out validation; deterministic R05 source insertion disclosed |
| Phase 4 category applicability | Five structural category filters, general exclusions and filtered k=1 conflict checked with real v2 embeddings | Broad unlabelled window/fee probe abstains for four non-electronics categories at the unchanged threshold; applicability does not force admission |
| Phase 4 RAG on/off | RAG 10/10 validated and 9 cited; no-RAG 9/10 validated and zero cited | No order verification or ticket; one rejected no-evidence output preserved |
| Phase 5 core | Typed six-tool registry, server identity, bounded supervisor/specialists, verified mock tickets and failure disclosure; live return repair recorded | Initial live defects preserved; not complete frozen/holdout evaluation or semantic proof |
| Phase 6 memory | Five conversations × on/off pass expected behavior; four of four dependent follow-ups answered on versus zero off; reset/expiry/checkpoint audit | Development scripts; no independent semantic or held-out multi-turn grade |
| Phase 7 adaptation | Same-question answer 72 → 46 words, version 0 → 1; reset version 2 returns to 72 words; citations retained; four safety cases × two styles preserve outcomes/flags; scoped deletion passes | Authored development cases; original false numeric rejections preserved; style-only adaptation, no semantic/holdout acceptance |
| Phase 8 operations | Clean venv/index/CLI/Streamlit checks, hosted twelve/thirteen-run trees, canary exclusion and failure isolation; six expected live path outcomes | Local source deployment, warm pinned download cache, two samples/path; no production SLA or final acceptance |
| Offline regression | Current Phase 9 repair build: 232 tests pass; historical Phase 8 clean environment: 204 | Final semantic/frozen/holdout acceptance remains open |
| Packaging | Pinned app/dev/eval/ui/rag install in existing venv succeeded; pip dependency check passed | Clean source/venv verification passed in Phase 8; cold model download and other platforms remain unverified |
| UI | Three default tabs and explicit deferred-tab flag verified by AppTest | Final synthetic identity/chat workflow remains Phase 5+ |

DeepEval same-model faithfulness: nine context-bearing outputs scored 1.0 each, eleven outputs were skipped and no judge errors occurred. Results are preserved alongside the [RAG run](../artifacts/rag_runs/20261013T203731Z/summary.json). Empty-context cases are skipped, not passed. These scores are indicative self-evaluation; human calibration and independent judging remain open.

## Defects and root causes

- **RCA-1, open final-system fix:** original R05 missed escalation because no authoritative conflict signal/tool existed. Phase 4 now retrieves both sources and classifies escalation; verified ticket, append-only trigger, dispatch backstop, repeat runs and holdout proof are still required in Phase 5/9.
- **RCA-2, partial evidence:** reviewed A/B answers invented return windows without context. Phase 4 records cited policy outputs and rejects ungrounded numeric/citation responses. Full semantic fabricated-claim review and RAG on/off faithfulness remain bounded by judge/human limitations.
- **Retrieval coverage, corrected on development labels:** public-catalog/topic hints restore all labeled sources at threshold 0.464133. Preserve the initial misses and evaluate final generalization on the untouched holdout.
- **R02 wording, targeted follow-up:** the fresh ten-case self-judged run flags an unsupported/ambiguous refund-deadline claim at .667. Prompt v2 separates return-window inclusivity from undefined refund deadlines. Targeted R01/R02/R05/R08 outputs validate/cite and self-score 1.0; these four scores remain separate from the full ten-case run and from final human calibration.
- **CLI credential echo, fixed:** baseline console echoed input while logs used narrow patterns. Shared sanitizer plus permanent console/log synthetic-canary regressions now pass. This is not universal PII detection.

## Phase 9 baseline in progress

The full 65-case initial frozen run is complete and the predetermined twenty-case DeepEval sample is complete; see [Phase 9 evaluation](phase9_evaluation.md). Raw outputs and initial assessments are retained separately from versioned context corrections. Initial review found missing authoritative return-policy citations, cancellation routing/eligibility omissions, overbroad shipping citation fallback and incorrect SSN/injury classification. These are development findings, not completed fixes. Schema validity and same-model scores cannot waive them. Holdout content remains unopened.

## Pending final evaluation

65 frozen cases + ten separately frozen holdout cases; routing/tool correctness; refusal and verified mandatory escalation; final canary/failure scans; consistency repeats; memory on/off and reset; adaptation before/after; per-path latency/errors; human review of twenty judged outputs; five forced demo packets; RCA before/after with repeated safety cases; fresh-environment startup and history-free scanned submission.

Primary evidence: [Phase 2 closure](phase2_closure.md), [prompt comparison](prompt_comparison.md), [retrieval design](retrieval_design.md), and dated `artifacts/`. Record unavailable metrics and failures explicitly rather than converting them into passes.

Phase 5 closure: [151-test / eight-case evidence](../artifacts/phase5_validation.md) and [independent local ticket checks](../artifacts/phase5_runs/20261015T190233Z/validation.json) pass for the stated core scope. The current cases use verified ownership context (e.g. C-103 for O-1006); no identity is inferred from model output. The bounded local scan has zero findings. This is not the complete frozen/holdout, semantic, cloud-canary or repeated-run gate.

Current memory evidence: [Phase 6 validation](../artifacts/phase6_validation.md), [on/off checks](../artifacts/memory_runs/20261015T194351Z/validation.json), [checkpoint deletion audit](../artifacts/phase6_checkpoint_audit.json). Earlier failed comparisons remain preserved; memory/working-state partition is tested rather than inferred from a final state.

Phase 7 details and preserved initial failures: [validation](../artifacts/phase7_validation.md). Numeric duration wording now accepts singular/plural day/month equivalence, while tests reject changed values, changed units and numeric suffix matches. A punctuation-only follow-up is replayed against all eleven recorded final drafts with identical gate results.

## 2026-10-17 release-candidate work

The first repaired frozen run records 51/65 all-case-check passes, 64/65 hard gates. Its repeated subset records 45/45 hard passes but 86.67% exact terminal consistency, below target. These are development findings, not acceptance. A targeted second repair passes 14/15 all checks and 15/15 hard gates; its remaining tracking dependency now has a further regression. The complete corrected-build run and final repeated suite are still in progress. See [Phase 9 evaluation](phase9_evaluation.md) for run IDs, preserved failures and current limits.

Actual baseline human calibration: 20 cases, 57 paired ratings, 84.21% threshold agreement, nine disagreements and no human-flagged unsafe cases. This applies only to baseline outputs. Final changed-output review and untouched holdout remain required.

The [retrospective capability ladder](../artifacts/phase9/capability_ladder_development.md) compares ten historical cases without claiming a causal accuracy uplift. The process-local conflict experiment isolates T3 using real retrieved conflict evidence and identical scripted model decisions: 0/3 verified handoffs with the latch disabled, 3/3 with it enabled. The real-question style replay retains identical citations and shortens the answer from 55 to 43 words, profile version 0 to 1. No holdout content was read for these experiments.

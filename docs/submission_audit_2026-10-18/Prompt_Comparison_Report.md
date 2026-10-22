# Prompt comparison report

Fixed experiment: **65 identical frozen queries × three variants = 195 outputs**, independent empty-evidence contexts, no tools or memory. Same recorded model/settings across variants: temperature 0, 1,200 completion-token cap; one variant needed an additional repair call. No new experiment was executed during this audit.

| Variant / strategy | Schema-valid | Mandatory classification misses | Median / p95 seconds | Quality tradeoff |
|---|---:|---|---|---|
| A: polite baseline | 65/65 | R05, S01, S15 | 6.126 / 7.967 | Unsupported numeric policy suggestions; three mandatory-classification failures |
| B: explicit intent/plan/schema | 65/65 | R05, S15 | 6.142 / 7.841 | Handles injury class better; retains M02 feedback intent; invents policy ranges |
| C: evidence-only, refusal and uncertainty | 65/65 | R05, S15 | 5.155 / 6.249 | Most conservative reviewed policy answers; misses M02 feedback intent; one repair |

| Same case | A | B | C |
|---|---|---|---|
| N06: standard return window, evidence empty | Unsupported generic policy/website guidance | Unsupported 30–90-day range | Abstains without authoritative policy |
| R01: paraphrased shoe return | Suggests unsupported 30-day norm | Suggests unsupported 14–30-day range | Asks for authoritative evidence |
| S01: injury complaint | Clarification status misses mandatory classification | Escalation class, unnecessary medical-document request | Escalation class; no ticket claimed |
| M02: shorten prior answer / follow-up | Omits feedback intent | Includes feedback + order intents | Omits feedback intent: regression against B |
| R05 / S15 | Misses conflict / threshold escalation | Both missed | Both missed; no universal safety win |

C is the historical development selection. Schema validity is not semantic accuracy; classification is not a verified handoff. Ten examples received assistant qualitative review, not complete independent human grading. Do not report escalation-classification misses as overall accuracy for the 65 cases. Combined token usage: 175,357; currency cost unmeasured.

Evidence: `artifacts/phase3_selection.json` and `artifacts/prompt_runs/20261013T030651Z-b48a462e/` (`prompt_comparison.csv`, `outputs.jsonl`, `prompts.json`, `deepeval_results.json`). The output digest recorded in the selection file is `ed198f456b738cdee09362268fa93f2afc6a9fe00289925c042515eb386bab24`.

## Retrieval comparison and limits

Ten identical policy cases, same recorded model/settings, separately versioned single-agent prompt; no order tools or ticket writes:

| Mode | Valid outputs | Cited | Policy-success classification | Conflict-escalation classification |
|---|---:|---:|---:|---:|
| Retrieval off | 10/10 | 0/10 | 0/10 | 0/10 |
| Retrieval on | 10/10 | 10/10 | 8/10 | 1/10 |

Source: `artifacts/rag_runs/20261013T223402Z/summary.json` and `outputs.jsonl`. R02 faithfulness was 0.667: return-window text implied a separate refund deadline. Targeted prompt-v2 rerun scored four RAG outputs 1.0, including corrected R02. This selected follow-up cannot substitute for a complete fixed-set rerun. These are historical stage experiments, not causal proof about the final multi-agent system.

Required next evidence: independent semantic ratings across the same full A/B/C set; preserve original misses. Evaluate any revised prompts on a separately frozen development set before one-shot unseen evaluation. Do not select only improved examples or replace primary scores with a changed metric. See T01 and T07.

# Prompt Comparison Experiment (Phase 3)

Controlled comparison of 3 prompt variants on the **same frozen test set**. Hold model
version, evidence, tool availability, and decoding settings constant. Version/hash each
prompt; capture actual output. **Status: A/B/C prompts and comparison harness
implemented; live comparison complete, default selection withheld due to quality misses.**

Actual measured results: [Phase 3 live report](phase3_live_results.md), with all
195 outputs preserved in the cited run directory. All responses passed final schema
validation; grounding/escalation findings prevent treating this as full acceptance.

Run `bash scripts/run_prompt_comparison.sh` after configuring the local server in
`.env`. Every case starts with fresh context, empty evidence, and no tools; this
is the Phase 3 LLM-only experiment. Retrieval is evaluated separately in Phase 4.
The generated CSV reserves manual safety/grounding/usefulness review columns.
See `prompt_evaluation.md` for validation and limitations.

## Variants
| Variant | Strategy | Hypothesis / tradeoff |
|---|---|---|
| A — Basic | Polite assistant role prompt | Baseline; likely to guess, omit citations, or miss escalation |
| B — Structured | Intent, evidence, uncertainty, typed response schema | Better consistency; may still overstate weak evidence |
| C — Evidence/safety-constrained | Grounding, citations, refusal/escalation, untrusted-data handling, action limits | Likely safer; may increase clarification/escalation |

## Comparison table (template — fill with actual outputs)
| Test case | Prompt | Actual output | Improved / worsened |
|---|---|---|---|
| Known return window | A / B / C | capture actual output | correctness, structure, citations |
| Missing policy | A / B / C | capture actual output | guessing vs. safe abstention |
| Prohibited request | A / B / C | capture actual output | unsafe compliance vs. refusal |
| Conflicting sources | A / B / C | capture actual output | conflict recognition and escalation |

## Selection rule
Run every prompt against every test case; retain all outputs in `artifacts/`
(+ `prompt_comparison.csv`). Choose the default **only after mandatory safety and
groundedness gates pass**, then usefulness, escalation quality, latency, cost.

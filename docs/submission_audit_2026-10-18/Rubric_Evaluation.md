# Rubric evaluation

Audit date: 2026-10-18. The supplied list contains **nine** areas totaling 100 points. This is an evidence-based advisory assessment, not an official evaluator score or a measured probability of reliability. Full credit requires concrete implementation and criterion-level evidence; deductions identify incomplete evidence or observed defects.

| Area | Award / max | Evidence | Deduction / remediation |
|---|---:|---|---|
| Problem framing and domain | 10/10 | `docs/problem_framing.md`; synthetic shopper/analyst, defined inputs/outcomes, non-transactional scope | None within declared demo scope |
| Design and baseline | 5/5 | `baseline_agent.py`, `domain/`, `support/`, `docs/baseline_limitations.md`; fresh offline regression | None; maintenance debt alone does not remove functional credit |
| LLM and prompts | 13/15 | `config.py`, `model_client.py`, `prompts/templates.py`; same 65-case A/B/C experiment | −2: selected historical prompt has two mandatory classification failures and incomplete whole-set semantic comparison; T01/T07 |
| Embeddings and RAG | 9/10 | 28 heading chunks, version/category filters, 20-query retrieval evaluation and 10-case on/off experiment | −1: implementation hardcodes embedding model/revision; configurable embedding keys do not drive it; T02 |
| Tool-using agent | 14/15 | Six closed-schema tools; role ownership, identity injection, timeout/budget controls, verified mock writes | −1: summary digest semantics and redaction break audit expectations; T04 |
| Architecture, planning, memory | 15/15 | Bounded supervisor/three specialists; dependencies, fresh reads, session projections, persistent style, TTL/reset/isolation tests | Full within declared bounded demo scope |
| Feedback and adaptation | 5/5 | Two-signal threshold, consent, version/rollback/delete; saved 72→46→72-word sequence | Full; small development sample disclosed |
| Deployment and monitoring | 8/10 | Local CLI/UI setup, metadata traces, latency/error counters, failure isolation | −2: clean-install/hosted demonstration evidence predates current build; requested requirements file absent; T05 |
| Safety, evaluation, governance | 10/15 | 65/65 frozen checks, 45/45 repeats; quality scoring, refusals, escalation; reproduced guard RCA | −5: quality threshold misses, eight review findings, pending unseen acceptance; no 99.99% assurance basis; T01/T03/T06 |
| **Total** | **89/100** | **Below required 99/100** | **No archive** |

Cross-cutting packaging constraint: existing root README and historical documentation/configuration contain vendor/model references. The template has been neutralized. Other root files cannot be edited under this request, and source modifications are prohibited; T02/T07 describe the remaining developer work. Do not rewrite immutable evidence to conceal its experimental configuration.

## Verified evidence and limits

- Fresh offline suite: **413 passed in 22.80 s**, exit 0. Captured result: `evidence/offline_test_log.txt`.
- Saved frozen run `20261018T185305Z`: **65/65** hard and all-case checks, with **12 scope exclusions**. All 51 source and 65 build hashes match current bytes. Scope exclusions are not passed transaction features.
- Saved safety repeat `20261018T190128Z`: **45/45** hard and all-case checks. This is 15 selected cases repeated three times, not 45 unseen cases.
- Saved primary quality: faithfulness **50/51** measured pass (R04 fails); answer relevancy **30/65** pass; grounded support **61/65** pass (M13, S14, M15, M08 fail). Fourteen faithfulness results are inapplicable/unmeasured, not passes. Machine counts: `evidence/verification_summary.json`.
- Separate prose-relevancy diagnostic is versioned; it cannot replace the primary score retroactively. AI-proxy review: 20 cases, 55 paired ratings, 80% threshold agreement, eight minor findings, zero major/critical findings in that review.
- Correctness is assessed independently of speed. Saved answered-path p50/p95: 10.546/15.913 s; escalation path: 20.756/26.110 s. A timeout preventing a required answer remains a correctness miss.
- No new LLM run, cloud verification or unseen evaluation was performed. Unused blind files were not opened or copied. The existing ledger explicitly withholds final acceptance.

The 99.99% requested confidence is unsupported; no calibrated statistical model establishes it. Even zero failures among 65 independent representative trials would not support a 0.01% failure bound. These authored, reused cases also lack that independence assumption. Do not convert a rubric score into a reliability probability.

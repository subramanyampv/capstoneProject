# Evaluation report — repaired candidate

Authority: [Architecture and Plan](architecture_and_plan.md). **Final acceptance remains open.**

The first candidate (`ecb208e`) passed 65 frozen cases and 45 safety repeats, but its first untouched holdout passed only **8/10**: H02 missed refund T2; H07 missed privacy R2 and made an unnecessary handoff. No refund execution or private tracking/address disclosure was observed. These boundaries do not waive the hard failures. Its actual human calibration is complete: 20 cases, 56 pairs, 82.14% threshold agreement, no human unsafe flags. Results and labels remain unchanged.

The repaired application **`cc0c3a8`** recognizes reimbursement requests beyond the literal word refund and refuses explicit third-party bare order references before models/tools. **248 offline tests, 65/65 frozen hard/all checks and 45/45 repeated safety checks pass**, with 15/15 identical terminal outcomes. Current handoffs read back (19 full, 24 repeats); key/canary scans and hosted answer/privacy/withdrawal trees pass. Nine memory/style/reset checks pass (58 →44 words, identical citations, reference deletion and style rollback); forced combined failure discloses no confirmed ticket with zero model calls.

All 65 unchanged-rubric same-model DeepEval judgments are complete: faithfulness .9964 (52 measured, 13 skipped, zero errors); relevancy .7730 (35/65 above threshold); grounded support .9523 (59/65 above threshold). These scores retain semantic/wording limitations and cannot waive safety. Three complete review packets are identical to the earlier actual review and carry those ratings with provenance; **17 changed packets still need actual review**. The replacement ten-case holdout was independently frozen by a separate authorized agent and remains unseen by the implementation agent. It cannot run before that review. Production extensions stay deferred.

**Acceptance remains open.** GitHub publishing is held because automatic approval review rejected exposing the new blind set; the user has chosen to keep the blind set local until its first evaluation, then publish it with results. The repairs/evidence are saved locally. No author/student name or new repository is required.

| Current evidence | Result | Limit |
|---|---|---|
| Offline regression | 248 tests pass | Existing project venv; not new clean install |
| Frozen cases | 65/65 hard and all in-scope checks | Fixed contexts v3; twelve legacy transaction criteria excluded, not passed |
| Safety repeats | 45/45;15/15 exact outcome consistency | Three repeats each; no reliability extrapolation |
| Handoffs | 19 full/24 repeat actual local store matches;14/14 frozen context-label precision | Synthetic mock handoffs; precision labels are not independent adjudication |
| Citation/contract | All applicable recorded gates pass | Canonical refs and required sections are checked; no universal entailment claim |
| Retrieval | Development Recall@5 100%, MRR .90 on 20 labels | Pinned index unchanged; not fresh holdout retrieval accuracy |
| Latency p95 | 32.102ms deterministic; 13.234s clarification; 18.137s single; 34.798s multi/escalation | All four observed targets met; concurrent case/judge load, warm embeddings; not SLA |
| Usage/errors | 466151 final-turn reported tokens; 7 invalid args, 2 not-found, 1 injected timeout, 1 step-limit | Setup/judging separate; no currency pricing; terminal success is not perfect tool selection |
| DeepEval faithfulness | 52 measured, .9964 mean, 52 above threshold; 13 skipped, 0 errors | Same-model indicative measurement |
| DeepEval relevancy | 65 measured, .7730 mean, 35 above threshold | Low scores remain; full typed JSON is graded |
| DeepEval grounded support | 65 measured, .9523 mean, 59 above threshold | No rubric tuning or score replacement |
| Memory/style/reset | All nine current replay checks; 58 to 44 words, identical citations, reset/rollback pass | One authored replay plus previous bounded on/off development evidence |
| Privacy/operations | Full/repeat known-canary/key scans and hosted 16/3/3-span read-backs pass | Not universal PII detection; unmatched names can remain in bounded RAM until deletion |

All 52/52 minimum required-tool assertions pass in the frozen summary; they verify expected presence, not all-call semantic precision. Pattern masking can alter exported UUID digit runs; actual hosted trees were correlated by a unique minimized-ID/latency/outcome match to content-free local records. No guessed correlation or source change was used.

Engineering review of low judged scores (not human calibration): generic refusal wording remains verbose; R06 and M08 clarification could be more specific. M13's zero score treats the real controlled preference save as an unsupported commerce write because the judge sees empty retrieval context; the recorded feedback event supplies the operational evidence. M15's .3 score flags multi-order/action ambiguity; current scope requests clarification and executes no transactions. These scores and wording limits remain recorded. The old M09 judge error remains in the old artifact; the new M09 grade succeeded without overwriting history.

The first untouched holdout is permanently recorded as 8/10, with missed mandatory refund T2 and privacy R2. No average or safe withholding waives those failures. Repairs are now development evidence; only the separately authored unseen set can provide the next generalization check after actual changed-output review. See [Phase9 chronology](phase9_evaluation.md), [new frozen report](../artifacts/final_runs/20261018T012141Z/report.md), [new consistency](../artifacts/final_runs/20261018T012903Z/consistency.json), [first holdout decision](../artifacts/phase9/first_holdout_acceptance_decision.json) and [pending acceptance evidence](../artifacts/phase9/repair_v2_acceptance_pending_review.md).

# Current candidate and acceptance gates

Updated 2026-10-18 (America/New_York). This is the current-candidate ledger. Other run narratives are historical unless they name this candidate. **No final acceptance or permission to publish unused blind tests is implied by a frozen-suite pass.**

- Current application: **`844ab3b`** (branch `fixes`), carrying the three `f403645` P1 repairs plus the residual own-reference privacy-refusal and injury-recall repairs (safety rules `2026-10-18-v7`). **413 offline tests pass**.
- Frozen regression `20261018T185305Z`: **65/65 hard and all case checks**, zero case failures, 19/19 mock handoffs read back. The N08 carrier-estimate question is resolved: answered with policy values and no fallback — the shipping-completeness gate over-block did not materialize.
- Repeated safety `20261018T190128Z`: **45/45 hard and all checks**, 15/15 identical outcomes across three repeats, worst-case hard checks pass, 24/24 handoffs read back. Key/canary scan: 1059 files, 0 findings.
- All-65 DeepEval on this build: faithfulness 50/51 measured ≥0.9 (R04 0.833), relevancy 30/65 ≥0.8, grounded support 61/65 ≥0.9 (M13 0.0, S14 0.6, M15 0.7, M08 0.8), zero judge errors. Same-model self-evaluation is disclosed; threshold misses remain explicit limitations. The separately versioned prose-relevancy diagnostic (`relevancy_v2`, recorded without replacing primary scores): 65/65 measured, mean 0.847, 47/65 above threshold.
- Twenty-case independent AI-proxy iteration review completed on this candidate's packet: gate `iteration_review_passed`, 55 paired ratings, 0.80 threshold agreement, no unsafe flags, zero critical/major and eight minor issues recorded (S01 misattributes "medical assistance" to retailer support; M02 states a UTC timestamp as Denver local; ambiguous mock-scope boilerplate in M01/N16/M05; three summary_hash equality/redaction defects that re-confirm the documented M2a/M2b P2 findings). AI proxy only, not actual human calibration.

| Gate | Current evidence / status |
|---|---|
| Frozen regression | Completed `20261018T185305Z`: **65/65 hard and all case checks** on `844ab3b`. |
| All-65 DeepEval | Completed 65/65 judged, zero errors; original prior scores and missing-measurement recovery retained historically. |
| Fresh independent answer review | Completed twenty-case AI-proxy review with exact packet digest; gate passed; eight minor issues open. Not actual human calibration. |
| Repeated safety suite | Completed `20261018T190128Z`: 45/45 with exact consistency. |
| Current ticket read-back/privacy checks | Completed 19+24 read-backs; scan clean. Hash integrity limitations (M2a/M2b) remain explicitly disclosed. |
| Current terminal/Streamlit and memory/style demos | Offline suite includes Streamlit AppTest; live recorder exercises the shared runtime. Hosted metadata tracing remains verified on the prior build; a refresh at the final accepted candidate is still scheduled. |
| Fresh blind v5 | Independently authored ten cases, root has only byte hashes. Local and uncommitted. All listed candidate gates above are now complete; **first use awaits explicit user direction** and remains one-shot. Never publish unused v5. |
| Publication/final acceptance | Candidate source and this evidence chain committed on `fixes` (`844ab3b` and the evidence commit); prior completed evidence published through `670d94f`. Current candidate is not yet accepted. |

## Superseded candidates

- `f403645`: implemented the three P1 repairs and passed the five affected frozen cases `20261018T175932Z` (5/5); superseded before its full-build run by review-identified residual defects: own-account requests such as "another order of mine" pre-empted into R2 refusal, and generic injury phrasing ("I got hurt", "needed stitches") missed T1. Its ledger record and evidence remain unchanged.
- `b3a9730`, run `20261018T144836Z`: 65/65 hard checks, **64/65 all case checks**. M02 safely abstained after the model repeated a rejected unsupported conclusion. This is a functional regression, not an accepted pass; `ce64d4e` adds a fully evidenced tracking-only code renderer. Its original record remains unchanged.

- `1cc0068`, run `20261018T031328Z`: frozen 65/65 complete; independent AI review found two major warranty-start/return-status issues. Blocked, not current.
- `2e2e60c` application, run `20261018T143615Z`: frozen 65/65 complete; reviewer found no major/critical issues but explicit unsupported-claim flags for M02/M05. M02 wording was repaired; packet-v2 exposes actual feedback/error receipts omitted from the prior packet. Original review remains unchanged and blocked.
- Used blind v1/v2/v3 failures and their actual-human reviews remain historical evidence. They cannot establish acceptance for this candidate.

## Review and publication policy

User clarification (2026-10-18): evaluate correctness independently of latency. A correct answer taking 15 seconds passes correctness; a wrong, unsupported or unexpected answer fails regardless of speed. Record latency as an operational measurement and defer performance root-cause work until correctness is stable. Runtime deadlines remain bounded resource controls, not correctness thresholds. A timeout that prevents the required answer remains a functional miss; do not relabel it as a successful answer.

The completed local retrieval probe (`artifacts/phase9/repair_v9_search_timing_probe.json`) succeeded in all twelve reads across direct, fresh-thread, persistent-thread and concurrent modes. It did not reproduce the full-run failures or establish their cause. Queue/execution timing instrumentation is available for the next controlled run. Performance tuning is deferred; missing required answers remain open correctness work.

The user authorized iterative independent AI agents as human proxies. They are recorded as `reviewed_by_independent_ai` / `ai_proxy`, separate from actual human calibration. Exact packet/output/build/model locks, the predetermined twenty-case review, complete judging and no unresolved major/critical or unsupported-claim flags are required before the new blind evaluation. The default human pipeline is unchanged. New blind questions and expected outcomes may publish only **after first evaluation, with results**. Any changed application build requires its own validation. Scores below target and unavailable measures remain explicit limitations.

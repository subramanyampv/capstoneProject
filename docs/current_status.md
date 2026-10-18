# Current candidate and acceptance gates

Updated 2026-10-18 (America/New_York). This is the current-candidate ledger. Other run narratives are historical unless they name this candidate. **No final acceptance or permission to publish unused blind tests is implied by a frozen-suite pass.**

- Application under validation: `7b2e33d` plus the user-approved policy-search timeout change from 10 to 20 seconds. **367 offline tests pass**; fresh live validation is required for this changed build.
- Targeted live check `20261018T153210Z`: **4/4 hard/all checks**; cancellation wording inspected.
- Current full run: **`20261018T153338Z`** — [manifest](../artifacts/final_runs/20261018T153338Z/manifest.json), [live summary](../artifacts/final_runs/20261018T153338Z/summary.json).
- Prior `b8a1ce2` completed full run `20261018T151500Z`: **65/65 hard/all**, **45/45 safety repeats** (`20261018T152232Z`, 100% outcomes), 19 full/24 repeated mock tickets read back, and scans passed. It remains **blocked**, because its AI reviewer flagged N07's unsupported 'outdated' description of an empty record.
- All 65 original judgments and the separate prose diagnostic completed for that prior candidate; those measurements do not transfer to changed source.


| Gate | Current evidence / status |
|---|---|
| Frozen regression | Prior 10-second build completed `20261018T153338Z`: 65/65 hard, 62/65 all checks. R02/R09/R10 lack the expected answer and required policy citation after real search timeouts. The 20-second build requires fresh validation. |
| All-65 DeepEval | Running on this exact run; prior all-65 scores remain historical and unchanged. |
| Fresh independent answer review | Pending completed new packet; fresh context-free AI proxy required. Prior actual human ratings do not transfer. |
| Repeated safety suite | Pending on this build. Earlier repeat run `20261018T144358Z` was stopped at 12/45 after its paired candidate was blocked; it is not completion evidence. |
| Current ticket read-back/privacy checks | Pending on completed candidate exports. Earlier candidate scans do not transfer automatically. |
| Current terminal/Streamlit and memory/style demos | Existing component evidence; current-build replay/read-back pending. |
| Fresh blind v4 | Unopened; must stay local before first evaluation. No acceptance based on earlier failed holdouts. |
| Publication/final acceptance | Blocked pending applicable gates; GitHub last published evidence is `434ee0f`. |

## Superseded candidates

- `b3a9730`, run `20261018T144836Z`: 65/65 hard checks, **64/65 all case checks**. M02 safely abstained after the model repeated a rejected unsupported conclusion. This is a functional regression, not an accepted pass; `ce64d4e` adds a fully evidenced tracking-only code renderer. Its original record remains unchanged.

- `1cc0068`, run `20261018T031328Z`: frozen 65/65 complete; independent AI review found two major warranty-start/return-status issues. Blocked, not current.
- `2e2e60c` application, run `20261018T143615Z`: frozen 65/65 complete; reviewer found no major/critical issues but explicit unsupported-claim flags for M02/M05. M02 wording was repaired; packet-v2 exposes actual feedback/error receipts omitted from the prior packet. Original review remains unchanged and blocked.
- Used blind v1/v2/v3 failures and their actual-human reviews remain historical evidence. They cannot establish acceptance for this candidate.

## Review and publication policy

User clarification (2026-10-18): evaluate correctness independently of latency. A correct answer taking 15 seconds passes correctness; a wrong, unsupported or unexpected answer fails regardless of speed. Record latency as an operational measurement and defer performance root-cause work until correctness is stable. Runtime deadlines remain bounded resource controls, not correctness thresholds. A timeout that prevents the required answer remains a functional miss; do not relabel it as a successful answer.

The completed local retrieval probe (`artifacts/phase9/repair_v9_search_timing_probe.json`) succeeded in all twelve reads across direct, fresh-thread, persistent-thread and concurrent modes. It did not reproduce the full-run failures or establish their cause. Queue/execution timing instrumentation is available for the next controlled run. Performance tuning is deferred; missing required answers remain open correctness work.

The user authorized iterative independent AI agents as human proxies. They are recorded as `reviewed_by_independent_ai` / `ai_proxy`, separate from actual human calibration. Exact packet/output/build/model locks, the predetermined twenty-case review, complete judging and no unresolved major/critical or unsupported-claim flags are required before the new blind evaluation. The default human pipeline is unchanged. New blind questions and expected outcomes may publish only **after first evaluation, with results**. Any changed application build requires its own validation. Scores below target and unavailable measures remain explicit limitations.

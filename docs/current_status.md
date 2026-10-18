# Current candidate and acceptance gates

Updated 2026-10-18 (America/New_York). This is the current-candidate ledger. Other run narratives are historical unless they name this candidate. **No final acceptance or permission to publish unused blind tests is implied by a frozen-suite pass.**

- Current application: **`7d10e67`**, with the user-approved 20-second policy-search timeout. **367 offline tests pass**; live frozen regression completed with **65/65 hard and all case checks**.
- Targeted live check `20261018T153210Z`: **4/4 hard/all checks**; cancellation wording inspected.
- Current completed full run: **`20261018T154651Z`** — [manifest](../artifacts/final_runs/20261018T154651Z/manifest.json), [summary](../artifacts/final_runs/20261018T154651Z/summary.json). No case failures; R02/R09/R10 now pass. Earlier failures remain preserved.
- Prior `b8a1ce2` completed full run `20261018T151500Z`: **65/65 hard/all**, **45/45 safety repeats** (`20261018T152232Z`, 100% outcomes), 19 full/24 repeated mock tickets read back, and scans passed. It remains **blocked**, because its AI reviewer flagged N07's unsupported 'outdated' description of an empty record.
- All 65 original judgments and the separate prose diagnostic completed for that prior candidate; those measurements do not transfer to changed source.


| Gate | Current evidence / status |
|---|---|
| Frozen regression | Completed `20261018T154651Z`: **65/65 hard and all case checks**. |
| All-65 DeepEval | Completed all 65; one missing faithfulness measurement recovered once with original primary bytes retained. Faithfulness 51/51 measured pass (14 no-context skips), relevancy 28/65, grounded support 58/65 above thresholds. Threshold misses remain. |
| Fresh independent answer review | Completed fresh twenty-case AI proxy review: gate passed, five minor issues, no unsafe/unsupported flags or major/critical issues. Not actual human calibration. |
| Repeated safety suite | Completed `20261018T155956Z`: **45/45 hard/all checks**, 15/15 cases have identical outcomes across three repeats. All 24 mock handoffs read back and privacy scan passed. |
| Current ticket read-back/privacy checks | All 19 full-run mock handoffs match local storage; current export scan passed. Scans must be repeated after final artifacts are written. |
| Current terminal/Streamlit and memory/style demos | Actual CLI safety smoke passed; nine style/reset checks passed; ten-case memory-off ladder complete. Clean committed-source offline suite: 367 pass (includes mocked Streamlit AppTest). Four actual hosted trace trees verified. Not a new live UI screenshot/visual test. |
| Fresh blind v4 | Completed `20261018T161532Z`: **9/10 hard,8/10 all checks**. B401 missed T1; B404 unexpected clarification. First evaluation complete; used set may publish with results. Additional expectation-blind AI review completed: major B401/B404/B410 issues; B410 shipping omission was not caught by original fixed checks. |
| Publication/final acceptance | **Acceptance blocked by v4 failures.** Source, completed evaluation evidence, used v4/results and review addendum published to GitHub in checkpoint `25cb752`. No unused next blind set may be pushed. |

## Superseded candidates

- `b3a9730`, run `20261018T144836Z`: 65/65 hard checks, **64/65 all case checks**. M02 safely abstained after the model repeated a rejected unsupported conclusion. This is a functional regression, not an accepted pass; `ce64d4e` adds a fully evidenced tracking-only code renderer. Its original record remains unchanged.

- `1cc0068`, run `20261018T031328Z`: frozen 65/65 complete; independent AI review found two major warranty-start/return-status issues. Blocked, not current.
- `2e2e60c` application, run `20261018T143615Z`: frozen 65/65 complete; reviewer found no major/critical issues but explicit unsupported-claim flags for M02/M05. M02 wording was repaired; packet-v2 exposes actual feedback/error receipts omitted from the prior packet. Original review remains unchanged and blocked.
- Used blind v1/v2/v3 failures and their actual-human reviews remain historical evidence. They cannot establish acceptance for this candidate.

## Review and publication policy

User clarification (2026-10-18): evaluate correctness independently of latency. A correct answer taking 15 seconds passes correctness; a wrong, unsupported or unexpected answer fails regardless of speed. Record latency as an operational measurement and defer performance root-cause work until correctness is stable. Runtime deadlines remain bounded resource controls, not correctness thresholds. A timeout that prevents the required answer remains a functional miss; do not relabel it as a successful answer.

The completed local retrieval probe (`artifacts/phase9/repair_v9_search_timing_probe.json`) succeeded in all twelve reads across direct, fresh-thread, persistent-thread and concurrent modes. It did not reproduce the full-run failures or establish their cause. Queue/execution timing instrumentation is available for the next controlled run. Performance tuning is deferred; missing required answers remain open correctness work.

The user authorized iterative independent AI agents as human proxies. They are recorded as `reviewed_by_independent_ai` / `ai_proxy`, separate from actual human calibration. Exact packet/output/build/model locks, the predetermined twenty-case review, complete judging and no unresolved major/critical or unsupported-claim flags are required before the new blind evaluation. The default human pipeline is unchanged. New blind questions and expected outcomes may publish only **after first evaluation, with results**. Any changed application build requires its own validation. Scores below target and unavailable measures remain explicit limitations.

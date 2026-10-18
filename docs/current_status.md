# Current candidate and acceptance gates

Updated 2026-10-18 (America/New_York). This is the current-candidate ledger. Other run narratives are historical unless they name this candidate. **No final acceptance or permission to publish unused blind tests is implied by a frozen-suite pass.**

- Current application: **`f403645`**, implementing the three P1 repairs. **394 offline tests pass**.
- Affected frozen live cases `20261018T175932Z`: **5/5 hard and all checks** (N03, N17, R10, S01, S13).
- Used-v4 failures plus broader development paraphrases are being checked separately. Previously seen cases are not fresh acceptance evidence.
- Previous candidate `7d10e67` remains blocked: v4 run `20261018T161532Z` passed 9/10 hard and 8/10 all fixed checks; independent answer review additionally flagged B410.

| Gate | Current evidence / status |
|---|---|
| Frozen regression | Affected 5/5 pass; full current-build run pending. Prior 65/65 does not transfer. |
| All-65 DeepEval | Pending current full outputs. Original prior scores and missing-measurement recovery retained. |
| Fresh independent answer review | Pending current twenty-case packet; no historical ratings transferred. AI proxy only, not human calibration. |
| Repeated safety suite | Pending current build; previous 45/45 preserved as historical. |
| Current ticket read-back/privacy checks | Pending completed candidate artifacts. Hash integrity limitations remain explicitly disclosed. |
| Current terminal/Streamlit and memory/style demos | Offline suite includes Streamlit AppTest; live current-build replay/read-back pending. |
| Fresh blind v5 | Independently authored ten cases, root has only byte hashes. Local and uncommitted; first use requires completed candidate gates. |
| Publication/final acceptance | Source `f403645` saved locally; prior completed evidence published through `670d94f`. Current candidate is not accepted. Never publish unused v5. |

## Superseded candidates

- `b3a9730`, run `20261018T144836Z`: 65/65 hard checks, **64/65 all case checks**. M02 safely abstained after the model repeated a rejected unsupported conclusion. This is a functional regression, not an accepted pass; `ce64d4e` adds a fully evidenced tracking-only code renderer. Its original record remains unchanged.

- `1cc0068`, run `20261018T031328Z`: frozen 65/65 complete; independent AI review found two major warranty-start/return-status issues. Blocked, not current.
- `2e2e60c` application, run `20261018T143615Z`: frozen 65/65 complete; reviewer found no major/critical issues but explicit unsupported-claim flags for M02/M05. M02 wording was repaired; packet-v2 exposes actual feedback/error receipts omitted from the prior packet. Original review remains unchanged and blocked.
- Used blind v1/v2/v3 failures and their actual-human reviews remain historical evidence. They cannot establish acceptance for this candidate.

## Review and publication policy

User clarification (2026-10-18): evaluate correctness independently of latency. A correct answer taking 15 seconds passes correctness; a wrong, unsupported or unexpected answer fails regardless of speed. Record latency as an operational measurement and defer performance root-cause work until correctness is stable. Runtime deadlines remain bounded resource controls, not correctness thresholds. A timeout that prevents the required answer remains a functional miss; do not relabel it as a successful answer.

The completed local retrieval probe (`artifacts/phase9/repair_v9_search_timing_probe.json`) succeeded in all twelve reads across direct, fresh-thread, persistent-thread and concurrent modes. It did not reproduce the full-run failures or establish their cause. Queue/execution timing instrumentation is available for the next controlled run. Performance tuning is deferred; missing required answers remain open correctness work.

The user authorized iterative independent AI agents as human proxies. They are recorded as `reviewed_by_independent_ai` / `ai_proxy`, separate from actual human calibration. Exact packet/output/build/model locks, the predetermined twenty-case review, complete judging and no unresolved major/critical or unsupported-claim flags are required before the new blind evaluation. The default human pipeline is unchanged. New blind questions and expected outcomes may publish only **after first evaluation, with results**. Any changed application build requires its own validation. Scores below target and unavailable measures remain explicit limitations.

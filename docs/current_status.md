# Current candidate and acceptance gates

Updated 2026-10-18 (America/New_York). This is the current-candidate ledger. Other run narratives are historical unless they name this candidate. **No final acceptance or permission to publish unused blind tests is implied by a frozen-suite pass.**

- Application repair: **`b8a1ce2`**, frozen after **361 passing offline tests**, also passing in an extracted committed-source copy with matching candidate hashes.
- Targeted affected-case smoke: **5/5 hard/all checks**, run `20261018T151346Z`; developer answer inspection confirms the negated disclaimer remains unchanged.
- Current full run: **`20261018T151500Z`** — [manifest](../artifacts/final_runs/20261018T151500Z/manifest.json), [live summary](../artifacts/final_runs/20261018T151500Z/summary.json). The summary reports actual progress, not final acceptance.
- Previous partial/failed candidates remain unaccepted and preserved. They do not establish current completion.


| Gate | Current evidence / status |
|---|---|
| Frozen regression | Running `20261018T151500Z`; requires completed 65/65 hard and all case checks. |
| All-65 DeepEval | Running against this exact full run with original rubric; prior scores remain historical. |
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

The user authorized iterative independent AI agents as human proxies. They are recorded as `reviewed_by_independent_ai` / `ai_proxy`, separate from actual human calibration. Exact packet/output/build/model locks, the predetermined twenty-case review, complete judging and no unresolved major/critical or unsupported-claim flags are required before the new blind evaluation. The default human pipeline is unchanged. New blind questions and expected outcomes may publish only **after first evaluation, with results**. Any changed application build requires its own validation. Scores below target and unavailable measures remain explicit limitations.

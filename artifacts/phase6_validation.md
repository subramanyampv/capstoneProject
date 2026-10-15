# Phase 6 validation — 2026-10-15 America/New_York

Bounded session context is implemented and development-tested. This is not final system acceptance, semantic/human calibration or held-out multi-turn generalization.

## Offline suite and checkpoint audit

```text
174 passed in 16.53s
```

The suite preserves existing baseline, prompt, retrieval and Phase 5 checks. Memory tests cover six-message bounds, every checkpoint version/pending write/blob, reset, exact 1,800-second expiry, automatic idle cleanup, account/session isolation, concurrent same-session serialization, capacity eviction, current status/event mutation, tracking-only reference promotion, product/order switching, rejected explicit references, missing-reference clarification, provider-independent reset, refusal/injury precedence, unresolved-clarification T5 and rejected substitution of a different owned order. UI tests verify server-bound identity, source rendering and new-session clearing.

[Checkpoint audit](phase6_checkpoint_audit.json) uses the actual projection LangGraph and support graph with a scripted model and temporary domain files. After five turns it retains six messages and three safe checkpoint versions, with no tested tool/record fields. Reset leaves storage/writes/blobs empty. At exact TTL, checkpoint versions, pending writes, blobs, messages and entities are zero. An empty read may recreate an opaque empty-key bucket; no retained values remain. This is logical store deletion, not forensic RAM erasure. Background cleanup and concurrency are separately unit-tested.

## Final five-conversation comparison

Final run: [20261015T194351Z](memory_runs/20261015T194351Z/summary.json). [Saved validation and metrics](memory_runs/20261015T194351Z/validation.json) pass all ten conversation/mode conditions. Support source hashes match the saved snapshots. Model settings and public-index startup are identical; each mode uses a separate synthetic session. No frozen cases or holdout data were changed.

| Measure | Memory off | Memory on |
|---|---:|---:|
| Conversations | 5 | 5 |
| Expected behavior passes | 5/5 | 5/5 |
| Context-dependent follow-ups answered with expected fresh tool evidence | 0/4 | 4/4 |
| Clarification responses | 5 | 1 |
| Unresolved context-dependent follow-ups within the fixed script | 4 | 0 |
| Reset followed by required clarification | Pass | Pass |

Tracking, return and product-care follow-ups resolve on scripted turn two with memory on; switching to the previous order resolves on turn three. Memory-off scripts stop at clarification, so turns-to-resolution is unknown rather than zero. Reset intentionally does not answer from earlier context. Reference/tool/outcome checks are structural; they do not independently grade every sentence's semantic faithfulness. Small authored development scripts and one final run do not establish production reliability or repeated-run consistency.

## Failures retained

- [192415Z](memory_runs/20261015T192415Z/validation.json): memory-on resolves two of four positive follow-ups. Tracking-only calls verified ownership but did not promote an order slot; tracking and switching asked for IDs again.
- [193034Z](memory_runs/20261015T193034Z/validation.json): promotion is fixed; three of four resolve. The planner still asks again for the code-resolved previous order.
- [193649Z](memory_runs/20261015T193649Z/validation.json): strict validation prevents an unsupported plan, but the planner still fails the contract twice and escalates. This is a failed resolution, not a passing memory answer.
- [Targeted switch](memory_runs/20261015T194224Z/summary.json): resolving reference phrases to an explicit planner request and presenting only the resolved entity fixes that case.
- The final full run above confirms all five scripts after normalization. Original messages still pass through safety guards; references never authorize records or supply cached facts. Old failed outputs are unchanged.

## Privacy and limits

[Bounded scan](phase6_privacy_scan.json): 103 Phase 6 artifact/runtime files, no configured-credential or known-canary matches. Checkpoint inspection is separate because session state is in process, not on disk. Operational logs contain only scalar memory metadata; submitted UI input clears. Pattern masking is not universal PII detection, and user-origin text can contain unmatched names/details until expiry/reset. No raw working state or assistant facts enter the checkpointer.

Memory is process-local and capped at 100 sessions. Durable cross-session storage, style preference adaptation, hosted masked LangSmith verification, full frozen/holdout safety/quality evaluation and final demo packaging remain later work. Knowledge graph remains deferred.

## Reproduce

```bash
make test
make compare-memory
.venv/bin/python scripts/summarize_memory.py artifacts/memory_runs/20261015T194351Z
make scan-memory
.venv/bin/capstone-agent support --chat --customer C-100
```

A live comparison creates a new dated directory and uses the configured model. Run the summarizer against that directory. CLI `/reset` clears context, `/quit` exits and clears the interactive session. One-shot invocations cannot carry memory across process restarts.

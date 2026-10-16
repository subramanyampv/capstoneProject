# Phase 6 — bounded session memory

Updated 2026-10-15, America/New_York. Authority: [Architecture revision 3.1](architecture_and_plan.md), Section 11. This phase adds context to the existing bounded support graph; it adds no store integration, transaction execution or style adaptation.

## Retention boundary

The working support graph still has **no checkpointer**. A separate tiny LangGraph stores only an explicitly built projection in `InMemorySaver`. Its input and intermediate checkpoints therefore cannot contain the working graph's tool/evidence state. Replacing a projection deletes every previous checkpoint, pending write and blob for that scoped thread; saving uses synchronous durability.

| Retained in process | Excluded from retained memory |
|---|---|
| Last six messages: masked customer questions and assistant outcome markers | Assistant answer prose, prior order status, prices, eligibility decisions, tracking payloads |
| Verified order/SKU/product references | Retrieved passages, source evidence sets, model/tool messages or private reasoning |
| Allowlisted last intents and last terminal outcome | Refusal/escalation flags, tickets, credentials, operational payloads |
| Monotonic activity timestamp outside checkpoint state | Disk-backed checkpoints or cross-restart history |

The deliberate assistant-message reduction prevents an earlier answer from becoming an alternative record source. The supervisor can reconstruct the topic from customer questions and verified references; specialists and the composer still receive only the current task/current facts. Historical customer text is untrusted data, never instructions or identity authority. Pattern masking is stronger than keeping raw messages, but it is not universal personal-data detection. User-provided names or other unmatched text can remain in the bounded in-process window until deletion.

## Resolution, isolation and deletion

Customer/session pairs map to opaque checkpoint keys. A model cannot select the memory key. Different accounts and sessions remain isolated, including identical raw handles under different customers. Same-session turns serialize before reading context; active sessions are protected against eviction. The default cap is 100 sessions, with idle eviction. Model calls do not hold a global memory lock.

A new explicit order reference replaces the active slot; a failed/non-owned explicit reference clears the earlier slot rather than silently reusing it. The previous verified order is available for one subsequent turn's “other order” reference. Empty references require clarification. Product references remain public catalog identifiers and are re-fetched. Multiple explicit order IDs need clarification rather than an arbitrary selection. Current turn tools still enforce ownership and compute decisions. Code resolves order-reference phrases into an explicit planner request, presenting only the resolved entity as current context. Structured plan validation rejects asking for that ID again, and the registry rejects substituting a different order. The original current message still goes through all safety guards and is used for the customer response.

Expiry uses elapsed monotonic time, independently of the frozen scenario date. The default inactivity boundary is 1,800 seconds. Requests enforce it exactly; a background reaper deletes idle checkpoint storage within the next 30-second sweep even if no request follows. Constructor parameters support isolated clock/TTL tests. Context is lost on process restart.

`/reset` deletes all retained versions and works even if provider/index configuration is unavailable. It never claims to delete real orders or tickets. New-session and account-switch controls clear the prior UI session's retained context. Unsupported commands still disclose their unavailability; style feedback and `/forget-preferences` are now implemented separately in [Phase 7](phase7_adaptation.md).

## Interfaces and comparison

```bash
.venv/bin/capstone-agent support --chat --customer C-100
# Track O-1001.
# Track that order.
# /reset
# Track that order.
# /quit
.venv/bin/capstone-agent support --chat --no-memory --customer C-100
.venv/bin/python scripts/compare_memory.py
```

`MEMORY_ENABLED=true` is the default; `false` clears/disables retained context for comparison. No credential changes are needed. One-shot CLI calls are separate processes and cannot share in-memory history. Streamlit keeps the selected synthetic identity between questions and supports `/reset` and New support session. Operational records keep only memory counters/booleans, never the retained window.

The comparison uses five authored development conversations: tracking follow-up, return follow-up, catalog care follow-up, order switching/other order, and reset. It records both expected reference-tool use and actual terminal outcomes, not just whether a hint existed. The holdout remains untouched. These results do not establish semantic faithfulness or broad multi-turn accuracy. All measured outcomes and preserved failures belong in the dated Phase 6 validation record.

## Measured completion

[Phase 6 validation](../artifacts/phase6_validation.md) records 174 passing tests, the complete checkpoint audit, preserved failures and the final five-conversation comparison. Four of four context-dependent follow-ups resolve with memory on versus zero of four off; clarifications fall from five to one. Reset correctly forces clarification in both modes. These are structural development results, not semantic/human or held-out acceptance.

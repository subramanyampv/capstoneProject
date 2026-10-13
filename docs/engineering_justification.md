# Engineering & Product Justification

Status: **initial decisions recorded from the architecture plan; revisit at Phase 9
with measured evidence. No results claimed.**

## Key decisions
| Area | Decision |
|---|---|
| Business scope | Tier-1 e-commerce support: order status, returns, shipping, product questions, escalation |
| Baseline vs. target | Demonstrate rule-based single-agent baseline and each stage before the final multi-agent build |
| Authority boundaries | LLM interprets and drafts; deterministic policy + authorization services decide eligibility and action permission |
| Knowledge sources | Policy/catalog/FAQ via RAG; order status and shipment events via structured mock services |
| Transactions | Simulated writes only; exact-action confirmation, authorization, result verification |
| Feedback | Bounded, auditable configuration changes; raw feedback never rewrites policy or disables safeguards |
| Framework strategy | Plain Python interfaces first; orchestration framework only if it materially improves tracing/routing/maintainability |
| Monitoring | Structured logs + trace IDs first; one tracing backend only if available and useful |

## Why supervisor–specialist (and its risk)
One orchestrator owns routing, plan execution, state transitions, budgets, final
assembly; specialists stay narrow and bounded. Main risk: multi-agent complexity
reducing reliability — mitigated by narrow specialists, bounded delegation, and
actually *measuring* the value of delegation (vs. single-agent paths).

## Risk register -> mitigations
| Risk | Mitigation |
|---|---|
| Agents conflict | Central policy service + validated specialist results |
| Irrelevant RAG evidence | Labeled retrieval set, ranking metrics, calibrated threshold, abstention |
| False claim of action success | Validated tool results + post-action state verification |
| Feedback weakens safety | Whitelisted adaptive params; policy/safety immutable to feedback |
| Memory retains sensitive data | Minimize retention, separate stores, tested reset/deletion |
| Averages hide safety failures | Hard safety gates independent of aggregate quality |
| Framework lock-in | Framework-independent domain logic, pinned dependencies |
| Scope creep | Synthetic data, local deployment, simulated writes, small corpus |

## Trace-stage capture (observability)
Request entry (trace ID, timestamp, sanitized intent) · safety gateway (decision
category, rule IDs) · orchestration (specialist, plan steps, iterations) · retrieval
(index version, source IDs, top-k, scores) · tool execution (name, duration, status,
retries) · model invocation (model ID, prompt version, latency, tokens if available) ·
final response (outcome, citation IDs, escalation state) · error (category, recovery
path, sanitized diagnostics). **Never log private chain-of-thought**; record plan
summaries, decisions, evidence refs, observable tool events.

## Roadmap priorities
Per-phase (see README status). Open items to resolve with evidence at Phase 9:
provider/embedding choice performance, whether an orchestration framework earns
adoption, whether to add the deferred API layer.

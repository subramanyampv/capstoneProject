# Engineering and product justification — v3

Authority: [Architecture and Plan v3](architecture_and_plan.md), sections 4, 18 and 19. Final outcome measurements are pending.

| Decision | Rationale |
|---|---|
| LangChain + LangGraph | Framework Track A; explicit routing, bounded agents and control state |
| Three specialists / six tools | Minimal genuine multi-agent design with clear authority boundaries |
| Deterministic guards | LLM interpretation cannot remove safety flags or grant permissions |
| Local Voyage-4-nano + Chroma | One embedding model; local document/query representation; version metadata and persistence |
| Mock escalation as the only write | Focus on support resolution; defer transaction confirmation complexity |
| In-process memory + style profile | Demonstrate follow-ups/reset and reversible adaptation with bounded retention |
| JSONL primary; masked LangSmith opt-in | Reproducible local evidence plus visual routing traces |
| DeepEval + deterministic gates + human calibration | Standardized quality measurement without judge-controlled safety |
| Development default Prompt C | Reviewed A/B outputs invent policy windows; C is faster, but known failures require later guards |

Knowledge graph, distance/weather delivery engine, external commerce APIs, extended corpus, asymmetric hosted embeddings and return/refund/cancellation writes are deferred until the initial product succeeds. Their historical code is preserved and excluded from default UI/evaluation.

The risks are latency from sequential LLM calls, small labeled datasets, same-model judging, lexical safety misses and simulated identity. Measure and disclose them. Future work follows v3's roadmap, including parallel routing, an independent judge, confirmed actions and durable checkpointing.

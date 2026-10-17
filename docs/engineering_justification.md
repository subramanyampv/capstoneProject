# Engineering and product justification — v3

Authority: [Architecture and Plan v3](architecture_and_plan.md), sections 4, 18 and 19. Release frozen/repeated measurements are complete; actual changed-output human calibration, untouched holdout and final acceptance remain pending.

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

Release evidence on the locked application build: 65/65 frozen hard/all-case checks, 45/45 safety repeats and 100% terminal consistency. Sample p95 latency is 47 ms for deterministic refusal/commands, 12.52 s clarification, 13.80 s one specialist and 32.39 s multi-specialist/escalation, within the four design targets. Three case workers overlapped model calls while local embedding access was serialized; this is not a production SLA. 448,777 reported final-turn tokens exclude setup and judges; endpoint currency pricing is unavailable.

Quality remains a separate decision: same-model mean relevancy is .7647 and grounded support .9446; one faithfulness judgment is unavailable. Fixed human review must assess these exact outputs before the untouched holdout. Generic refusal and multi-order clarification wording are remaining limitations. Pattern masking can retain unmatched names in bounded process memory until reset/expiry; logs/spans exclude raw conversations. The retained failed/interrupted runs and controlled RCA probes make the repairs reviewable without claiming universal safety.

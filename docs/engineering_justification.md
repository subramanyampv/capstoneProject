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

The first untouched holdout passed only 8/10 after 65/65 frozen and 45/45 repeats: lexical financial intent and explicit third-party reference classification were incomplete. These failures are preserved; no transaction or private tracking/address disclosure was observed, but mandatory safety gates failed. The repaired source adds bounded reimbursement obligations and deterministic R2 refusal routing, with 248 offline tests, 65/65 frozen and 45/45 repeats passing. A separately authored replacement holdout remains unseen; seventeen changed human packets still need actual review before it can run.

Current observed p95 meets four design targets; same-model mean relevancy .7730 and grounded support .9523 retain quality misses. All 52 measured faithfulness scores exceed threshold (13 skips); this is not independent semantic proof. Unmatched names can remain in bounded process memory until reset/expiry; logs/spans exclude conversation content. Production persistence, parallel reads, classifiers and OTel are deferred while these existing defects are independently validated. No accepted release or quantified business benefit is claimed.

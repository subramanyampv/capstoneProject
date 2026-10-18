# Engineering and product justification — v3

Authority: [Architecture and Plan v3](architecture_and_plan.md), sections 4, 18 and 19. Frozen/repeated measurements, quality judgments and actual current review are complete; independent v3 failed its safety gate, so product-illness repair and independent v4 validation remain.

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

Two independent holdouts exposed generalization defects despite earlier 65/65 frozen and 45/45 repeat passes. The first scored 8/10; the second scored 9/10 hard and 7/10 overall after actual review (20 cases, 56 pairs, 85.71% judge/human threshold agreement). Both failures remain preserved. Repairs now reconcile public policy with pronoun memory, require shipping evidence for arrival-certainty requests, and retain actually retrieved citations in fallbacks. Development testing also caught and corrected a temporal false positive and required the exact international shipping section. A real five-second local retrieval timeout then caused a hard conflict-classification miss; the CPU deadline is now ten seconds, retaining late-result rejection and honest failure disclosure.

Candidate d57aa4a passes 261 offline tests, including an isolated committed-source run using the existing dependencies, and 65/65 frozen hard/all checks. Its four observed p95 targets are met: 36.576ms deterministic refusal/command, 13.300s clarification, 16.984s single specialist and 31.630s multiple specialists/escalation. These samples are not a production SLA. Tool/schema errors and a specialist provider failure remain recorded even when code backstops preserve the correct outcome. Current repeats pass 45/45 and actual review is complete: 20 cases, 56 pairs, 76.79% agreement, no unsafe flags. All-65 means are .9867 faithfulness (53 measured,12 skipped), .7583 relevancy and .9585 grounded support, with threshold misses retained. Independent v3 passed 9/10; reported food-related illness missed mandatory T1/high-priority safety routing. That blocks acceptance. A separately authored v4 stays unseen while the safety class is repaired.

The earlier cc0c3a8 same-model means (.9964 faithfulness on 52 measured/13 skipped, .7730 relevancy and .9523 grounded support) describe that earlier candidate only. Fresh metrics must be reported separately. Unmatched names can remain in bounded process memory until reset/expiry; logs/spans exclude conversation content. Production persistence, parallel reads, classifiers and OTel remain deferred while core acceptance is evaluated. No accepted release or quantified business benefit is claimed.

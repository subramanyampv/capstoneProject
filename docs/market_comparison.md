# Market comparison: customer-support AI agents

Research date: **2026-10-13, America/New_York**. This is a comparison and analysis artifact, not a change to the authoritative [Architecture and Plan v3.1](architecture_and_plan.md).

## Purpose and evidence boundaries

Our closest product reference is **Intercom Fin**, with **Zendesk AI agents** and **Salesforce Agentforce Service Agent** as complementary references. These are documented customer-facing service products rather than general-purpose chat assistants. The useful comparison is how they connect knowledge, actions, customer identity, conversation context and human support. We are building a deliberately smaller synthetic e-commerce prototype, not reproducing an enterprise helpdesk.

Every vendor capability below is a statement supported by official documentation. None was independently tested in this project. Features can depend on edition, configuration, channel, access approval or early-access enrollment. Documentation availability does not prove that every capability is enabled in a particular customer account. Vendor statements such as “best-performing,” “instant,” and “high resolution rate” are marketing claims; this analysis does not adopt them as measured results. [Fin overview](https://www.intercom.com/help/en/articles/7120684-fin-ai-agent-explained), [Zendesk overview](https://support.zendesk.com/hc/en-us/articles/6970583409690-About-AI-agents), [Agentforce Service Agent overview](https://help.salesforce.com/s/articleView?id=service.bots_service_asa_about.htm&language=en_US&type=5).

“Real-time support” here means an interactive customer conversation with retrieval or business-system operations during the interaction. It does not imply hard real-time guarantees, continuous monitoring or a verified response-time SLA.

## Our current comparison baseline

The following snapshot separates measured implementation from the target design. Refer to [implementation status](implementation_status.md), [retrieval design](retrieval_design.md), [task list](task_list.md) and the underlying run artifacts for the evolving execution record.

| Area | Implemented / measured | Planned for the initial product |
|---|---|---|
| Interaction | Local Python Streamlit and CLI; deterministic baseline plus configurable model experiments | Integrated final workflow with synthetic customer/session selection and accurate ticket/failure rendering |
| Model workflow | LangChain model adapter; bounded single-agent LangGraph workflow; schema checks and repair limits | Supervisor and three bounded tool-using specialists |
| Knowledge | Seven authored documents; 28 indexed sections; pinned local Voyage-4-nano embeddings and Chroma; sourced RAG probe | Policy retrieval through the specialist tool contract, integrated grounding checks and final evaluation |
| Retrieval evidence | On 20 development labels, retained Recall@5 improved from 80% to 100%; MRR remains 0.900 after the final hint refinement; five of five unanswerable queries abstained | Untouched holdout generalization and integrated-path calibration |
| Actions | Deterministic baseline helpers and experimental retrieval exist | Six registered typed tools; verified ownership; tool budgets, failure paths and idempotent mock escalation tickets |
| Handoff | Escalation classifications can be evaluated; earlier comparison identified seven misses | Confirmed ticket creation, handoff failure disclosure and preservation of mandatory escalation triggers |
| Memory | No completed final session-memory implementation | Scoped checkpointer state, entity slots, TTL, reset and memory on/off comparison |
| Adaptation | No completed final adaptation experiment | Bounded style preferences, feedback, versioning and rollback |
| Evaluation | Frozen 65 cases; saved prompt outputs; DeepEval and local redacted evidence; 104 offline tests passed in the root validation run | Full workflow/holdout/consistency/canary evaluation and human calibration |
| Observability | Local evidence and opt-in LangSmith metadata/privacy wrapper | Hosted verification and final hierarchical agent/tool traces |

The 100% development Recall@5 is not an answer-accuracy rate, a held-out result or final safety acceptance. An intermediate hint profile reduced MRR to 0.867; separating injury-review questions from general human requests restored it to 0.900. These are development-set measurements. Passing offline tests demonstrates the tested contracts, not production reliability. Knowledge graph and external-API delivery estimation remain deferred until the initial product is successfully completed.

## Documented vendor capabilities

### Intercom Fin: closest end-to-end reference

Fin documents multi-source knowledge answers, a centralized content library, audience targeting, answer inspection and configurable human handoff. It supports customer conversations across several channels, but our comparison focuses on chat. [Fin overview](https://www.intercom.com/help/en/articles/7120684-fin-ai-agent-explained).

Fin Tasks combines triggers, positive/negative examples, branching instructions, external Data connectors, temporary attributes and escalation to a team. Drafts and simulations allow testing before publishing. These are configured workflows; they do not mean a new merchant's refund or order API works without implementation. [Fin Tasks setup](https://www.intercom.com/help/en/articles/10257113-how-to-set-up-fin-tasks).

Fin's connector guidance warns that missing authentication can enable unauthorized actions. Messenger verification does not cover every channel; OTP or another verification method may be needed before exposing customer data. This is an integration responsibility. [Data connectors FAQs](https://www.intercom.com/help/en/articles/9916507-data-connectors-faqs).

Its Agent API documents conversation status events through webhooks/SSE and follow-up messages. A one-shot `ask` call does not autonomously run procedures or escalate; the conversational mode has different behavior. API access requires approval in the workspace. This distinction matters when comparing a standalone answer with an operational support agent. [Fin Agent API](https://developers.intercom.com/docs/guides/fin-agent-api).

Fin also offers reusable batch tests with answer inspection. Ratings help quality assurance; the documentation says they do not retrain Fin. [Batch testing](https://www.intercom.com/help/en/articles/10521711-batch-test-fin-ai-agent).

### Zendesk AI agents: helpdesk-native automation reference

Zendesk documents grounded replies, generative procedures, scripted dialogues, authorized actions and integrations with existing systems. Capabilities and resolution allowances depend on the customer's plan. [AI agents overview](https://support.zendesk.com/hc/en-us/articles/6970583409690-About-AI-agents).

Its documentation distinguishes configured actions, events, conversation actions and voice actions. It also lists flow/email testing, A/B tests, reporting dashboards, conversation logs and satisfaction analysis. Some newer functionality, including the listed conversation simulator and custom agent builder, is marked EAP; availability should be checked before assuming parity. [Creating actions](https://support.zendesk.com/hc/en-us/sections/8264365827098-Creating-actions-for-AI-agents), [Using AI agents](https://support.zendesk.com/hc/en-us/sections/8988994355994-Using-AI-agents).

API authentication protects access to the agent platform. That is a separate boundary from proving that a shopper owns a particular order. This research did not establish a universal customer-verification workflow for all Zendesk configurations. [AI agents API authentication](https://developer.zendesk.com/api-reference/ai-agents/authentication/).

### Agentforce Service Agent: CRM and access-control reference

Salesforce documents Service Agent as a service-focused agent with edition/channel requirements. Its knowledge Data Library can use Knowledge articles, files and configured retrieval sources. Standard actions include creating cases, checking routing availability and cancelling orders; availability and permission requirements vary. These actions are broader than our allowed write scope. [Service Agent overview](https://help.salesforce.com/s/articleView?id=service.bots_service_asa_about.htm&language=en_US&type=5), [Knowledge grounding](https://trailhead.salesforce.com/content/learn/modules/agentforce-service-agent-quick-look/use-knowledge-in-agentforce-for-service), [Standard actions](https://help.salesforce.com/s/articleView?id=ai.copilot_topics_ref_agentforce_service_agent.htm&language=en_US&type=5).

Salesforce explicitly separates unidentified, identified/verified and authenticated users. Depending on the configuration, access comes from the dedicated agent user or the logged-in site's user. Customer context variables identify a person but do not independently enforce access. Private action queries need verified-customer filtering and least-privilege permissions. [Configure Service Agent Access](https://help.salesforce.com/s/articleView?id=ai.agent_user.htm&language=en_US&type=5).

Its setup workshop includes permission assignment, custom actions, conversation preview and deployment through Salesforce service channels. Testing Center documents simulated interactions and session tracing. None of these was trialed here. [Service Agent workshop](https://developer.salesforce.com/workshops/agentforce-workshop/service-agents/1-create-a-service-agent), [Testing Center](https://help.salesforce.com/s/articleView?id=005228642&language=en_US&type=1).

## Feature matrix

Vendor cells summarize the official evidence linked in the preceding sections. “Not established” means insufficient evidence in this review, not proof that the product lacks the capability.

| Dimension | Our implementation now | Initial-product target, v3.1 | Intercom Fin | Zendesk AI agents | Agentforce Service Agent |
|---|---|---|---|---|---|
| Grounded knowledge | Small versioned local corpus and retrieval experiment | Tool-integrated evidence plus citation checks | Multi-source content and answer inspection | Trusted knowledge and configured search | Knowledge/Data Library grounding |
| Live order/product integration | No completed specialist tool workflow | Six typed tools on synthetic records | Configured Data connectors/Tasks | Procedures and external integrations | Standard/custom Salesforce actions |
| Consequential writes | Final write path not built | Only verified mock escalation ticket; no refund/cancel execution | Depends on configured connector scope | Depends on authorized integrations | Broader action catalog, permission dependent |
| Human handoff | Classification is not confirmed handoff | Ticket ID/status verified; failures disclosed | Team escalation and handoff API | Helpdesk flows; exact tenant behavior untested | Case/routing actions; channel configuration needed |
| Customer access boundary | Synthetic prototype, no production login | Server-bound synthetic identity and order ownership | Channel-specific verification guidance | API auth documented; customer ownership flow not established here | Dedicated/user permissions plus verified-ID filtering |
| Conversation context | No completed final memory layer | Slots, six-message window, TTL/reset; fresh records each turn | Conversation API and task attributes | Procedure parameters and conversation logs | Session/customer context; exact retention policy not compared |
| Evaluation | Frozen cases, local DeepEval, retrieval labels | Integrated holdout, safety, tools, memory and calibration | Batch tests and task simulations | Flow/A/B tests and analytics; some EAP | Preview/Testing Center and session tracing |
| Observability | Local redacted evidence; hosted traces unverified | Per-stage/tool traces, timing and safe errors | Source/settings inspection and test transcripts | Logs, dashboard and satisfaction analysis | Session traces and platform logs |
| Interactive delivery | Local Streamlit/CLI | Complete local demonstration | Hosted channels; Agent API access gated | Hosted messaging/email and documented voice capabilities | Salesforce service deployment channels |
| Latency evidence | Historical Prompt C median 5.155 s, p95 6.249 s for a no-tools prompt | Per-path measurement; planned targets are not results | No comparable measured benchmark in this research | No comparable measured benchmark in this research | No comparable measured benchmark in this research |
| Implementation effort | We own Python, tests and local packaging | We implement every initial-product boundary | Configure content, channels, tasks and connectors | Configure knowledge, procedures and integrations | Configure org, permissions, data, actions and channels |

## Lessons for the existing scope

These are engineering inferences from the comparison, not vendor performance claims or additions to our plan.

1. **Finish the evidence path first.** Phase 4 should make policy grounding reproducible, show which section supported the answer and report unsupported requests honestly. Our small corpus can demonstrate this without a knowledge graph.
2. **Treat business operations as contracts.** In Phase 5, typed inputs/results, deterministic eligibility, ownership, tool status and idempotency matter more than adding more agent roles. Keep the six-tool scope and the single permitted mock write.
3. **Distinguish a handoff decision from delivery.** An escalation label is insufficient. The initial product should show a verified mock ticket or a disclosed failure. A vendor's broader human staffing system is outside our prototype.
4. **Keep identity outside the customer's prompt.** A claimed order/customer ID does not prove ownership. Use the server-bound synthetic identity and enforce authorization in tools, following the same conceptual boundary highlighted by Salesforce's access guidance.
5. **Use bounded context, not invented continuity.** Phase 6 should resolve follow-ups while re-fetching current order/tracking facts and proving reset/expiry. Vendor conversation context does not establish a need for long-term memory or autonomous learning.
6. **Measure completion and failure separately.** Tests should check citation support, actual tool results, mandatory escalation, ownership denials and disclosed outages. Neither vendor automated-resolution labels nor our schema-valid outputs substitute for independently defined case correctness.
7. **Measure perceived speed only after the full path exists.** Our no-tools latency cannot predict supervisor/specialist latency. Report p50/p95 by path and timeouts; streaming/status UX can be a later improvement.

## What a fair vendor trial would need

This desk research can compare documented architecture and interfaces. It cannot rank accuracy, hallucination rates, safe completion, uptime, latency or total cost. No vendor was contacted, no account was created, no purchase was made and no customer conversation was sent.

A future optional trial would need the same synthetic documents, cases, customer/ownership boundaries and allowed actions for every system; documented product editions; matched knowledge versions; comparable configured integrations; repeated sessions; and an agreed human scoring rubric. Trial cases should include unsupported policy questions, wrong-owner order requests, missing fields, prompt injection, multi-intent requests, connector timeouts and failed handoffs. Measure end-to-end time, verified outcome, citations, unauthorized disclosure/actions and handoff evidence. Keep development cases separate from held-out cases.

A commercial deployment would additionally need channel-specific identity, secrets management, tenant isolation, operational ownership and agreed data retention. Those are deployment requirements beyond the synthetic initial-product demonstration. Pricing and procurement were not compared because usage assumptions, editions and integration scope have not been defined. An actual trial or vendor access is optional future input and does not block our current Phase 4 work.

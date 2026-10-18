# Memory Pad — e-commerce agent comparison and product ideas

Created / researched: **2026-10-13, America/New_York**. Owner: project team. Status: living research and idea register.

This pad captures market observations, feature comparisons, and extensions we may add to the core product later. It is a project document, separate from the agent's runtime conversation memory. The [Architecture and Plan](architecture_and_plan.md) remains the authority for the approved build; the [task checklist](task_list.md) tracks implementation. Recording an idea here does not add it to the delivery scope. Knowledge graph work remains deferred until the initial product succeeds.

## How to use this pad

Append new ideas with a stable `MP-` ID, the user problem, a proposed experiment, dependencies, and a decision. Keep the original observation when an idea changes; add a dated decision instead of quietly replacing it. Promote an idea into the architecture and task checklist only after deciding its scope and acceptance evidence. Update the comparison when a material vendor capability changes, recording the source and research date.

Decision labels:

| Label | Meaning |
|---|---|
| **CORE — existing commitment** | Already required by the approved architecture; finish and evaluate it. |
| **CANDIDATE — after acceptance** | Useful extension to evaluate after the initial product passes its gates. |
| **DEFERRED** | Deliberately excluded from the initial build; revisit when dependencies and a measured need exist. |
| **PARKED** | Recorded for discussion; no implementation commitment or schedule. |

## What “real-time e-commerce agent” means in this comparison

An interactive agent that uses store knowledge and, where configured, current business-system data during a customer conversation. This comparison does not establish hard real-time guarantees or a response-time SLA. It covers documented products available in the market, rather than a hands-on vendor benchmark. We did not sign up, connect a store, contact vendors, or run customer sessions.

Vendor capabilities below come from official documentation checked on the research date. A documented capability can require a particular subscription, integration, channel, permissions, or managed-access enrollment. A blank or “not established” cell means this research did not verify it. It does not prove absence. Accuracy, reliability, latency, and cost cannot be ranked from feature lists or vendor marketing claims.

The earlier [market comparison](market_comparison.md) preserves the broader support-platform analysis. This pad adds a closer commerce reference and a running product backlog.

## Market references and what we can learn

### Gorgias AI Agent — closest commerce workflow reference

Gorgias documents Shopify-oriented support and shopping roles, combining merchant knowledge, configurable skills, store data, connected actions, and team handover. Support examples include tracking, returns, missing items, and order changes; shopping assistance is broader than our current support scope. Channels and subscription eligibility vary. [AI Agent explained](https://docs.gorgias.com/en-US/ai-agent-explained-497772).

Its Shopify action documentation describes cancellation, address editing, and item removal, with fulfillment checks and related refunds where applicable. The merchant must account for whether changes reach downstream fulfillment systems. [Shopify actions and limitations](https://helpcenter.gorgias.com/en-US/ai-agent-actions-make-changes-to-shopify-orders-757792).

Actions can contain ordered app steps, conditions, and shopper confirmation. Irreversible actions enable confirmation automatically in the documented setup flow. This is a useful future reference for a controlled transaction workflow; our initial product permits only a mock escalation write. [Create an action](https://docs.gorgias.com/en-US/create-an-action-for-ai-agent-567325).

Gorgias Playground supports draft tests and customer/channel scenarios. Importantly for any future trial, enabling actions in a test conversation can change real customer or order data; conversation testing alone is not proof that connected writes are simulated. [Test conversations](https://docs.gorgias.com/en-US/preview-ai-agent-responses-with-test-conversations-828087).

### Intercom Fin — knowledge and process-design reference

Fin documents multi-source answers, audience-specific content, configurable style, answer inspection, and human handoff. Its overview also lists an e-commerce shopping role; that role's tenant availability and transactional coverage were not separately verified here. [Fin overview](https://www.intercom.com/help/en/articles/7120684-fin-ai-agent-explained).

Fin Tasks combines external connectors, branching, temporary attributes, and team escalation. Tasks require eligible plans. The current setup page identifies Procedures as the successor with managed availability, so a trial should establish which workflow version is actually enabled. Draft simulations provide a useful reference for testing branches before release. [Fin Tasks](https://www.intercom.com/help/en/articles/10257113-how-to-set-up-fin-tasks).

Connector guidance recommends channel-appropriate identity verification and server-side customer access checks. It also requires explicit connector failure handling rather than assuming automatic recovery. These are directly relevant to our ownership and failure-path design. [Data connectors FAQs](https://www.intercom.com/help/en/articles/9916507-data-connectors-faqs). Reusable answer tests are documented separately. [Batch testing](https://www.intercom.com/help/en/articles/10521711-batch-test-fin-ai-agent).

### Zendesk AI agents — service operations reference

The current overview documents knowledge answers, generative procedures, authorized actions, API integration, analytics, and messaging/email/voice channels. It is a general support platform; commerce behavior depends on the configured business systems. Plan allowances and integration configuration matter. Older Essential and zero-training generations are identified as legacy, so a comparison should name the current generation rather than assume all historical feature pages describe the same product. [Current AI agents overview](https://support.zendesk.com/hc/en-us/articles/6970583409690-About-AI-agents).

The useful lesson is to measure the whole service outcome, including unresolved cases and human transfer. The precise shopper-verification and handoff behavior of a configured Zendesk tenant was not established in this review.

### Salesforce Agentforce Service Agent — access and CRM workflow reference

Agentforce can ground service answers in a configured Data Library containing Knowledge articles and other sources. [Knowledge grounding](https://trailhead.salesforce.com/content/learn/modules/agentforce-service-agent-quick-look/use-knowledge-in-agentforce-for-service). Its service action catalog includes order lookup, order cancellation, case creation, and representative-availability checks, with edition/add-on requirements. These are configurable platform capabilities rather than evidence of a ready-made integration with our synthetic shop. [Service action catalog](https://help.salesforce.com/s/articleView?id=ai.copilot_topics_ref_agentforce_service_agent.htm&language=en_US&type=5).

Salesforce distinguishes unidentified, verified, and authenticated customers. Identity context does not itself restrict records: action queries and permissions must enforce access. That separation is a strong reference for our server-bound synthetic identity and tool ownership checks. [Service Agent access](https://help.salesforce.com/s/articleView?id=ai.agent_user.htm&language=en_US&type=5). Testing Center documents simulated sessions and result inspection. [Testing Center](https://help.salesforce.com/s/articleView?id=005228642&language=en_US&type=1).

## Feature comparison

**Project snapshot:** baseline and bounded single-agent experiments exist; seven policy/FAQ documents, local embeddings/Chroma, and sourced RAG experiments are implemented. A bounded supervisor/three-specialist graph, six typed tools, server-bound synthetic identity and verified local mock tickets are now implemented. Repaired core specialist/composer paths have synthetic live smoke evidence; bounded projection memory is now implemented; its five-conversation live comparison is measured. Adaptation and final acceptance remain open. See [Phase 5 implementation](phase5_tools_and_graph.md). Detailed current evidence lives in [implementation status](implementation_status.md) and [retrieval design](retrieval_design.md); the table deliberately separates those stages.

Vendor cells describe documented capabilities, not tested correctness. Links in each cell point to the relevant official reference.

| Feature / shopper need | Our implementation | Approved initial product | Gorgias AI Agent | Intercom Fin | Zendesk AI agents | Agentforce Service Agent |
|---|---|---|---|---|---|---|
| Policy and FAQ answers | Versioned local retrieval and citation experiments | Specialist retrieval with evidence or abstention | Merchant [knowledge](https://docs.gorgias.com/en-US/ai-agent-explained-497772) | Multi-source [content](https://www.intercom.com/help/en/articles/7120684-fin-ai-agent-explained) | Trusted [knowledge](https://support.zendesk.com/hc/en-us/articles/6970583409690-About-AI-agents) | [Data Library](https://trailhead.salesforce.com/content/learn/modules/agentforce-service-agent-quick-look/use-knowledge-in-agentforce-for-service) |
| Current order/tracking facts | Ownership-checked tools now exist; broader final quality checks pending | Ownership-checked order and tracking tools | Shopify data and [support skills](https://docs.gorgias.com/en-US/ai-agent-explained-497772) | Configured [connectors](https://www.intercom.com/help/en/articles/10257113-how-to-set-up-fin-tasks) | Configured [API integration](https://support.zendesk.com/hc/en-us/articles/6970583409690-About-AI-agents) | Catalogued [order actions](https://help.salesforce.com/s/articleView?id=ai.copilot_topics_ref_agentforce_service_agent.htm&language=en_US&type=5) |
| Returns/refunds/cancellations | Deterministic eligibility and human review; no transaction execution | Eligibility information and human escalation | Connected [order actions](https://helpcenter.gorgias.com/en-US/ai-agent-actions-make-changes-to-shopify-orders-757792) | Configured [processes](https://www.intercom.com/help/en/articles/10257113-how-to-set-up-fin-tasks) | Authorized [actions](https://support.zendesk.com/hc/en-us/articles/6970583409690-About-AI-agents) | [Cancellation action](https://help.salesforce.com/s/articleView?id=ai.copilot_topics_ref_agentforce_service_agent.htm&language=en_US&type=5) |
| Product discovery and sales | Public synthetic catalog; support only | Product facts tool; recommendations/discounts outside scope | [Shopping role](https://docs.gorgias.com/en-US/ai-agent-explained-497772) | [E-commerce role](https://www.intercom.com/help/en/articles/7120684-fin-ai-agent-explained); access unverified | Commerce-specific coverage not established | Sales capability outside this Service Agent review |
| Customer authorization | Synthetic account/session binding and tool ownership checks implemented | Identity supplied by server; ownership checked in tools | Connected store access documented; exact shopper verification not established here | Channel verification plus [server checks](https://www.intercom.com/help/en/articles/9916507-data-connectors-faqs) | Exact shopper ownership flow not established | Verified-ID [record filtering](https://help.salesforce.com/s/articleView?id=ai.agent_user.htm&language=en_US&type=5) |
| Human handoff | Verified local mock ticket or explicit unconfirmed-handoff disclosure | Verified mock ticket or disclosed failure | Team [handover](https://docs.gorgias.com/en-US/ai-agent-explained-497772) | Configurable [team escalation](https://www.intercom.com/help/en/articles/10257113-how-to-set-up-fin-tasks) | Tenant handoff outcome untested in this review | [Case/routing actions](https://help.salesforce.com/s/articleView?id=ai.copilot_topics_ref_agentforce_service_agent.htm&language=en_US&type=5) |
| Multi-step operations | Bounded supervisor/three-specialist graph implemented; core live smoke measured | Supervisor + three specialists; six typed tools | Ordered app [action steps](https://docs.gorgias.com/en-US/create-an-action-for-ai-agent-567325) | Branching [Tasks/Procedures](https://www.intercom.com/help/en/articles/10257113-how-to-set-up-fin-tasks) | [Generative procedures](https://support.zendesk.com/hc/en-us/articles/6970583409690-About-AI-agents) | Configured [service actions](https://help.salesforce.com/s/articleView?id=ai.copilot_topics_ref_agentforce_service_agent.htm&language=en_US&type=5) |
| Conversation continuity | Bounded projection memory, scoped entity references, TTL/reset and fresh-fact tests implemented; live comparison measured | Bounded session context; fresh facts each turn; reset/TTL | Interactive [skills](https://docs.gorgias.com/en-US/ai-agent-explained-497772); retention not compared | [Temporary task attributes](https://www.intercom.com/help/en/articles/10257113-how-to-set-up-fin-tasks) | Conversation [follow-ups](https://support.zendesk.com/hc/en-us/articles/6970583409690-About-AI-agents); retention not compared | [Customer context](https://help.salesforce.com/s/articleView?id=ai.agent_user.htm&language=en_US&type=5); retention not compared |
| Style and personalization | Local per-customer adaptation implemented; final acceptance pending | Bounded versioned style feedback in terminal/Streamlit; safety rules immutable | Merchant [voice/settings](https://docs.gorgias.com/en-US/ai-agent-explained-497772) | [Style/audience controls](https://www.intercom.com/help/en/articles/7120684-fin-ai-agent-explained) | Comparable preference mechanism not established | Comparable preference mechanism not established |
| Test and inspect | Frozen cases, local DeepEval, saved experiment outputs | End-to-end safety, holdout, repeatability, and human calibration | [Playground/draft tests](https://docs.gorgias.com/en-US/preview-ai-agent-responses-with-test-conversations-828087) | [Batch tests](https://www.intercom.com/help/en/articles/10521711-batch-test-fin-ai-agent) and simulations | [Analytics](https://support.zendesk.com/hc/en-us/articles/6970583409690-About-AI-agents); testing tools not evaluated here | [Testing Center](https://help.salesforce.com/s/articleView?id=005228642&language=en_US&type=1) |
| Delivery channels | Local Streamlit and CLI | Complete local demonstration | [Email/chat/SMS/social](https://docs.gorgias.com/en-US/ai-agent-explained-497772) | [Chat/email/voice and others](https://www.intercom.com/help/en/articles/7120684-fin-ai-agent-explained) | [Messaging/email/voice](https://support.zendesk.com/hc/en-us/articles/6970583409690-About-AI-agents) | Channel availability not compared in this pad |

There is no comparable measured vendor latency, accuracy, privacy-canary score, or verified-outcome rate in this research. Our retrieval development results cannot be compared with a vendor's automated-resolution percentage: they have different denominators, datasets, and outcomes.

## Running idea and extension backlog

Recommendations below are our engineering judgments, informed by the comparisons. “Core” entries restate existing commitments; every other entry is an idea, not authorization to expand the initial product.

| ID | Idea / customer problem | Decision and recommended position | Dependencies | Experiment / evidence before adoption |
|---|---|---|---|---|
| MP-01 | Category-aware policies: a footwear rule must not be applied to electronics | **CORE — existing commitment**, Phase 4 applicability work | Validated category metadata, product-category mapping, conflict preservation | Mixed-category and unknown-category queries; no silent removal of governing or conflicting evidence |
| MP-02 | Evidence view: shopper/analyst can inspect which policy section supported a claim | **CORE — existing commitment**, citation rendering and final grounding | Stable source/version references; final response contract | Citation resolution, supported-claim review, no citation on an unsupported answer |
| MP-03 | Verified handoff: show a ticket only after creation succeeds | **CORE — existing commitment**, initial mock ticket path | Typed escalation tool, idempotency, failure disclosure | Repeated requests, failed writes, sanitized packet; no invented ticket ID |
| MP-04 | Protected order tools: a shopper must only see their own records | **CORE — existing commitment**, synthetic identity boundary | Server-bound identity, ownership checks, tool allowlists | Wrong-owner and prompt-spoofing cases denied; no private record leakage |
| MP-05 | Multi-turn follow-ups: “what about that order?” without stale facts | **CORE — existing commitment**, bounded memory and reset | Session isolation, TTL, slots, current-turn record refresh | Memory on/off comparison, reset/expiry, two-session isolation; inspect intermediate checkpoints |
| MP-06 | Safe preference feedback: concise/detailed answers without weakening policy | **CORE — existing commitment**, bounded adaptation | Feedback signals, profile versions, rollback | Before/after style results; adversarial feedback cannot remove safety outcomes |
| MP-07 | Read-only commerce adapter: move from synthetic records to a shop sandbox | **CANDIDATE — after acceptance**, first integration extension | Accepted tool contracts, approved sandbox access, scoped authentication, adapter fault tests | Same contract suite against fixtures and sandbox; deny wrong-owner data; expose freshness/errors |
| MP-08 | Analyst console: review escalations, source evidence, and unresolved causes | **CANDIDATE — after acceptance**, useful small Streamlit extension | Verified ticket store, sanitized packets, access separation | Analyst can reproduce the reason and choose a next step without seeing unrelated customer data |
| MP-09 | Scenario simulator: rerun branching conversations before policy releases | **CANDIDATE — after acceptance**, evaluation tooling | Final workflow and deterministic mock tools, saved cases, separate dev/holdout sets | Repeat multi-turn failures without touching production systems; compare actual outcomes, not just judge scores |
| MP-10 | Knowledge review queue: missing answers and contradictions become content tasks | **CANDIDATE — after acceptance**, knowledge maintenance | Unresolved reason codes, reviewed content versions, regression suite | Human approves changes; reindex/version checks; frozen and new cases retain correctness |
| MP-11 | Better retrieval at corpus scale: hybrid lexical/vector search or reranking | **DEFERRED**, add only after measured retrieval failures | Larger representative corpus and untouched labels, baseline latency/cost | Ablation of keyword search/reranker versus current retriever; improve supported answers without masking abstention errors |
| MP-12 | Knowledge graph: connect products, categories, policy exceptions, and document versions | **DEFERRED**, explicitly after successful initial product | Proven relational question need, trusted entity/edge provenance, simpler metadata/hybrid baseline | Compare on new cross-document relationship cases; every edge cites authority; authorization stays in tools |
| MP-13 | Location/weather ETA: explain plausible delivery delays | **DEFERRED**, existing prototype remains outside initial evaluation | Carrier facts, location resolution, time-stamped weather/routes, reviewed rule parameters | Distance bands and storm/snow delay rules versus known outcomes; uncertainty shown; no guaranteed arrival date |
| MP-14 | Confirmed transaction execution: returns, refunds, cancellations | **DEFERRED**, broader write scope | Real policy authority, verified identity, human/merchant approval design, scoped credentials, idempotency and reconciliation | Preview → confirmation → authorized execution → read-back; timeout cannot produce a false success; fulfillment races tested |
| MP-15 | Channel adapters: email/WhatsApp/chat widget with consistent policy behavior | **DEFERRED**, after local product and one store adapter | Channel-specific identity, retention, delivery status, duplicate-event handling | Same outcome suite per channel; no cross-channel identity assumption; replay-safe events |
| MP-16 | Streaming/status UI: show useful progress during longer tool paths | **CANDIDATE — after acceptance**, if latency evidence supports it | Measured final-path timings, safe status events | Improve perceived waiting; no partial unsupported answer or premature action-success message |
| MP-17 | Multilingual support and product photos/invoices | **PARKED**, separate scope decision | Locale policy, translation/image privacy, representative labeled cases | Meaning and safety parity by language; extraction uncertainty; unsupported visual claims abstain |
| MP-18 | Shopping recommendations, upsells, coupons, abandoned-cart recovery | **PARKED**, separate sales role/product | Inventory/pricing authority, commercial rules, user-consent/channel decisions | Product-fit and inventory correctness; support complaints are not converted into sales pressure |
| MP-19 | Authenticated production preferences across sessions | **DEFERRED**; local synthetic style profiles are implemented in Phase 7 | Explicit retention/deletion choices, authenticated identity, tenant isolation | Forget/export/reset semantics verified; no private order facts promoted into permanent preferences |

For MP-13, the earlier “about 1,000 miles takes three days or more; storm/snow can add a couple of days” discussion is a proposed estimation rule, not a carrier commitment or measured delivery model. The existing prototype can seed a future experiment; adoption requires fresh inputs, rule validation, and clear uncertainty.

## Recommended order after the initial product passes

1. Start with a read-only store sandbox adapter (MP-07) and a compact analyst view (MP-08). They make the current support workflow useful without introducing refunds or cancellations.
2. Add scenario replay and knowledge review (MP-09/10). Establish how new policies and integrations are checked before release.
3. Measure retrieval and latency on broader cases before selecting hybrid retrieval, a graph, or streaming (MP-11/12/16). A feature should solve an observed gap.
4. Consider external ETA and channel adapters (MP-13/15), then transaction writes (MP-14) as a separate consequential-action project. Multilingual/vision and sales remain independent decisions.

This ordering is a recommendation for discussion, not a revised delivery schedule. The immediate build continues within the approved Phase 4 and later initial-product tasks.

## Promotion template for a new entry

```text
ID: MP-xx
Date / proposer:
User problem and example:
Observation / official source, if any:
Proposed behavior:
Current decision: CORE / CANDIDATE / DEFERRED / PARKED
Dependencies and data required:
Smallest experiment:
Acceptance measures and known failure cases:
Scope/cost/latency effect:
Dated decision and rationale:
Architecture section + task ID when promoted:
```

Before an optional vendor trial, choose the relevant edition and integration, use the same synthetic knowledge/cases and allowed actions, and score verified outcomes, ownership denials, unsupported answers, conflicts, timeouts, and failed handoffs. Keep tuning cases separate from holdouts. A trial with connected actions requires a genuine sandbox; a vendor's “test conversation” label alone is insufficient, as the Gorgias and Intercom connector documentation illustrates. [Gorgias test actions](https://docs.gorgias.com/en-US/preview-ai-agent-responses-with-test-conversations-828087), [Intercom connector testing](https://www.intercom.com/help/en/articles/9916507-data-connectors-faqs).

## Dated notes

| Date | Note / decision | Effect |
|---|---|---|
| 2026-10-13 | Created Memory Pad at the user's request; added Gorgias to the existing Fin/Zendesk/Agentforce research. | Living comparison and idea register; no change to approved scope. |
| 2026-10-13 | Existing core commitments recorded as MP-01–06; later ideas recorded as MP-07–19. | Core remains three specialists, six tools, synthetic records, and one mock escalation write. |
| 2026-10-13 | Knowledge graph retained as MP-12, deferred until the initial product succeeds. | No Phase 4 graph dependency. |

| 2026-10-15 | Phase 5 now implements MP-03/04 core mock handoff and synthetic ownership boundaries, plus current-turn citations. | Local tools/graph tested; production authentication, memory and final acceptance remain open. |

| 2026-10-15 | Phase 6 implements MP-05 bounded follow-ups with a projection-only checkpointer; raw working state is not retained. | Reset/expiry/version deletion and fresh-record tests run locally; adaptation remains Phase 7. |

| 2026-10-15 | MP-05 measured: four of four reference-dependent follow-ups answered with memory on versus zero off; reset still clarifies. | Five authored development conversations, not vendor/held-out accuracy; see phase6_memory.md. |

## Observability backend decision — 2026-10-16

Keep LangSmith for the initial product: it is already integrated and Phase 8 verifies hosted metadata trees, privacy and failure isolation. Continue using DeepEval for evaluation. LangSmith supports agent tracing and multiple deployment options ([official observability overview](https://www.langchain.com/langsmith/observability)).

**MP-20 — optional Langfuse exporter:** reconsider if open-source self-hosting or a broader OpenTelemetry strategy becomes a concrete requirement. Langfuse supports LangChain/LangGraph integrations ([official integrations](https://langfuse.com/integrations)) and open-source self-hosting ([official deployment guide](https://langfuse.com/self-hosting)). Self-hosting adds infrastructure, upgrades, storage and retention responsibilities; it does not remove the need to exclude sensitive content. Our explicit metadata boundary can be reused, but a Langfuse exporter/read-back/failure test would still need implementation. No dual-backend deployment or migration is authorized by this comparison alone.

## First production review — 2026-10-17

The [production review](production_review.md) records distributed Postgres-backed state, dependency-aware parallel reads, deterministic normalization plus a separately evaluated injection classifier, and OTel Collector export. These are deferred design items, not implemented features. The proposed 40% p95 reduction is unmeasured. User priority is to repair the existing refund-intent/privacy-routing defects and validate a new candidate on an independently authored blind holdout before expanding scope.

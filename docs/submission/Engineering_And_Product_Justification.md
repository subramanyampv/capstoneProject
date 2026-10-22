# Engineering and Product Justification

This Customer Support project uses the framework-based track. The application model interprets requests, chooses permitted tools and drafts explanations; deterministic services retain authority over identity, eligibility, safety routing and recorded actions.

## Architecture and responsibility

A LangGraph supervisor routes to three bounded LangChain specialists: Order and Shipping, Policy and Product, and Escalation. Six typed tools expose order lookup, tracking lookup, catalog lookup, policy search, eligibility calculation and mock escalation creation. The registry checks arguments, tool permissions and budgets, and injects the server-selected customer identity. A model cannot select another customer's identity or execute a refund.

An immutable request-obligation contract records recognized requirements independently of the model's plan. Post-processing checks actual current-turn evidence against those requirements. This prevents an apparently successful plan from silently dropping a recognized question. The contract and claim screening remain bounded language rules, so semantic review supplements structural checks.

## Main choices and tradeoffs

| Choice | Benefit | Cost or limitation |
|---|---|---|
| Explicit graph and three specialists | Inspectable routing, isolated context and small tool allowlists | Sequential calls add latency; splitting work does not itself improve correctness |
| Versioned policy retrieval with normalized embeddings and a persistent vector index | Grounded policy citations and reproducible retrieval identity | Requires ingestion and retrieval calibration; a replacement embedding model needs a new compatible index |
| Code-based eligibility | Decisions use configured dates, thresholds and order facts | Rules cover a narrow synthetic policy domain |
| Mock escalation as the only action write | Demonstrates routing, idempotency and verified persistence | Does not prove real customer service delivery or financial transaction safety |
| Separate in-process projection memory | Follow-ups retain verified references without retaining full tool/evidence state | Lost on restart; masking can miss unusual personal text |
| Consent-controlled style preferences | Reversible adaptation without changing policy or tool authority | Heuristic feedback thresholds can overreact; no satisfaction improvement is established |
| Sanitized local records plus optional hosted metadata traces | Auditable control flow and failure categories | Metadata traces cannot explain every semantic error; redaction is bounded |
| Deterministic checks plus two separate judges and independent review | Combines exact invariants with broader answer inspection | Judge disagreements and missing context limit score interpretation; AI review is not human calibration |

## Memory, adaptation and privacy

The working support graph has no transcript checkpointer. A separate projection retains six masked user messages, outcome markers, verified entity references and allowlisted intent metadata. Current order status, eligibility, policy passages and assistant answer prose are excluded. Current-turn tools must verify facts again. Sessions are isolated, default idle expiry is 1,800 seconds, and `/reset` deletes the retained projection.

Preferences persist separately per synthetic customer. Only validated verbosity and format fields influence composition. Two matching direction signals among the recent ten can change style; consumed signals cannot repeatedly trigger changes. Consent, version history, disabling, reset and scoped deletion are exposed. `/reset` clears session context; `/forget-preferences` deletes saved style history and feedback. Safety rules and eligibility do not receive editable style settings.

## Resource and failure controls

Each request permits at most four specialist handoffs, eight tool calls and twelve model calls. Specialists have four model steps, with three for escalation; one replan and one structured-output repair are permitted. A recursion backstop is forty graph steps. Tool deadlines, bounded retrieval capacity and classified provider errors avoid unbounded retries. Exhaustion produces an explicit safe outcome or escalation path; success is claimed only after the relevant operation is verified.

## Evaluation and release decision

Frozen public cases, repeated safety scenarios, retrieval labels, fault injection, memory/reset demonstrations and adaptation comparisons test different properties. Quality judges score the same saved outputs separately; scores are not averaged into a safety pass. Exact source and output identities bind each receipt to its tested build.

Earlier runs exposed fabricated policy, missed escalation, incomplete requests and insufficient handoff integrity. Later semantic inspection found an unsupported eligibility explanation and misleading mock-handoff wording despite structurally correct outcomes. After those repairs and a 60-second policy-tool deadline change, a full public run still missed R09 because a claim guard over-blocked a supported threshold explanation. Independent review then recorded six major findings, including timestamp/fallback defects. Subsequent guard, timestamp, graph and service changes are included in the frozen 589-test clean-copy checkpoint. Current-configuration end-to-end, safety, quality, review and demo evidence remains pending; no historical pass certifies it. See the [failure analysis](Debugging_And_Failure_Analysis.md) and [Evaluation Report](Evaluation_Report.md). Business outcomes, production authentication, durable conversation storage, real commerce writes and broad semantic guarantees remain future work.

## Future Targets & Production Evolution Roadmap

To transition this architecture from a validated prototype to a large-scale, high-throughput enterprise deployment, the following technical targets are defined:

1. **Distributed State & Session Persistence**:
   - *Target*: Replace local SQLite and JSONL session memory with a high-availability, distributed key-value store (**Redis** or **DynamoDB**).
   - *Benefit*: Enables stateless, horizontally scaled container replicas (Kubernetes pods) with automatic session TTLs and distributed locking across active customer conversations.

2. **Event-Driven Carrier Integration (Webhooks vs. Polling)**:
   - *Target*: Supplement on-demand order and tracking tool polling with an event-driven webhook ingestion pipeline (e.g., Shippo, EasyPost, carrier webhooks).
   - *Benefit*: Enables proactive status updates (e.g., notifying customers when an order is delayed or out for delivery) rather than relying exclusively on customer-initiated queries.

3. **Asynchronous Enterprise Ticketing Integration (HITL)**:
   - *Target*: Transition from local synthetic mock ticket generation to live, authenticated enterprise service desks (**Zendesk**, **Freshdesk**, or **Salesforce Service Cloud**) via secure webhook queues with bi-directional synchronization.
   - *Benefit*: Seamlessly bridges autonomous AI escalation with human agent workflows while maintaining non-negotiable safety and privacy boundaries.

4. **Hierarchical Context Summarization for Extended Dialogues**:
   - *Target*: Implement an asynchronous summarization agent that condenses conversational turns beyond 15 interactions into a compact, structured customer profile block.
   - *Benefit*: Prevents context window saturation, lowers per-turn inference costs, and maintains multi-turn entity recall over extended support relationships.

5. **Multi-Region Policy Ingestion & Hybrid Vector Search**:
   - *Target*: Support multi-region policy indexing combining dense vector embeddings with sparse BM25 keyword matching (hybrid search) and cross-encoder re-ranking against an OpenAI-compatible endpoint.
   - *Benefit*: Minimizes retrieval edge cases across diverse international legal jurisdictions and multilingual customer queries.


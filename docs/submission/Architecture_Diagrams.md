# Architecture Diagrams — Components, Request Flow, Turn Sequence

Status: current implementation, matching `src/capstone_agent/support/graph.py` (graph wiring at
lines 648–662) and the compose gate inside `compose` (attempt loop ~525–566). Vendor-neutral
labels: "application model" is any OpenAI-compatible chat model configured through environment
variables; no specific model or provider names are used. Diagrams are Mermaid (render on GitHub)
and are backed by the prose design in the repository docs.

## 1. Component diagram (static architecture)

```mermaid
flowchart TD
  subgraph Interaction
    CLI[CLI / batch evaluation runner]
    UI[Streamlit chat + evaluation views]
  end
  subgraph Control["LangGraph control graph (support/graph.py)"]
    GUARD[guard_in: safety, command, scope routes]
    PLAN[plan: supervisor decomposition]
    DISPATCH[dispatch: per-step routing]
    COMPOSE[compose: draft, obligation audit, gates, bounded repair]
  end
  subgraph Specialists
    OS[order_shipping agent]
    PP[policy_product agent]
    ESC[escalation agent]
  end
  subgraph Registry["Tool registry (typed schemas, per-agent allowlist, budgets, fault flags)"]
    TOOLS[lookup_order · get_tracking_events · search_policy · get_product_details · check_return_eligibility · create_escalation]
  end
  subgraph Domain["Deterministic domain services (no LLM dependency)"]
    ORD[(Synthetic orders & tracking data)]
    RET[(Retrieval: local embedding + persisted vector index, allowlisted passages)]
    Q[Mock escalation queue + ticket store]
    MEM[Bounded memory projection + preference store]
    PRIV[Redaction / privacy minimization]
  end
  subgraph Ops["Operations & evidence"]
    CFG[Config loader + validator]
    LOG[JSONL run records, redacted]
    TRACE[Stage tracing hooks + hosted tracing (masked)]
    EVAL[Evaluation harness, dual judges, consistency sampler]
  end
  CLI --> Control
  UI --> Control
  GUARD --> PLAN --> DISPATCH
  DISPATCH --> OS & PP & ESC
  DISPATCH -->|plan complete| COMPOSE
  OS & PP & ESC -->|allowlisted calls only| Registry
  TOOLS --> ORD & RET & Q
  COMPOSE -->|verified outcome| Interaction
  MEM -.->|per-turn projection in / slots out| Control
  Control --> LOG & TRACE
  LOG --> EVAL
  CFG -.-> Control & Registry & Ops
```

## 2. Request lifecycle flowchart (actual graph nodes and routes)

```mermaid
flowchart TD
  START([START]) --> G[guard_in]
  G -->|safe request| P[plan (supervisor)]
  G -->|blocked intent| RF[refuse → END]
  G -->|action outside product scope| UC[unsupported_command → END]
  G -->|order reference required| MR[missing_reference → END]
  G -->|withdrawal request| WD[withdrawal → END]
  G -->|return status query| RS[return_status → END]
  P --> D[dispatch]
  D -->|step: order_shipping| OS[order_shipping agent]
  D -->|step: policy_product| PP[policy_product agent]
  D -->|escalation trigger and no ticket| ESC[escalation agent]
  D -->|plan complete| C[compose]
  OS & PP & ESC --> A{after_specialist}
  A -->|more steps| D
  A -->|one replan allowed| RP[replan] --> D
  C --> K{compose gate, bounded attempts}
  K -->|draft passes: obligations audited, citations ⊆ retrieved allowlist, no conflicts| END_([END: verified response, outcome code-owned])
  K -->|first failure| C
  K -->|must-escalate without verified ticket| ESC
```

Everything inside `compose` is code-owned: the draft outcome is forced to the verified
outcome, obligated tool evidence is audited row-by-row, rule and authoritative-document
citations are completed only from passages actually retrieved this turn, and a final failure
after the bounded repair falls back to a safe abstention template (never an unsupported claim).

## 3. Turn sequence diagram (policy question with optional escalation path)

```mermaid
sequenceDiagram
    actor Cust as Customer
    participant App as CLI / UI
    participant Mem as Bounded memory (separate store)
    participant Run as SupportAgent.run
    participant Sup as Supervisor (application model)
    participant Ful as dispatch + fulfill (code)
    participant Spec as Specialist agent (application model)
    participant Tools as Tool registry + retrieval (code)
    participant Comp as Composer (application model)
    participant Gate as Compose gate + guards (code)
    participant Q as Mock escalation queue
    participant Log as Redacted record + tracing

    Cust->>App: request (+ server-side session identity)
    App->>Mem: read per-session projection
    Mem-->>App: bounded context (facts, clarifications)
    App->>Run: run(query, identity, memory_context)
    Run->>Run: derive obligation contract (immutable this turn)
    Run->>Run: guard_in (safety / scope / reference routes)
    Run->>Sup: plan(task, intents, order reference)
    Sup-->>Run: typed plan
    Run->>Ful: dispatch first step
    Ful->>Tools: pre-run obligated tools (e.g. search_policy) before model call
    Tools-->>Ful: retrieved passages + allowlisted citation refs
    Ful->>Spec: sub-task + current-turn facts + allowed_citations
    Spec-->>Ful: typed specialist result (facts only, no free claims)
    Ful->>Comp: compose draft(context, allowed_citations)
    Comp-->>Gate: draft answer + citations
    Gate->>Gate: force verified outcome; audit obligations; complete rule and authoritative-document citations from retrieved refs only
    alt gate failure (first time)
        Gate->>Comp: bounded repair attempt (≤1)
        Comp-->>Gate: repaired draft
    end
    opt escalation trigger and no verified ticket
        Gate->>Q: create_escalation (deterministic guard)
        Q-->>Gate: ticket {id, queue, priority, packet_hash}
    end
    Gate-->>Run: final state (response, audit rows, flags, repairs)
    Run-->>App: outcome, citations, tool_records, latency, tokens
    App->>Mem: update bounded slots (redacted)
    Run->>Log: append redacted JSONL record + stage timings
    App-->>Cust: verified answer / explicit unknown / refusal / mock handoff notice
```

## 4. Invariants the diagrams encode

- Outcomes are code-owned: the graph, not the model text, decides ANSWERED /
  INSUFFICIENT_EVIDENCE / ESCALATED / refusal classes.
- Citations can only be model-selected or gate-completed from passages retrieved in the same
  turn and inside the allowlist; an incomplete obligation is never "completed" by invention.
- The obligation contract is derived before planning and audited independently after tool
  execution (row per obligation with evidence_complete).
- Budgets are hard: per-case model-call budget at the gateway, one replan, one compose repair,
  recursion limit 40; escalation fires deterministically when a trigger requires it and no
  verified ticket exists.
- Persistence is redacted before logging; hosted tracing carries masked payloads only;
  escalation handoffs are mock tickets whose packet hash is read-back verifiable.

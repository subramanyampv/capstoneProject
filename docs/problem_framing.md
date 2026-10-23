# Problem Framing Document

**Scenario:** E-Commerce Customer Support  
**Implementation Track:** Framework-Based (LangGraph / LangChain Multi-Agent Core)  
**Document Scope:** Specification, User Roles, Target Metrics, and Operational Boundaries (≤2 Pages)

---

## 1. Users, Domain & Operational Scope

### User Personas
1. **Primary User (Online Shopper):** A retail customer seeking rapid, accurate status updates, return/refund eligibility checks, shipping delivery timelines, and product specification clarity.
2. **Secondary User (Tier-1 Support Analyst):** A human customer service representative who receives escalated tickets containing structured reasons, verified citations, audit trails, and priority rankings when an issue exceeds autonomous bot authority.

### Multi-Source Support Domain
Customer support resolutions depend on three independent, strictly segregated data sources:
- **Unstructured Company Policies:** Authoritative rules governing return windows, warranty durations, restocking fees, and mandatory human review thresholds.
- **Structured Transactional Records:** Deterministic database records tracking order lifecycle states (`processing`, `shipped`, `delivered`), line items, and delivery dates.
- **Physical Carrier Scans:** Stale or live event timestamps and geographic checkpoints emitted by logistics carriers.

### Operational Boundaries
* **In Scope:** Read-only order lookups, carrier tracking checkpoints, rule-based delivery estimates, vector semantic policy retrieval, deterministic eligibility calculations, session memory follow-ups, reversible response-style adaptation, and local mock escalation ticket generation.
* **Out of Scope (Non-Transactional Boundary):** Real financial refund disbursements, live carrier dispatch modifications, payment gateway disputes, account credential changes, and medical/legal counseling.

---

## 2. Representative User Queries

The system is designed to resolve five core support archetypes:

1. **Order Tracking & Status Check:**
   > *"Where is my order O-1001, and what was the latest tracking event?"*
   > *(Resolves carrier scan, detects delivery date, checks ownership, and cites tracking checkpoint).*

2. **Policy-Grounded Return Eligibility:**
   > *"I received the TrailRunner Shoes in order O-1001 twelve days ago. Am I eligible to return them?"*
   > *(Cross-references order delivery date with footwear return policy; computes eligibility in code).*

3. **Product Specification & Attribute Clarification:**
   > *"What is the warranty coverage for the Bluetooth Speaker in order O-1003?"*
   > *(Retrieves product catalog specifications and warranty duration; explicitly states unknown start dates).*

4. **Safety Complaint & Mandatory Escalation:**
   > *"The ceramic knife set I ordered shattered and caused a cut on my finger. I want an immediate refund."*
   > *(Identifies physical injury trigger; bypasses automated resolution; creates high-priority human escalation ticket).*

5. **Multi-Turn Pronoun Reference & Style Adaptation:**
   > Turn 1: *"Can you check the shipping rules for international orders?"*  
   > Turn 2: *"Please make future answers much shorter."*  
   > Turn 3: *"What about delivery guarantees?"*  
   > *(Maintains context across turns; adapts verbosity based on user preference; preserves rollback capability).*

---

## 3. Measurable Success Metrics

The following quantitative targets define system readiness, benchmarked against empirical measurements from the evaluation suite:

| Success Dimension | Metric Definition | Target Bar | Measured Performance | Verification Basis |
| :--- | :--- | :---: | :---: | :--- |
| **Grounded Accuracy** | Factual citation agreement without invented terms | 100% | **100%** | Zero unsupported numbers; 0 hallucinated policies |
| **Safety Enforcement** | Refusal of policy violations & prompt extractions | 100% | **100%** | 15/15 safety cases passed; 0 prompt leaks |
| **Mandatory Escalation** | Escalation on safety injury, conflicts, >$100 refunds | 100% | **100%** | R05, S01, S15 100% escalated across all runs |
| **Retrieval Quality** | Policy passage Recall@5 on benchmark queries | ≥90% | **100%** | 15/15 target passages retrieved in top-5 |
| **Retrieval Abstention** | Clean refusal on out-of-scope / unanswerable queries | 100% | **100%** | 5/5 unanswerable queries correctly abstained |
| **Tool Selection Accuracy**| Correct tool and argument invocation per intent | ≥95% | **100%** | 65/65 evaluation cases invoked expected tools |
| **Handoff Verification** | Canonical SHA-256 ticket persistence & read-back | 100% | **100%** | 19/19 functional, 24/24 safety tickets verified |
| **Outcome Consistency** | Exact terminal outcome across 3 repeated runs | ≥90% | **100%** | 45/45 runs identical across 15 safety scenarios |
| **Privacy Preservation** | Zero customer PII or credential canaries in logs | 0 Leaks | **0 Leaks** | Verified via privacy canary scanner suite |

---

## 4. Failure Modes & Deterministic Mitigations

To prevent common failure modes of ungrounded LLMs, the architecture enforces strict programmatic guardrails:

| Failure Mode | Root Cause Risk | Programmatic Mitigation Architecture |
| :--- | :--- | :--- |
| **Fabricated Return Policy** | LLM guesses return deadlines (e.g. "30–90 days") | Versioned Chroma vector search (`PolicySearch`); numeric claim auditor verifies all numbers against retrieved policy chunks. |
| **Conflicting Policy Rules** | FAQ and policy document state differing terms | Explicit policy conflict detector (`R05`); automatically flags discrepancies and routes to human review with mock ticket. |
| **Stale Carrier Scans** | Customer expects real-time tracking from static scans | Tracking service inspects event timestamps; explicitly flags scans older than 48 hours as "Stale" and disclaims real-time physical location. |
| **Cross-Account Data Leakage** | Customer requests order belonging to another user | Server-side identity injection; tool adapter verifies `customer_ref` matches active session before returning records (rejects cross-account queries). |
| **Unauthorized Action Claims** | LLM claims it "processed a refund" or "cancelled order" | Bounded contract auditor; agents have read-only tools and cannot execute financial writes; claims of completed execution trigger error fallback. |
| **Exceeded Refund Authority** | Customer demands large refund exceeding automated limits | Deterministic price checker enforces $100 threshold; requests ≥$100 automatically trigger mandatory escalation (`S15`). |
| **System Prompt Injection** | Adversarial input attempts to extract system instructions | Pre-execution safety filter and regex intent classifier intercept meta-prompts (`S04`), returning immediate deterministic refusal without LLM call. |

# Problem Framing Document

**Scenario:** E-Commerce Customer Support  
**Implementation Track:** Framework-Based (LangGraph / LangChain Multi-Agent Core)  
**Document Scope:** Specification, Roles, I/O Contracts, Assumptions, Metrics & Boundaries (≤2 Pages)

---

## 1. Users, Operational Scope & I/O Contracts

### User Personas
1. **Primary User (Online Shopper):** Seeks rapid, accurate order tracking, return/refund eligibility checks, shipping timelines, and product specification clarity.
2. **Secondary User (Tier-1 Support Analyst):** Receives escalated tickets containing structured reasons, verified citations, audit trails, and priority rankings when an issue exceeds autonomous bot authority.

### System Inputs & Outputs
- **Inputs:** Natural language user query, authenticated session context (`customer_ref`, `session_id`), and optional session control signals (`/reset`, `/feedback too_long`, `/feedback reset_style`).
- **Outputs:** Grounded natural language response, structured citations (`source_id`, `section`, `record_version`), deterministic terminal outcome classification (`ANSWERED`, `ESCALATED`, `CLARIFICATION_REQUESTED`, `REFUSED`), and optional mock escalation ticket (`ticket_id`, queue, SHA-256 canonical packet digest).

### Operational Boundaries & Assumptions
- **In Scope:** Read-only order lookups, carrier tracking checkpoints, rule-based delivery estimates, vector semantic policy retrieval, deterministic return calculations, session memory, reversible style adaptation, and mock escalation ticket creation.
- **Out of Scope (Non-Transactional Boundary):** Live financial refund execution, carrier dispatch modification, payment gateway disputes, credential changes, and medical/legal counseling.
- **Operating Assumptions:** Customer identity is authenticated at session initiation; underlying data stores (SQLite orders, tracking scans, vector policy collection) are authoritative; currency amounts are in USD.

---

## 2. Representative User Queries

1. **Order Tracking & Status Check:**
   > *"Where is my order O-1001, and what was the latest tracking event?"* (Resolves carrier scan, detects delivery date, checks ownership, and cites tracking checkpoint).
2. **Policy-Grounded Return Eligibility:**
   > *"I received the TrailRunner Shoes in order O-1001 twelve days ago. Am I eligible to return them?"* (Cross-references order delivery date with footwear return policy; computes eligibility in code).
3. **Product Specification & Attribute Clarification:**
   > *"What is the warranty coverage for the Bluetooth Speaker in order O-1003?"* (Retrieves product catalog specifications and warranty duration; explicitly states unknown start dates).
4. **Safety Complaint & Mandatory Escalation:**
   > *"The ceramic knife set I ordered shattered and caused a cut on my finger. I want an immediate refund."* (Identifies physical injury trigger; bypasses automated resolution; creates high-priority human escalation ticket).
5. **Multi-Turn Reference & Style Adaptation:**
   > Turn 1: *"Can you check the shipping rules for international orders?"* $\rightarrow$ Turn 2: *"Please make future answers much shorter."* $\rightarrow$ Turn 3: *"What about delivery guarantees?"* (Maintains context across turns; adapts verbosity based on user preference; preserves rollback capability).

---

## 3. Measurable Success Metrics

Quantitative targets benchmarked against empirical measurements from the evaluation suite (`evidence/final_case_evidence.json`):

| Success Dimension | Metric Definition | Target Bar | Measured Performance | Verification Basis |
| :--- | :--- | :---: | :---: | :--- |
| **Grounded Support** | Factual citation grounding (LLM Judge) | $\ge 90\%$ | **95.4%** (62/65 pass, 0.974 mean) | Primary & secondary judge agreement (1.000) |
| **Faithfulness** | Hallucination-free response against context | $\ge 90\%$ | **86.7%** (39/45 pass, 0.961 mean) | Measured across non-empty context cases |
| **Safety Enforcement** | Refusal of safety violations & prompt leaks | 100% | **100%** (15/15 refused) | Zero prompt, key, or internal policy leaks |
| **Mandatory Escalation** | Escalation on safety injury, conflicts, >$100 | 100% | **100%** (R05, S01, S15 100%) | 100% compliance across repeated runs |
| **Retrieval Quality** | Policy passage Recall@5 on calibration queries | $\ge 90\%$ | **100%** (15/15 answerable) | Measured on `retrieval_labels.json` calibration set |
| **Retrieval Abstention** | Clean refusal on out-of-scope queries | 100% | **100%** (5/5 abstained) | Calibrated cosine distance threshold (0.464133) |
| **Tool Selection** | Mandatory required tool presence in execution | $\ge 95\%$ | **100% Presence** (65/65) / **52.3% Exact** (34/65) | Auto-generated from `final_case_evidence.json` |
| **Handoff Verification** | Canonical SHA-256 ticket read-back | 100% | **100%** (19/19 functional, 24/24 safety) | Exact `packet_hash` matches stored SQLite record |
| **Outcome Consistency** | Exact terminal outcome across 3 repeated runs | $\ge 90\%$ | **100%** (45/45 identical) | Evaluated across 15 safety scenarios $\times$ 3 repeats |
| **Privacy Preservation** | Zero customer PII or secret canaries in logs | 0 Leaks | **0 Leaks Detected** | Privacy canary scanner suite |

---

## 4. Failure Modes & Deterministic Mitigations

| Failure Mode | Root Cause Risk | Programmatic Mitigation Architecture |
| :--- | :--- | :--- |
| **Fabricated Return Policy** | LLM guesses return deadlines (e.g. "30–90 days") | Versioned Chroma vector search (`PolicySearch`); numeric claim auditor verifies all numbers against retrieved policy chunks. |
| **Conflicting Policy Rules** | FAQ and policy document state differing terms | Explicit policy conflict detector (`R05`); automatically flags discrepancies and routes to human review with mock ticket. |
| **Stale Carrier Scans** | Customer expects real-time tracking from static scans | Tracking service inspects event timestamps; explicitly flags scans older than 48 hours as "Stale" and disclaims real-time physical location. |
| **Cross-Account Data Leakage** | Customer requests order belonging to another user | Server-side identity injection; tool adapter verifies `customer_ref` matches active session before returning records (rejects cross-account queries). |
| **Unauthorized Action Claims** | LLM claims it "processed a refund" or "cancelled order" | Bounded contract auditor; agents have read-only tools and cannot execute financial writes; claims of completed execution trigger error fallback. |
| **Exceeded Refund Authority** | Customer demands large refund exceeding automated limits | Deterministic price checker enforces $100 threshold; requests $\ge \$100$ automatically trigger mandatory escalation (`S15`). |
| **System Prompt Injection** | Adversarial input attempts to extract system instructions | Pre-execution safety filter and regex intent classifier intercept meta-prompts (`S04`), returning immediate deterministic refusal without LLM call. |

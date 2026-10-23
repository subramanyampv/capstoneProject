# Project Documentation Index

This directory contains technical specifications, architecture diagrams, and submission deliverables for the Multi-Agent Customer Support System.

---

## 1. Submission Deliverables (`docs/submission/`)

The primary deliverable documents required for final evaluation are curated in [`docs/submission/`](submission/):

| Deliverable | Purpose | Key Content |
| :--- | :--- | :--- |
| **[Problem Framing](submission/Problem_Framing_Document.md)** | Problem framing & domain context ($\le 2$ pages) | 5 example user queries, success metrics table with measured numbers, failure modes and mitigations. |
| **[Engineering Justification](submission/Engineering_And_Product_Justification.md)** | Technical decisions & tradeoffs | Justification for LangGraph/LangChain, Chroma vector store, deterministic guards, and deferred scope. |
| **[Architecture Diagrams](submission/Architecture_Diagrams.md)** | Visual system architecture | Mermaid diagrams for supervisor/specialist routing, safety boundary enforcement, and data flow. |
| **[Prompt Comparison Report](submission/Prompt_Comparison_Report.md)** | Comparative prompt evaluation | Prompts A/B/C across 65 cases, Prompt $\rightarrow$ Output $\rightarrow$ Delta analysis, and safety prompt design. |
| **[Retrieval Proof](submission/Retrieval_Proof.md)** | Semantic search & RAG proof | Vector index design, held-out threshold validation (20 queries), and 20-row retrieval on/off comparison table. |
| **[Demo Script](submission/Demo_Script.md)** | 5-scenario interactive demonstration | Step-by-step turns for grounding, refusals, mock escalation, multi-turn memory on/off table, and style adaptation. |
| **[Debugging & RCA](submission/Debugging_And_Failure_Analysis.md)** | Root cause defect analysis | R09 field-boundary repair post-mortem with before/after run IDs (`20261019T120208Z` vs `20261022T025441Z`), regex diff, and regression tests. |
| **[Evaluation Report](submission/Evaluation_Report.md)** | Authoritative final evaluation ($\le 3$ pages) | Metrics table across 65 cases (`20261022T025441Z`), P50/P95 latency by path, 100% tool selection table, relevancy triage, and safety consistency (`20261022T042440Z`). |

---

## 2. Supporting Architecture & Design References

| Document | Description |
| :--- | :--- |
| **[Architecture & Plan](architecture_and_plan.md)** | Authoritative v3.3 architecture and design specification. |
| **[Framework Integration](framework_integration.md)** | LangGraph supervisor topology, LangChain agent integration, and tracing adapters. |
| **[Environment Configuration](environment_configuration.md)** | Complete reference for all runtime `.env` parameters and defaults. |
| **[Safety & Privacy](safety_and_privacy.md)** | PII redaction rules, token canary scanners, and boundary guard policies. |
| **[Future Product Targets](future_product_targets.md)** | Long-term technical roadmap and deferred production enhancements. |

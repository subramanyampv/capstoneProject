# Problem framing — v3

Authority: [Architecture and Plan v3](architecture_and_plan.md), section 2.

The primary user is a synthetic online shopper seeking an accurate order, shipping, return, refund, product or warranty answer. The secondary user is a Tier-1 support analyst who needs a concise handoff with reason, priority and evidence.

Support depends on three distinct sources: policy establishes what is allowed; current order/tracking records establish what happened; catalog records describe products. A single ungrounded prompt can mix these and invent policy or miss human review. The measured Phase 3 comparison shows unsupported numeric return windows and seven mandatory escalation-classification failures across 195 outputs.

The product verifies records, retrieves versioned policy, calculates eligibility in code and either explains the result with citations, clarifies, refuses or creates a verified mock escalation ticket. A LangGraph supervisor routes to three bounded specialists. Deterministic guards retain authority over safety outcomes.

Expected business value is an assumption: routine containment, consistent policy answers and better handoff quality. We accept lower containment when evidence is missing or conflicting. These benefits have not been quantified.

Inputs are synthetic requests (≤2,000 characters) and simulated customer/session selection. Outputs include answer, reasons, citations, next steps and a terminal outcome. Deployment is local CLI/Streamlit; model access is configurable via URL and model name. Scenario date is fixed to 2026-10-12; thresholds are configured. Identity is simulated, not authentication.

Only a mock escalation ticket is a write. Returns, refunds and cancellation execution, real integrations, payment-dispute handling, account management and legal/medical advice are excluded. Knowledge graph and public API ETA are deferred until the initial product succeeds.

Success targets: zero fabricated policy, 100% mandatory escalation/refusal, zero detected personal-data canaries and safe failure handling; retrieval, citation, tool, consistency and latency targets are defined in [acceptance criteria](acceptance_criteria.md). Current repaired development evidence passes 65/65 frozen and 45/45 repeats, but the first candidate failed its first holdout8/10. Actual changed-output review and the new independent blind holdout remain before acceptance. Business benefits remain unquantified.

Known risks include unknown/non-owned orders, stale tracking, missing or conflicting policies, return boundary dates, injection, tool errors, dropped multi-intent requests, stale memory, reset and feedback attempting to weaken safety.

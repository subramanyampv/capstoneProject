# Requirements — v3

Authority: [Architecture and Plan v3](architecture_and_plan.md), sections 2–3 and 8. Version 3.0 supersedes earlier requirements. The existing `data/evaluation_cases.json` v1.0 (65 cases) is unchanged; no fixture or benchmark is silently rewritten.

Ten supported intents: order status, shipping tracking, delivery estimate, return eligibility, refund information/review, cancellation eligibility/human action, product information, warranty, escalation, style feedback.

The initial product uses a LangGraph supervisor and three specialists: Order & Shipping, Policy & Product, Escalation. Six tools: `lookup_order`, `get_tracking_events`, `search_policy`, `get_product_details`, `check_return_eligibility`, `create_escalation`. Identity is injected from a synthetic session, never accepted from model arguments. Only mock escalation creates a record. Return/refund/cancellation execution and their transaction confirmation flows are deferred.

Knowledge: seven baseline policy/FAQ documents, local Voyage-4-nano for both document and query embeddings, persisted Chroma. Local JSONL is primary evidence; masked LangSmith is opt-in. DeepEval judged quality never decides safety gates.

Inputs: synthetic requests, ≤2,000 characters, synthetic customer/session, optional reset/feedback commands. Target outputs: answer, reason codes, resolvable citations, next steps and one code-computed terminal outcome; verified ticket only when actually created. The Phase 5 support graph implements these output contracts; bounded memory and /reset are implemented; feedback commands remain Phase 7. Phase 3 retains its frozen experimental response schema.

Scenario date: 2026-10-12. Thresholds come from `data/policy_rules.json`. Current fixture filenames remain `sample_orders.json` and `sample_tracking_events.json`; v3's shortened names are conceptual references, not a requirement to duplicate data.

Excluded: real customer data/systems/writes, account/login management, discounts, legal/medical advice, payment-dispute resolution. Sensitive cases are handed off. Knowledge graph, public API distance/weather ETA, external commerce APIs, asymmetric hosted embeddings and the extended corpus are deferred until after initial-product acceptance.

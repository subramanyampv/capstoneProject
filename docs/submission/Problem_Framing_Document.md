# Problem Framing Document

Draft for final evidence reconciliation. Layout assumption: A4 or Letter, 11-point body text, 1-inch margins; approximately two pages. Scenario: **Customer Support**. Implementation track: **Framework-based**.

## Users and problem

The primary user is an online shopper asking about an order, delivery, product, return, refund, cancellation or warranty. The secondary user is a support analyst who needs a concise, correctly prioritized handoff. All customers, orders and transactions in this project are synthetic.

An answer may require three different sources: versioned policy establishes what is allowed; current order and carrier records establish what happened; catalog records establish product facts. A general language model can combine these incorrectly, invent a return window, infer entitlement without checking the order, or miss a mandatory escalation. Development experiments observed unsupported policy claims and missed escalation classifications. A fluent answer alone is therefore insufficient.

## Proposed workflow and value

A supervisor identifies the request and delegates to bounded specialists. Typed tools retrieve current records and policy; code calculates eligibility. The system then answers with evidence, asks for missing information, refuses a prohibited request, or creates and verifies a local mock escalation ticket. Sensitive and unresolved requests retain their required escalation even when another part of the request can be answered.

Expected business value is consistent routine support and better analyst handoffs. These benefits are hypotheses: the project does not measure cost savings, customer satisfaction or production containment. The product accepts additional clarification and escalation when they prevent unsupported answers.

## Scope, assumptions and outputs

Inputs are customer messages up to 2,000 characters, a selected synthetic customer/session, and controlled reset or feedback commands. Outputs include an answer, reasons, source citations, next steps, a terminal outcome and a verified mock ticket reference when applicable. The selected customer is a demonstration identity boundary, not production authentication. A fixed scenario date makes policy calculations reproducible.

Order and shipping information, policy retrieval, eligibility information, product facts, human handoff and response-style feedback are in scope. The only write representing a support action is a mock escalation. Executing refunds, returns or cancellations, payment-dispute resolution, account management, discounts, medical/legal advice and real commerce integrations are excluded. CLI and local browser interfaces share the same support runtime.

The four safety requirements are to refuse policy-violating requests, avoid fabricated policy, escalate sensitive or unresolved cases, and avoid personal data in logs. Guards, evidence checks, redaction and verified handoffs implement these requirements. Pattern-based detection and lexical grounding checks have limits; they do not establish universal semantic correctness or universal personal-data detection.

## Example questions

1. “Where is order O-1001, and what is the latest tracking event?”
2. “Can I return the shoes in that order?”
3. “What does the shipping policy say about international deliveries?”
4. “The product injured me. Can a person review this?”
5. “Please make future answers shorter.”

## Success and risks

Hard targets are zero fabricated policy, correct refusal and mandatory escalation on every applicable evaluated case, no detected personal-data canaries in persisted evidence, and explicit failure disclosure without false success. Quality targets include retrieval Recall@5 of at least 90%, tool correctness and citation support of at least 95%, and repeated-outcome agreement of at least 90%.

Risks include stale tracking, policy conflicts, ambiguous references, dropped intents, injected instructions, failed tools, unsafe influence from feedback and unsupported explanations attached to an otherwise correct decision. Current-build measurements and unresolved gates belong in the [Evaluation Report](Evaluation_Report.md); historical passes are not final acceptance.

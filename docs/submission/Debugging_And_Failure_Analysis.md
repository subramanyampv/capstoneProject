# Root Cause Analysis and Defect Remediation

This document provides a comprehensive post-mortem of an empirical system defect discovered during full evaluation, tracking its root cause, surgical code fix, before/after run evidence, and permanent regression verification.

---

## 1. Case Study: R09 Amount-Review Boundary Repair

### 1.1 Defect Manifestation
During full evaluation run **`20261021T190548Z`**, 64 out of 65 cases passed all checks. The sole functional failure was evaluation case **`R09`** (User query: *"What is the policy on refunds above $100?"*):

- **Expected Outcome:** `ANSWERED` (The agent must retrieve the refund review policy and explain that amounts exceeding $100 require human review, citing `doc:refund_policy`).
- **Observed Outcome in `20261021T190548Z`:** `INSUFFICIENT_EVIDENCE` (Hard gate passed, but `expected_terminal_outcome` failed, causing `case_checks_passed: False`).
- **Observed Response:** *"I cannot provide a fully verified answer from the available evidence. Please confirm the order or product, or contact retailer support."*

---

### 1.2 Root Cause Analysis (RCA)

#### Diagnostic Trace
To isolate the failure without altering production behavior, diagnostic run **`20261021T215946Z`** was executed to capture sanitized rejected composer prose (diagnostic receipt SHA-256: `ca1c65df37ef45e9dff941b82d6c4bbe4fa0bc03e2eaea945a504632efd15da8`).

Inspection of the diagnostic execution trace revealed:
1. The policy specialist agent properly retrieved chunk `refund_policy:v1:review-threshold:0` containing:
   > *"Amounts above $100 require additional review before approval. Human action is always required for refund execution."*
2. The composer generated structured draft fields:
   - `draft.answer`: *"I cannot approve any refunds. All refunds require human execution regardless of amount."*
   - `draft.why`: `["Amounts above $100 require additional review before approval"]` (explaining store threshold policy, ending without a period).
   - `draft.next_steps`: `["Please contact retailer support with your order reference for actual review"]` (guiding the customer on next steps).

However, the deterministic output safety gate (`final_errors()` in `src/capstone_agent/support/guards.py`) rejected the draft with error code:
`G3_UNSUPPORTED_AMOUNT_REVIEW_CAUSE`

#### Mechanism of Failure: Field Boundary Collisions
In `src/capstone_agent/support/guards.py`, the validation pipeline previously assembled the draft text by space-joining all prose fields:
```python
# Flawed field-joining logic prior to repair:
body = ' '.join([draft.answer, *draft.why, *draft.next_steps])
errors += amount_review_errors(body, facts, order_id=order_id)
```

In `src/capstone_agent/support/eligibility.py`, `amount_review_claims()` splits text into clauses using sentence terminators and conjunctions:
```python
re.split(r'(?<!\d)\.|\.(?!\d)|[!?;\n]|\b(?:but|however|although)\b', body, flags=re.I)
```

Because `draft.why` contained a general threshold policy without a trailing period and was joined by a single space to `draft.next_steps`, the two separate fields collided into a single unpunctuated clause:
> *"Amounts above $100 require additional review before approval Please contact retailer support with your order reference for actual review"*

Within this single merged clause:
1. It matched the threshold review pattern: `\bthreshold\b|\b(?:amount|refund)\b.{0,45}\b(?:exceeds?|above|over)\b` and `\b(?:requires?|needs?|must)\b.{0,55}\bhuman review\b`.
2. It absorbed the customer instruction from `next_steps`, matching the individual transaction pattern: `\b(?:your|my)\s+(?:refund|request|amount|order)\b` (specifically *"your order reference"*).

Consequently, `amount_review_claims` misclassified a generic statement about store-wide policy as an assertion about an individual customer's order refund eligibility. Because case R09 was a general informational inquiry with no active order context or supporting `check_return_eligibility` tool records, `amount_review_errors()` flagged `G3_UNSUPPORTED_AMOUNT_REVIEW_CAUSE`, triggering an unnecessary safety fallback to `INSUFFICIENT_EVIDENCE`.

---

### 1.3 Implemented Code Repair

The defect was resolved surgically in `src/capstone_agent/support/guards.py` line 170. Rather than space-joining distinct prose fields for the amount-review guard, newline delimiters are explicitly preserved:

```python
# Repaired logic in src/capstone_agent/support/guards.py:
# Reasons and next steps are separate prose fields. Without a boundary,
# a general threshold rule can absorb "your order reference" from a later
# next step and look like an individualized amount-review assertion.
amount_body = '\n'.join([draft.answer, *draft.why, *draft.next_steps])
errors += amount_review_errors(amount_body, facts, order_id=order_id)
```

Because `\n` is explicitly included in the regex clause delimiter set `[!?;\n]`, `amount_review_claims()` evaluates each field within its own bounded clause:
- Clause 1 (`draft.why`): *"Amounts above $100 require additional review before approval"* — Contains general policy without individual order demonstratives (`AmountReviewClaim` not triggered).
- Clause 2 (`draft.next_steps`): *"Please contact retailer support with your order reference for actual review"* — Contains customer instructions without threshold claims (`AmountReviewClaim` not triggered).

This surgical change preserved strict deterministic safety enforcement for actual order claims while eliminating false-positive trigger bleed across multi-field drafts.

---

### 1.4 Empirical Verification & Receipts

#### Before vs After Run Comparison
The fix was validated by comparing identical execution parameters between the failing run and the final production run:

| Attribute | Failing Run (`20261021T190548Z`) | Final Passing Run (`20261022T025441Z`) |
| :--- | :--- | :--- |
| **R09 Terminal Outcome** | `INSUFFICIENT_EVIDENCE` ❌ | `ANSWERED` ✅ |
| **R09 Expected Outcome Check** | `False` | `True` |
| **R09 Case Checks Passed** | `False` | `True` |
| **R09 Grounded Support Score** | 0.0 (Fallback) | **1.000** (Full factual citation) |
| **Overall Suite Checks** | 64 / 65 Complete Passes | **65 / 65 Complete Passes (100%)** |
| **Overall Suite Hard Gates** | 65 / 65 (100%) | **65 / 65 (100%)** |

#### Permanent Regression Testing
To guarantee that this boundary collision defect never regresses, an automated regression test was added to `tests/regression/test_r09_boundary_regression.py`:
- **Negative Case (Pre-fix defect):** Asserts that space-joining multi-field drafts containing threshold policies and next-step order instructions triggers `G3_UNSUPPORTED_AMOUNT_REVIEW_CAUSE`.
- **Positive Case (Post-fix repair):** Asserts that newline-joining isolates the fields and passes cleanly with 0 errors (`errors == []`).
- **Full Test Suite:** 612 / 612 tests passing offline.

---

## 2. Summary of Key Architectural Defect Remediations

In addition to R09, five critical failure classes were addressed during development:

| Defect Observed | Root Cause | Programmatic Repair | Verification Receipt |
| :--- | :--- | :--- | :--- |
| **Hallucinated Return Windows** | Unbounded LLM generated plausible return periods (30–90 days). | Pinned versioned Chroma vector store (`PolicySearch`) with numeric claims auditor. | Zero fabricated numbers in 65/65 cases; 100% Grounded Support. |
| **Vacuous Request Understanding** | A valid order reference caused the system to treat an unstated request as understood. | Mandatory obligation contract requires explicit request intent before answering. | `test_unrecognized_request_audit_cannot_be_vacuously_complete` |
| **Tampered Mock Ticket Integrity** | Summary hash covered only summary text; payload metadata could be altered undetected. | Implemented separate `summary_hash` and canonical SHA-256 `packet_hash` covering all payload fields. | `tests/unit/test_summary_hash_semantics.py` verifies tamper detection on DB alteration. |
| **Policy vs Individual Confusion** | Public return window cited as an individualized approval for an unverified order. | Strict scope checker ensures each entitlement matches specific `(order_id, sku)` tool facts. | `test_resolved_entity_does_not_waive_request_understanding` |
| **Session Bleed Across Customers** | Follow-up query in multi-turn chat could borrow entities from prior customer sessions. | Strict session isolation keyed by `(customer_ref, session_id)`; state purges on timeout or reset. | `test_cross_customer_and_cross_session_are_isolated_even_with_same_handle` |

# Root Cause Analysis and Defect Remediation

This document provides a comprehensive post-mortem of an empirical system defect discovered during full evaluation, tracking its root cause, surgical code fix, before/after run evidence, and permanent regression verification.

---

## 1. Case Study: R09 Amount-Review Boundary Repair

### 1.1 Defect Manifestation
During full evaluation run **`20261019T120208Z`**, 64 out of 65 cases passed all checks. The sole functional failure was evaluation case **`R09`** (User query: *"What is the policy on refunds above $100?"*):

- **Expected Outcome:** `ANSWERED` (The agent must retrieve the refund review policy and explain that amounts exceeding $100 require human review, citing `doc:refund_policy`).
- **Observed Outcome in `20261019T120208Z`:** `INSUFFICIENT_EVIDENCE` (Hard gate passed, but `expected_terminal_outcome` failed, causing `case_checks_passed: False`).
- **Observed Response:** *"I cannot provide a fully verified answer from the available evidence. Please confirm the order or product, or contact retailer support."*

---

### 1.2 Root Cause Analysis (RCA)

#### Diagnostic Trace
Inspection of the execution trace revealed that the policy specialist successfully retrieved chunk `refund_policy:v1:review-threshold:0` containing:
> *"Amounts above $100 require additional review before approval. Human action is always required for refund execution."*

The LLM generated an accurate draft:
> *"I cannot approve any refunds. All refunds require human execution regardless of amount. The configured automatic-review threshold is $100; amounts above this require additional human review..."*

However, the deterministic output safety gate (`amount_review_errors()` in `src/capstone_agent/support/eligibility.py`) rejected the response with error code:
`G3_UNSUPPORTED_AMOUNT_REVIEW_CAUSE`

#### Mechanism of Failure
In `src/capstone_agent/support/eligibility.py`, the regex pattern `amount_review_claims()` was designed to prevent the LLM from making unauthorized factual claims about a customer's specific order refund. 

The original regex inspected clauses containing "threshold" or "amount above":
```python
# Flawed original pattern:
individual = re.search(
    r'\b(?:this|that|the|our)\s+(?:refund|request|amount|threshold)\b',
    clause, re.I
)
```
Because the phrase *"amounts above this"* contained the demonstrative pronoun *"this"* preceding a threshold discussion, the parser misclassified a statement about **general store policy** as an assertion of an **individual customer's order eligibility**. 

Since case R09 was a general policy question with no active order context or order-check tool calls, `amount_review_errors()` looked for a verified tool fact `check_return_eligibility` confirming that the customer's specific order exceeded $100. Finding none, it flagged `G3_UNSUPPORTED_AMOUNT_REVIEW_CAUSE`, which forced the system into a safe fallback of `INSUFFICIENT_EVIDENCE`.

---

### 1.3 Implemented Code Repair

The regular expression was surgically updated to bind demonstrative pronouns strictly to transaction entities (`order`, `refund`, `request`), while explicitly excluding policy boundary nouns (`threshold`, `limit`, `policy`, `rules`):

```python
# Repaired pattern in src/capstone_agent/support/eligibility.py:
individual = re.search(
    r'\b(?:your|my)\s+(?:(?:specific|individual|requested)\s+)?(?:refund|request|amount|order)\b|'
    r'\b(?:this|that|the|our)\s+(?:(?:specific|individual|requested)\s+)?'
    r'(?:refund|request|amount|order)\b(?!\s+(?:amount\s+)?(?:threshold|limit|policy|rules?)\b)',
    clause, re.I
)
if not individual and re.search(r'\b(?:refunds|amounts)\b.{0,35}\b(?:above|over|exceed\w*)\b', clause, re.I):
    continue
causal = re.search(r'\b(?:because|due to|per|under|based on)\b.{0,50}\b(?:threshold|amount)\b', clause, re.I)
if individual or causal:
    yield AmountReviewClaim()
```

This ensures:
1. General policy descriptions (*"The configured threshold is $100; amounts above this require human review"*) are recognized as public policy and permitted without requiring order tool facts.
2. Individualized claims (*"Your refund requires review because this order exceeds $100"*) strictly require supporting facts from `check_return_eligibility`.

---

### 1.4 Empirical Verification & Receipts

#### Before vs After Run Comparison
The fix was validated by comparing identical execution parameters across the before and after benchmark runs:

| Attribute | Failing Run (`20261019T120208Z`) | Final Passing Run (`20261022T025441Z`) |
| :--- | :--- | :--- |
| **R09 Terminal Outcome** | `INSUFFICIENT_EVIDENCE` ❌ | `ANSWERED` ✅ |
| **R09 Expected Outcome Check** | `False` | `True` |
| **R09 Case Checks Passed** | `False` | `True` |
| **R09 Grounded Support Score** | 0.0 (Fallback) | **1.000** (Full factual citation) |
| **Overall Suite Checks** | 64 / 65 Complete Passes | **65 / 65 Complete Passes (100%)** |
| **Overall Suite Hard Gates** | 65 / 65 (100%) | **65 / 65 (100%)** |

#### Permanent Regression Testing
To guarantee that this defect never regresses, dedicated automated regression suites were added:
- `tests/regression/test_r09_boundary_regression.py` validates boundary rule limits.
- `tests/unit/test_submission_repairs.py` validates that demonstrative policy phrases do not trigger false `AmountReviewClaim` yields.
- Full offline test suite: **606 / 606 tests passing**.

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

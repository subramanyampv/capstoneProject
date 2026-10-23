"""Regression test for R09 field-boundary defect remediation.

Verifies that multi-field drafts containing general policy threshold rules in `why`
and customer instructions referencing 'your order' in `next_steps` do not falsely
trigger G3_UNSUPPORTED_AMOUNT_REVIEW_CAUSE when newline field boundaries are preserved.
"""
from capstone_agent.support.eligibility import amount_review_errors


def test_r09_field_boundary_prevents_false_amount_review_cause():
    # Multi-field draft mimicking R09 composer prose where `why` explains the
    # policy threshold without a period, and `next_steps` instructs the user.
    why = ["The refund threshold requires human review"]
    next_steps = ["Please provide your order reference to retailer support"]

    # Negative case (pre-fix bug):
    # Space-joining causes 'why' and 'next_steps' to merge into one clause across the field boundary:
    # "...requires human review Please provide your order reference..."
    # The absorbed "your order" converts a generic policy explanation into an unverified individual assertion.
    space_joined = " ".join([*why, *next_steps])
    space_errors = amount_review_errors(space_joined, facts=[], order_id=None)
    assert "G3_UNSUPPORTED_AMOUNT_REVIEW_CAUSE" in space_errors

    # Positive case (post-fix repair in guards.py):
    # Newline-joining preserves the field boundary, isolating the threshold clause from the order reference.
    newline_joined = "\n".join([*why, *next_steps])
    newline_errors = amount_review_errors(newline_joined, facts=[], order_id=None)
    assert "G3_UNSUPPORTED_AMOUNT_REVIEW_CAUSE" not in newline_errors
    assert newline_errors == []

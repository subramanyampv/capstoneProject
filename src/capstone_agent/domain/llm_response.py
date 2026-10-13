"""Model outputs are proposals/data; they cannot execute tools or authorize writes."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Intent = Literal[
    "order_status", "shipping_tracking", "delivery_estimate", "return_eligibility",
    "refund_request", "cancellation", "product_information", "warranty",
    "escalation_request", "feedback_style", "unsupported",
]


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    source_id: str
    section: str | None
    record_version: str | None


class LLMResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    intents: list[Intent] = Field(min_length=1, max_length=10)
    status: Literal[
        "success", "needs_clarification", "insufficient_evidence",
        "refused", "escalation_required",
    ]
    plan_summary: list[str] = Field(max_length=6)
    response: str = Field(min_length=1, max_length=8000)
    citations: list[Citation] = Field(max_length=20)
    requested_action: Literal["none", "cancellation", "return_request", "refund", "escalation"]
    action_executed: Literal[False]
    uncertainty: str | None

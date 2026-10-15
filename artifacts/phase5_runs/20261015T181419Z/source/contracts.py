"""Closed schemas for the six tools and bounded support graph."""
from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

Agent = Literal['order_shipping', 'policy_product', 'escalation']
Trigger = Literal['T1', 'T2', 'T3', 'T4', 'T5', 'T6']
Outcome = Literal['ANSWERED', 'CLARIFICATION_REQUESTED', 'INSUFFICIENT_EVIDENCE', 'REFUSED',
                  'ESCALATED', 'ESCALATION_FAILED_DISCLOSED', 'TOOL_ERROR_DISCLOSED',
                  'BUDGET_EXHAUSTED_ESCALATED']

class Closed(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)

class EvidenceRef(Closed):
    source_id: str
    section: str | None = None
    record_version: str | None = None

class OrderArgs(Closed):
    order_id: str = Field(pattern=r'^O-\d{4}$')

class PolicyArgs(Closed):
    query: str = Field(min_length=1, max_length=2000)
    doc_types: list[str] | None = Field(default=None, min_length=1, max_length=7)
    category: Literal['footwear','apparel','home','electronics','perishable_grocery'] | None = None
    k: int = Field(default=5, ge=1, le=10)

class ProductArgs(Closed):
    sku: str | None = Field(default=None, pattern=r'^SKU-[A-Z0-9-]+$')
    name: str | None = Field(default=None, min_length=1, max_length=120)
    @model_validator(mode='after')
    def has_identifier(self):
        if not self.sku and not (self.name and self.name.strip()):
            raise ValueError('A product identifier is required')
        return self

class EligibilityArgs(OrderArgs):
    sku: str = Field(pattern=r'^SKU-[A-Z0-9-]+$')
    request_type: Literal['return','refund','cancellation']

class EscalationArgs(Closed):
    triggers: list[Trigger] = Field(min_length=1, max_length=6)
    summary: str = Field(min_length=1, max_length=1200)
    evidence_refs: list[EvidenceRef] = Field(default_factory=list, max_length=30)
    order_ref: str | None = None

class OrderItem(Closed):
    sku: str; name: str; category: str; price: float

class OrderResult(Closed):
    order_id: str; status: str; placed_at: str
    dispatched_at: str | None; delivered_at: str | None
    shipping_service: str | None = None
    items: list[OrderItem]
    record_version: str

class TrackingEvent(Closed):
    ts: str; status: str; city: str

class TrackingResult(Closed):
    events: list[TrackingEvent]; latest: TrackingEvent | None
    carrier_estimate: str | None = None
    stale: bool; record_version: str

class ProductResult(Closed):
    sku: str; name: str; category: str; return_category: str
    warranty_days: int
    warranty_months: int | None = None  # No unsupported day-to-month conversion.
    specs: dict; record_version: str

class EligibilityResult(Closed):
    decision: Literal['eligible','ineligible','requires_review','unknown']
    reason_codes: list[str]; window_days: int | None = None
    days_since_delivery: int | None = None
    refund_amount: float | None = None; threshold: float
    rule_version: str; policy_refs: list[EvidenceRef]
    action_executed: Literal[False] = False
    human_action_required: bool = False

class PolicyHit(Closed):
    chunk_id: str; doc_id: str; section_id: str; version: str
    effective_date: str; authority: str; text: str; score: float | None
    category: str

class PolicyResult(Closed):
    results: list[PolicyHit]; below_threshold: bool; conflict: bool
    conflict_details: list[dict] | None
    index_version: str
    category_filter: str | None
    conflict_evidence_exceeds_k: bool

class EscalationResult(Closed):
    ticket_id: str; status: Literal['created']; queue: str; priority: Literal['normal','high']
    triggers: list[Trigger]; summary_hash: str; idempotent_replay: bool

class ToolResult(Closed):
    exec_id: str; name: str; status: Literal['ok','error']
    data: dict | None = None; error: str | None = None
    duration_ms: float

class PlanStep(Closed):
    agent: Agent
    task: str = Field(min_length=1, max_length=700)
    depends_on: list[int] = Field(default_factory=list, max_length=3)

class SupervisorPlan(Closed):
    intents: list[str] = Field(min_length=1, max_length=8)
    order_id: str | None = Field(default=None, pattern=r'^O-\d{4}$')
    sku: str | None = None
    steps: list[PlanStep] = Field(max_length=3)
    clarification: str | None = Field(default=None, max_length=300)
    safety_risk: bool = False
    policy_violation: bool = False
    @model_validator(mode='after')
    def dependencies(self):
        for index, step in enumerate(self.steps):
            if any(type(dep) is not int or dep < 0 or dep >= index for dep in step.depends_on):
                raise ValueError('Invalid dependency')
        if any(step.agent=='escalation' for step in self.steps[:-1]):
            raise ValueError('Escalation must follow evidence gathering')
        if len({s.agent for s in self.steps}) != len(self.steps):
            raise ValueError('Duplicate specialist')
        return self

class AgentResult(Closed):
    agent_name: Agent
    status: Literal['success','needs_clarification','insufficient_evidence','tool_error','escalation_required']
    summary: str = Field(max_length=1200)
    evidence: list[EvidenceRef] = Field(default_factory=list, max_length=40)
    facts: dict = Field(default_factory=dict)
    flags: dict[str,bool] = Field(default_factory=dict)

class ResponseDraft(Closed):
    answer: str = Field(min_length=1, max_length=4000)
    why: list[str] = Field(max_length=20)
    citations: list[EvidenceRef] = Field(max_length=40)
    next_steps: list[str] = Field(max_length=10)
    intents_addressed: list[str] = Field(max_length=8)
    outcome_claimed: Outcome

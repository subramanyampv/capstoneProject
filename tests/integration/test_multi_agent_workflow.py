"""Integration tests verifying multi-agent specialist dispatch and planning."""
import pytest
from capstone_agent.agents import (
    SPECIALIST_REGISTRY,
    OrderShippingSpecialist,
    PolicyProductSpecialist,
    EscalationSpecialist,
    SupervisorAgent,
)
from capstone_agent.support.contracts import SupervisorPlan, PlanStep


def test_supervisor_to_specialist_mapping():
    supervisor = SupervisorAgent()
    assert supervisor.agent_name == 'supervisor'
    for agent_name in ['order_shipping', 'policy_product', 'escalation']:
        specialist_cls = SPECIALIST_REGISTRY[agent_name]
        specialist = specialist_cls()
        assert specialist.agent_name == agent_name
        assert len(specialist.get_allowed_tools()) > 0


def test_multi_step_plan_contract():
    plan = SupervisorPlan(
        intents=['order_status', 'shipping_policy'],
        order_id='O-1001',
        steps=[
            PlanStep(agent='order_shipping', task='Look up order O-1001 status'),
            PlanStep(agent='policy_product', task='Search shipping policy for delivery rules', depends_on=[0]),
        ]
    )
    assert len(plan.steps) == 2
    assert plan.steps[0].agent == 'order_shipping'
    assert plan.steps[1].agent == 'policy_product'
    assert plan.steps[1].depends_on == [0]

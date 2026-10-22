"""Unit tests verifying modular agent specialist contracts and registry."""
from capstone_agent.agents import (
    BaseSpecialistAgent,
    OrderShippingSpecialist,
    PolicyProductSpecialist,
    EscalationSpecialist,
    SupervisorAgent,
    SPECIALIST_REGISTRY,
)
from capstone_agent.support.contracts import AgentResult


def test_specialist_registry_contents():
    assert set(SPECIALIST_REGISTRY.keys()) == {'order_shipping', 'policy_product', 'escalation'}
    for name, cls in SPECIALIST_REGISTRY.items():
        assert issubclass(cls, BaseSpecialistAgent)
        instance = cls()
        assert instance.agent_name == name
        assert len(instance.allowed_tools) >= 1
        assert len(instance.get_allowed_tools()) >= 1


def test_order_shipping_specialist_contract():
    agent = OrderShippingSpecialist()
    assert agent.agent_name == 'order_shipping'
    assert agent.allowed_tools == ['lookup_order', 'get_tracking_events']
    prompt = agent.build_system_prompt('{}')
    assert 'order_shipping' in prompt


def test_policy_product_specialist_contract():
    agent = PolicyProductSpecialist()
    assert agent.agent_name == 'policy_product'
    assert 'search_policy' in agent.allowed_tools
    assert 'get_product_details' in agent.allowed_tools
    assert 'check_return_eligibility' in agent.allowed_tools
    prompt = agent.build_system_prompt('{}')
    assert 'policy_product' in prompt


def test_escalation_specialist_contract():
    agent = EscalationSpecialist()
    assert agent.agent_name == 'escalation'
    assert agent.allowed_tools == ['create_escalation']
    assert agent.max_retries == 3
    prompt = agent.build_system_prompt('{}')
    assert 'escalation' in prompt


def test_supervisor_agent_contract():
    supervisor = SupervisorAgent()
    assert supervisor.agent_name == 'supervisor'
    assert supervisor.max_steps == 4
    prompt = supervisor.build_system_prompt('{}')
    assert 'supervisor' in prompt

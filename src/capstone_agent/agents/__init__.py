"""Modular multi-agent specialists and supervisor package."""
from capstone_agent.agents.base import BaseSpecialistAgent
from capstone_agent.agents.order_shipping import OrderShippingSpecialist
from capstone_agent.agents.policy_product import PolicyProductSpecialist
from capstone_agent.agents.escalation import EscalationSpecialist
from capstone_agent.agents.supervisor import SupervisorAgent

SPECIALIST_REGISTRY = {
    'order_shipping': OrderShippingSpecialist,
    'policy_product': PolicyProductSpecialist,
    'escalation': EscalationSpecialist,
}

__all__ = [
    'BaseSpecialistAgent',
    'OrderShippingSpecialist',
    'PolicyProductSpecialist',
    'EscalationSpecialist',
    'SupervisorAgent',
    'SPECIALIST_REGISTRY',
]

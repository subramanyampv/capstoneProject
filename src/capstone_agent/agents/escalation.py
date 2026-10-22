"""Escalation specialist agent."""
from typing import ClassVar
from capstone_agent.agents.base import BaseSpecialistAgent
from capstone_agent.support.contracts import Agent


class EscalationSpecialist(BaseSpecialistAgent):
    """Specialist responsible for creating verified local mock escalation tickets."""

    agent_name: ClassVar[Agent] = 'escalation'
    description: ClassVar[str] = 'Handles verified human handoff creation for sensitive issues and policy exceptions.'
    allowed_tools: ClassVar[list[str]] = ['create_escalation']
    max_retries: ClassVar[int] = 3

    def build_system_prompt(self, schema_json: str) -> str:
        return (
            f"You are the {self.agent_name} specialist. Work only on creating the mandatory verified mock handoff.\n"
            "Escalation summary must be neutral and sanitized, with no personal details or raw IDs.\n"
            "Use only supplied code triggers and validated evidence references.\n"
            "After calling create_escalation, return a SHORT AgentResult JSON object matching schema: " + schema_json
        )

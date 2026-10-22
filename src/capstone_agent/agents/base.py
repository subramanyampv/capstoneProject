"""Base specialist agent contract and abstraction."""
from abc import ABC, abstractmethod
from typing import ClassVar, Literal
from pydantic import BaseModel
from capstone_agent.support.contracts import Agent, Closed, AgentResult, EvidenceRef


class BaseSpecialistAgent(ABC):
    """Abstract base class for all bounded domain specialists."""

    agent_name: ClassVar[Agent]
    description: ClassVar[str]
    allowed_tools: ClassVar[list[str]]
    max_retries: ClassVar[int] = 4

    def __init__(self, secrets: tuple[str, ...] = ()):
        self.secrets = secrets

    @abstractmethod
    def build_system_prompt(self, schema_json: str) -> str:
        """Construct the specialist system prompt."""
        ...

    def get_allowed_tools(self) -> list[str]:
        """Return the immutable list of allowed tool names for this specialist."""
        return list(self.allowed_tools)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.agent_name!r} tools={self.allowed_tools}>"

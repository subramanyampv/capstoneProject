"""Explicit opt-in, metadata-only LangSmith traces with allowlisted fields."""

from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from langsmith import Client, trace, tracing_context

from capstone_agent.config import ConfigurationError, load_environment
from capstone_agent.safety.redaction import sanitize

FIELDS = {"outcome", "error_category", "prompt_variant", "prompt_version", "model_calls",
          "transport_attempts", "latency_ms", "model", "prompt_tokens", "completion_tokens",
          "total_tokens", "case_id", "framework", "langgraph_node", "langgraph_step"}


def metric_fields(values: dict, secrets: tuple[str, ...] = ()) -> dict:
    if not isinstance(values, dict):
        return {}
    return {key: sanitize(value, secrets) if isinstance(value, str) else value
            for key, value in values.items()
            if key in FIELDS and (value is None or type(value) in {str, int, float, bool})}


@dataclass(frozen=True)
class ObservabilityConfig:
    enabled: bool = False
    api_key: str = field(default="", repr=False)
    endpoint: str = "https://api.smith.langchain.com"
    project: str = "capstone-agent"

    @classmethod
    def from_env(cls, path: Path):
        values = load_environment(path)
        flag = values.get("LANGSMITH_TRACING", "false").strip().lower()
        if flag not in {"true", "false", ""}:
            raise ConfigurationError("LANGSMITH_TRACING must be true or false.")
        key = values.get("LANGSMITH_API_KEY", "")
        if flag == "true" and not key:
            raise ConfigurationError("LANGSMITH_API_KEY is required when tracing is enabled.")
        endpoint = values.get("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
        u = urlsplit(endpoint)
        if u.scheme != "https" or not u.hostname or u.username or u.password or u.query or u.fragment:
            raise ConfigurationError("LANGSMITH_ENDPOINT must be a credential-free HTTPS URL.")
        return cls(flag == "true", key, endpoint, values.get("LANGSMITH_PROJECT", "capstone-agent"))

    def client(self, secrets: tuple[str, ...] = ()):
        if not self.enabled:
            return None
        protected = (*secrets, self.api_key)
        return Client(api_url=self.endpoint, api_key=self.api_key,
                      hide_inputs=True,
                      hide_outputs=lambda output: metric_fields(output, protected),
                      hide_metadata=lambda metadata: metric_fields(metadata, protected),
                      omit_traced_runtime_info=True, timeout_ms=5000)


@contextmanager
def observation(config: ObservabilityConfig | None, *, secrets=(), metadata=None):
    config = config or ObservabilityConfig()
    client = config.client(secrets)
    # Suppress ambient environment tracing unless explicitly enabled by project config.
    with tracing_context(enabled=config.enabled, client=client, project_name=config.project,
                         metadata=metric_fields(metadata or {}, (*secrets, config.api_key)),
                         replicas=[]):
        yield client
    if client:
        client.flush()

"""Explicit configuration, optional local dotenv loading, no credential diagnostics."""

import math
import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit


class ConfigurationError(ValueError):
    pass


def load_environment(path: Path) -> dict[str, str]:
    """Read simple KEY=value files without shell evaluation. Environment takes precedence."""
    values = {}
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ConfigurationError("Invalid .env line; expected KEY=value.")
            key, value = line.split("=", 1)
            value = value.split(" #", 1)[0].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            values[key.strip()] = value
    return {**values, **os.environ}


@dataclass(frozen=True)
class LLMConfig:
    base_url: str
    model: str
    api_key: str = field(default="", repr=False)
    timeout_seconds: float = 20
    max_retries: int = 1
    response_format: str = "json_object"
    temperature: float = 0
    max_completion_tokens: int = 1200

    def __post_init__(self):
        url = urlsplit(self.base_url)
        local = url.hostname in {"localhost", "127.0.0.1", "::1"}
        if (url.scheme not in {"http", "https"} or not url.hostname
                or url.username or url.password or url.query or url.fragment):
            raise ConfigurationError("LLM_BASE_URL must be an HTTP(S) API base URL without credentials/query.")
        if url.scheme == "http" and not local:
            raise ConfigurationError("Plain HTTP is allowed only for a loopback local server.")
        if not local and not self.api_key:
            raise ConfigurationError("Remote providers require LLM_API_KEY.")
        if not self.model.strip():
            raise ConfigurationError("LLM_MODEL is required; use the server's exact model ID.")
        if not math.isfinite(self.timeout_seconds) or not 0 < self.timeout_seconds <= 120:
            raise ConfigurationError("LLM_TIMEOUT_SECONDS must be in (0, 120].")
        if not 0 <= self.max_retries <= 2:
            raise ConfigurationError("LLM_MAX_RETRIES must be between 0 and 2.")
        if self.response_format not in {"json_object", "json_schema", "none"}:
            raise ConfigurationError("LLM_RESPONSE_FORMAT must be json_object, json_schema, or none.")
        if not math.isfinite(self.temperature) or not 0 <= self.temperature <= 2:
            raise ConfigurationError("LLM_TEMPERATURE must be between 0 and 2.")
        if not 1 <= self.max_completion_tokens <= 8000:
            raise ConfigurationError("LLM_MAX_COMPLETION_TOKENS must be between 1 and 8000.")

    @classmethod
    def from_env(cls, path: Path):
        env = load_environment(path)
        if env.get("CAPSTONE_LLM_PROVIDER") != "openai_compatible":
            raise ConfigurationError("Set CAPSTONE_LLM_PROVIDER=openai_compatible.")
        try:
            return cls(
                base_url=env.get("LLM_BASE_URL", "").rstrip("/"),
                model=env.get("LLM_MODEL", ""), api_key=env.get("LLM_API_KEY", ""),
                timeout_seconds=float(env.get("LLM_TIMEOUT_SECONDS", "20")),
                max_retries=int(env.get("LLM_MAX_RETRIES", "1")),
                response_format=env.get("LLM_RESPONSE_FORMAT", "json_object"),
                temperature=float(env.get("LLM_TEMPERATURE", "0")),
                max_completion_tokens=int(env.get("LLM_MAX_COMPLETION_TOKENS", "1200")),
            )
        except ValueError as exc:
            if isinstance(exc, ConfigurationError):
                raise
            raise ConfigurationError("Invalid numeric LLM configuration.") from None

    def public_settings(self):
        # Endpoint paths may contain credentials; omit endpoint and API key entirely.
        return {"provider": "openai_compatible", "model": self.model,
                "timeout_seconds": self.timeout_seconds, "max_retries": self.max_retries,
                "response_format": self.response_format, "temperature": self.temperature,
                "max_completion_tokens": self.max_completion_tokens}

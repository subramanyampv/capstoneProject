"""Provider-independent interface and a bounded OpenAI-compatible HTTP adapter."""

import json
import time
from dataclasses import dataclass
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from capstone_agent.config import LLMConfig
from capstone_agent.domain.llm_response import LLMResponse


class ModelError(RuntimeError):
    def __init__(self, category: str, retryable: bool = False):
        super().__init__(category)
        self.category = category
        self.retryable = retryable
        self.attempts = 1


@dataclass
class ModelCompletion:
    content: str
    model: str
    usage: dict
    attempts: int = 1


class ModelClient(Protocol):
    def complete(self, messages: list[dict[str, str]]) -> ModelCompletion: ...


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class OpenAICompatibleClient:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.opener = build_opener(NoRedirect())

    def complete(self, messages: list[dict[str, str]]) -> ModelCompletion:
        body = {"model": self.config.model, "messages": messages,
                "temperature": self.config.temperature,
                "max_completion_tokens": self.config.max_completion_tokens,
                "stream": False}
        if self.config.response_format == "json_schema":
            body["response_format"] = {"type": "json_schema", "json_schema": {
                "name": "support_response", "strict": True,
                "schema": LLMResponse.model_json_schema()}}
        elif self.config.response_format == "json_object":
            body["response_format"] = {"type": "json_object"}
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        request = Request(self.config.base_url.rstrip("/") + "/chat/completions",
                          data=json.dumps(body).encode(), headers=headers, method="POST")
        for attempt in range(self.config.max_retries + 1):
            try:
                with self.opener.open(request, timeout=self.config.timeout_seconds) as response:
                    raw = response.read(1_000_001)
                if len(raw) > 1_000_000:
                    raise ModelError("response_too_large")
                payload = json.loads(raw)
                choice = payload["choices"][0]
                if choice.get("finish_reason") != "stop":
                    raise ModelError("incomplete_or_tool_response")
                message = choice["message"]
                if message.get("refusal") or message.get("tool_calls"):
                    raise ModelError("provider_refusal_or_tool_call")
                content = message["content"]
                model = payload.get("model", self.config.model)
                usage = payload.get("usage") or {}
                if not isinstance(content, str) or not isinstance(model, str) or not isinstance(usage, dict):
                    raise ModelError("invalid_provider_response")
                # Keep only known numeric counters, never arbitrary provider diagnostic fields.
                usage = {key: value for key, value in usage.items()
                         if key in {"prompt_tokens", "completion_tokens", "total_tokens"}
                         and type(value) is int and value >= 0}
                return ModelCompletion(content, model, usage, attempt + 1)
            except ModelError as exc:
                exc.attempts = attempt + 1
                raise
            except HTTPError as exc:
                error = ModelError(f"http_{exc.code}", exc.code in {429, 500, 502, 503, 504})
                exc.close()
            except (TimeoutError, URLError, OSError):
                error = ModelError("connection_or_timeout", True)
            except (ValueError, KeyError, IndexError, TypeError, AttributeError):
                error = ModelError("invalid_provider_response")
            error.attempts = attempt + 1
            if not error.retryable or attempt == self.config.max_retries:
                raise error from None
            time.sleep(0.25 * (attempt + 1))
        raise ModelError("retry_budget_exhausted")

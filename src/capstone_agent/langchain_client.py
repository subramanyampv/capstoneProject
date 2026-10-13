"""LangChain model integration implementing the existing provider-independent contract."""

import time

import httpx
from langchain_openai import ChatOpenAI
from langsmith import tracing_context
from openai import APIConnectionError, APIStatusError, APITimeoutError

from capstone_agent.config import LLMConfig
from capstone_agent.domain.llm_response import LLMResponse
from capstone_agent.model_client import ModelCompletion, ModelError


class LangChainChatClient:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.http = httpx.Client(follow_redirects=False, timeout=config.timeout_seconds)
        self.chat = ChatOpenAI(
            model=config.model, base_url=config.base_url, api_key=config.api_key or "local-no-key",
            timeout=config.timeout_seconds, max_retries=0,
            temperature=config.temperature, max_completion_tokens=config.max_completion_tokens,
            use_responses_api=False, stream_usage=False,
            http_client=self.http,
            extra_body={} if config.enable_thinking is None else {"enable_thinking": config.enable_thinking},
        )

    def close(self):
        self.http.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def complete(self, messages: list[dict[str, str]]) -> ModelCompletion:
        return self.generate(messages, schema=LLMResponse if self.config.response_format == "json_schema" else None)

    def generate(self, messages: list[dict[str, str]], schema=None) -> ModelCompletion:
        options = {}
        if schema is not None:
            options["response_format"] = {"type": "json_schema", "json_schema": {
                "name": "typed_response", "strict": True, "schema": schema.model_json_schema()}}
        elif self.config.response_format == "json_object":
            options["response_format"] = {"type": "json_object"}
        for attempt in range(self.config.max_retries + 1):
            try:
                # Native model traces can capture provider exceptions and additional fields.
                # The graph emits a separate metadata-only model span instead.
                with tracing_context(enabled=False):
                    result = self.chat.invoke(messages, **options)
                metadata = result.response_metadata
                if (metadata.get("finish_reason") != "stop" or result.tool_calls
                        or result.additional_kwargs.get("refusal")):
                    raise ModelError("incomplete_or_tool_response")
                if not isinstance(result.content, str) or len(result.content.encode()) > 1_000_000:
                    raise ModelError("invalid_or_oversize_provider_response")
                counters = metadata.get("token_usage", {})
                if result.usage_metadata:
                    counters = {"prompt_tokens": result.usage_metadata.get("input_tokens"),
                                "completion_tokens": result.usage_metadata.get("output_tokens"),
                                "total_tokens": result.usage_metadata.get("total_tokens")}
                counters = {k: v for k, v in counters.items()
                            if k in {"prompt_tokens", "completion_tokens", "total_tokens"}
                            and type(v) is int and v >= 0}
                return ModelCompletion(result.content, metadata.get("model_name", self.config.model),
                                       counters, attempt + 1)
            except ModelError as exc:
                exc.attempts = attempt + 1
                raise
            except APIStatusError as exc:
                error = ModelError(f"http_{exc.status_code}", exc.status_code in {429, 500, 502, 503, 504})
            except (APITimeoutError, APIConnectionError, httpx.HTTPError):
                error = ModelError("connection_or_timeout", True)
            except (ValueError, KeyError, TypeError, AttributeError):
                error = ModelError("invalid_provider_response")
            error.attempts = attempt + 1
            if not error.retryable or attempt == self.config.max_retries:
                raise error from None
            time.sleep(0.25 * (attempt + 1))
        raise ModelError("retry_budget_exhausted")

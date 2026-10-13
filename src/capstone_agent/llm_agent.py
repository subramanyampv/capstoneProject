"""Single-agent Phase 3. No tools, retrieval, memory or transactional execution."""

import json
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import date

from pydantic import ValidationError

from capstone_agent.domain.llm_response import LLMResponse
from capstone_agent.model_client import ModelClient, ModelError
from capstone_agent.prompts.templates import VERSION, prompt_hash, system_prompt
from capstone_agent.safety.redaction import sanitize, sanitize_data


@dataclass
class LLMRun:
    request_id: str
    prompt_variant: str
    prompt_version: str
    prompt_hash: str
    scenario_date: str
    outcome: str
    response: dict | None
    raw_outputs: list[str]
    returned_models: list[str]
    usage: list[dict]
    latency_ms: float
    model_calls: int
    transport_attempts: int
    error_category: str | None
    tool_calls: list

    def as_dict(self):
        return asdict(self)


def respond(message: str, client: ModelClient, *, variant: str,
            today: date, secrets: tuple[str, ...] = (), repair: bool = True) -> LLMRun:
    if not message.strip() or len(message) > 16000:
        raise ValueError("Message must contain 1–16000 characters.")
    messages = [{"role": "system", "content": system_prompt(variant)},
                {"role": "user", "content": json.dumps({
                    "customer_message": sanitize(message, secrets),
                    "scenario_date": today.isoformat(), "evidence": [],
                })}]
    started = time.perf_counter()
    raw_outputs, models, usage = [], [], []
    error, result, calls, attempts = None, None, 0, 0
    for index in range(2 if repair else 1):
        calls += 1
        try:
            completion = client.complete(messages)
        except ModelError as exc:
            attempts += exc.attempts
            error = exc.category
            break
        attempts += completion.attempts
        raw_outputs.append(sanitize(completion.content, secrets))
        models.append(sanitize(completion.model, secrets))
        usage.append(completion.usage)
        try:
            parsed = LLMResponse.model_validate_json(completion.content)
            if json.loads(completion.content).get("action_executed") is not False:
                raise ValueError("action_execution_claim")
            if parsed.citations:
                # No evidence was supplied; no generated source ID can be resolved.
                raise ValueError("unresolved_citation")
            result = sanitize_data(parsed.model_dump(), secrets)
            error = None
            break
        except (ValidationError, ValueError):
            error = "invalid_output_or_unresolved_citation"
            # Do not echo arbitrary model text or validation details back into the prompt.
            messages.append({"role": "user", "content":
                             "Your previous response failed validation. Return only valid JSON "
                             "matching the supplied schema, with no citations (evidence is empty). "
                             "action_executed must be false. No tools are available."})
    return LLMRun(uuid.uuid4().hex, variant, VERSION, prompt_hash(variant), today.isoformat(),
                  "validated" if result else "error", result, raw_outputs, models, usage,
                  round((time.perf_counter() - started) * 1000, 3), calls, attempts, error, [])

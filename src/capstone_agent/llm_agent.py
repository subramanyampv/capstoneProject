"""Single-agent Phase 3. No tools, retrieval, memory or transactional execution."""

import json
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import date

from pydantic import ValidationError
from typing_extensions import TypedDict
from langgraph.graph import START, END, StateGraph
from langsmith import trace
from capstone_agent.observability.langsmith_tracing import observation, ObservabilityConfig

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
    framework: str = "langgraph"
    graph_steps: list[str] | None = None

    def as_dict(self):
        return asdict(self)


class RequestState(TypedDict, total=False):
    request: str
    messages: list[dict]
    raw_outputs: list[str]
    models: list[str]
    usage: list[dict]
    calls: int
    attempts: int
    content: str | None
    error: str | None
    result: dict | None
    steps: list[str]
    completed: LLMRun


def respond(message: str, client: ModelClient, *, variant: str,
            today: date, secrets: tuple[str, ...] = (), repair: bool = True,
            observability: ObservabilityConfig | None = None) -> LLMRun:
    if not message.strip() or len(message) > 2000:
        raise ValueError("Message must contain 1–2000 characters.")
    started = time.perf_counter()
    request_id = uuid.uuid4().hex

    def prepare(state):
        return {"messages": [{"role": "system", "content": system_prompt(variant)},
                {"role": "user", "content": json.dumps({"customer_message": state["request"],
                    "scenario_date": today.isoformat(), "evidence": []})}],
                "raw_outputs": [], "models": [], "usage": [], "calls": 0,
                "attempts": 0, "error": None, "result": None, "steps": ["prepare"]}

    def call_model(state):
        update = {"calls": state["calls"] + 1, "steps": state["steps"] + ["model"]}
        with trace("model_call", run_type="llm", inputs={}) as span:
            try:
                completion = client.complete(state["messages"])
            except ModelError as exc:
                update.update(error=exc.category, attempts=state["attempts"] + exc.attempts,
                              content=None)
                span.end(outputs={"error_category": exc.category, "model_calls": 1})
                return update
            update.update(content=completion.content, attempts=state["attempts"] + completion.attempts,
                          raw_outputs=state["raw_outputs"] + [sanitize(completion.content, secrets)],
                          models=state["models"] + [sanitize(completion.model, secrets)],
                          usage=state["usage"] + [completion.usage], error=None)
            span.end(outputs={"model": sanitize(completion.model, secrets), **completion.usage})
            return update

    def validate(state):
        update = {"steps": state["steps"] + ["validate"]}
        try:
            parsed = LLMResponse.model_validate_json(state["content"])
            if json.loads(state["content"]).get("action_executed") is not False or parsed.citations:
                raise ValueError("execution_claim_or_unresolved_citation")
            update.update(result=sanitize_data(parsed.model_dump(), secrets), error=None)
        except (ValidationError, ValueError):
            update.update(error="invalid_output_or_unresolved_citation", result=None)
        return update

    def repair_output(state):
        return {"messages": state["messages"] + [{"role": "user", "content":
            "Your previous response failed validation. Return only valid JSON "
            "matching the supplied schema, with no citations (evidence is empty). "
            "action_executed must be false. No tools are available."}],
                "steps": state["steps"] + ["repair"]}

    def finalize(state):
        steps = state["steps"] + ["finalize"]
        completed = LLMRun(request_id, variant, VERSION, prompt_hash(variant), today.isoformat(),
                           "validated" if state["result"] else "error", state["result"],
                           state["raw_outputs"], state["models"], state["usage"],
                           round((time.perf_counter() - started) * 1000, 3), state["calls"],
                           state["attempts"], state["error"], [], graph_steps=steps)
        return {"completed": completed, "steps": steps}

    builder = StateGraph(RequestState)
    for name, node in [("prepare", prepare), ("model", call_model), ("validate", validate),
                       ("repair", repair_output), ("finalize", finalize)]:
        builder.add_node(name, node)
    builder.add_edge(START, "prepare")
    builder.add_edge("prepare", "model")
    builder.add_conditional_edges("model", lambda s: "finalize" if s["error"] else "validate")
    builder.add_conditional_edges("validate", lambda s: "repair" if (
        s["error"] and repair and s["calls"] < 2) else "finalize")
    builder.add_edge("repair", "model")
    builder.add_edge("finalize", END)
    graph = builder.compile()
    with observation(observability, secrets=secrets,
                     metadata={"prompt_variant": variant, "prompt_version": VERSION, "framework": "langgraph"}):
        with trace("support_request", inputs={}, run_id=request_id) as span:
            completed = graph.invoke({"request": sanitize(message, secrets)},
                                     {"recursion_limit": 12})["completed"]
            span.end(outputs={"outcome": completed.outcome, "model_calls": completed.model_calls,
                              "transport_attempts": completed.transport_attempts,
                              "latency_ms": completed.latency_ms, "error_category": completed.error_category})
    return completed

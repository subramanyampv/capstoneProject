import json
import os
from datetime import date
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage

from capstone_agent.config import ConfigurationError, LLMConfig
from capstone_agent.domain.delivery_estimate import DeliveryFacts, estimate_delivery
from capstone_agent.langchain_client import LangChainChatClient
from capstone_agent.llm_agent import respond
from capstone_agent.model_client import ModelCompletion
from capstone_agent.observability.langsmith_tracing import ObservabilityConfig, metric_fields
from capstone_agent.retrieval.knowledge_graph import KnowledgeGraph

TODAY = date(2026, 10, 12)


def valid():
    return json.dumps(dict(intents=["return_eligibility"], status="insufficient_evidence",
        plan_summary=[], response="No evidence supplied.", citations=[], requested_action="none",
        action_executed=False, uncertainty="Missing evidence."))


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)

    def complete(self, messages):
        return ModelCompletion(self.responses.pop(0), "offline-test", {})


def test_graph_repair_route_and_budget():
    result = respond("Return?", FakeClient(["bad", valid()]), variant="C", today=TODAY)
    assert result.graph_steps == ["prepare", "model", "validate", "repair", "model", "validate", "finalize"]
    assert result.model_calls == 2 and result.outcome == "validated"


def test_graph_does_not_repair_when_disabled():
    result = respond("Return?", FakeClient(["bad"]), variant="C", today=TODAY, repair=False)
    assert result.outcome == "error" and result.model_calls == 1
    assert "repair" not in result.graph_steps


def test_langchain_adapter_keeps_standard_usage_only():
    config = LLMConfig(base_url="http://localhost:1234/v1", model="test", enable_thinking=False)
    client = LangChainChatClient(config)

    class FakeChat:
        def invoke(self, messages, **kwargs):
            assert kwargs["response_format"] == {"type": "json_object"}
            return AIMessage(content=valid(), response_metadata={"finish_reason": "stop", "model_name": "test"},
                             usage_metadata={"input_tokens": 5, "output_tokens": 7, "total_tokens": 12})

    client.chat = FakeChat()
    result = client.complete([])
    assert result.usage == {"prompt_tokens": 5, "completion_tokens": 7, "total_tokens": 12}


def test_trace_filters_drop_payloads_and_credentials():
    values = {"outcome": "validated", "model_calls": 1, "response": "private text",
              "messages": [{"content": "secret"}], "api_key": "secret", "model": "secret"}
    assert metric_fields(values, ("secret",)) == {
        "outcome": "validated", "model_calls": 1, "model": "[REDACTED-SECRET]"}


def test_langsmith_explicit_key_required(tmp_path, monkeypatch):
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_TRACING", raising=False)
    path = tmp_path / ".env"
    path.write_text("LANGSMITH_TRACING=true\n")
    with pytest.raises(ConfigurationError):
        ObservabilityConfig.from_env(path)


def facts(**changes):
    return DeliveryFacts(**{**dict(destination="Denver, CO", dispatch_date=TODAY,
        distance_miles=1000, weather="clear", distance_source="synthetic-distance",
        weather_source="synthetic-weather", observed_on=TODAY), **changes})


@pytest.mark.parametrize("miles,base", [(0, 1), (999, 3), (1000, 3), (1001, 4), (2000, 6)])
def test_distance_boundaries(miles, base):
    result = estimate_delivery(facts(distance_miles=miles), today=TODAY)
    assert result["base_days"] == base
    assert result["guaranteed"] is False
    assert result["rule_version"] == "demo-eta-v1"


@pytest.mark.parametrize("weather", ["storm", "snow", "storm_and_snow"])
def test_weather_delay_is_added_once(weather):
    result = estimate_delivery(facts(weather=weather), today=TODAY)
    assert result["weather_delay_days"] == 2
    assert result["earliest"] == "2026-10-17"
    assert result["latest"] == "2026-10-19"


def test_unknown_weather_does_not_become_clear_weather():
    result = estimate_delivery(facts(weather="unknown", weather_source=None), today=TODAY)
    assert result["status"] == "insufficient_evidence" and result["earliest"] is None


def test_stale_weather_requires_refresh():
    result = estimate_delivery(facts(observed_on=date(2026, 10, 13)), today=TODAY)
    assert result["status"] == "insufficient_evidence"


def test_elapsed_window_requests_tracking():
    result = estimate_delivery(facts(dispatch_date=date(2026, 9, 1)), today=TODAY)
    assert result["status"] == "needs_review"


def test_graph_provenance_and_no_private_order_data():
    graph = KnowledgeGraph.from_fixtures()
    result = graph.neighborhood("SKU-SHOES-001")
    assert any(n["id"] == "category:footwear" for n in result["nodes"])
    assert all(e["source_id"] and e["version"] for e in graph.edges)
    assert all(n["kind"] != "order" for n in graph.nodes.values())
    with pytest.raises(ValueError):
        graph.add_edge("SKU-SHOES-001", "applies_to", "category:footwear", source_id="", version="")


def test_deepeval_metrics_report_known_escalation_miss():
    from capstone_agent.evaluation.deepeval_runner import ContractMetric, MandatoryEscalationMetric, LLMTestCase
    case = LLMTestCase(input="Policies conflict", actual_output=valid(), metadata={"case_id": "R05"})
    assert ContractMetric().measure(case) == 1
    assert MandatoryEscalationMetric().measure(case) == 0
    assert os.environ["DEEPEVAL_DISABLE_DOTENV"] == "1"


def test_deepeval_import_does_not_load_private_environment(tmp_path):
    import subprocess
    env = dict(os.environ)
    env.pop("LLM_API_KEY", None)
    (tmp_path / ".env").write_text("LLM_API_KEY=private-canary\n")
    code = "import os; import capstone_agent.evaluation.deepeval_runner; assert 'LLM_API_KEY' not in os.environ"
    import sys
    python = sys.executable  # Use the active local venv, including isolated reproducibility runs.
    result = subprocess.run([python, "-c", code], cwd=tmp_path, env=env, capture_output=True)
    assert result.returncode == 0


def test_distance_tool_validates_units_and_fixed_host():
    from capstone_agent.tools.external_facts import route_distance, FactToolError
    seen = []
    def fetch(url):
        seen.append(url)
        return {"code": "Ok", "routes": [{"distance": 1609344}]}
    result = route_distance(40, -74, 39, -105, fetch=fetch)
    assert result["distance_miles"] == 1000
    assert seen[0].startswith("https://router.project-osrm.org/")
    with pytest.raises(FactToolError):
        route_distance(float("nan"), -74, 39, -105, fetch=fetch)


def test_absent_alerts_are_not_claimed_as_clear_forecast():
    from capstone_agent.tools.external_facts import weather_alerts
    result = weather_alerts(39, -105, fetch=lambda _: {"features": []})
    assert result["weather"] == "no_disruption_alert"
    estimate = estimate_delivery(facts(weather=result["weather"], weather_source=result["source"]), today=TODAY)
    assert estimate["weather_delay_days"] == 0


def test_unmodeled_alerts_require_uncertainty():
    from capstone_agent.tools.external_facts import weather_alerts
    result = weather_alerts(39, -105, fetch=lambda _: {"features": [
        {"properties": {"event": "Air Quality Alert"}}]})
    assert result["weather"] == "unknown"


def test_invalid_weather_payload_is_not_silently_accepted():
    from capstone_agent.tools.external_facts import weather_alerts, FactToolError
    with pytest.raises(FactToolError):
        weather_alerts(39, -105, fetch=lambda _: {"features": None})


def test_judge_failure_is_unmeasured_and_diagnostics_are_not_persisted(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from capstone_agent.evaluation import deepeval_runner as runner
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "outputs.jsonl").write_text(json.dumps({"case_id": "N01", "prompt_variant": "C",
                                                     "response": json.loads(valid())}) + "\n")
    dataset = tmp_path / "cases.json"
    dataset.write_text(json.dumps({"cases": [{"id": "N01", "input": "Return?", "expected_behavior": "Abstain."}]}))
    class FailedMetric:
        def __init__(self, **kwargs): pass
        def measure(self, case): raise RuntimeError("private-diagnostic-canary")
    monkeypatch.setattr(runner, "GEval", FailedMetric)
    judge = SimpleNamespace(config=SimpleNamespace(api_key="private-diagnostic-canary"), get_model_name=lambda: "fake-judge")
    report = runner.evaluate_saved_outputs(run_dir, dataset, judge=judge)
    metric = report["results"][0]["metrics"][-1]
    assert metric["pass"] is None and metric["error_category"] == "judge_failed"
    assert "private-diagnostic-canary" not in (run_dir / "deepeval_results.json").read_text()

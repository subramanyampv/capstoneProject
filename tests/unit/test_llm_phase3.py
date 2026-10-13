import json
from datetime import date
from io import BytesIO
from urllib.error import HTTPError, URLError

import pytest

from capstone_agent.config import ConfigurationError, LLMConfig
from capstone_agent.evaluation.prompt_comparison import ROOT, run_comparison
from capstone_agent.llm_agent import respond
from capstone_agent.model_client import ModelCompletion, ModelError, OpenAICompatibleClient
from capstone_agent.prompts.templates import prompt_hash

TODAY = date(2026, 10, 12)


def output(**changes):
    value = dict(intents=["return_eligibility"], status="insufficient_evidence",
                 plan_summary=["Ask for authoritative policy evidence."],
                 response="I cannot verify the return policy from the supplied evidence.",
                 citations=[], requested_action="none", action_executed=False,
                 uncertainty="No policy or order evidence supplied.")
    return json.dumps({**value, **changes})


class FakeClient:
    def __init__(self, *results):
        self.results = list(results) or [output()]
        self.messages = []

    def complete(self, messages):
        self.messages.append([dict(m) for m in messages])
        result = self.results.pop(0) if len(self.results) > 1 else self.results[0]
        if isinstance(result, Exception):
            raise result
        return ModelCompletion(result, "test-model", {"total_tokens": 42})


def config(**changes):
    return LLMConfig(**{**dict(base_url="http://127.0.0.1:1234/v1", model="test-model"), **changes})


@pytest.mark.parametrize("changes", [
    {"model": ""}, {"timeout_seconds": float("nan")}, {"timeout_seconds": 0},
    {"max_retries": 3}, {"base_url": "http://example.com/v1"},
    {"base_url": "https://example.com/v1"}, {"response_format": "invalid"},
    {"base_url": "http://user:key@localhost/v1"}, {"temperature": float("nan")},
])
def test_invalid_configuration(changes):
    with pytest.raises(ConfigurationError):
        config(**changes)


def test_dotenv_precedence_and_no_shell_evaluation(tmp_path, monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    env = tmp_path / ".env"
    env.write_text('CAPSTONE_LLM_PROVIDER=openai_compatible\nLLM_BASE_URL=http://localhost:1234/v1\n'
                   'LLM_MODEL="file-model" # comment\nLLM_API_KEY=$(secret)\n')
    monkeypatch.setenv("LLM_MODEL", "environment-model")
    loaded = LLMConfig.from_env(env)
    assert loaded.model == "environment-model"
    assert loaded.api_key == "$(secret)"
    assert loaded.api_key not in repr(loaded)


def test_semantic_multi_intent_survives_contract():
    fake = FakeClient(output(intents=["shipping_tracking", "return_eligibility"]))
    result = respond("Where is my order and can I return it?", fake, variant="B", today=TODAY)
    assert result.response["intents"] == ["shipping_tracking", "return_eligibility"]
    assert result.tool_calls == []
    assert result.prompt_hash == prompt_hash("B")


@pytest.mark.parametrize("bad", [
    "not json", output(action_executed=True), output(action_executed=0),
    output(intents=["arbitrary_python"]), output(plan_summary=["step"] * 7),
    output(citations=[dict(source_id="invented", section=None, record_version=None)]),
    output(extra="unexpected"),
])
def test_bounded_repair_then_safe_failure(bad):
    fake = FakeClient(bad)
    result = respond("Return my shoes", fake, variant="C", today=TODAY)
    assert result.outcome == "error" and result.response is None
    assert result.model_calls == 2
    assert len(fake.messages) == 2
    assert bad not in fake.messages[1][-1]["content"]


def test_repair_can_recover():
    result = respond("Return my shoes", FakeClient("not json", output()), variant="C", today=TODAY)
    assert result.outcome == "validated" and result.model_calls == 2


def test_failed_model_does_not_fabricate_success():
    result = respond("Cancel", FakeClient(ModelError("connection_or_timeout")), variant="C", today=TODAY)
    assert result.outcome == "error" and result.response is None
    assert result.error_category == "connection_or_timeout"
    assert result.transport_attempts == 1


def test_sensitive_content_redacted_before_send_and_in_outputs():
    secret = 'local-key-"quoted"'
    text = f"123-45-6789 4111 1111 1111 1111 me@example.com {secret}"
    fake = FakeClient(output(response=text))
    result = respond(text, fake, variant="C", today=TODAY, secrets=(secret,))
    saved = json.dumps(result.as_dict())
    sent = fake.messages[0][-1]["content"]
    for sensitive in ["123-45-6789", "4111 1111 1111 1111", "me@example.com", secret]:
        assert sensitive not in saved and sensitive not in sent


def test_live_harness_isolates_cases_and_keeps_quality_review_pending(tmp_path):
    fake = FakeClient()
    dest = run_comparison(fake, config(), dataset=ROOT / "data/evaluation_cases.json",
                          output_root=tmp_path, today=TODAY, case_ids=["R01", "S07"])
    records = [json.loads(line) for line in (dest / "outputs.jsonl").read_text().splitlines()]
    assert len(records) == len(fake.messages) == 6
    assert {record["prompt_variant"] for record in records} == {"A", "B", "C"}
    assert all(len(messages) == 2 for messages in fake.messages)
    assert all(json.loads(messages[-1]["content"])["evidence"] == [] for messages in fake.messages)
    assert json.loads((dest / "summary.json").read_text())["default_prompt"] is None
    assert "123-45-6789" not in (dest / "outputs.jsonl").read_text()


def test_full_dry_run_makes_no_model_calls(tmp_path):
    fake = FakeClient()
    dest = run_comparison(fake, config(), dataset=ROOT / "data/evaluation_cases.json",
                          output_root=tmp_path, today=TODAY, dry_run=True)
    assert fake.messages == []
    manifest = json.loads((dest / "manifest.json").read_text())
    assert manifest["scheduled_requests"] == 195
    assert len(manifest["case_ids"]) == 65
    assert not (dest / "outputs.jsonl").exists()


def test_concurrent_comparison_uses_independent_clients_and_complete_records(tmp_path):
    clients = []

    def factory():
        client = FakeClient()
        clients.append(client)
        return client

    dest = run_comparison(FakeClient(), config(), dataset=ROOT / "data/evaluation_cases.json",
                          output_root=tmp_path, today=TODAY, case_ids=["N01", "R01"],
                          workers=3, client_factory=factory)
    records = [json.loads(line) for line in (dest / "outputs.jsonl").read_text().splitlines()]
    assert len(records) == len(clients) == 6
    assert all(len(client.messages) == 1 for client in clients)
    assert [(r["case_id"], r["prompt_variant"]) for r in records] == [
        (case, variant) for case in ["N01", "R01"] for variant in "ABC"]


class FakeOpener:
    def __init__(self, *results):
        self.results = list(results)
        self.requests = []

    def open(self, request, timeout):
        self.requests.append((request, timeout))
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return BytesIO(json.dumps(result).encode())


def wire_response(**changes):
    return {**dict(model="test-model", choices=[dict(finish_reason="stop", message={"content": output()})],
                   usage={"total_tokens": 42, "debug": "do not persist"}), **changes}


def test_adapter_contract_and_no_key_for_local_server():
    client = OpenAICompatibleClient(config())
    client.opener = FakeOpener(wire_response())
    result = client.complete([{"role": "user", "content": "JSON please"}])
    request, timeout = client.opener.requests[0]
    assert request.full_url == "http://127.0.0.1:1234/v1/chat/completions"
    assert request.get_header("Authorization") is None
    assert json.loads(request.data)["response_format"] == {"type": "json_object"}
    assert result.usage == {"total_tokens": 42}
    assert timeout == 20
    assert "enable_thinking" not in json.loads(request.data)


def test_qwen_thinking_setting_is_explicit_and_recorded():
    client = OpenAICompatibleClient(config(enable_thinking=False))
    client.opener = FakeOpener(wire_response())
    client.complete([])
    assert json.loads(client.opener.requests[0][0].data)["enable_thinking"] is False
    assert client.config.public_settings()["enable_thinking"] is False


def test_openai_provider_alias(tmp_path, monkeypatch):
    monkeypatch.delenv("CAPSTONE_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("LLM_ENABLE_THINKING", raising=False)
    env = tmp_path / ".env"
    env.write_text('CAPSTONE_LLM_PROVIDER=openai\nLLM_BASE_URL=http://localhost:1234/v1\n'
                   'LLM_MODEL=test-model\n')
    assert LLMConfig.from_env(env).enable_thinking is None


def test_committed_env_template_contains_no_api_key():
    lines = (ROOT / ".env.example").read_text().splitlines()
    key_values = [line.split("=", 1)[1].split(" #", 1)[0].strip().strip("\"'")
                  for line in lines if line.strip().startswith("LLM_API_KEY=")]
    assert key_values == [""]


def test_timeout_retries_are_bounded(monkeypatch):
    monkeypatch.setattr("capstone_agent.model_client.time.sleep", lambda _: None)
    client = OpenAICompatibleClient(config(max_retries=2))
    client.opener = FakeOpener(*[URLError("private diagnostics") for _ in range(3)])
    with pytest.raises(ModelError) as error:
        client.complete([])
    assert len(client.opener.requests) == error.value.attempts == 3
    assert "private diagnostics" not in str(error.value)


def test_auth_failure_is_not_retried_or_echoed():
    client = OpenAICompatibleClient(config(api_key="secret-value"))
    client.opener = FakeOpener(HTTPError("http://localhost", 401, "secret-value", {}, None))
    with pytest.raises(ModelError, match="http_401"):
        client.complete([])
    assert len(client.opener.requests) == 1


@pytest.mark.parametrize("payload", [
    {}, wire_response(choices=[]), wire_response(choices=["malformed-choice"]),
    wire_response(choices=[dict(finish_reason="length", message={"content": output()})]),
    wire_response(choices=[dict(finish_reason="stop", message={"content": output(), "tool_calls": [{}]})]),
])
def test_invalid_provider_envelopes_fail_safely(payload):
    client = OpenAICompatibleClient(config())
    client.opener = FakeOpener(payload)
    with pytest.raises(ModelError):
        client.complete([])


def test_prompt_hashes_are_distinct_and_stable():
    assert len({prompt_hash(v) for v in "ABC"}) == 3
    assert prompt_hash("C") == prompt_hash("C")


def test_v3_default_and_input_limit():
    from capstone_agent.main import build_parser
    assert build_parser().parse_args(["llm-ask", "return question"]).prompt == "C"
    fake = FakeClient()
    with pytest.raises(ValueError, match="2000"):
        respond("x" * 2001, fake, variant="C", today=TODAY)
    assert fake.messages == []


def test_v3_model_aliases_and_deferred_ui_defaults(tmp_path, monkeypatch):
    from capstone_agent.config import show_deferred_ui
    for name in ["CAPSTONE_LLM_PROVIDER", "MODEL_BASE_URL", "MODEL_NAME", "MODEL_API_KEY", "UI_SHOW_DEFERRED"]:
        monkeypatch.delenv(name, raising=False)
    env = tmp_path / ".env"
    env.write_text('CAPSTONE_LLM_PROVIDER=openai_compatible\nMODEL_BASE_URL=http://localhost:1234/v1\nMODEL_NAME=canonical-model\nMODEL_API_KEY=synthetic-key\n')
    config = LLMConfig.from_env(env)
    assert config.model == "canonical-model" and config.api_key == "synthetic-key"
    assert not show_deferred_ui(env)
    monkeypatch.setenv("UI_SHOW_DEFERRED", "true")
    assert show_deferred_ui(env)
    monkeypatch.setenv("UI_SHOW_DEFERRED", "invalid")
    with pytest.raises(ConfigurationError):
        show_deferred_ui(env)

"""Local DeepEval metrics over saved outputs; explicit optional model judge."""

import asyncio
import hashlib
import json
import os
from pathlib import Path

# Avoid implicit dotenv loading, analytics, logins, or a second cloud tracing service.
os.environ["DEEPEVAL_DISABLE_DOTENV"] = "1"
os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"
os.environ["DEEPEVAL_UPDATE_WARNING_OPT_OUT"] = "YES"

from deepeval.metrics import BaseMetric, GEval
from deepeval.models import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase, SingleTurnParams
from langsmith import tracing_context
from pydantic import ValidationError

from capstone_agent.domain.llm_response import LLMResponse
from capstone_agent.langchain_client import LangChainChatClient
from capstone_agent.safety.redaction import sanitize, sanitize_data


class ContractMetric(BaseMetric):
    threshold = 1
    async_mode = False
    evaluation_cost = 0

    @property
    def __name__(self):
        return "Schema and action-claim contract"

    def measure(self, test_case, **kwargs):
        try:
            parsed = LLMResponse.model_validate_json(test_case.actual_output)
            passed = (json.loads(test_case.actual_output).get("action_executed") is False
                      and not parsed.citations)
        except (ValueError, ValidationError):
            passed = False
        self.score = float(passed)
        self.success = passed
        self.reason = "Typed contract passed; no actions/citations allowed in Phase 3." if passed else "Contract failed."
        return self.score

    async def a_measure(self, test_case, **kwargs):
        return self.measure(test_case, **kwargs)

    def is_successful(self):
        return self.success


class MandatoryEscalationMetric(ContractMetric):
    @property
    def __name__(self):
        return "Mandatory escalation classification (final requirement)"

    def measure(self, test_case, **kwargs):
        self.reason = "Checks classification only, not ticket creation or policy authority."
        metadata = test_case.metadata or {}
        if metadata.get("case_id") not in {"R05", "S01", "S15"}:
            self.score = None
            self.success = None
            self.reason = "Not applicable to this case."
            return None
        try:
            self.success = json.loads(test_case.actual_output).get("status") == "escalation_required"
        except (ValueError, AttributeError):
            self.success = False
        self.score = float(self.success)
        return self.score


class ConfiguredJudge(DeepEvalBaseLLM):
    def __init__(self, config):
        self.config = config
        self.client = LangChainChatClient(config)

    def load_model(self):
        return self.client

    def get_model_name(self):
        return self.config.model

    def generate(self, prompt: str, schema=None):
        instructions = "Return only JSON matching the requested evaluation schema."
        if schema is not None:
            instructions += json.dumps(schema.model_json_schema())
        completion = self.client.generate([
            {"role": "system", "content": instructions},
            {"role": "user", "content": sanitize(prompt, (self.config.api_key,))}], schema=schema)
        if schema is not None:
            return schema.model_validate_json(completion.content)
        return completion.content

    async def a_generate(self, prompt: str, schema=None):
        return await asyncio.to_thread(self.generate, prompt, schema)


def evaluate_saved_outputs(run_dir: Path, dataset: Path, *, judge=None, case_ids=None):
    source = run_dir / "outputs.jsonl"
    cases = {case["id"]: case for case in json.loads(dataset.read_text())["cases"]}
    rows = [json.loads(line) for line in source.read_text().splitlines()]
    output = []
    # Direct metric.measure keeps evaluation local and avoids Confident AI uploads.
    with tracing_context(enabled=False):
        for row in rows:
            if case_ids and row["case_id"] not in case_ids:
                continue
            case = cases[row["case_id"]]
            response = row.get("response")
            test = LLMTestCase(input=sanitize(case["input"]), actual_output=json.dumps(response),
                               expected_output=case["expected_behavior"], metadata={"case_id": row["case_id"]})
            metrics = []
            for metric in (ContractMetric(), MandatoryEscalationMetric()):
                metric.measure(test)
                metrics.append({"name": metric.__name__, "score": metric.score,
                                "pass": metric.success, "reason": metric.reason})
            if judge and response:
                semantic = LLMTestCase(input=sanitize(case["input"]), actual_output=response["response"],
                                       expected_output=case["expected_behavior"])
                metric = GEval(name="Phase 3 evidence restraint", model=judge, async_mode=False,
                    threshold=.9, evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
                    evaluation_steps=["The system has no verified records, tools or retrieved evidence.",
                        "Check whether the answer invents retailer policy, order facts or completed actions.",
                        "Reward clear abstention, refusal, appropriate human review, and coverage of all intents."])
                try:
                    metric.measure(semantic)
                    metrics.append({"name": metric.__name__, "score": metric.score,
                                    "pass": metric.is_successful(), "reason": sanitize(metric.reason or "", (judge.config.api_key,))})
                except Exception:
                    # Do not expose SDK/provider errors or treat failed judges as passes.
                    metrics.append({"name": "Phase 3 evidence restraint", "score": None,
                                    "pass": None, "error_category": "judge_failed",
                                    "reason": "Judge failed; quality not measured."})
            output.append({"case_id": row["case_id"], "prompt": row["prompt_variant"], "metrics": metrics})
    report = {"library": "deepeval", "source_run": run_dir.name,
              "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "judge": judge.get_model_name() if judge else None, "results": output,
              "limits": "Contract checks are not semantic accuracy. Escalation checks flag final requirements; "
                        "ticket execution and threshold evidence await later phases. No cloud uploads."}
    secrets = (judge.config.api_key,) if judge else ()
    (run_dir / "deepeval_results.json").write_text(json.dumps(sanitize_data(report, secrets), indent=2) + "\n")
    return report

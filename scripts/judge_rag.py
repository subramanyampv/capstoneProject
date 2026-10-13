"""Local DeepEval faithfulness on saved RAG outputs; never silently pass missing context."""

import hashlib
import json
import os
import sys
from pathlib import Path

os.environ["DEEPEVAL_DISABLE_DOTENV"] = "1"
os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"
os.environ["DEEPEVAL_UPDATE_WARNING_OPT_OUT"] = "YES"

from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase

from capstone_agent.config import LLMConfig
from capstone_agent.evaluation.deepeval_runner import ConfiguredJudge
from capstone_agent.safety.redaction import sanitize_data

ROOT = Path(__file__).resolve().parents[1]


def main():
    directory = Path(sys.argv[1])
    configuration = LLMConfig.from_env(ROOT / ".env")
    judge = ConfiguredJudge(configuration)
    inputs = {c["id"]: c["input"] for c in json.loads((ROOT / "data/evaluation_cases.json").read_text())["cases"]}
    results = []
    for row in map(json.loads, (directory / "outputs.jsonl").read_text().splitlines()):
        result = {"case_id": row["case_id"], "retrieval_enabled": row["retrieval_enabled"],
                  "score": None, "pass": None, "status": "skipped", "reason": "No validated answer with retrieval context."}
        if row["response"] and row["evidence"]:
            try:
                metric = FaithfulnessMetric(threshold=.9, model=judge, async_mode=False, include_reason=True)
                metric.measure(LLMTestCase(input=inputs[row["case_id"]], actual_output=row["response"]["response"],
                               retrieval_context=[e["text"] for e in row["evidence"]]))
                result.update(score=float(metric.score), **{"pass": metric.is_successful()},
                              status="measured", reason=metric.reason)
            except Exception:
                result.update(status="judge_error", reason="Judge could not produce a valid score.")
        results.append(result)
        print(row["case_id"], "rag" if row["retrieval_enabled"] else "no-rag", result["status"], flush=True)
    report = {"library": "deepeval", "metric": "Faithfulness", "threshold": .9,
              "judge_model": configuration.model, "same_as_generation": True,
              "source_sha256": hashlib.sha256((directory / "outputs.jsonl").read_bytes()).hexdigest(),
              "limits": "Same-model indicative judging; human calibration not performed. Empty context skipped, never passed. Safety gates remain deterministic.",
              "results": results}
    (directory / "deepeval_faithfulness.json").write_text(json.dumps(sanitize_data(report, (configuration.api_key,)), indent=2) + "\n")
    return int(any(r["status"] == "judge_error" for r in results))


if __name__ == "__main__":
    raise SystemExit(main())

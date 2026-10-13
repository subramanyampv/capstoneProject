"""Actual per-case outputs and manual review sheet; never manufacture quality scores."""

import csv
import hashlib
import json
import platform
import uuid
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path

from capstone_agent.config import LLMConfig
from capstone_agent.llm_agent import respond
from capstone_agent.model_client import ModelClient
from capstone_agent.prompts.templates import VERSION, STRATEGIES, prompt_hash, system_prompt
from capstone_agent.safety.redaction import sanitize_data

ROOT = Path(__file__).resolve().parents[3]


def load_cases(path: Path):
    payload = json.loads(path.read_text())
    cases = payload["cases"]
    ids = [case["id"] for case in cases]
    if len(ids) != len(set(ids)) or not cases:
        raise ValueError("Dataset must contain distinct case IDs.")
    return payload, hashlib.sha256(path.read_bytes()).hexdigest()


def run_comparison(client: ModelClient, config: LLMConfig, *, dataset: Path,
                   output_root: Path, today: date, case_ids: list[str] | None = None,
                   dry_run: bool = False, progress=None, workers: int = 1, client_factory=None,
                   observability=None) -> Path:
    if not 1 <= workers <= 4:
        raise ValueError("workers must be between 1 and 4.")
    if workers > 1 and client_factory is None:
        raise ValueError("Concurrent runs require an independent client factory.")
    payload, dataset_hash = load_cases(dataset)
    cases = payload["cases"]
    if case_ids:
        unknown = set(case_ids) - {case["id"] for case in cases}
        if unknown:
            raise ValueError("Unknown evaluation case IDs: " + ", ".join(sorted(unknown)))
        cases = [case for case in cases if case["id"] in case_ids]
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    output = output_root / run_id
    output.mkdir(parents=True, exist_ok=False)
    manifest = {
        "run_id": run_id, "mode": "dry_run" if dry_run else "live",
        "python_version": platform.python_version(), "application_version": "0.1.0",
        "scenario_date": today.isoformat(), "dataset_version": payload["schema_version"],
        "dataset_sha256": dataset_hash, "case_ids": [case["id"] for case in cases],
        "settings": config.public_settings(), "prompt_version": VERSION,
        "prompt_hashes": {v: prompt_hash(v) for v in STRATEGIES},
        "evidence": [], "tools": [], "memory": False, "repair_attempts": 1,
        "workers": workers,
        "scheduled_requests": len(cases) * len(STRATEGIES),
        "max_http_attempts": len(cases) * len(STRATEGIES) * 2 * (config.max_retries + 1),
        "default_prompt": None, "quality_review_status": "pending",
        "workflow": "langgraph", "model_client": type(client).__name__,
        "langsmith_tracing": bool(observability and observability.enabled),
    }
    secrets = (config.api_key, observability.api_key if observability else "")
    (output / "manifest.json").write_text(json.dumps(sanitize_data(manifest, secrets), indent=2) + "\n")
    (output / "prompts.json").write_text(json.dumps({
        v: system_prompt(v)
        for v in STRATEGIES}, indent=2) + "\n")
    if dry_run:
        (output / "summary.json").write_text(json.dumps({
            "mode": "dry_run", "model_requests": 0, "default_prompt": None,
            "note": "Plan only. No model outputs or quality measurements."}, indent=2) + "\n")
        return output
    counts = Counter()
    fields = ["case_id", "category", "prompt", "outcome", "response", "citations",
              "latency_ms", "error_category", "expected_behavior", "safety_pass",
              "grounding_pass", "usefulness_score", "reviewer_notes"]
    with (output / "outputs.jsonl").open("w") as records, (output / "prompt_comparison.csv").open("w", newline="") as sheet:
        writer = csv.DictWriter(sheet, fieldnames=fields)
        writer.writeheader()
        tasks = [(case, variant) for case in cases for variant in STRATEGIES]

        def evaluate(task):
            case, variant = task
            worker_client = client_factory() if client_factory else client
            try:
                result = respond(case["input"], worker_client, variant=variant, today=today, secrets=secrets,
                                 observability=observability)
            finally:
                if client_factory and hasattr(worker_client, "close"):
                    worker_client.close()
            return case, variant, result

        with ThreadPoolExecutor(max_workers=workers) as executor:
            for case, variant, result in executor.map(evaluate, tasks):
                record = {"case_id": case["id"], "category": case["category"],
                          "expected_behavior": case["expected_behavior"], **result.as_dict()}
                records.write(json.dumps(sanitize_data(record, secrets)) + "\n")
                records.flush()
                response = result.response or {}
                writer.writerow({"case_id": case["id"], "category": case["category"],
                                 "prompt": variant, "outcome": result.outcome,
                                 "response": response.get("response", ""),
                                 "citations": json.dumps(response.get("citations", [])),
                                 "latency_ms": result.latency_ms, "error_category": result.error_category,
                                 "expected_behavior": case["expected_behavior"]})
                sheet.flush()
                counts[f"{variant}:{result.outcome}"] += 1
                if progress:
                    progress(case["id"], variant, result.outcome)
    (output / "summary.json").write_text(json.dumps({
        "mode": "live", "counts": dict(counts), "default_prompt": None,
        "note": "Validated means schema/citation validation only. Human safety/grounding review "
                "is required. Future retrieval/tools/memory gates are not measured here."}, indent=2) + "\n")
    return output

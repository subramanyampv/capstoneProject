"""Verify Phase 2 demo evidence without a model, network or private configuration."""

import hashlib
import json
import statistics
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from capstone_agent.baseline_agent import DEMO_SEQUENCE, DataBundle, log_line, respond

ROOT = Path(__file__).resolve().parents[1]
CLOCK = date(2026, 10, 12)
EXPECTED = [
    ("shipping_tracking", True, "No carrier events yet"),
    ("return_eligibility", True, "ELIGIBLE: 12 days"),
    ("fallback", False, "didn't understand"),
    ("return_eligibility", True, "has not been delivered"),
    ("return_eligibility", True, "NOT ELIGIBLE: 31 days"),
    ("shipping_tracking", True, "not found in verified records"),
    ("cancellation", True, "baseline cannot execute"),
    ("product_information", True, "comes in sizes"),
]


def main():
    log_path = ROOT / "artifacts/baseline_run.log"
    demo_path = ROOT / "artifacts/baseline_demo_outputs.txt"
    logs = [json.loads(line) for line in log_path.read_text().splitlines()]
    demo = demo_path.read_text()
    data = DataBundle.load(ROOT)
    observations = []
    evidence_matches = len(logs) == len(EXPECTED) == len(DEMO_SEQUENCE)
    for index, ((label, message), (intent, matched, snippet)) in enumerate(zip(DEMO_SEQUENCE, EXPECTED)):
        result = respond(message, today=CLOCK, data=data)
        observed = logs[index] if index < len(logs) else {}
        verified = (result.intent == intent and result.matched == matched
                    and snippet in result.response and result.response in demo
                    and observed.get("input") == message
                    and observed.get("intent") == intent
                    and observed.get("matched") == matched)
        if index == 3:
            verified = verified and "Latest tracking event" not in result.response
        observations.append({"case": index + 1, "label": label,
                             "kind": "known_limitation" if index in (2, 3) else "supported_demo",
                             "expected_intent": intent, "observed_intent": result.intent,
                             "evidence_verified": verified})
        evidence_matches = evidence_matches and verified

    canaries = ["123-45-6789", "4111 1111 1111 1111", "sk-syntheticcanary123",
                "synthetic-canary-token", "synthetic-canary-key", "customer@example.test"]
    message = (f"{canaries[0]} {canaries[1]} {canaries[2]} Bearer {canaries[3]} "
               f"api_key={canaries[4]} {canaries[5]} track order O-1003")
    sanitized = log_line(respond(message, today=CLOCK, data=data), message)
    redaction_passed = all(canary not in sanitized for canary in canaries)
    paths = ["data/policy_rules.json", "data/sample_orders.json",
             "data/sample_tracking_events.json", "data/product_catalog.json",
             "data/evaluation_cases.json", "src/capstone_agent/baseline_agent.py",
             "src/capstone_agent/safety/redaction.py", "scripts/run_baseline.sh",
             "scripts/verify_baseline.py", "tests/unit/test_baseline_agent.py",
             "artifacts/baseline_run.log", "artifacts/baseline_demo_outputs.txt"]
    report = {
        "phase": 2, "status": "passed" if evidence_matches and redaction_passed else "failed",
        "verified_at": datetime.now(ZoneInfo("America/New_York")).isoformat(),
        "scenario_clock": CLOCK.isoformat(), "policy_version": data.rules["version"],
        "catalog_version": data.catalog_version,
        "supported_demo_cases": 6, "known_limitations_demonstrated": 2,
        "demo_evidence_matches": evidence_matches, "log_canary_check_passed": redaction_passed,
        "median_demo_latency_ms": statistics.median([line["latency_ms"] for line in logs]) if logs else None,
        "scope": "Eight scripted demo cases and pattern-based synthetic canaries; not the 65-case final acceptance suite.",
        "cases": observations,
        "sha256": {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in paths},
    }
    (ROOT / "artifacts/phase2_verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Phase 2 verification: {report['status']}; report: artifacts/phase2_verification.json")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

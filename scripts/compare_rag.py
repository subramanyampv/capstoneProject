"""Run the same ten frozen policy queries with retrieval disabled/enabled."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from capstone_agent.config import LLMConfig
from capstone_agent.langchain_client import LangChainChatClient
from capstone_agent.retrieval.chroma_store import PolicySearch
from capstone_agent.retrieval.configured_embeddings import ConfiguredEmbeddings
from capstone_agent.retrieval.grounded_answer import SYSTEM, VERSION, answer
from capstone_agent.retrieval.query_expansion import PROFILE
from capstone_agent.safety.redaction import sanitize_data

ROOT = Path(__file__).resolve().parents[1]
CASES = ['R01', 'R02', 'R05', 'R07', 'R08', 'R09', 'R10', 'R12', 'R13', 'R15']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", action="append", choices=CASES, help="Optional targeted frozen-case subset")
    arguments = parser.parse_args()
    selected = list(dict.fromkeys(arguments.case)) if arguments.case else CASES
    search = PolicySearch(ConfiguredEmbeddings())
    config = LLMConfig.from_env(ROOT / ".env")
    cases = json.loads((ROOT / "data/evaluation_cases.json").read_text())["cases"]
    directory = ROOT / "artifacts/rag_runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "prompt.txt").write_text(SYSTEM + "\n")
    (directory / "query_expansion_snapshot.py").write_text((ROOT / "src/capstone_agent/retrieval/query_expansion.py").read_text())
    records = []
    with LangChainChatClient(config) as client, (directory / "outputs.jsonl").open("w") as stream:
        for case in [c for c in cases if c["id"] in selected]:
            for enabled in [False, True]:
                retrieval = search.search(case["input"]) if enabled else {"results": [], "conflict": False}
                result = answer(case["input"], client, retrieval, secrets=(config.api_key,))
                record = {"case_id": case["id"], "retrieval_enabled": enabled,
                          "query_hints": retrieval.get("query_hints", []),
                          "retrieval_results": retrieval["results"], **result}
                records.append(record); stream.write(json.dumps(record) + "\n"); stream.flush()
                print(case["id"], "rag" if enabled else "no-rag", result["outcome"], flush=True)
    report = {"case_ids": selected, "dataset_sha256": hashlib.sha256((ROOT / "data/evaluation_cases.json").read_bytes()).hexdigest(),
              "prompt_version": VERSION, "prompt_sha256": hashlib.sha256(SYSTEM.encode()).hexdigest(),
              "settings": config.public_settings(), "index_version": search.manifest["index_version"],
              "threshold": search.threshold, "query_profile": PROFILE,
              "query_expansion_sha256": hashlib.sha256((ROOT / "src/capstone_agent/retrieval/query_expansion.py").read_bytes()).hexdigest(),
              "results": {}}
    for enabled in [False, True]:
        group = [r for r in records if r["retrieval_enabled"] is enabled]
        report["results"]["rag" if enabled else "no_rag"] = {
            "validated": sum(r["outcome"] == "validated" for r in group),
            "errors": sum(r["outcome"] == "error" for r in group),
            "cited_outputs": sum(bool((r["response"] or {}).get("citations")) for r in group),
            "success_status": sum((r["response"] or {}).get("status") == "success" for r in group),
            "escalation_classification": sum((r["response"] or {}).get("status") == "escalation_required" for r in group),
            "output_validation": "Citation resolution and syntactic numeric grounding; not semantic faithfulness or final safety acceptance."}
    report["limits"] = "Single-agent Phase 4 experiment, not final multi-agent workflow. No records/tools/tickets. Guard failures are errors, not fabricated-claim passes. DeepEval faithfulness and human calibration pending."
    (directory / "summary.json").write_text(json.dumps(sanitize_data(report, (config.api_key,)), indent=2) + "\n")
    print("Evidence:", directory)
    return int(any(r["outcome"] == "error" for r in records))


if __name__ == "__main__":
    raise SystemExit(main())

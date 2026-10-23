"""Calibrate on development labels, then record measured retrieval and abstention."""

import csv
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from capstone_agent.retrieval.chroma_store import PolicySearch
from capstone_agent.retrieval.configured_embeddings import ConfiguredEmbeddings
from capstone_agent.retrieval.query_expansion import PROFILE

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--index-version", default="v2")
    parser.add_argument("--labels", default="data/retrieval_labels.json")
    parser.add_argument("--output", default="artifacts/retrieval/category_v2_20261013")
    arguments = parser.parse_args()
    label_path = ROOT / arguments.labels
    labels = json.loads(label_path.read_text())["labels"]
    search = PolicySearch(ConfiguredEmbeddings(), version=arguments.index_version, threshold=-1)
    raw = [(label, search.search(label["query"])) for label in labels]
    thresholds = sorted({0., 1., *(round(c["score"] + delta, 6) for _, result in raw
                                  for c in result["raw_vector_top_k"] for delta in (0, .000001))})
    def calibration(threshold):
        tp = sum(any(c["score"] >= threshold for c in result["raw_vector_top_k"])
                 for label, result in raw if label["answerable"])
        tn = sum(not any(c["score"] >= threshold for c in result["raw_vector_top_k"])
                 for label, result in raw if not label["answerable"])
        positives = sum(label["answerable"] for label in labels)
        negatives = len(labels) - positives
        return ((tp / positives + tn / negatives) / 2, tn, tp)
    threshold = max(thresholds, key=calibration)
    search.threshold = threshold
    records = []
    for label, first in raw:
        # Reuse embedded candidates; avoid repeated local query work in this small calibration set.
        ranked = first["raw_vector_top_k"]
        expected = {tuple(item) for item in label["expected"]}
        found = [(r["doc_id"], r["section_id"]) for r in ranked]
        recall = len(expected & set(found)) / len(expected) if expected else None
        rr = next((1 / (index + 1) for index, target in enumerate(found) if target in expected), 0) if expected else None
        admitted = [r for r in ranked if r["score"] >= threshold]
        # Report pure vector quality separately from deterministic conflict source insertion.
        records.append({"id": label["id"], "query": label["query"], "answerable": label["answerable"],
                        "recall_at_5": recall, "reciprocal_rank": rr,
                        "post_threshold_recall_at_5": len(expected & {(r['doc_id'], r['section_id']) for r in admitted}) / len(expected) if expected else None,
                        "below_threshold": not admitted, "abstention_correct": not admitted if not expected else None,
                        "top_score": max((c["score"] for c in ranked), default=None),
                        "query_hints": first["query_hints"],
                        "top_5": [r["chunk_id"] for r in ranked]})
    answerable = [r for r in records if r["answerable"]]
    unknown = [r for r in records if not r["answerable"]]
    conflict = search.search(labels[3]["query"])
    summary = {"recorded_at": datetime.now(timezone.utc).isoformat(), "index_version": search.manifest["index_version"],
               "query_profile": PROFILE,
               "query_expansion_sha256": hashlib.sha256((ROOT / "src/capstone_agent/retrieval/query_expansion.py").read_bytes()).hexdigest(),
               "labels_sha256": hashlib.sha256(label_path.read_bytes()).hexdigest(), "queries": len(records),
               "answerable": len(answerable), "unanswerable": len(unknown), "threshold": threshold,
               "threshold_selection": "Maximize balanced answerability accuracy on the same development label set; not held-out validation.",
               "raw_vector_recall_at_5": sum(r["recall_at_5"] for r in answerable) / len(answerable),
               "raw_vector_mrr": sum(r["reciprocal_rank"] for r in answerable) / len(answerable),
               "post_threshold_recall_at_5": sum(r["post_threshold_recall_at_5"] for r in answerable) / len(answerable),
               "answerable_abstentions": sum(r["below_threshold"] for r in answerable),
               "unanswerable_abstention_correct": sum(r["abstention_correct"] for r in unknown),
               "r05_conflict_detected": conflict["conflict"], "r05_sources": conflict["conflict_details"],
               "limits": "Small assistant-authored calibration set; declared R05 conflict handling is deterministic and not part of raw vector Recall@5. Final safety/ticket creation not measured."}
    artifacts = ROOT / arguments.output
    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (artifacts / "results.json").write_text(json.dumps(records, indent=2) + "\n")
    with (artifacts / "retrieval_eval.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(records)
    examples = []
    for index in [0, 3, 17]:
        label, result = raw[index]
        expected = {tuple(item) for item in label["expected"]}
        hits = [{**hit, "labeled_relevant": (hit["doc_id"], hit["section_id"]) in expected,
                 "review_note": "Matches the labeled governing section." if (hit["doc_id"], hit["section_id"]) in expected
                 else "Not the labeled governing section; similarity alone is not policy authority."}
                for hit in result["raw_vector_top_k"][:3]]
        examples.append({"query": label["query"], "expected": label["expected"], "top_3": hits})
    (artifacts / "relevance_examples.json").write_text(json.dumps(examples, indent=2) + "\n")
    (ROOT / "config").mkdir(exist_ok=True)
    (ROOT / "config/retrieval.json").write_text(json.dumps({"index_version": search.manifest["index_version"], "threshold": threshold,
                  "dimension": search.manifest["dimension"], "top_k": 5, "query_profile": PROFILE,
                  "query_expansion_sha256": summary["query_expansion_sha256"]}, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

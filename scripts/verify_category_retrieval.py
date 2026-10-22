"""Offline category-filter checks with the real pinned local embedding/index."""

import json
from datetime import datetime, timezone
from pathlib import Path

from capstone_agent.retrieval.chroma_store import PolicySearch
from capstone_agent.retrieval.configured_embeddings import ConfiguredEmbeddings

ROOT = Path(__file__).resolve().parents[1]


def main():
    search = PolicySearch(ConfiguredEmbeddings())
    records = []
    for category in ["footwear", "apparel", "home", "electronics", "perishable_grocery"]:
        result = search.search("return window and restocking fee", category=category,
                               doc_types=["return_policy"], k=10)
        assert all(row[f"applies_{category}"] for row in result["results"] + result["raw_vector_top_k"])
        assert ("restocking" in {r["section_id"] for r in result["raw_vector_top_k"]}) == (category == "electronics")
        # Filtering must preserve general governing candidates, but it must not
        # bypass the calibrated similarity threshold to force an answer.
        assert "window" in {r["section_id"] for r in result["raw_vector_top_k"]}
        assert result["conflict"] == (category == "electronics")
        records.append({"category": category, **result})
    conflict = search.search("electronics return policy", category="electronics", doc_types=["return_policy"], k=1)
    assert conflict["conflict"] and conflict["conflict_evidence_exceeds_k"]
    assert {row["doc_id"] for row in conflict["results"]} == {"faq", "return_policy"}
    exclusions = search.search("perishable grocery return exclusions", category="perishable_grocery",
                               doc_types=["return_policy"], k=10)
    assert "exclusions" in {row["section_id"] for row in exclusions["raw_vector_top_k"]}
    evidence = {"recorded_at": datetime.now(timezone.utc).isoformat(), "index_version": search.manifest["index_version"],
                "metadata_profile": search.manifest["metadata_profile"], "threshold": search.threshold,
                "checks_passed": True, "categories": records, "conflict_k1": conflict,
                "perishable_exclusions": exclusions,
                "limits": "Structural applicability checks on authored synthetic metadata, not held-out relevance or final agent acceptance."}
    destination = ROOT / "artifacts/retrieval/category_v2_20261013/category_checks.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(evidence, indent=2) + "\n")
    print("Five category filters, general exclusions and filtered k=1 conflict: passed")


if __name__ == "__main__":
    main()

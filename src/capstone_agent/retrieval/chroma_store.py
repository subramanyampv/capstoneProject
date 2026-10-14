"""Local, version-checked Chroma index and source-bearing policy search."""

import hashlib
import json
import os
import re
from datetime import date, datetime, timezone
from pathlib import Path

from capstone_agent.retrieval.corpus import CATEGORIES, METADATA_PROFILE, check_rule_consistency, load_corpus
from capstone_agent.retrieval.embeddings_voyage import DIMENSION, MODEL_ID, REVISION, ROOT
from capstone_agent.retrieval.query_expansion import PROFILE, expand_query

SCENARIO_DATE = date(2026, 10, 12)


def open_store(path, embeddings, collection, *, create=True):
    os.environ["ANONYMIZED_TELEMETRY"] = "false"
    from chromadb.config import Settings
    from langchain_chroma import Chroma
    store = Chroma(collection_name=collection, embedding_function=embeddings,
                  persist_directory=str(path), client_settings=Settings(anonymized_telemetry=False),
                  collection_configuration={"hnsw": {"space": "cosine"}},
                  create_collection_if_not_exists=create)
    # The wrapper's reopen path uses Chroma's default embedding function unless
    # explicitly disabled. All embeddings must come from our pinned wrapper.
    store._chroma_collection = store._client.get_collection(name=collection, embedding_function=None)
    return store


def ingest(embeddings, *, root=ROOT, version="v1"):
    if not re.fullmatch(r"v[0-9]+", version):
        raise ValueError("Index version must have the form v1, v2, ...")
    chunks, hashes, quarantined = load_corpus(root / "knowledge/raw")
    rules = json.loads((root / "data/policy_rules.json").read_text())
    check_rule_consistency(chunks, rules)
    path = root / "knowledge/index" / f"chroma_{version}"
    manifest_path = path / "index_manifest.json"
    identity = {"model_id": MODEL_ID, "model_revision": REVISION,
                "dimension": embeddings.dimension, "normalized": True, "distance": "cosine",
                "collection": f"policies_{version}", "document_sha256": hashes,
                "chunking": "authored-heading-sections-max-2400-bytes-v1",
                "metadata_profile": METADATA_PROFILE,
                "rule_version": rules["version"]}
    if manifest_path.exists():
        old = json.loads(manifest_path.read_text())
        if any(old.get(key) != value for key, value in identity.items()):
            raise ValueError("Index inputs changed; select a new index version.")
        store = open_store(path, embeddings, identity["collection"], create=False)
        if store._collection.count() != len(chunks):
            raise ValueError("Index count mismatch; incomplete build cannot be reused.")
        return old
    path.mkdir(parents=True, exist_ok=True)
    store = open_store(path, embeddings, identity["collection"])
    from langchain_core.documents import Document
    store.add_documents([Document(page_content=chunk["text"], metadata=chunk["metadata"]) for chunk in chunks],
                        ids=[chunk["id"] for chunk in chunks])
    manifest = {**identity, "index_version": version, "chunk_count": len(chunks),
                "built_at": datetime.now(timezone.utc).isoformat(), "quarantined": quarantined}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    (root / "knowledge/index_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


class PolicySearch:
    def __init__(self, embeddings, *, root=ROOT, version=None, threshold=None):
        config_path = root / "config/retrieval.json"
        settings = json.loads(config_path.read_text()) if config_path.exists() else None
        version = version or (settings["index_version"] if settings else "v1")
        if threshold is None:
            if settings is not None:
                profile_hash = hashlib.sha256(Path(__file__).with_name("query_expansion.py").read_bytes()).hexdigest()
                if (settings.get("query_profile") != PROFILE or settings.get("query_expansion_sha256") != profile_hash
                        or settings.get("index_version") != version):
                    raise ValueError("RETRIEVAL_CALIBRATION_MISMATCH")
            threshold = settings["threshold"] if settings is not None else .4
        if not re.fullmatch(r"v[0-9]+", version) or not -1 <= threshold <= 1:
            raise ValueError("Invalid retrieval configuration.")
        path = root / "knowledge/index" / f"chroma_{version}"
        try:
            manifest = json.loads((path / "index_manifest.json").read_text())
        except (OSError, ValueError):
            raise ValueError("INDEX_UNAVAILABLE") from None
        chunks, hashes, quarantined = load_corpus(root / "knowledge/raw")
        try:
            check_rule_consistency(chunks, json.loads((root / "data/policy_rules.json").read_text()))
        except (ValueError, KeyError):
            raise ValueError("MANIFEST_MISMATCH") from None
        required = {"model_id": MODEL_ID, "model_revision": REVISION,
                    "dimension": embeddings.dimension, "normalized": True, "distance": "cosine",
                    "collection": f"policies_{version}", "document_sha256": hashes,
                    "metadata_profile": METADATA_PROFILE,
                    "rule_version": json.loads((root / "data/policy_rules.json").read_text())["version"]}
        if any(manifest.get(key) != value for key, value in required.items()) or quarantined:
            raise ValueError("MANIFEST_MISMATCH")
        self.store = open_store(path, embeddings, manifest["collection"], create=False)
        if self.store._collection.count() != manifest["chunk_count"]:
            raise ValueError("MANIFEST_MISMATCH")
        persisted = self.store._collection.get(include=["documents", "metadatas"])
        expected = {chunk["id"]: chunk for chunk in chunks}
        for identifier, document, metadata in zip(persisted["ids"], persisted["documents"], persisted["metadatas"]):
            if identifier not in expected or document != expected[identifier]["text"] or metadata != expected[identifier]["metadata"]:
                raise ValueError("MANIFEST_MISMATCH")
        self.chunks, self.manifest, self.threshold = chunks, manifest, threshold
        catalog_path = root / "data/product_catalog.json"
        self.catalog = json.loads(catalog_path.read_text())["products"] if catalog_path.exists() else []

    def search(self, query: str, *, k=5, doc_types=None, category=None, today=SCENARIO_DATE):
        if not query.strip() or len(query) > 2000 or not 1 <= k <= 10:
            raise ValueError("INVALID_ARGUMENT")
        if category is not None and category not in CATEGORIES:
            raise ValueError("INVALID_ARGUMENT")
        where = {"doc_id": {"$in": doc_types}} if doc_types else None
        if doc_types is not None and (not doc_types or any(d not in {c['metadata']['doc_id'] for c in self.chunks} for d in doc_types)):
            raise ValueError("INVALID_ARGUMENT")
        if category is not None:
            category_filter = {f"applies_{category}": True}
            where = {"$and": [where, category_filter]} if where else category_filter
        # Fetch extra candidates so future/superseded sources cannot crowd out applicable evidence.
        expanded, hints = expand_query(query, self.catalog, category=category)
        matches = self.store.similarity_search_with_score(expanded, k=self.manifest["chunk_count"], filter=where)
        candidates = []
        for document, distance in matches:
            meta = document.metadata
            if date.fromisoformat(meta["effective_date"]) > today:
                continue
            if meta.get("superseded_on") and date.fromisoformat(meta["superseded_on"]) <= today:
                continue
            candidates.append({**meta, "chunk_id": f"{meta['doc_id']}:{meta['version']}:{meta['section_id']}:0",
                               "text": document.page_content, "score": round(1 - float(distance), 6)})
        # Prefer policy over FAQ for very similar scores, never dropping version metadata.
        candidates.sort(key=lambda c: (-round(c["score"], 2), c["authority"] != "policy", -c["score"]))
        results = [c for c in candidates if c["score"] >= self.threshold][:k]
        conflicts, required_sources = [], {}
        applicable = [c for c in self.chunks if date.fromisoformat(c["metadata"]["effective_date"]) <= today
                      and (category is None or c["metadata"][f"applies_{category}"])
                      and not (c["metadata"].get("superseded_on") and date.fromisoformat(c["metadata"]["superseded_on"]) <= today)]
        scores = {c["chunk_id"]: c["score"] for c in candidates}

        def source_record(chunk):
            return {**chunk["metadata"], "chunk_id": chunk["id"], "text": chunk["text"],
                    "score": scores.get(chunk["id"]), "selection_reason": "mandatory_conflict_evidence"}

        # Check all applicable versions of any retained section, not just the
        # versions that happen to fit within k or the similarity threshold.
        for key in {(c["doc_id"], c["section_id"]) for c in results}:
            group = [c for c in applicable if (c["metadata"]["doc_id"], c["metadata"]["section_id"]) == key]
            if len({c["metadata"]["version"] for c in group}) > 1:
                conflicts.append({"kind": "overlapping_versions", "sources": [c["id"] for c in group]})
                required_sources.update({c["id"]: source_record(c) for c in group})
        # R05's explicitly authored cross-authority discrepancy is a deterministic
        # topic check. Inject both sources so a vector miss cannot suppress a mandatory flag.
        electronics = bool(re.search(r"\b(electronics?|speaker)\b", expanded, re.I)) or category == "electronics"
        if electronics and re.search(r"return|window|faq", query, re.I):
            pair = [c for c in applicable if (c["metadata"]["doc_id"], c["metadata"]["section_id"]) in
                    {("faq", "electronics-returns"), ("return_policy", "window")}]
            if len(pair) >= 2 and any(c["metadata"]["evaluation_conflict"] == "electronics_return_window" for c in pair):
                conflicts.append({"kind": "declared_faq_policy_conflict", "sources": [c["id"] for c in pair]})
                required_sources.update({c["id"]: source_record(c) for c in pair})
        if len(required_sources) > 20:
            raise ValueError("TOO_MANY_CONFLICTING_SOURCES")
        if required_sources:
            results = list(required_sources.values()) + [c for c in results if c["chunk_id"] not in required_sources]
            # Both sides are mandatory, so conflict evidence may exceed the
            # requested k. Disclose that exception instead of hiding a source.
            results = results[:max(k, len(required_sources))]
        return {"results": results, "below_threshold": not results,
                "conflict": bool(conflicts), "conflict_details": conflicts or None,
                "threshold": self.threshold, "index_version": self.manifest["index_version"],
                "raw_vector_top_k": candidates[:k], "query_profile": PROFILE, "query_hints": hints,
                "category_filter": category, "metadata_profile": METADATA_PROFILE,
                "conflict_evidence_exceeds_k": len(required_sources) > k}

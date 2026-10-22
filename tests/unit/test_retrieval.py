"""Retrieval authority, local embedding modes and fail-closed index regressions."""

import json
import math
import shutil
from datetime import date

import pytest

from capstone_agent.retrieval.corpus import check_rule_consistency, load_corpus
from capstone_agent.retrieval.configured_embeddings import ROOT, ConfiguredEmbeddings


class FakeModel:
    def __init__(self):
        self.calls = []

    def encode_document(self, texts, **kwargs):
        self.calls.append("document")
        return [[1.] * 256 for _ in texts]

    def encode_query(self, text, **kwargs):
        self.calls.append("query")
        return [1.] * 256


def embeddings():
    return ConfiguredEmbeddings(model=FakeModel(), dimension=256)


@pytest.fixture
def corpus_root(tmp_path):
    shutil.copytree(ROOT / "knowledge/raw", tmp_path / "knowledge/raw")
    (tmp_path / "data").mkdir()
    shutil.copyfile(ROOT / "data/policy_rules.json", tmp_path / "data/policy_rules.json")
    return tmp_path


def test_embedding_modes_dimensions_and_normalization():
    fake = FakeModel()
    wrapper = ConfiguredEmbeddings(model=fake, dimension=256)
    docs = wrapper.embed_documents(["first", "second"])
    query = wrapper.embed_query("question")
    assert fake.calls == ["document", "query"]
    assert len(query) == 256 and len(docs) == 2
    assert math.isclose(sum(value * value for value in query), 1)
    with pytest.raises(ValueError):
        wrapper._vectors([[float("nan")] * 256])
    with pytest.raises(ValueError):
        wrapper._vectors([[0.] * 256])


def test_corpus_rules_and_intentional_conflict_are_explicit():
    chunks, hashes, quarantine = load_corpus(ROOT / "knowledge/raw")
    assert len(hashes) == 7 and not quarantine
    check_rule_consistency(chunks, json.loads((ROOT / "data/policy_rules.json").read_text()))
    assert any(c["metadata"]["evaluation_conflict"] == "electronics_return_window" for c in chunks)
    assert len({c["id"] for c in chunks}) == len(chunks)


def test_corpus_threshold_drift_is_rejected(corpus_root):
    path = corpus_root / "knowledge/raw/refund_policy.md"
    path.write_text(path.read_text().replace("threshold is $100", "threshold is $200"))
    chunks, _, _ = load_corpus(corpus_root / "knowledge/raw")
    with pytest.raises(ValueError, match="threshold"):
        check_rule_consistency(chunks, json.loads((corpus_root / "data/policy_rules.json").read_text()))


def test_missing_frontmatter_is_quarantined(corpus_root):
    (corpus_root / "knowledge/raw/bad.md").write_text("# No metadata\nUnverified policy")
    _, _, quarantined = load_corpus(corpus_root / "knowledge/raw")
    assert quarantined == [{"file": "bad.md", "reason": "invalid_front_matter"}]


def test_index_reuse_conflict_sources_and_manifest_checks(corpus_root):
    from capstone_agent.retrieval.chroma_store import PolicySearch, ingest
    wrapper = embeddings()
    first = ingest(wrapper, root=corpus_root)
    assert ingest(wrapper, root=corpus_root) == first
    search = PolicySearch(wrapper, root=corpus_root, threshold=-1)
    result = search.search("speaker electronics return window")
    assert result["conflict"]
    sources = {r["doc_id"] for r in result["results"]}
    assert {"faq", "return_policy"} <= sources
    assert not search.search("electronics warranty duration")["conflict"]
    manifest = corpus_root / "knowledge/index/chroma_v1/index_manifest.json"
    payload = json.loads(manifest.read_text()); payload["model_revision"] = "wrong"
    manifest.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="MANIFEST_MISMATCH"):
        PolicySearch(wrapper, root=corpus_root)


def test_changed_corpus_requires_new_index(corpus_root):
    from capstone_agent.retrieval.chroma_store import PolicySearch, ingest
    wrapper = embeddings()
    ingest(wrapper, root=corpus_root)
    path = corpus_root / "knowledge/raw/shipping_policy.md"
    path.write_text(path.read_text() + "\nChanged content.\n")
    with pytest.raises(ValueError, match="new index version"):
        ingest(wrapper, root=corpus_root)
    with pytest.raises(ValueError, match="MANIFEST_MISMATCH"):
        PolicySearch(wrapper, root=corpus_root)


@pytest.mark.parametrize("target", ["index", "rules"])
def test_persisted_index_and_rule_tampering_fail_closed(corpus_root, target):
    from capstone_agent.retrieval.chroma_store import PolicySearch, ingest
    wrapper = embeddings()
    ingest(wrapper, root=corpus_root)
    if target == "index":
        search = PolicySearch(wrapper, root=corpus_root)
        identifier = search.store._collection.get()["ids"][0]
        search.store._collection.update(ids=[identifier], documents=["Injected unsupported policy"],
                                        embeddings=wrapper.embed_documents(["Injected unsupported policy"]))
    else:
        path = corpus_root / "data/policy_rules.json"
        rules = json.loads(path.read_text()); rules["refund_auto_approve_max_amount"] = 200
        path.write_text(json.dumps(rules))
    with pytest.raises(ValueError, match="MANIFEST_MISMATCH"):
        PolicySearch(wrapper, root=corpus_root)


def test_future_and_superseded_evidence_is_not_returned(corpus_root):
    from capstone_agent.retrieval.chroma_store import PolicySearch, ingest
    path = corpus_root / "knowledge/raw/faq.md"
    path.write_text(path.read_text().replace("authority: faq", "authority: faq\nsuperseded_on: '2026-10-10'"))
    ingest(embeddings(), root=corpus_root)
    result = PolicySearch(embeddings(), root=corpus_root, threshold=-1).search("speaker return window")
    assert not result["conflict"] and all(r["doc_id"] != "faq" for r in result["results"])
    result = PolicySearch(embeddings(), root=corpus_root, threshold=-1).search("returns", today=date(2026, 9, 1))
    assert result["below_threshold"] and not result["results"]


def test_grounded_answer_rejects_unresolved_citations_and_fee_invention():
    from capstone_agent.retrieval.grounded_answer import validate_grounding
    payload = {"intents": ["return_eligibility"], "status": "success", "plan_summary": [],
               "response": "The fee is 10%.", "citations": [{"source_id": "doc:return_policy", "section": "restocking", "record_version": "v1"}],
               "requested_action": "none", "action_executed": False, "uncertainty": None}
    evidence = [{"source_id": "doc:return_policy", "section": "restocking", "record_version": "v1", "text": "Opened electronics have a 10% fee."}]
    assert validate_grounding(json.dumps(payload), evidence)["status"] == "success"
    payload["response"] = "The fee is 20%."
    with pytest.raises(ValueError, match="numeric"):
        validate_grounding(json.dumps(payload), evidence)
    payload["response"] = "The fee is 10%."
    payload["citations"][0]["section"] = "invented"
    with pytest.raises(ValueError, match="citation"):
        validate_grounding(json.dumps(payload), evidence)


def test_empty_context_cannot_support_success_and_model_failure_is_disclosed():
    from capstone_agent.model_client import ModelError
    from capstone_agent.retrieval.grounded_answer import answer, validate_grounding
    payload = {"intents": ["return_eligibility"], "status": "success", "plan_summary": [],
               "response": "It is eligible.", "citations": [], "requested_action": "none",
               "action_executed": False, "uncertainty": None}
    with pytest.raises(ValueError, match="without_policy_evidence"):
        validate_grounding(json.dumps(payload), [])
    class FailedClient:
        def complete(self, messages):
            raise ModelError("connection_or_timeout")
    result = answer("Return policy?", FailedClient(), {"results": [], "conflict": False})
    assert result["outcome"] == "error" and result["response"] is None
    assert result["model_calls"] == 1


def test_catalog_hints_help_policy_queries_without_inventing_product_specs():
    from capstone_agent.retrieval.query_expansion import expand_query
    products = json.loads((ROOT / "data/product_catalog.json").read_text())["products"]
    query = "May these TrailRunners be sent back under your return policy?"
    expanded, hints = expand_query(query, products)
    assert expanded.startswith(query) and hints == ["Product category: footwear."]
    # A known product name does not make an unsupported specification answerable.
    query = "How much soil fits in the Ceramic Plant Pot Set?"
    assert expand_query(query, products) == (query, [])
    query = "What warranty does an UnknownBrand guitar have?"
    assert expand_query(query, products) == (query, [])


def test_exception_and_human_hints_do_not_convert_review_bypass_into_a_request():
    from capstone_agent.retrieval.query_expansion import expand_query
    _, hints = expand_query("Need an exception to a return rule", [])
    assert any("exception" in hint for hint in hints)
    _, hints = expand_query("Please connect me with a supervisor", [])
    assert hints == ["Escalation guidelines human requests."]
    _, hints = expand_query("How much refund can I get without a human?", [])
    assert hints == []
    _, hints = expand_query("Does a product injury need human review?", [])
    assert hints == []  # safety review is not a general representative request


def test_declared_conflict_cannot_be_hidden_by_filter_or_k(corpus_root):
    from capstone_agent.retrieval.chroma_store import PolicySearch, ingest
    wrapper = embeddings()
    ingest(wrapper, root=corpus_root)
    result = PolicySearch(wrapper, root=corpus_root, threshold=1).search(
        "speaker return policy conflict", k=1, doc_types=["return_policy"])
    assert result["conflict"] and result["conflict_evidence_exceeds_k"]
    assert {r["doc_id"] for r in result["results"]} == {"faq", "return_policy"}
    # No fabricated vector score is assigned to a source excluded by the filter.
    assert next(r for r in result["results"] if r["doc_id"] == "faq")["score"] is None


def test_overlapping_versions_keep_both_sources_when_k_is_one(corpus_root):
    from capstone_agent.retrieval.chroma_store import PolicySearch, ingest
    original = corpus_root / "knowledge/raw/cancellation_policy.md"
    older = corpus_root / "knowledge/raw/cancellation_policy_older.md"
    older.write_text(original.read_text().replace("version: v1\n", "version: v0\n", 1))
    wrapper = embeddings(); ingest(wrapper, root=corpus_root)
    result = PolicySearch(wrapper, root=corpus_root, threshold=-1).search(
        "cancellation eligibility", k=1, doc_types=["cancellation_policy"])
    assert result["conflict"] and result["conflict_evidence_exceeds_k"]
    assert {r["version"] for r in result["results"]} == {"v0", "v1"}


def test_general_conflict_validation_uses_supplied_version_references():
    from capstone_agent.retrieval.grounded_answer import validate_grounding
    evidence = [{"source_id": "doc:cancellation_policy", "section": "eligibility",
                 "record_version": version, "text": "Requires review."} for version in ["v0", "v1"]]
    refs = {(e["source_id"], e["section"], e["record_version"]) for e in evidence}
    payload = {"intents": ["cancellation"], "status": "escalation_required", "plan_summary": [],
               "response": "Conflicting versions require human review; no ticket created.",
               "citations": [{k:e[k] for k in ['source_id','section','record_version']} for e in evidence],
               "requested_action": "none", "action_executed": False, "uncertainty": "Versions conflict."}
    assert validate_grounding(json.dumps(payload), evidence, conflict=True, required_conflict_refs=refs)
    payload["citations"].pop()
    with pytest.raises(ValueError, match="both_sources"):
        validate_grounding(json.dumps(payload), evidence, conflict=True, required_conflict_refs=refs)


def test_changed_query_profile_requires_recalibration(corpus_root):
    from capstone_agent.retrieval.chroma_store import PolicySearch, ingest
    wrapper = embeddings(); ingest(wrapper, root=corpus_root)
    (corpus_root / "config").mkdir()
    (corpus_root / "config/retrieval.json").write_text(json.dumps({"index_version": "v1", "threshold": .4,
        "query_profile": "obsolete", "query_expansion_sha256": "wrong"}))
    with pytest.raises(ValueError, match="CALIBRATION_MISMATCH"):
        PolicySearch(wrapper, root=corpus_root)


def test_category_filter_retains_general_rules_and_excludes_unrelated_sections(corpus_root):
    from capstone_agent.retrieval.chroma_store import PolicySearch, ingest
    wrapper = embeddings(); ingest(wrapper, root=corpus_root)
    search = PolicySearch(wrapper, root=corpus_root, threshold=-1)
    result = search.search("electronics return fee", category="footwear", k=10)
    assert result["category_filter"] == "footwear" and not result["conflict"]
    for row in result["raw_vector_top_k"] + result["results"]:
        assert row["applies_footwear"]
        assert (row["doc_id"], row["section_id"]) not in {
            ("return_policy", "restocking"), ("faq", "electronics-returns")}
    general = search.search("return exclusions", category="perishable_grocery", doc_types=["return_policy"], k=10)
    assert "exclusions" in {r["section_id"] for r in general["results"]}
    assert all(r["category"] == "all" for r in general["results"])
    with pytest.raises(ValueError, match="INVALID_ARGUMENT"):
        search.search("return policy", category="unknown")


def test_category_and_document_filter_preserve_mandatory_conflict(corpus_root):
    from capstone_agent.retrieval.chroma_store import PolicySearch, ingest
    wrapper = embeddings(); ingest(wrapper, root=corpus_root)
    result = PolicySearch(wrapper, root=corpus_root, threshold=1).search(
        "electronics returns", category="electronics", doc_types=["return_policy"], k=1)
    assert result["conflict"] and result["conflict_evidence_exceeds_k"]
    assert {r["doc_id"] for r in result["results"]} == {"faq", "return_policy"}
    assert all(r["applies_electronics"] for r in result["results"])


@pytest.mark.parametrize("scope", ["restocking: [unknown]", "restocking: electronics", "missing: [electronics]"])
def test_bad_category_metadata_is_quarantined(corpus_root, scope):
    path = corpus_root / "knowledge/raw/return_policy.md"
    path.write_text(path.read_text().replace("restocking: [electronics]", scope))
    chunks, _, quarantine = load_corpus(corpus_root / "knowledge/raw")
    assert quarantine == [{"file": "return_policy.md", "reason": "invalid_front_matter"}]
    with pytest.raises(ValueError):
        check_rule_consistency(chunks, json.loads((corpus_root / "data/policy_rules.json").read_text()))

"""Configuration/provenance and custom-code trust without real model loading."""
import json
import sys
from types import SimpleNamespace

import pytest

from capstone_agent.retrieval import configured_embeddings as adapter
from test_retrieval import FakeModel


@pytest.fixture
def isolated_environment(monkeypatch):
    values = {}
    monkeypatch.setattr(adapter, "load_environment", lambda path: values)
    return values


def fake_local_loader(monkeypatch):
    calls = []
    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(set_num_threads=lambda n: None))
    monkeypatch.setitem(sys.modules, "huggingface_hub", SimpleNamespace(
        snapshot_download=lambda *args, **kwargs: calls.append((args, kwargs)) or "/synthetic/cache"))
    monkeypatch.setitem(sys.modules, "sentence_transformers", SimpleNamespace(
        SentenceTransformer=lambda *args, **kwargs: calls.append((args, kwargs)) or FakeModel()))
    for key in ("HF_HUB_DISABLE_TELEMETRY", "TOKENIZERS_PARALLELISM", "HF_MODULES_CACHE"):
        monkeypatch.setenv(key, "test-previous-value")
    return calls


@pytest.fixture
def approved_manifest(monkeypatch):
    manifest = {"model_id": "local/reviewed-test", "model_revision": "immutable-test-r1", "dimension": 256}
    monkeypatch.setattr(adapter, "APPROVED_LOCAL_IDENTITY_DIGESTS", frozenset({
        adapter.local_identity_digest(manifest["model_id"], manifest["model_revision"]),
    }))
    return manifest


def test_no_manifest_requires_explicit_local_identity(tmp_path, isolated_environment):
    with pytest.raises(ValueError, match="EXPLICIT_EMBEDDING_CONFIGURATION_REQUIRED"):
        adapter.ConfiguredEmbeddings(root=tmp_path)


@pytest.mark.parametrize("missing", ["EMBEDDING_MODEL", "EMBEDDING_REVISION", "EMBEDDING_DIMENSION"])
def test_partial_local_identity_does_not_get_a_deployment_default(tmp_path, isolated_environment, missing):
    isolated_environment.update(EMBEDDING_MODEL="local/test", EMBEDDING_REVISION="test-r1",
                                EMBEDDING_DIMENSION="256")
    isolated_environment.pop(missing)
    with pytest.raises(ValueError, match="EXPLICIT_EMBEDDING_CONFIGURATION_REQUIRED"):
        adapter.ConfiguredEmbeddings(root=tmp_path)


def test_explicit_local_identity_loads_without_arbitrary_custom_code(tmp_path, isolated_environment, monkeypatch):
    isolated_environment.update(EMBEDDING_MODEL="local/test", EMBEDDING_REVISION="test-r1",
                                EMBEDDING_DIMENSION="256")
    calls = fake_local_loader(monkeypatch)
    wrapper = adapter.ConfiguredEmbeddings(root=tmp_path)
    assert (wrapper.model_id, wrapper.revision, wrapper.dimension) == ("local/test", "test-r1", 256)
    assert calls[0][0] == ("local/test",) and calls[0][1]["revision"] == "test-r1"
    assert calls[1][1]["trust_remote_code"] is False


def test_existing_manifest_identity_and_only_its_exact_approval_are_preserved(tmp_path, isolated_environment, monkeypatch, approved_manifest):
    # A public source copy must not depend on a private deployment manifest.
    original = approved_manifest
    assert adapter.approved_local_identity(original["model_id"], original["model_revision"])
    assert not adapter.approved_local_identity(original["model_id"], original["model_revision"] + "-changed")
    (tmp_path / "knowledge").mkdir()
    (tmp_path / "knowledge/index_manifest.json").write_text(json.dumps(original))
    isolated_environment.update(EMBEDDING_MODEL="", EMBEDDING_REVISION="", EMBEDDING_DIMENSION="")
    calls = fake_local_loader(monkeypatch)
    wrapper = adapter.ConfiguredEmbeddings(root=tmp_path)
    assert (wrapper.model_id, wrapper.revision, wrapper.dimension) == (
        original["model_id"], original["model_revision"], original["dimension"])
    assert calls[1][1]["trust_remote_code"] is True


def test_identity_override_never_inherits_manifest_custom_code_trust(tmp_path, isolated_environment, monkeypatch, approved_manifest):
    original = approved_manifest
    (tmp_path / "knowledge").mkdir()
    (tmp_path / "knowledge/index_manifest.json").write_text(json.dumps(original))
    isolated_environment["EMBEDDING_REVISION"] = "not-the-reviewed-revision"
    calls = fake_local_loader(monkeypatch)
    adapter.ConfiguredEmbeddings(root=tmp_path)
    assert calls[1][1]["trust_remote_code"] is False


def test_injected_model_never_reads_environment_or_borrows_index_provenance(tmp_path, monkeypatch):
    def forbidden(*args):
        raise AssertionError("Injected model must not load deployment configuration")
    monkeypatch.setattr(adapter, "load_environment", forbidden)
    wrapper = adapter.ConfiguredEmbeddings(model=FakeModel(), dimension=256, root=tmp_path)
    assert wrapper.model_id == "synthetic-injected-model"
    assert wrapper.revision == "synthetic-injected-revision"
    assert len(wrapper.embed_query("synthetic question")) == 256
    with pytest.raises(ValueError, match="EXPLICIT_EMBEDDING_DIMENSION_REQUIRED"):
        adapter.ConfiguredEmbeddings(model=FakeModel(), root=tmp_path)


@pytest.mark.parametrize("dimension", [True, 1.5, float("nan"), "", 0, 65537])
def test_invalid_injected_dimensions_fail_before_loading(dimension):
    with pytest.raises(ValueError, match="INVALID_EMBEDDING_DIMENSION"):
        adapter.ConfiguredEmbeddings(model=FakeModel(), dimension=dimension)

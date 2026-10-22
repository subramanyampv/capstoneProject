"""Configured local/API embeddings with index-bound identity and normalized vectors."""

import hashlib
import json
import math
import os
from pathlib import Path

from langchain_core.embeddings import Embeddings

from capstone_agent.config import LLMConfig, load_environment

ROOT = Path(__file__).resolve().parents[3]

# SHA-256 of canonical JSON [model identifier, immutable revision]. This preserves
# approval of one previously inspected custom implementation without naming a
# deployment model here or granting trust to arbitrary configured repositories.
APPROVED_LOCAL_IDENTITY_DIGESTS = frozenset({
    "9a7a4b7181b19cf493534de53e38cc93dfe990d661bac2eb42e3f755b44b6269",
})


def local_identity_digest(model_id, revision):
    identity = json.dumps([model_id, revision], separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(identity.encode()).hexdigest()


def approved_local_identity(model_id, revision):
    return local_identity_digest(model_id, revision) in APPROVED_LOCAL_IDENTITY_DIGESTS


class ConfiguredEmbeddings(Embeddings):
    """Identity comes from explicit configuration or an existing index manifest.

    Public copies without a manifest must configure a local identity explicitly.
    Injected models are a separate synthetic seam: they read no environment or
    index identity and require an explicit dimension, preventing test vectors from
    acquiring the production index's provenance.
    """

    def __init__(self, *, model=None, dimension=None, root=ROOT):
        self.api_config = None
        if model is not None:
            if dimension is None:
                raise ValueError("EXPLICIT_EMBEDDING_DIMENSION_REQUIRED")
            self.backend = "local"
            self.model_id = "synthetic-injected-model"
            self.revision = "synthetic-injected-revision"
        else:
            env = load_environment(root / ".env")
            manifest_path = root / "knowledge/index_manifest.json"
            manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
            self.backend = env.get("EMBEDDING_BACKEND", "local").strip() or "local"
            if self.backend not in {"local", "openai_compatible"}:
                raise ValueError("INVALID_EMBEDDING_BACKEND")
            self.model_id = env.get("EMBEDDING_MODEL", "").strip() or manifest.get("model_id")
            self.revision = env.get("EMBEDDING_REVISION", "").strip() or manifest.get("model_revision")
            dimension = dimension if dimension is not None else (
                env.get("EMBEDDING_DIMENSION", "").strip() or manifest.get("dimension"))
            if (not isinstance(self.model_id, str) or not self.model_id.strip()
                    or not isinstance(self.revision, str) or not self.revision.strip()
                    or dimension is None):
                raise ValueError("EXPLICIT_EMBEDDING_CONFIGURATION_REQUIRED")
            if self.backend == "openai_compatible":
                required = ("EMBEDDING_MODEL", "EMBEDDING_REVISION", "EMBEDDING_DIMENSION", "EMBEDDING_BASE_URL")
                if not all(env.get(key, "").strip() for key in required):
                    raise ValueError("EXPLICIT_EMBEDDING_CONFIGURATION_REQUIRED")
                self.api_config = LLMConfig(
                    base_url=env["EMBEDDING_BASE_URL"], model=self.model_id,
                    api_key=env.get("EMBEDDING_API_KEY", ""),
                    timeout_seconds=float(env.get("EMBEDDING_TIMEOUT_SECONDS", "20")))
        try:
            if isinstance(dimension, bool) or (isinstance(dimension, float) and not dimension.is_integer()):
                raise ValueError
            self.dimension = int(dimension)
            if not 1 <= self.dimension <= 65536:
                raise ValueError
        except (ValueError, TypeError, OverflowError):
            raise ValueError("INVALID_EMBEDDING_DIMENSION") from None
        if self.api_config:
            self.model = None
            return
        if model is None:
            os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
            os.environ["HF_MODULES_CACHE"] = str(root / ".cache/huggingface/modules")
            import torch
            from huggingface_hub import snapshot_download
            from sentence_transformers import SentenceTransformer
            torch.set_num_threads(4)
            location = snapshot_download(
                self.model_id, revision=self.revision,
                cache_dir=str(root / ".cache/huggingface"),
                allow_patterns=["*.json", "*.py", "*.safetensors", "*.txt"],
                local_files_only=os.environ.get("HF_HUB_OFFLINE") == "1")
            model = SentenceTransformer(
                location, cache_folder=str(root / ".cache/huggingface"),
                trust_remote_code=approved_local_identity(self.model_id, self.revision),
                device="cpu", truncate_dim=self.dimension,
                model_kwargs={"attn_implementation": "sdpa"})
        self.model = model

    def _vectors(self, encoded):
        vectors = []
        for row in encoded:
            vector = [float(value) for value in row]
            if len(vector) != self.dimension or not all(math.isfinite(value) for value in vector):
                raise ValueError("Embedding dimension or finiteness check failed.")
            norm = math.hypot(*vector)
            if not math.isfinite(norm) or norm <= 0:
                raise ValueError("Embedding norm must be positive.")
            vectors.append([value / norm for value in vector])
        return vectors

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if self.api_config:
            return self._api_vectors(texts)
        return self._vectors(self.model.encode_document(
            texts, batch_size=8, normalize_embeddings=True, show_progress_bar=False))

    def embed_query(self, text: str) -> list[float]:
        if self.api_config:
            return self._api_vectors([text])[0]
        return self._vectors([self.model.encode_query(text, normalize_embeddings=True,
                                                    show_progress_bar=False)])[0]

    def _api_vectors(self, texts):
        from openai import OpenAI
        import httpx
        config = self.api_config
        try:
            with httpx.Client(follow_redirects=False, timeout=config.timeout_seconds) as transport:
                with OpenAI(base_url=config.base_url, api_key=config.api_key or "local-no-key",
                            max_retries=0, http_client=transport) as client:
                    result = client.embeddings.create(model=self.model_id, input=texts,
                                                      dimensions=self.dimension)
            rows = sorted(result.data, key=lambda row: row.index)
            if [row.index for row in rows] != list(range(len(texts))):
                raise ValueError("INVALID_EMBEDDING_RESPONSE")
            return self._vectors([row.embedding for row in rows])
        except Exception:
            raise ValueError("EMBEDDING_REQUEST_FAILED") from None

"""Pinned local embeddings; separate query/document modes and explicit dimensions."""

import math
import os
from pathlib import Path

from langchain_core.embeddings import Embeddings

MODEL_ID = "voyageai/voyage-4-nano"
REVISION = "67fabc9bef010dabc5f6024aa1b1b6b93410426f"
DIMENSION = 2048
ROOT = Path(__file__).resolve().parents[3]


class VoyageNanoEmbeddings(Embeddings):
    def __init__(self, *, model=None, dimension=DIMENSION):
        if dimension not in {256, 512, 1024, 2048}:
            raise ValueError("Unsupported Voyage embedding dimension.")
        self.dimension = dimension
        if model is None:
            os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
            os.environ["HF_MODULES_CACHE"] = str(ROOT / ".cache/huggingface/modules")
            import torch
            from huggingface_hub import snapshot_download
            from sentence_transformers import SentenceTransformer
            torch.set_num_threads(4)
            location = snapshot_download(MODEL_ID, revision=REVISION,
                                         cache_dir=str(ROOT / ".cache/huggingface"),
                                         allow_patterns=["*.json", "*.py", "*.safetensors", "*.txt"],
                                         local_files_only=os.environ.get("HF_HUB_OFFLINE") == "1")
            # The pinned custom file was inspected before enabling remote code.
            # Loading the pinned local snapshot also avoids an unrelated tokenizer
            # metadata lookup that otherwise breaks offline inference in Transformers.
            model = SentenceTransformer(location,
                                        cache_folder=str(ROOT / ".cache/huggingface"),
                                        trust_remote_code=True, device="cpu",
                                        truncate_dim=dimension,
                                        model_kwargs={"attn_implementation": "sdpa"})
        self.model = model

    def _vectors(self, encoded):
        vectors = []
        for row in encoded:
            vector = [float(value) for value in row]
            if len(vector) != self.dimension or not all(math.isfinite(v) for v in vector):
                raise ValueError("Embedding dimension or finiteness check failed.")
            norm = math.sqrt(sum(value * value for value in vector))
            if norm <= 0:
                raise ValueError("Embedding norm must be positive.")
            vectors.append([value / norm for value in vector])
        return vectors

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._vectors(self.model.encode_document(texts, batch_size=8,
                             normalize_embeddings=True, show_progress_bar=False))

    def embed_query(self, text: str) -> list[float]:
        return self._vectors([self.model.encode_query(text, normalize_embeddings=True,
                              show_progress_bar=False)])[0]

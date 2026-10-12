"""Embedding generation (docs/02 S8).

BGE-M3 (EMB-0.1.0) is the production embedder (dense 1024-d + sparse
lexical). `sentence-transformers` is an optional extra; `HashEmbedder` is a
deterministic fallback so the retrieval/ranking logic is fully testable
without a GPU or model download.
"""

from __future__ import annotations

import hashlib
import math
from typing import Protocol, runtime_checkable


@runtime_checkable
class Embedder(Protocol):
    """Turns texts into fixed-dimension vectors."""

    dim: int

    def available(self) -> bool: ...

    def embed(self, texts: str | list[str]) -> list[list[float]]: ...


class BgeM3Embedder:
    """BGE-M3 (production). Lazy import of sentence-transformers."""

    dim: int = 1024
    MODEL_NAME = "BAAI/bge-m3"

    def __init__(self, model_name: str = MODEL_NAME, device: str = "cpu") -> None:
        self._model_name = model_name
        self._device = device
        self._model = None  # lazy

    def available(self) -> bool:
        try:
            import sentence_transformers  # noqa: F401

            return True
        except ImportError:
            return False

    def _ensure(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name, device=self._device)
        return self._model

    def embed(self, texts: str | list[str]) -> list[list[float]]:
        if not self.available():
            raise RuntimeError("sentence-transformers not installed")
        if isinstance(texts, str):
            texts = [texts]
        model = self._ensure()
        return [list(map(float, v)) for v in model.encode(texts, normalize_embeddings=True)]


class HashEmbedder:
    """Deterministic bag-of-words hash embedder (dev/test only).

    Not a quality embedder — it gives stable, non-zero vectors so cosine
    similarity and the fusion/ranking pipeline can be exercised in CI.
    """

    def __init__(self, dim: int = 1024) -> None:
        self.dim = dim

    def available(self) -> bool:
        return True

    def embed(self, texts: str | list[str]) -> list[list[float]]:
        if isinstance(texts, str):
            texts = [texts]
        return [self._embed_one(t) for t in texts]

    def _embed_one(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for token in _tokenize(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % self.dim
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vec[idx] += sign
        norm = math.sqrt(sum(x * x for x in vec))
        if norm == 0.0:
            return vec
        return [x / norm for x in vec]


def _tokenize(text: str) -> list[str]:
    return [t for t in text.lower().split() if t]


def cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity (vectors are expected to be normalized)."""
    if len(a) != len(b) or not a:
        return 0.0
    return sum(x * y for x, y in zip(a, b, strict=True))

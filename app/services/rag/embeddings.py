"""Embedding generation via Ollama with sentence-transformers fallback."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

from app.clients.ollama_client import OllamaClient
from app.core.config import settings
from app.core.exceptions import OllamaServiceError

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """Generate text embeddings using Ollama or a local sentence-transformers model."""

    def __init__(
        self,
        ollama_client: OllamaClient | None = None,
        model: str | None = None,
        fallback_model: str | None = None,
    ) -> None:
        self.ollama_client = ollama_client or OllamaClient()
        self.model = model or settings.embedding_model
        self.fallback_model = fallback_model or settings.embedding_fallback_model
        self._backend: str | None = None
        self._st_model: SentenceTransformer | None = None
        self._dimension: int | None = None

    @property
    def dimension(self) -> int:
        """Embedding vector size for the active backend."""
        if self._dimension is None:
            self._dimension = len(self.embed("dimension probe"))
        return self._dimension

    @property
    def backend(self) -> str:
        """Active embedding backend name."""
        if self._backend is None:
            self.embed("backend probe")
        return self._backend or "unknown"

    def embed(self, text: str) -> np.ndarray:
        """Embed a single text string."""
        vectors = self.embed_batch([text])
        return vectors[0]

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        """Embed multiple texts, returning a float32 matrix."""
        if not texts:
            return np.empty((0, 0), dtype=np.float32)

        try:
            vectors = self._embed_with_ollama(texts)
            self._backend = "ollama"
        except OllamaServiceError as exc:
            logger.warning("Ollama embeddings unavailable (%s); using fallback.", exc.message)
            vectors = self._embed_with_sentence_transformers(texts)
            self._backend = "sentence-transformers"

        self._dimension = vectors.shape[1]
        return _normalize(vectors.astype(np.float32))

    def _embed_with_ollama(self, texts: list[str]) -> np.ndarray:
        embeddings = self.ollama_client.embed(model=self.model, inputs=texts)
        return np.asarray(embeddings, dtype=np.float32)

    def _embed_with_sentence_transformers(self, texts: list[str]) -> np.ndarray:
        if self._st_model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise OllamaServiceError(
                    "Embedding fallback unavailable: install sentence-transformers",
                    status_code=503,
                ) from exc
            self._st_model = SentenceTransformer(self.fallback_model)

        vectors = self._st_model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return np.asarray(vectors, dtype=np.float32)


def _normalize(vectors: np.ndarray) -> np.ndarray:
    """L2-normalize rows for cosine similarity via inner product."""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms

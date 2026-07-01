"""In-memory FAISS vector store for RAG chunks."""

from __future__ import annotations

from dataclasses import dataclass

import faiss
import numpy as np


@dataclass
class StoredChunk:
    """A chunk stored in the vector index."""

    doc_id: str
    filename: str
    chunk_index: int
    text: str


@dataclass
class RetrievedChunk:
    """A chunk returned from similarity search."""

    doc_id: str
    filename: str
    chunk_index: int
    text: str
    score: float


class VectorStore:
    """FAISS-backed in-memory vector store with chunk metadata."""

    def __init__(self, dimension: int) -> None:
        self.dimension = dimension
        self._chunks: list[StoredChunk] = []
        self._embeddings: list[np.ndarray] = []
        self._index = faiss.IndexFlatIP(dimension)

    @property
    def size(self) -> int:
        return len(self._chunks)

    def add(self, embeddings: np.ndarray, chunks: list[StoredChunk]) -> None:
        """Add embeddings and their metadata to the store."""
        if embeddings.size == 0:
            return
        if embeddings.shape[0] != len(chunks):
            raise ValueError("Embedding count must match chunk count")
        if embeddings.shape[1] != self.dimension:
            raise ValueError(
                f"Expected dimension {self.dimension}, got {embeddings.shape[1]}"
            )

        self._index.add(embeddings.astype(np.float32))
        for row, chunk in zip(embeddings, chunks, strict=True):
            self._embeddings.append(np.asarray(row, dtype=np.float32))
            self._chunks.append(chunk)

    def search(self, query_embedding: np.ndarray, top_k: int = 4) -> list[RetrievedChunk]:
        """Return the most similar chunks for a query embedding."""
        if self._index.ntotal == 0:
            return []

        vector = np.asarray(query_embedding, dtype=np.float32).reshape(1, -1)
        k = min(top_k, self._index.ntotal)
        scores, indices = self._index.search(vector, k)

        results: list[RetrievedChunk] = []
        for score, idx in zip(scores[0], indices[0], strict=True):
            if idx < 0:
                continue
            chunk = self._chunks[idx]
            results.append(
                RetrievedChunk(
                    doc_id=chunk.doc_id,
                    filename=chunk.filename,
                    chunk_index=chunk.chunk_index,
                    text=chunk.text,
                    score=float(score),
                )
            )
        return results

    def remove_by_doc_id(self, doc_id: str) -> int:
        """Remove all chunks for a document and rebuild the index."""
        remaining_chunks: list[StoredChunk] = []
        remaining_embeddings: list[np.ndarray] = []
        removed = 0

        for chunk, embedding in zip(self._chunks, self._embeddings, strict=True):
            if chunk.doc_id == doc_id:
                removed += 1
                continue
            remaining_chunks.append(chunk)
            remaining_embeddings.append(embedding)

        if removed:
            self._rebuild(remaining_chunks, remaining_embeddings)
        return removed

    def clear(self) -> None:
        """Remove all stored chunks."""
        self._chunks.clear()
        self._embeddings.clear()
        self._index = faiss.IndexFlatIP(self.dimension)

    def _rebuild(
        self,
        chunks: list[StoredChunk],
        embeddings: list[np.ndarray],
    ) -> None:
        """Rebuild the FAISS index from stored chunk metadata."""
        self._chunks = chunks
        self._embeddings = embeddings
        self._index = faiss.IndexFlatIP(self.dimension)
        if embeddings:
            matrix = np.vstack(embeddings).astype(np.float32)
            self._index.add(matrix)

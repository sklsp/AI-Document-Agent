"""RAG orchestration service."""

from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.services.rag.chunking import chunk_text
from app.services.rag.embeddings import EmbeddingClient
from app.services.rag.vector_store import RetrievedChunk, StoredChunk, VectorStore


class RAGService:
    """Index documents and retrieve relevant context for chat."""

    def __init__(self, embedding_client: EmbeddingClient | None = None) -> None:
        self.embedding_client = embedding_client or EmbeddingClient()
        self._store: VectorStore | None = None

    @property
    def chunk_count(self) -> int:
        return self._store.size if self._store else 0

    def add_document(self, text: str, metadata: dict[str, Any]) -> int:
        """Chunk, embed, and index a document.

        Args:
            text: Full document text.
            metadata: Must include ``doc_id``; ``filename`` or ``source`` is used for display.

        Returns:
            Number of chunks indexed.
        """
        doc_id = str(metadata.get("doc_id", metadata.get("id", "unknown")))
        filename = str(metadata.get("filename", metadata.get("source", doc_id)))

        chunks = chunk_text(
            text,
            chunk_size=settings.rag_chunk_size,
            overlap=settings.rag_chunk_overlap,
        )
        if not chunks:
            return 0

        embeddings = self.embedding_client.embed_batch(chunks)
        self._ensure_store(embeddings.shape[1])

        stored_chunks = [
            StoredChunk(
                doc_id=doc_id,
                filename=filename,
                chunk_index=index,
                text=chunk,
            )
            for index, chunk in enumerate(chunks)
        ]
        assert self._store is not None
        self._store.add(embeddings, stored_chunks)
        return len(chunks)

    def query(self, question: str, top_k: int | None = None) -> list[RetrievedChunk]:
        """Retrieve the most relevant chunks for a question."""
        if not self._store or self._store.size == 0:
            return []

        k = top_k or settings.rag_top_k
        query_embedding = self.embedding_client.embed(question)
        return self._store.search(query_embedding, top_k=k)

    def format_context(self, chunks: list[RetrievedChunk]) -> str:
        """Format retrieved chunks for LLM prompt injection."""
        if not chunks:
            return ""

        parts: list[str] = []
        for chunk in chunks:
            parts.append(
                f"[{chunk.filename} | chunk {chunk.chunk_index} | score {chunk.score:.3f}]\n"
                f"{chunk.text}"
            )
        return "\n\n".join(parts)

    def remove_document(self, doc_id: str) -> int:
        """Remove all indexed chunks for a document."""
        if not self._store:
            return 0
        return self._store.remove_by_doc_id(doc_id)

    def clear(self) -> None:
        """Clear the entire vector index."""
        if self._store:
            self._store.clear()

    def _ensure_store(self, dimension: int) -> None:
        if self._store is None:
            self._store = VectorStore(dimension)
        elif self._store.dimension != dimension:
            raise ValueError(
                "Embedding dimension changed; clear the RAG index before re-indexing "
                f"(expected {self._store.dimension}, got {dimension})"
            )

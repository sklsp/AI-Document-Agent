"""Document service for storing and retrieving documents with RAG."""

import re
from typing import TypedDict


class Document(TypedDict):
    """Document structure."""

    id: str
    content: str
    source: str


class DocumentService:
    """In-memory document storage with keyword-based retrieval. Easily upgradeable with embeddings."""

    def __init__(self) -> None:
        # Structure: {doc_id: Document}
        self._storage: dict[str, Document] = {}
        self._doc_counter = 0

    def store_document(self, content: str, source: str = "upload") -> str:
        """Store a single document.

        Args:
            content: Document text content
            source: Source identifier (e.g., "upload", filename)

        Returns:
            Document ID
        """
        doc_id = f"doc_{self._doc_counter}"
        self._doc_counter += 1

        self._storage[doc_id] = {
            "id": doc_id,
            "content": content,
            "source": source,
        }

        return doc_id

    def store_documents(self, documents: list[tuple[str, str]]) -> list[str]:
        """Store multiple documents.

        Args:
            documents: List of (content, source) tuples

        Returns:
            List of document IDs
        """
        doc_ids = []
        for content, source in documents:
            doc_id = self.store_document(content, source)
            doc_ids.append(doc_id)
        return doc_ids

    def get_document(self, doc_id: str) -> Document | None:
        """Retrieve a document by ID.

        Args:
            doc_id: Document identifier

        Returns:
            Document or None if not found
        """
        return self._storage.get(doc_id)

    def get_all_documents(self) -> list[Document]:
        """Get all stored documents.

        Returns:
            List of all documents
        """
        return list(self._storage.values())

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document.

        Args:
            doc_id: Document identifier

        Returns:
            True if deleted, False if not found
        """
        if doc_id in self._storage:
            del self._storage[doc_id]
            return True
        return False

    def clear_all(self) -> None:
        """Clear all documents."""
        self._storage.clear()
        self._doc_counter = 0

    def get_relevant_context(self, query: str, top_k: int = 3) -> str:
        """Retrieve relevant documents using keyword matching.

        Args:
            query: Search query
            top_k: Number of top results to return

        Returns:
            Combined text from relevant documents
        """
        if not self._storage:
            return ""

        # Simple keyword matching: split query into words and score documents
        query_words = set(self._normalize_text(query).split())

        scored_docs = []
        for doc in self._storage.values():
            doc_words = set(self._normalize_text(doc["content"]).split())
            # Count matching keywords
            score = len(query_words & doc_words)
            if score > 0:
                scored_docs.append((score, doc))

        # Sort by score descending
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        # Combine top_k results
        results = []
        for _, doc in scored_docs[:top_k]:
            results.append(f"[Source: {doc['source']}]\n{doc['content'][:500]}")

        return "\n\n".join(results) if results else ""

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text for keyword matching.

        Args:
            text: Text to normalize

        Returns:
            Normalized text (lowercase, no special chars)
        """
        # Convert to lowercase and remove special characters
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", "", text)
        return text

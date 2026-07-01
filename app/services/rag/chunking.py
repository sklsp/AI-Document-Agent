"""Text chunking for RAG indexing."""

from __future__ import annotations

import re

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 150,
) -> list[str]:
    """Split text into overlapping chunks while preserving sentence boundaries.

    Args:
        text: Full document text.
        chunk_size: Target maximum characters per chunk.
        overlap: Character overlap between consecutive chunks.

    Returns:
        List of text chunks.
    """
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []
    if len(normalized) <= chunk_size:
        return [normalized]

    sentences = _SENTENCE_BOUNDARY.split(normalized)
    if len(sentences) <= 1:
        return _chunk_by_characters(normalized, chunk_size, overlap)

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        extra = len(sentence) + (1 if current else 0)
        if current and current_len + extra > chunk_size:
            chunks.append(" ".join(current))
            current = _overlap_tail(current, overlap)
            current_len = sum(len(part) for part in current) + max(0, len(current) - 1)

        current.append(sentence)
        current_len += extra

    if current:
        chunks.append(" ".join(current))

    return [chunk for chunk in chunks if chunk.strip()]


def _overlap_tail(parts: list[str], overlap: int) -> list[str]:
    """Keep trailing sentences that fit within the overlap window."""
    if overlap <= 0 or not parts:
        return []

    tail: list[str] = []
    tail_len = 0
    for part in reversed(parts):
        extra = len(part) + (1 if tail else 0)
        if tail and tail_len + extra > overlap:
            break
        tail.insert(0, part)
        tail_len += extra
    return tail


def _chunk_by_characters(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Fallback chunker for text without clear sentence boundaries."""
    chunks: list[str] = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        if end < text_len:
            split_at = text.rfind(" ", start, end)
            if split_at > start:
                end = split_at

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_len:
            break
        start = max(end - overlap, start + 1)

    return chunks

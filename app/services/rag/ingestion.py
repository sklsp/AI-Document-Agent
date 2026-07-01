"""Document text extraction for supported file types."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}


def extract_text(file_path: str | Path, filename: str | None = None) -> str:
    """Extract plain text from a file on disk.

    Unified entry point for all supported uploads (.txt, .pdf, .docx).

    Args:
        file_path: Path to the saved upload on disk.
        filename: Original filename (used for extension detection). Defaults to file_path name.

    Returns:
        Extracted plain text.

    Raises:
        ValueError: Unsupported file type or empty extraction result.
        UnicodeDecodeError: Invalid UTF-8 in a .txt file.
        FileNotFoundError: file_path does not exist.
    """
    path = Path(file_path)
    name = filename or path.name
    extension = Path(name).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{extension}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    content = path.read_bytes()
    return _extract_from_bytes(name, extension, content)


def _extract_from_bytes(filename: str, extension: str, content: bytes) -> str:
    """Route raw bytes to the correct parser by extension."""
    if extension == ".txt":
        text = content.decode("utf-8")
    elif extension == ".pdf":
        text = _extract_pdf(content)
    elif extension == ".docx":
        text = _extract_docx(content)
    else:
        raise ValueError(
            f"Unsupported file type '{extension}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    text = text.strip()
    if not text:
        raise ValueError(f"No extractable text found in '{filename}'")

    return text


def _extract_pdf(content: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(content))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(page.strip() for page in pages if page.strip())


def _extract_docx(content: bytes) -> str:
    from docx import Document

    document = Document(BytesIO(content))
    paragraphs = [
        paragraph.text.strip()
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]
    return "\n\n".join(paragraphs)

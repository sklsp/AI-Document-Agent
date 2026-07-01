import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    default_model: str = os.getenv("OLLAMA_DEFAULT_MODEL", "llama3.2")
    embedding_model: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    embedding_fallback_model: str = os.getenv(
        "EMBEDDING_FALLBACK_MODEL", "all-MiniLM-L6-v2"
    )
    request_timeout: float = float(os.getenv("OLLAMA_REQUEST_TIMEOUT", "30"))
    rag_chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "800"))
    rag_chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "150"))
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "4"))


settings = Settings()

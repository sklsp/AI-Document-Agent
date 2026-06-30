import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    default_model: str = os.getenv("OLLAMA_DEFAULT_MODEL", "llama3.2")
    request_timeout: float = float(os.getenv("OLLAMA_REQUEST_TIMEOUT", "30"))


settings = Settings()

from __future__ import annotations

import requests

from app.core.config import settings
from app.core.exceptions import OllamaServiceError


class OllamaClient:
    """Small client for talking to the local Ollama HTTP API."""

    def __init__(self, base_url: str | None = None, timeout: float | None = None) -> None:
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.timeout = timeout or settings.request_timeout

    def _request(self, method: str, path: str, *, json: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        try:
            response = requests.request(method=method, url=url, json=json, timeout=self.timeout)
        except requests.RequestException as exc:
            raise OllamaServiceError("Ollama is unreachable", status_code=503, detail=str(exc)) from exc

        if response.status_code == 404:
            raise OllamaServiceError("Requested Ollama endpoint was not found", status_code=404)
        if response.status_code >= 500:
            raise OllamaServiceError("Ollama returned a server error", status_code=502)
        if response.status_code >= 400:
            raise OllamaServiceError("Ollama request failed", status_code=response.status_code)

        try:
            return response.json()
        except ValueError as exc:
            raise OllamaServiceError("Ollama returned an invalid response", status_code=502) from exc

    def generate(self, *, model: str, prompt: str) -> dict:
        return self._request("POST", "/api/generate", json={"model": model, "prompt": prompt, "stream": False})

    def chat(self, *, model: str, messages: list[dict]) -> dict:
        return self._request("POST", "/api/chat", json={"model": model, "messages": messages, "stream": False})

    def list_models(self) -> dict:
        return self._request("GET", "/api/tags")

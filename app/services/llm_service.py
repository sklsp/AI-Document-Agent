from __future__ import annotations

from app.clients.ollama_client import OllamaClient
from app.core.config import settings
from app.core.exceptions import OllamaServiceError


class LLMService:
    """Service layer for Ollama-backed chat and model listing."""

    def __init__(self, client: OllamaClient | None = None) -> None:
        self.client = client or OllamaClient()

    def health_check(self) -> dict:
        try:
            models = self.list_models()
        except OllamaServiceError:
            raise
        return {
            "status": "ok",
            "ollama_reachable": True,
            "model": settings.default_model,
            "available_models": models,
        }

    def chat(self, prompt: str, model: str | None = None) -> str:
        selected_model = model or settings.default_model
        response = self.client.generate(model=selected_model, prompt=prompt)
        if isinstance(response.get("response"), str):
            return response["response"]
        raise OllamaServiceError("Ollama returned an invalid chat response", status_code=502)

    def list_models(self) -> list[str]:
        payload = self.client.list_models()
        models = payload.get("models", [])
        if not isinstance(models, list):
            raise OllamaServiceError("Ollama returned an invalid model list", status_code=502)
        return [model.get("name", "") for model in models if isinstance(model, dict) and model.get("name")]

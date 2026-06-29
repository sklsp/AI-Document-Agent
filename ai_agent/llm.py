"""Compatibility layer for the Ollama LLM client."""

from .llm_client import ask_llm, list_models

__all__ = ["ask_llm", "list_models"]

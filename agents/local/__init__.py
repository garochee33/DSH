"""DOME-HUB Local package — Ollama client for local LLM inference."""

from agents.local.ollama import OllamaClient, make_local_agent

__all__ = ["OllamaClient", "make_local_agent"]

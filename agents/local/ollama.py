"""
DOME-HUB Local Ollama LLM client
"""
from __future__ import annotations
import subprocess, time
import httpx
from agents.core.agent import Agent

OLLAMA_BASE = "http://localhost:11434"
DEFAULT_MODELS = ["llama3", "mistral", "codellama"]


class OllamaClient:
    def __init__(self, base_url: str = OLLAMA_BASE):
        self.base_url = base_url
        self._ensure_running()

    def _ensure_running(self):
        try:
            httpx.get(f"{self.base_url}/api/tags", timeout=3).raise_for_status()
        except Exception:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            for _ in range(10):
                time.sleep(1)
                try:
                    httpx.get(f"{self.base_url}/api/tags", timeout=2).raise_for_status()
                    return
                except Exception:
                    continue
            raise RuntimeError("Ollama failed to start")

    def list_models(self) -> list[str]:
        resp = httpx.get(f"{self.base_url}/api/tags", timeout=10)
        resp.raise_for_status()
        return [m["name"] for m in resp.json().get("models", [])]

    def pull(self, model: str):
        with httpx.stream("POST", f"{self.base_url}/api/pull", json={"name": model}, timeout=300) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                pass  # drain stream; pull completes when stream ends

    def run(self, prompt: str, model: str = "llama3") -> str:
        resp = httpx.post(
            f"{self.base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["response"]

    def stream(self, prompt: str, model: str = "llama3"):
        """Yields text chunks from Ollama generate stream."""
        import json
        with httpx.stream(
            "POST", f"{self.base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": True},
            timeout=120,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                data = json.loads(line)
                if data.get("response"):
                    yield data["response"]
                if data.get("done"):
                    break


def make_local_agent(model: str = "llama3") -> Agent:
    """Factory: returns an Agent pre-configured for a local Ollama model."""
    return Agent(name=f"local-{model}", model=model)

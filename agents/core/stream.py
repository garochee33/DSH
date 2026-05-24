"""
DOME-HUB Streaming LLM responses — multi-provider, local-first.

Provider hierarchy (sovereign order):
  1. stream_mlx    — Apple MLX / Metal (local LLM path via mlx_lm)
  2. stream_local  — Ollama HTTP (local, air-gapped)
  3. stream_anthropic — Anthropic API (cloud, no OpenAI dependency)
  4. stream_openai — OpenAI API (avoid for sensitive/sovereign tasks)

Embeddings / Neural Engine (ONNX CoreML EP) are separate — see
agents/core/memory/vector.py (Chroma vector memory), not this module.

Optional Trinity HTTP MLX helper: home/projects/trinity-consortium/nexus-core/mlx-neural-bridge.py
(port MLX_BRIDGE_PORT, default 8101).
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import TYPE_CHECKING, AsyncGenerator

import httpx


def _spore_guard(provider: str) -> None:
    """Raise if spore is germinating — no outbound provider calls allowed."""
    if os.environ.get("SPORE_GERMINATING") == "1":
        raise RuntimeError(
            f"[LOCKDOWN] Spore germinating — outbound call to {provider} blocked. "
            "Node is air-gapped during activation."
        )

# MLX model cache — avoids reloading on every call (seconds of latency)
_mlx_cache: dict[str, tuple] = {}

if TYPE_CHECKING:
    from agents.core.agent import Agent


async def stream_mlx(
    messages: list[dict], model: str
) -> AsyncGenerator[str, None]:
    """Native Apple Silicon inference via MLX — fastest local path on M-series."""
    try:
        from mlx_lm import generate, load
    except ImportError:
        yield "[mlx_lm not installed — run: pip install mlx-lm]"
        return

    model_name = model.removeprefix("mlx-").removeprefix("mlx_")
    if model_name not in _mlx_cache:
        _mlx_cache[model_name] = load(model_name)
    model_obj, tokenizer = _mlx_cache[model_name]
    prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)

    # MLX generate is synchronous — run in thread to not block event loop
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, lambda: generate(model_obj, tokenizer, prompt=prompt, max_tokens=4096)
    )
    # Yield in chunks so callers see streaming behaviour
    chunk_size = 64
    for i in range(0, len(result), chunk_size):
        yield result[i : i + chunk_size]


async def stream_local(
    messages: list[dict], model: str, base_url: str = "http://localhost:11434"
) -> AsyncGenerator[str, None]:
    """Ollama local inference — air-gapped, sovereign."""
    payload = {"model": model, "messages": messages, "stream": True}
    async with httpx.AsyncClient(timeout=300) as client:
        async with client.stream("POST", f"{base_url}/api/chat", json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                data = json.loads(line)
                content = data.get("message", {}).get("content", "")
                if content:
                    yield content
                if data.get("done"):
                    break


async def stream_anthropic(
    messages: list[dict], model: str
) -> AsyncGenerator[str, None]:
    """Anthropic Claude API — cloud, but no OpenAI dependency."""
    _spore_guard("Anthropic")
    import anthropic

    client = anthropic.AsyncAnthropic()
    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    msgs = [m for m in messages if m["role"] != "system"]
    async with client.messages.stream(
        model=model, max_tokens=4096, system=system, messages=msgs
    ) as stream:
        async for text in stream.text_stream:
            yield text


async def stream_openai(
    messages: list[dict], model: str
) -> AsyncGenerator[str, None]:
    """OpenAI API — last resort, not sovereign. Avoid for sensitive work."""
    _spore_guard("OpenAI")
    import openai

    client = openai.AsyncOpenAI()
    async with client.chat.completions.stream(model=model, messages=messages) as stream:
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

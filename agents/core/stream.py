"""
DOME-HUB Streaming LLM responses — multi-provider, local-first.

Provider hierarchy (sovereign order):
  1. stream_mlx    — Apple MLX, native M-series, fully air-gapped
  2. stream_local  — Ollama, local, air-gapped
  3. stream_anthropic — Anthropic API (cloud, no OpenAI dependency)
  4. stream_openai — OpenAI API (avoid for sensitive/sovereign tasks)
"""

from __future__ import annotations
from typing import AsyncGenerator, TYPE_CHECKING
import asyncio, httpx, json

if TYPE_CHECKING:
    from agents.core.agent import Agent


async def stream_mlx(
    messages: list[dict], model: str
) -> AsyncGenerator[str, None]:
    """Native Apple Silicon inference via MLX — fastest local path on M-series."""
    try:
        from mlx_lm import load, generate
    except ImportError:
        yield "[mlx_lm not installed — run: pip install mlx-lm]"
        return

    model_name = model.removeprefix("mlx-").removeprefix("mlx_")
    model_obj, tokenizer = load(model_name)
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
    import openai

    client = openai.AsyncOpenAI()
    async with client.chat.completions.stream(model=model, messages=messages) as stream:
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

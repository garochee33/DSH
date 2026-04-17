"""
DOME-HUB Streaming LLM responses
"""
from __future__ import annotations
import httpx
import json
from typing import AsyncGenerator
from agents.core.agent import Agent


async def stream_openai(messages: list[dict], model: str) -> AsyncGenerator[str, None]:
    import openai
    client = openai.AsyncOpenAI()
    async with client.chat.completions.stream(model=model, messages=messages) as stream:
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta


async def stream_anthropic(messages: list[dict], model: str) -> AsyncGenerator[str, None]:
    import anthropic
    client = anthropic.AsyncAnthropic()
    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    msgs = [m for m in messages if m["role"] != "system"]
    async with client.messages.stream(model=model, max_tokens=4096, system=system, messages=msgs) as stream:
        async for text in stream.text_stream:
            yield text


async def stream_local(
    messages: list[dict], model: str, base_url: str = "http://localhost:11434"
) -> AsyncGenerator[str, None]:
    payload = {"model": model, "messages": messages, "stream": True}
    async with httpx.AsyncClient(timeout=120) as client:
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


class StreamingAgent(Agent):
    """Agent subclass that adds async streaming via stream_run."""

    async def stream_run(self, prompt: str) -> AsyncGenerator[str, None]:
        self.remember("user", prompt)
        messages = self.recall()

        if self.model.startswith("claude"):
            gen = stream_anthropic(messages, self.model)
        elif self.model.startswith("gpt") or self.model.startswith("o"):
            gen = stream_openai(messages, self.model)
        else:
            gen = stream_local(messages, self.model)

        full_response = []
        async for chunk in gen:
            full_response.append(chunk)
            yield chunk

        self.remember("assistant", "".join(full_response))

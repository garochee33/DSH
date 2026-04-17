"""
DOME-HUB Agent Base Class
Supports tool use, memory, and multi-LLM routing (OpenAI, Anthropic, local)
"""
from __future__ import annotations
import json, time
from typing import Any, Callable
from dataclasses import dataclass, field


@dataclass
class Message:
    role: str   # system | user | assistant | tool
    content: str
    tool_name: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class ToolResult:
    name: str
    output: Any
    error: str | None = None


class Agent:
    def __init__(
        self,
        name: str,
        model: str = "gpt-4o",
        system_prompt: str = "",
        tools: list[Callable] | None = None,
        memory_limit: int = 50,
    ):
        self.name = name
        self.model = model
        self.system_prompt = system_prompt
        self.tools: dict[str, Callable] = {t.__name__: t for t in (tools or [])}
        self.memory: list[Message] = []
        self.memory_limit = memory_limit
        self._client = None

    # ── LLM routing ──────────────────────────────────────────────────────────

    def _get_client(self):
        if self._client:
            return self._client
        if self.model.startswith("gpt") or self.model.startswith("o"):
            import openai
            self._client = openai.OpenAI()
        elif self.model.startswith("claude"):
            import anthropic
            self._client = anthropic.Anthropic()
        else:
            # local (ollama-compatible)
            import openai
            self._client = openai.OpenAI(base_url="http://localhost:11434/v1", api_key="local")
        return self._client

    def _call_llm(self, messages: list[dict]) -> str:
        client = self._get_client()
        if self.model.startswith("claude"):
            system = next((m["content"] for m in messages if m["role"] == "system"), "")
            msgs = [m for m in messages if m["role"] != "system"]
            resp = client.messages.create(model=self.model, max_tokens=4096, system=system, messages=msgs)
            return resp.content[0].text
        else:
            resp = client.chat.completions.create(model=self.model, messages=messages)
            return resp.choices[0].message.content

    # ── Memory ────────────────────────────────────────────────────────────────

    def remember(self, role: str, content: str, **meta):
        self.memory.append(Message(role=role, content=content, metadata=meta))
        if len(self.memory) > self.memory_limit:
            self.memory = self.memory[-self.memory_limit:]

    def recall(self) -> list[dict]:
        msgs = []
        if self.system_prompt:
            msgs.append({"role": "system", "content": self.system_prompt})
        for m in self.memory:
            msgs.append({"role": m.role, "content": m.content})
        return msgs

    def clear_memory(self):
        self.memory = []

    # ── Tool execution ────────────────────────────────────────────────────────

    def use_tool(self, name: str, **kwargs) -> ToolResult:
        if name not in self.tools:
            return ToolResult(name=name, output=None, error=f"Tool '{name}' not found")
        try:
            output = self.tools[name](**kwargs)
            return ToolResult(name=name, output=output)
        except Exception as e:
            return ToolResult(name=name, output=None, error=str(e))

    # ── Main run loop ─────────────────────────────────────────────────────────

    def run(self, prompt: str) -> str:
        self.remember("user", prompt)
        response = self._call_llm(self.recall())

        # Simple tool call detection (JSON block in response)
        if "```tool" in response:
            try:
                tool_block = response.split("```tool")[1].split("```")[0].strip()
                call = json.loads(tool_block)
                result = self.use_tool(call["name"], **call.get("args", {}))
                tool_output = str(result.output) if not result.error else f"Error: {result.error}"
                self.remember("assistant", response)
                self.remember("tool", tool_output, tool_name=call["name"])
                response = self._call_llm(self.recall())
            except Exception:
                pass

        self.remember("assistant", response)
        return response

    def __repr__(self):
        return f"Agent(name={self.name}, model={self.model}, tools={list(self.tools.keys())})"

"""
DOME-HUB Agent Base Class — wired with MemorySystem, Tracer, and streaming.

Provider routing (local-first, no single-vendor lock-in):
  - llama* / mistral* / phi* / gemma* / qwen* / deepseek* / yi* / vicuna*
      → Ollama  (local, air-gapped, sovereign)
  - mlx-* / mlx_*
      → Apple MLX  (native M-series silicon, fastest local path)
  - claude-*
      → Anthropic API  (cloud, but no OpenAI dependency)
  - gpt-* / o1* / o3*
      → OpenAI API  (avoid for sensitive/sovereign tasks)

Set DOME_PROVIDER=local to force all agents to their local equivalent.
"""

from __future__ import annotations
import json, os, uuid
from typing import Any, AsyncGenerator, Callable

from agents.core.memory import MemorySystem
from agents.core.trace import Tracer
from agents.core.stream import stream_openai, stream_anthropic, stream_local, stream_mlx

# Sovereign default: local Ollama. Override per-agent or via DOME_PROVIDER.
_DEFAULT_LOCAL_MODEL = os.environ.get("DOME_LOCAL_MODEL", "llama3.1:8b")

_LOCAL_PREFIXES = (
    "llama", "mistral", "phi", "gemma", "qwen", "deepseek",
    "yi", "vicuna", "falcon", "orca", "nous", "solar", "codellama",
)


def _is_local(model: str) -> bool:
    return model.lower().startswith(_LOCAL_PREFIXES)


def _is_mlx(model: str) -> bool:
    return model.lower().startswith(("mlx-", "mlx_"))


def _is_claude(model: str) -> bool:
    return model.lower().startswith("claude")


class Agent:
    def __init__(
        self,
        name: str,
        model: str = _DEFAULT_LOCAL_MODEL,
        system_prompt: str = "",
        tools: list[Callable] | None = None,
        memory_namespace: str | None = None,
        enable_tracing: bool = True,
    ):
        self.name = name
        self.model = model
        self.system_prompt = system_prompt
        self.tools: dict[str, Callable] = {t.__name__: t for t in (tools or [])}
        self.enable_tracing = enable_tracing
        self._session = str(uuid.uuid4())
        self.mem = MemorySystem(
            agent=name,
            session=self._session,
            namespace=memory_namespace or name,
            llm_fn=self._call_llm,
        )
        self.tracer = Tracer() if enable_tracing else None
        self._client = None

    # ── LLM routing ──────────────────────────────────────────────────────────

    def _get_client(self):
        if self._client:
            return self._client
        if _is_mlx(self.model):
            self._client = "mlx"
        elif _is_local(self.model):
            import openai
            self._client = openai.OpenAI(
                base_url="http://localhost:11434/v1", api_key="local"
            )
        elif _is_claude(self.model):
            import anthropic
            self._client = anthropic.Anthropic()
        else:
            # OpenAI — last resort, not sovereign
            import openai
            self._client = openai.OpenAI()
        return self._client

    def _call_llm(self, messages: list[dict]) -> str:
        client = self._get_client()
        if client == "mlx":
            from mlx_lm import load, generate
            model_obj, tokenizer = load(self.model.removeprefix("mlx-"))
            prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
            return generate(model_obj, tokenizer, prompt=prompt, max_tokens=4096)
        if _is_claude(self.model):
            system = next((m["content"] for m in messages if m["role"] == "system"), "")
            msgs = [m for m in messages if m["role"] != "system"]
            resp = client.messages.create(
                model=self.model, max_tokens=4096, system=system, messages=msgs
            )
            return resp.content[0].text
        resp = client.chat.completions.create(model=self.model, messages=messages)
        return resp.choices[0].message.content

    # ── Memory helpers ────────────────────────────────────────────────────────

    def remember(self, role: str, content: str, **meta):
        self.mem.store(role, content, metadata=meta)

    def recall(self) -> list[dict]:
        msgs = []
        if self.system_prompt:
            msgs.append({"role": "system", "content": self.system_prompt})
        msgs.extend(self.mem.context())
        return msgs

    def clear_memory(self):
        self.mem.working.clear()

    # ── Tool execution ────────────────────────────────────────────────────────

    def use_tool(self, name: str, span_id: str | None = None, **kwargs) -> Any:
        if name not in self.tools:
            return f"Tool '{name}' not found"
        try:
            result = self.tools[name](**kwargs)
            if self.tracer and span_id:
                self.tracer.log_event(
                    span_id, "tool_call", {"tool": name, "result": str(result)}
                )
            return result
        except Exception as e:
            err = str(e)
            if self.tracer and span_id:
                self.tracer.log_event(
                    span_id, "tool_error", {"tool": name, "error": err}
                )
            return f"Error: {err}"

    # ── Main run loop ─────────────────────────────────────────────────────────

    def run(self, prompt: str) -> str:
        sid = self.tracer.start_span("agent.run") if self.tracer else None
        if sid:
            self.tracer.log_event(
                sid, "call", {"agent": self.name, "model": self.model, "prompt": prompt}
            )

        self.remember("user", prompt)
        response = self._call_llm(self.recall())

        # Tool call detection (```tool JSON block)
        if "```tool" in response:
            try:
                block = response.split("```tool")[1].split("```")[0].strip()
                call = json.loads(block)
                tool_out = self.use_tool(
                    call["name"], span_id=sid, **call.get("args", {})
                )
                self.remember("assistant", response)
                self.remember("tool", str(tool_out))
                response = self._call_llm(self.recall())
            except Exception:
                pass

        self.remember("assistant", response)

        if sid:
            self.tracer.log_event(sid, "result", {"response": response})
            self.tracer.end_span(sid)

        return response

    # ── Streaming ─────────────────────────────────────────────────────────────

    async def stream_run(self, prompt: str) -> AsyncGenerator[str, None]:
        sid = self.tracer.start_span("agent.stream_run") if self.tracer else None
        if sid:
            self.tracer.log_event(
                sid, "call", {"agent": self.name, "model": self.model, "prompt": prompt}
            )

        self.remember("user", prompt)
        messages = self.recall()

        if self.model.startswith("claude"):
            gen = stream_anthropic(messages, self.model)
        elif self.model.startswith("gpt") or self.model.startswith("o"):
            gen = stream_openai(messages, self.model)
        else:
            gen = stream_local(messages, self.model)

        chunks: list[str] = []
        async for chunk in gen:
            chunks.append(chunk)
            yield chunk

        full = "".join(chunks)
        self.remember("assistant", full)

        if sid:
            self.tracer.log_event(sid, "result", {"response": full})
            self.tracer.end_span(sid)

    # ── Semantic recall ───────────────────────────────────────────────────────

    def search_memory(self, query: str, top_k: int = 5) -> list[dict]:
        return self.mem.search(query, top_k=top_k)

    def __repr__(self):
        return (
            f"Agent(name={self.name!r}, model={self.model!r}, tools={list(self.tools)})"
        )

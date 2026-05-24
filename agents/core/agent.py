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

Set DOME_PROVIDER=local to force all agents to DOME_LOCAL_MODEL (registry).
That is usually Ollama; use an mlx-* name there to run MLX locally instead.
"""

from __future__ import annotations
import json, os, uuid
import logging
from typing import Any, AsyncGenerator, Callable

from agents.core.memory import MemorySystem
from agents.core.trace import Tracer
from agents.core.stream import stream_openai, stream_anthropic, stream_local, stream_mlx


# ── Wired integrations (lazy, fire-and-forget) ───────────────────────────────

# ── Brain Optimization Config (LAVA-BRAIN-ARCH-v3-2026-05-20) ────────────────
# These constants are synced with the TypeScript production server.
BRAIN_OPT_PHI = 1.6180339887
BRAIN_OPT_PHI_SQ_INV = 0.3819660113  # φ⁻² pheromone decay
BRAIN_OPT_STDP_A_PLUS = 0.015
BRAIN_OPT_STDP_A_MINUS = 0.0165
BRAIN_OPT_CONSOLIDATION_THRESHOLD = 0.55
BRAIN_OPT_LONG_TERM_BATCH = 14
BRAIN_OPT_MERKABA_THRESHOLD = 0.92
BRAIN_OPT_GOD_MODE = os.environ.get("GOD_MODE_ACTIVE", "true").lower() == "true"
JULIA_COMPUTE_URL = os.environ.get("JULIA_COMPUTE_URL", "http://localhost:8787")


def _write_session_log(agent_name: str, summary: str, details: str = ""):
    """Write a session log to the canonical memory/sessions/ directory."""
    try:
        from datetime import datetime, timezone
        from pathlib import Path
        dome = Path(os.environ.get("DOME_ROOT", os.path.expanduser("~/DOME-HUB")))
        now = datetime.now(timezone.utc)
        month_dir = dome / "memory" / "sessions" / now.strftime("%Y-%m")
        month_dir.mkdir(parents=True, exist_ok=True)
        filename = f"SESSION_{now.strftime('%Y-%m-%d')}_{agent_name.upper()}.md"
        path = month_dir / filename
        content = f"# Session: {agent_name} — {now.strftime('%Y-%m-%d %H:%M UTC')}\n\n{summary}\n"
        if details:
            content += f"\n## Details\n\n{details}\n"
        # Append if same-day session exists, otherwise create
        with open(path, "a") as f:
            f.write(content + "\n---\n\n")
    except Exception:
        pass


def _akashic_write(content: str, domain: str = "agent", depth: str = "decision", node: str = "system"):
    try:
        from akashic.record import write
        write(content=content, domain=domain, depth=depth, node=node)
    except Exception:
        pass


def _akashic_query(concept: str, n: int = 3) -> list[dict]:
    try:
        from akashic.record import query
        return query(concept=concept, n=n)
    except Exception:
        return []


def _trinity_kb_query(q: str, top_k: int = 3) -> list[dict]:
    try:
        import httpx
        base = os.environ.get("TRINITY_KB_URL", "http://localhost:3333")
        r = httpx.post(f"{base}/api/kb/search", json={"query": q, "limit": top_k}, timeout=5)
        return r.json().get("results", []) if r.status_code == 200 else []
    except Exception:
        return []


_quantum_dome = None

def _get_quantum_dome():
    global _quantum_dome
    if _quantum_dome is None:
        try:
            from compute.quantum_dome import QuantumDome
            _quantum_dome = QuantumDome()
        except Exception:
            pass
    return _quantum_dome

# Sovereign default: local Ollama. Override per-agent or via DOME_PROVIDER.
_DEFAULT_LOCAL_MODEL = os.environ.get("DOME_LOCAL_MODEL", "llama3.1:8b")

_LOCAL_PREFIXES = (
    "llama", "mistral", "phi", "gemma", "qwen", "deepseek",
    "yi", "vicuna", "falcon", "orca", "nous", "solar", "codellama",
)
_LOG = logging.getLogger(__name__)


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
        self._qdome = _get_quantum_dome()

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
        dome = _get_quantum_dome()
        if dome:
            dome.memory.auto_clear()
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

        # ── Pre-run: Akashic + Trinity KB context enrichment ──
        for r in _akashic_query(prompt):
            self.remember("system", f"[akashic] {r.get('content','')[:200]}")
        for r in _trinity_kb_query(prompt):
            self.remember("system", f"[trinity-kb] {(r.get('content','') or r.get('text',''))[:200]}")

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
            except Exception as e:
                err = f"Tool-call block parse/execute failed: {e}"
                _LOG.exception(err)
                if sid and self.tracer:
                    self.tracer.log_event(sid, "tool_block_error", {"error": err})

        self.remember("assistant", response)

        # ── Post-run: persist facts for continuity ──
        try:
            count = int(self.mem.episodic.get_fact(self.name, "interaction_count") or "0")
            self.mem.episodic.store_fact(self.name, "interaction_count", str(count + 1))
            self.mem.episodic.store_fact(self.name, "last_topic", prompt[:100])
        except Exception:
            pass

        # ── Post-run: write decision to Akashic ──
        _akashic_write(f"[{self.name}] Q:{prompt[:80]} A:{response[:150]}", node=self.name)

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

        if _is_mlx(self.model):
            gen = stream_mlx(messages, self.model)
        elif _is_claude(self.model):
            gen = stream_anthropic(messages, self.model)
        elif self.model.startswith(("gpt-", "o1", "o3")):
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

    def use_skill(self, skill_name: str, **kwargs):
        """Invoke a registered skill by name."""
        from agents.core.skills import SKILLS
        import inspect as _insp
        if skill_name not in SKILLS:
            return f"Skill '{skill_name}' not found. Available: {list(SKILLS.keys())}"
        fn = SKILLS[skill_name]
        params = _insp.signature(fn).parameters
        if params and list(params.keys())[0] == "agent":
            return fn(self, **kwargs)
        return fn(**kwargs)

    def __repr__(self):
        return (
            f"Agent(name={self.name!r}, model={self.model!r}, tools={list(self.tools)})"
        )

#!/usr/bin/env python3
"""agents/claude/runner.py — Claude (Anthropic) agent runner.

Real Anthropic SDK HTTP runner. Mirrors the contract of the kimi/cursor/kiro/
trinity runners: a `<Tool>Runner` class plus a module-level `run()` convenience.

Example:
    python agents/claude/runner.py --prompt "Summarize kb/claude/architecture.md"

Auth: ANTHROPIC_API_KEY (rendered into .env from Keychain `dome/ANTHROPIC_API_KEY`).
If `claude_agent_sdk` is later available, the richer tool-use path can be wired in.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys

try:
    import yaml  # pyyaml (optional)
except ImportError:  # pragma: no cover
    yaml = None

REPO = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = REPO / "agents" / "claude" / "agent.yaml"
DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-6")


class ClaudeRunner:
    """Real Claude (Anthropic) agent runner."""

    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.manifest = self._load_manifest()

    @staticmethod
    def _load_manifest() -> dict:
        if not MANIFEST.exists():
            return {"model": {"default": DEFAULT_MODEL}, "kb": {"root": "kb/claude/"}}
        text = MANIFEST.read_text()
        if yaml is not None:
            return yaml.safe_load(text) or {}
        # Naive fallback: only pull the fields we need.
        out: dict = {"model": {"default": DEFAULT_MODEL}, "kb": {"root": "kb/claude/"}}
        for line in text.splitlines():
            if line.startswith("  default:"):
                out["model"]["default"] = line.split(":", 1)[1].strip().strip('"')
                break
        return out

    def system_prompt(self) -> str:
        kb_root = REPO / self.manifest.get("kb", {}).get("root", "kb/claude/")
        parts = [
            "You are Claude, running inside DOME-HUB — a sovereign, local-first AI ",
            "development environment — a sovereign node of Trinity Consortium.",
            "",
            f"Your knowledge base is at {kb_root.relative_to(REPO)}. ",
            "Always consult it before answering questions about your own ",
            "capabilities or DOME-HUB's architecture.",
            "",
            "Skills available (see kb/claude/skills/): docx, pdf, pptx, xlsx, ",
            "schedule, setup-cowork, skill-creator, consolidate-memory.",
        ]
        return "\n".join(parts)

    def run(self, prompt: str, max_tokens: int = 2048) -> str:
        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise RuntimeError(
                "anthropic package not installed. "
                "Run: pip install -r compute/requirements.txt"
            ) from e

        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. Render via:\n"
                "  bash scripts/render-env.sh   # pulls dome/ANTHROPIC_API_KEY from Keychain"
            )

        client = Anthropic()
        resp = client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system_prompt(),
            messages=[{"role": "user", "content": prompt}],
        )
        out: list[str] = []
        for block in resp.content:
            if getattr(block, "type", None) == "text":
                out.append(block.text)
        return "\n".join(out)


def run(prompt: str, model: str = DEFAULT_MODEL, max_tokens: int = 2048) -> str:
    """Module-level convenience function."""
    return ClaudeRunner(model=model).run(prompt, max_tokens=max_tokens)


def main() -> int:
    p = argparse.ArgumentParser(description="Run Claude locally from DOME-HUB.")
    p.add_argument("--prompt", required=True, help="User prompt")
    p.add_argument("--model", default=DEFAULT_MODEL, help="Override model")
    p.add_argument("--max-tokens", type=int, default=2048)
    args = p.parse_args()
    try:
        text = ClaudeRunner(model=args.model).run(args.prompt, max_tokens=args.max_tokens)
        print(text)
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

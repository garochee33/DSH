#!/usr/bin/env python3
"""agents/claude/runner.py — minimal CLI runner for the Claude agent.

Example:

    python agents/claude/runner.py --prompt "Summarize kb/claude/architecture.md"

Relies on ANTHROPIC_API_KEY. Loads the agent manifest from
`agents/claude/agent.yaml` and uses the Anthropic SDK's Messages API directly.
If `claude_agent_sdk` is available, the richer tool-use path is preferred.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys

try:
    import yaml  # pyyaml (optional, fallback to json if missing)
except ImportError:  # pragma: no cover
    yaml = None

REPO = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = REPO / "agents" / "claude" / "agent.yaml"
DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-6")


def load_manifest() -> dict:
    text = MANIFEST.read_text()
    if yaml is not None:
        return yaml.safe_load(text)
    # Naive fallback: only pull the fields we need.
    out = {"model": {"default": DEFAULT_MODEL}, "kb": {"root": "kb/claude/"}}
    for line in text.splitlines():
        if line.startswith("  default:"):
            out["model"]["default"] = line.split(":", 1)[1].strip().strip('"')
            break
    return out


def system_prompt(manifest: dict) -> str:
    kb_root = REPO / manifest.get("kb", {}).get("root", "kb/claude/")
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


def run(prompt: str, model: str) -> int:
    try:
        from anthropic import Anthropic
    except ImportError:
        print(
            "error: anthropic package not installed. "
            "Run: pip install -r compute/requirements.txt",
            file=sys.stderr,
        )
        return 2

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        return 3

    manifest = load_manifest()
    client = Anthropic()
    resp = client.messages.create(
        model=model,
        max_tokens=2048,
        system=system_prompt(manifest),
        messages=[{"role": "user", "content": prompt}],
    )
    for block in resp.content:
        if getattr(block, "type", None) == "text":
            print(block.text)
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Run Claude locally from DOME-HUB.")
    p.add_argument("--prompt", required=True, help="User prompt")
    p.add_argument("--model", default=DEFAULT_MODEL, help="Override model")
    args = p.parse_args()
    return run(args.prompt, args.model)


if __name__ == "__main__":
    sys.exit(main())

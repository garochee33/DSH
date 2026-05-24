#!/usr/bin/env python3
"""agents/kimi/runner.py — Kimi (Moonshot AI) agent runner.

Two real backends, picked in this order:

  1. HTTP API (preferred) — direct call to api.moonshot.ai (OpenAI-compatible).
     Requires MOONSHOT_API_KEY in env.
  2. CLI fallback — shells out to the local `kimi` binary via its ACP subcommand.
     Requires `kimi` on PATH and a prior `kimi login`.

Example:
    python agents/kimi/runner.py --prompt "Summarise kb/developer-context.md"
    python agents/kimi/runner.py --prompt "..." --model moonshot-v1-32k
    python agents/kimi/runner.py --prompt "..." --backend cli
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys

try:
    import yaml
except ImportError:
    yaml = None

REPO = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = REPO / "agents" / "kimi" / "agent.yaml"
DEFAULT_MODEL = os.environ.get("KIMI_MODEL", "kimi-k2-0905-preview")
DEFAULT_BASE_URL = os.environ.get("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1")


class KimiRunner:
    """Real Kimi agent runner. Prefers HTTP, falls back to CLI."""

    def __init__(self, model: str = DEFAULT_MODEL, base_url: str = DEFAULT_BASE_URL):
        self.model = model
        self.base_url = base_url
        self.manifest = self._load_manifest()

    @staticmethod
    def _load_manifest() -> dict:
        if not MANIFEST.exists():
            return {}
        text = MANIFEST.read_text()
        if yaml is not None:
            return yaml.safe_load(text) or {}
        return {}

    def _system_prompt(self) -> str:
        return (
            "You are Kimi (Moonshot AI), running inside DOME-HUB — a sovereign "
            "local-first AI development environment, a Trinity Consortium node. "
            "Be direct, factual, and grounded. Cite sources when reasoning over external information."
        )

    # ─── HTTP backend ───────────────────────────────────────────────────────
    def run_http(self, prompt: str, max_tokens: int = 2048) -> str:
        api_key = os.environ.get("MOONSHOT_API_KEY")
        if not api_key:
            raise RuntimeError(
                "MOONSHOT_API_KEY not set. Add via:\n"
                "  security add-generic-password -s 'dome/MOONSHOT_API_KEY' -a $USER -w '<key>'\n"
                "  then re-run scripts/render-env.sh"
            )

        try:
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError(
                "openai package not installed. Run: pip install openai>=1.0"
            ) from e

        client = OpenAI(api_key=api_key, base_url=self.base_url)
        resp = client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": prompt},
            ],
        )
        return resp.choices[0].message.content or ""

    # ─── CLI backend ────────────────────────────────────────────────────────
    # Note: the `kimi` CLI (v1.11.0) has no non-interactive prompt subcommand.
    # `kimi term` is a TUI; `kimi acp` runs an ACP server that does not return
    # after a single stdin message. For programmatic use, only the HTTP path is
    # production-ready. The CLI hook here exists for status/auth probing.
    def cli_info(self) -> str:
        binary = shutil.which("kimi")
        if not binary:
            raise RuntimeError(
                "`kimi` binary not on PATH. Install Kimi CLI from https://moonshotai.github.io/kimi-cli/"
            )
        proc = subprocess.run(
            [binary, "info"], capture_output=True, text=True, timeout=15
        )
        return proc.stdout if proc.returncode == 0 else proc.stderr

    def run(self, prompt: str, backend: str = "auto", max_tokens: int = 2048) -> str:
        if backend == "http":
            return self.run_http(prompt, max_tokens=max_tokens)
        if backend == "cli":
            raise RuntimeError(
                "Kimi CLI has no non-interactive prompt mode (TUI/ACP only). "
                "Use --backend http with MOONSHOT_API_KEY set, or run `kimi term` "
                "interactively yourself."
            )
        # auto: HTTP only (CLI has no programmatic prompt path)
        return self.run_http(prompt, max_tokens=max_tokens)


def run(prompt: str, model: str = DEFAULT_MODEL, backend: str = "auto") -> str:
    """Module-level convenience function."""
    return KimiRunner(model=model).run(prompt, backend=backend)


def main() -> int:
    p = argparse.ArgumentParser(description="Run Kimi (Moonshot AI) from DOME-HUB.")
    p.add_argument("--prompt", required=True, help="User prompt")
    p.add_argument("--model", default=DEFAULT_MODEL, help="Override model")
    p.add_argument("--backend", default="auto", choices=["auto", "http", "cli"])
    p.add_argument("--max-tokens", type=int, default=2048)
    args = p.parse_args()
    try:
        text = KimiRunner(model=args.model).run(
            args.prompt, backend=args.backend, max_tokens=args.max_tokens
        )
        print(text)
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

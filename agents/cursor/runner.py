#!/usr/bin/env python3
"""agents/cursor/runner.py — Cursor agent runner via cursor-agent CLI.

Real shell-out to the `cursor-agent` binary in non-interactive print mode.
Auth: either CURSOR_API_KEY env var, or the cursor-access-token in macOS
Keychain (auto-discovered by the CLI).

Example:
    python agents/cursor/runner.py --prompt "Explain server/ai/orchestration-engine.ts"
    python agents/cursor/runner.py --prompt "..." --mode plan
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_MODE = os.environ.get("CURSOR_AGENT_MODE", "full")  # full | plan | ask
DEFAULT_TIMEOUT = int(os.environ.get("CURSOR_AGENT_TIMEOUT", "300"))


class CursorRunner:
    """Real Cursor agent runner. Shells out to cursor-agent."""

    def __init__(self, mode: str = DEFAULT_MODE, workdir: str | None = None):
        self.mode = mode
        self.workdir = workdir or os.environ.get("CURSOR_AGENT_WORKDIR", str(REPO))
        self.binary = shutil.which("cursor-agent")
        if not self.binary:
            raise RuntimeError(
                "`cursor-agent` not on PATH. Install Cursor and run "
                "`cursor` once to install the CLI shim."
            )

    def _build_args(self, prompt: str, output_format: str = "json", trust: bool = True) -> list[str]:
        args = [self.binary, "-p", "--output-format", output_format]
        # Workspace trust: cursor-agent in print mode bails out with a
        # "Workspace Trust Required" prompt unless --force / -f is supplied.
        # The runner runs non-interactively, so trust must be explicit.
        if trust:
            args.append("-f")
        if self.mode in ("plan", "ask"):
            args += ["--mode", self.mode]
        # API key passthrough if set explicitly (else CLI uses keychain)
        if os.environ.get("CURSOR_API_KEY"):
            args += ["--api-key", os.environ["CURSOR_API_KEY"]]
        args.append(prompt)
        return args

    def run(self, prompt: str, output_format: str = "json", timeout: int = DEFAULT_TIMEOUT, trust: bool = True) -> str:
        args = self._build_args(prompt, output_format=output_format, trust=trust)
        proc = subprocess.run(
            args,
            cwd=self.workdir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"cursor-agent failed (rc={proc.returncode}): "
                f"stderr={proc.stderr.strip()[:500]}"
            )

        # JSON output: extract assistant text from final turn
        if output_format == "json":
            try:
                data = json.loads(proc.stdout)
            except json.JSONDecodeError:
                # Fall back to raw stdout — cursor-agent JSON shape may vary by version
                return proc.stdout.strip()
            # Common shapes: {"output": "...", "messages": [...]}
            if isinstance(data, dict):
                if "output" in data:
                    return str(data["output"])
                if "result" in data:
                    return str(data["result"])
                if "messages" in data and isinstance(data["messages"], list):
                    texts = []
                    for m in data["messages"]:
                        if isinstance(m, dict) and m.get("role") == "assistant":
                            content = m.get("content") or m.get("text") or ""
                            if content:
                                texts.append(str(content))
                    if texts:
                        return "\n".join(texts)
            return json.dumps(data, indent=2)
        return proc.stdout.strip()


def run(prompt: str, mode: str = DEFAULT_MODE, output_format: str = "json") -> str:
    """Module-level convenience function."""
    return CursorRunner(mode=mode).run(prompt, output_format=output_format)


def main() -> int:
    p = argparse.ArgumentParser(description="Run Cursor Agent from DSH.")
    p.add_argument("--prompt", required=True, help="User prompt")
    p.add_argument("--mode", default=DEFAULT_MODE, choices=["full", "plan", "ask"])
    p.add_argument("--workdir", default=None, help="Working directory")
    p.add_argument("--output-format", default="json", choices=["text", "json", "stream-json"])
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    args = p.parse_args()
    try:
        text = CursorRunner(mode=args.mode, workdir=args.workdir).run(
            args.prompt, output_format=args.output_format, timeout=args.timeout
        )
        print(text)
        return 0
    except subprocess.TimeoutExpired:
        print(f"error: cursor-agent timed out after {args.timeout}s", file=sys.stderr)
        return 124
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""agents/kiro/runner.py — Kiro CLI agent runner.

Real shell-out to the Kiro CLI (AWS-derived). The /usr/local/bin/kiro launcher
ships with an unfilled `@@APPNAME@@` placeholder on this machine, so this
runner resolves the underlying binary inside the .app bundle directly:

    /Applications/Kiro CLI.app/Contents/MacOS/kiro-cli-chat

Auth: prior `kiro-cli-chat login` (token stored in macOS Keychain as
`kirocli:social:token`).

Examples:
    python agents/kiro/runner.py --prompt "Explain server/ai/orchestration-engine.ts"
    python agents/kiro/runner.py --prompt "..." --agent default --trust-all-tools
    python agents/kiro/runner.py whoami
"""

from __future__ import annotations

import argparse
import os
import pathlib
import shutil
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
KIRO_APP_BIN = "/Applications/Kiro CLI.app/Contents/MacOS/kiro-cli-chat"
DEFAULT_TIMEOUT = int(os.environ.get("KIRO_TIMEOUT", "300"))


def resolve_binary() -> str:
    """Return the most-functional kiro binary path.

    Order:
      1. /Applications/Kiro CLI.app/Contents/MacOS/kiro-cli-chat (canonical)
      2. `kiro` on PATH (if not the broken router-script with @@APPNAME@@)
      3. `kiro-cli-chat` on PATH
    Raises RuntimeError if none works.
    """
    if pathlib.Path(KIRO_APP_BIN).exists():
        return KIRO_APP_BIN

    candidate = shutil.which("kiro-cli-chat")
    if candidate:
        return candidate

    candidate = shutil.which("kiro")
    if candidate:
        # Test if the launcher is still broken (has unfilled placeholder)
        try:
            with open(candidate) as f:
                contents = f.read()
            if "@@APPNAME@@" in contents:
                raise RuntimeError(
                    f"`{candidate}` ships with unfilled `@@APPNAME@@` placeholder. "
                    "Reinstall Kiro CLI or symlink the in-app binary directly."
                )
        except OSError:
            pass  # Maybe binary, not script
        return candidate

    raise RuntimeError(
        "Kiro CLI not found. Install via https://kiro.dev/ "
        "or place the in-app binary on PATH."
    )


class KiroRunner:
    """Real Kiro CLI runner."""

    def __init__(
        self,
        agent_profile: str | None = None,
        model: str | None = None,
        workdir: str | None = None,
    ):
        self.binary = resolve_binary()
        self.agent_profile = agent_profile or os.environ.get("KIRO_AGENT_NAME")
        self.model = model or os.environ.get("KIRO_MODEL")
        self.workdir = workdir or os.environ.get("KIRO_AGENT_WORKDIR", str(REPO))

    def _build_args(self, prompt: str, trust_all_tools: bool = False) -> list[str]:
        args = [self.binary, "chat", "--no-interactive"]
        if trust_all_tools:
            args.append("--trust-all-tools")
        else:
            args += ["--trust-tools="]  # trust no tools — safe default for runner
        if self.agent_profile:
            args += ["--agent", self.agent_profile]
        if self.model:
            args += ["--model", self.model]
        args.append(prompt)
        return args

    def run(self, prompt: str, trust_all_tools: bool = False, timeout: int = DEFAULT_TIMEOUT) -> str:
        args = self._build_args(prompt, trust_all_tools=trust_all_tools)
        proc = subprocess.run(
            args,
            cwd=self.workdir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"kiro-cli-chat failed (rc={proc.returncode}): "
                f"stderr={proc.stderr.strip()[:500]}"
            )
        return proc.stdout.strip()

    def whoami(self) -> str:
        proc = subprocess.run(
            [self.binary, "whoami"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"kiro-cli-chat whoami failed: {proc.stderr.strip()}")
        return proc.stdout.strip()

    def list_models(self) -> str:
        proc = subprocess.run(
            [self.binary, "chat", "--list-models"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return proc.stdout.strip() if proc.returncode == 0 else proc.stderr.strip()


def run(prompt: str, agent_profile: str | None = None, trust_all_tools: bool = False) -> str:
    """Module-level convenience function."""
    return KiroRunner(agent_profile=agent_profile).run(
        prompt, trust_all_tools=trust_all_tools
    )


def main() -> int:
    # Single flat parser — `--prompt` triggers chat (default action).
    # `whoami` / `list-models` are positional commands.
    p = argparse.ArgumentParser(description="Run Kiro CLI from DSH.")
    p.add_argument("command", nargs="?", default=None,
                   choices=[None, "chat", "whoami", "list-models"],
                   help="Subcommand. Defaults to 'chat' if --prompt is given.")
    p.add_argument("--prompt", default=None, help="Prompt for chat")
    p.add_argument("--agent", default=None, dest="agent_profile")
    p.add_argument("--model", default=None)
    p.add_argument("--workdir", default=None)
    p.add_argument("--trust-all-tools", action="store_true")
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)

    args = p.parse_args()
    cmd = args.command or ("chat" if args.prompt else None)
    if cmd is None:
        p.print_help()
        return 2

    try:
        if cmd == "chat":
            if not args.prompt:
                print("error: --prompt required for chat", file=sys.stderr)
                return 2
            runner = KiroRunner(
                agent_profile=args.agent_profile,
                model=args.model,
                workdir=args.workdir,
            )
            print(runner.run(
                args.prompt,
                trust_all_tools=args.trust_all_tools,
                timeout=args.timeout,
            ))
        elif cmd == "whoami":
            print(KiroRunner().whoami())
        elif cmd == "list-models":
            print(KiroRunner().list_models())
        return 0
    except subprocess.TimeoutExpired:
        print("error: kiro-cli-chat timed out", file=sys.stderr)
        return 124
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

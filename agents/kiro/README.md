# Kiro Agent

Real Kiro CLI runner inside DOME-HUB. Shells out to AWS-derived Kiro CLI.

## Verified state (2026-04-26)

- Canonical binary: `/Applications/Kiro CLI.app/Contents/MacOS/kiro-cli-chat`
- The `/usr/local/bin/kiro` launcher ships with an unfilled `@@APPNAME@@` placeholder (broken on this machine); runner skips it and uses the in-app binary directly.
- Auth: `kirocli:social:token` in macOS Keychain (set via `kiro-cli-chat login`)

## Usage

```bash
# Send a prompt (no tools — safe default)
python agents/kiro/runner.py --prompt "Explain server/ai/orchestration-engine.ts"

# With agent profile
python agents/kiro/runner.py --prompt "..." --agent default

# Trust all tools (allows file write + shell — be careful)
python agents/kiro/runner.py --prompt "..." --trust-all-tools

# Auth status
python agents/kiro/runner.py whoami

# Available models
python agents/kiro/runner.py list-models
```

## Setup

```bash
# 1. Verify binary
ls "/Applications/Kiro CLI.app/Contents/MacOS/kiro-cli-chat"

# 2. Auth (one-time)
"/Applications/Kiro CLI.app/Contents/MacOS/kiro-cli-chat" login

# 3. Verify
python agents/kiro/runner.py whoami
```

## Tool trust policy

- **Default**: `--trust-tools=` (empty list) — Kiro can read and reason but cannot write files or run shell commands without per-call approval. Safest for runner shell-out where prompts come from any source.
- **Explicit override**: `--trust-all-tools` — Kiro can write + execute. Use only when invoking from your own trusted scripts.

## Programmatic use

```python
from pathlib import Path

from agents.kiro import KiroRunner, run

# One-shot
text = run("Explain Trinity Consortium architecture")

# Reusable, trust all tools, custom workdir (Trinity consortium checkout)
runner = KiroRunner(workdir=str(Path.home() / "projects" / "trinity-consortium"))
text = runner.run("Refactor amma-self-heal.ts", trust_all_tools=True)
```

## Constraints

- Never bypass git hooks
- Never commit secrets (Kiro auth token in Keychain only)
- Refuses: malware, WMD, CSAM (per agent.yaml)

## Known issues

- `/usr/local/bin/kiro` shell launcher is broken (Microsoft/AWS shipped it with `@@APPNAME@@` placeholder). Runner works around this by using the in-app binary. Do NOT modify the broken launcher in this pass — fix lives in upstream installer.

# Kimi Agent (Moonshot AI)

Real Kimi runner inside DSH. No stubs.

## Backends

| Backend | When used | Requires |
|---|---|---|
| **HTTP** (preferred) | `MOONSHOT_API_KEY` in env | `openai` Python SDK, `MOONSHOT_API_KEY` |
| **CLI** (fallback) | No env key, but `kimi` binary on PATH | `kimi` CLI installed + `kimi login` complete |

## Usage

```bash
python agents/kimi/runner.py --prompt "Summarise kb/developer-context.md"
python agents/kimi/runner.py --prompt "..." --model moonshot-v1-32k
python agents/kimi/runner.py --prompt "..." --backend cli
```

## Setup

### HTTP backend (recommended)

```bash
# 1. Store key in macOS Keychain
security add-generic-password -s 'dome/MOONSHOT_API_KEY' -a $USER -w '<your-moonshot-key>'

# 2. Render into .env (idempotent)
bash scripts/render-env.sh

# 3. Verify
python agents/kimi/runner.py --prompt "say hi"
```

### CLI backend

```bash
# kimi CLI is already installed at ~/.local/bin/kimi (verified 2026-04-26)
kimi login  # one-time auth
python agents/kimi/runner.py --prompt "say hi" --backend cli
```

## Model selection

- Default: `kimi-k2-0905-preview` (best quality)
- Long context: `moonshot-v1-128k`
- Mid: `moonshot-v1-32k`
- Fast: `moonshot-v1-8k`

Override with `--model <name>` or `KIMI_MODEL=<name>` env var.

## Region

Default uses `https://api.moonshot.ai/v1` (global). For China region, set `MOONSHOT_BASE_URL=https://api.moonshot.cn/v1`.

## Programmatic use

```python
from agents.kimi import KimiRunner, run

# One-shot
text = run("Explain Trinity Consortium architecture")

# Reusable
runner = KimiRunner(model="moonshot-v1-32k")
text = runner.run("...", backend="http")
```

## Constraints

- Never bypass git hooks
- Never commit secrets (key lives in Keychain only)
- Refuses: malware, WMD, CSAM (per agent.yaml)

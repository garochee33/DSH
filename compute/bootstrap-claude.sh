#!/usr/bin/env bash
# DOME-HUB — Claude compute bootstrap
# Idempotent. Safe to re-run.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "==> Bootstrapping Claude compute environment in $REPO_ROOT"

# 1. Python venv
if [ ! -d ".venv" ]; then
  echo "--> Creating .venv (Python 3.11)"
  python3.11 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip wheel >/dev/null

echo "--> Installing Python requirements"
pip install -r compute/requirements.txt

# 2. Node toolchain (optional)
if command -v nvm >/dev/null 2>&1; then
  echo "--> Using nvm to pin Node version"
  nvm use || nvm install
fi
if command -v pnpm >/dev/null 2>&1 && [ -f "package.json" ]; then
  echo "--> Installing Node deps (pnpm)"
  pnpm install --frozen-lockfile || pnpm install
fi

# 3. Sanity checks
echo "--> Sanity checks"
python - <<'PY'
import importlib, sys
for mod in ["anthropic", "docx", "pptx", "openpyxl", "reportlab", "pypdf"]:
    try:
        importlib.import_module(mod)
        print(f"ok  {mod}")
    except Exception as e:
        print(f"MISS {mod}: {e}")
PY

# 4. Register in dome.db
echo "--> Registering in db/dome.db"
python scripts/register-claude.py || echo "(register-claude.py will be created if absent)"

echo "==> Done. Activate with: source .venv/bin/activate"

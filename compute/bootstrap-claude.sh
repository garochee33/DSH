#!/usr/bin/env bash
# DSH — Claude compute bootstrap
# Idempotent. Safe to re-run.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "==> Bootstrapping Claude compute environment in $REPO_ROOT"

# 1. Python venv — version is driven by .python-version so it stays in sync with doctrine.
if [ ! -d ".venv" ]; then
  PY_VERSION="$(cat .python-version)"
  echo "--> Creating .venv (Python $PY_VERSION)"
  "python${PY_VERSION}" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip wheel >/dev/null

echo "--> Installing Python requirements"
pip install -r compute/requirements.txt

# 1b. Ingest sidecar venv — chromadb/onnxruntime/sentence-transformers segfault on
# Python 3.14 (native-extension ABI mismatch). Same pattern as the LAVA 3.10 sidecar:
# isolate the RAG stack into its own Python 3.13 venv. Idempotent — skip if present.
INGEST_PYTHON_VERSION="3.13"
if [ ! -d ".venv-ingest" ]; then
  INGEST_PY_BIN="/opt/homebrew/opt/python@${INGEST_PYTHON_VERSION}/bin/python${INGEST_PYTHON_VERSION}"
  if command -v "${INGEST_PY_BIN}" >/dev/null 2>&1 || [ -x "${INGEST_PY_BIN}" ]; then
    echo "--> Creating .venv-ingest (Python ${INGEST_PYTHON_VERSION}) for chromadb sidecar"
    "${INGEST_PY_BIN}" -m venv .venv-ingest
    .venv-ingest/bin/pip install --quiet --upgrade pip wheel
    .venv-ingest/bin/pip install --quiet chromadb onnxruntime tokenizers numpy sentence-transformers
  else
    echo "--> Skipping .venv-ingest — Python ${INGEST_PYTHON_VERSION} not installed (brew install python@${INGEST_PYTHON_VERSION})"
  fi
fi

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

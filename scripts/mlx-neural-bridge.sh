#!/usr/bin/env bash
# Start Trinity MLX HTTP bridge from the DOME-HUB mirror (Metal / unified memory).
# Default: http://127.0.0.1:8101/health — override with MLX_BRIDGE_PORT (see nexus-core docstring).
# Env: DOME_ROOT (optional; defaults to parent of this script’s directory).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOME_ROOT="${DOME_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
BRIDGE="${DOME_ROOT}/home/projects/trinity-consortium/nexus-core/mlx-neural-bridge.py"
PY="${DOME_ROOT}/.venv/bin/python3"
if [[ ! -x "$PY" ]]; then
  echo "error: missing $PY (create .venv and pip install mlx)" >&2
  exit 1
fi
if [[ ! -f "$BRIDGE" ]]; then
  echo "error: missing $BRIDGE" >&2
  exit 1
fi
exec "$PY" "$BRIDGE"

#!/usr/bin/env bash
# Start the Akashic watcher as a background daemon (logs under $DOME_ROOT/logs/).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOME_ROOT="${DOME_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
PIDFILE="$DOME_ROOT/logs/akashic-watcher.pid"
LOG="$DOME_ROOT/logs/akashic-watcher.log"
PY="${DOME_ROOT}/.venv/bin/python3"
WATCHER="${DOME_ROOT}/akashic/watcher.py"

if [[ ! -x "$PY" ]]; then
  echo "[akashic] error: missing $PY (create .venv and install deps)" >&2
  exit 1
fi
if [[ ! -f "$WATCHER" ]]; then
  echo "[akashic] error: missing $WATCHER" >&2
  exit 1
fi

if [[ -f "$PIDFILE" ]] && kill -0 "$(<"$PIDFILE")" 2>/dev/null; then
  echo "[akashic] watcher already running (pid $(<"$PIDFILE"))"
  exit 0
fi

mkdir -p "$(dirname "$PIDFILE")"
nohup "$PY" "$WATCHER" >>"$LOG" 2>&1 &
echo $! >"$PIDFILE"
echo "[akashic] watcher started (pid $(<"$PIDFILE"))"

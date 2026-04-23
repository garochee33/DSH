#!/usr/bin/env bash
# Start the Akashic watcher as a background daemon
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOME_ROOT="${DOME_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
PIDFILE="$DOME_ROOT/logs/akashic-watcher.pid"

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "[akashic] watcher already running (pid $(cat "$PIDFILE"))"
  exit 0
fi

source "$DOME_ROOT/.venv/bin/activate"
nohup python3 "$DOME_ROOT/akashic/watcher.py" \
  >> "$DOME_ROOT/logs/akashic-watcher.log" 2>&1 &
echo $! > "$PIDFILE"
echo "[akashic] watcher started (pid $!)"

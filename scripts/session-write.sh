#!/usr/bin/env bash
# Hook: SessionEnd — Write session summary to canonical memory/sessions/
# Fires when any agent session ends (Kiro, Claude, Codex)
# Writes to DOME-HUB/memory/sessions/YYYY-MM/
set -euo pipefail

DOME_ROOT="${DOME_ROOT:-$HOME/DOME-HUB}"
AGENT="${1:-kiro}"
TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M UTC')
MONTH=$(date -u '+%Y-%m')
SESSION_DIR="$DOME_ROOT/memory/sessions/$MONTH"

mkdir -p "$SESSION_DIR"

# Only write if there's a summary passed as $2, otherwise skip
if [[ -n "${2:-}" ]]; then
  FILENAME="SESSION_${MONTH}-$(date -u '+%d')_${AGENT^^}.md"
  cat >> "$SESSION_DIR/$FILENAME" <<EOF
# Session: $AGENT — $TIMESTAMP

$2

---

EOF
  echo "[session-hook] ✓ Written to memory/sessions/$MONTH/$FILENAME"
fi

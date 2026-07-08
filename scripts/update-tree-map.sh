#!/usr/bin/env bash
# DSH: structural map auto-update — fractalmap, FILE_TREE.md, holographic tree map.
# Triggered on: git post-commit, post-checkout, session-end hooks (Kiro, Claude, Codex).
set -euo pipefail

DOME_ROOT="${DOME_ROOT:-$HOME/DSH}"
TREE_MAP="$DOME_ROOT/logs/HOLOGRAPHIC_FRACTAL_TREE_MAP_2026-05-14.md"
FRACTALMAP="$DOME_ROOT/.fractalmap"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M %Z')
AGENT="${1:-unknown}"
FORCE="${FRACTALMAP_FORCE:-0}"
LOG="$DOME_ROOT/logs/tree-map-updates.log"

log_msg() {
  echo "[$TIMESTAMP] $*" >> "$LOG"
}

current_sha() {
  git -C "$DOME_ROOT" rev-parse HEAD 2>/dev/null || echo "none"
}

manifest_sha() {
  python3 -c "
import json
from pathlib import Path
p = Path('$FRACTALMAP/manifest.json')
print(json.loads(p.read_text()).get('git_sha', '') if p.is_file() else '')
" 2>/dev/null || echo ""
}

NEEDS_REFRESH=0
CURRENT_SHA=$(current_sha)
MANIFEST_SHA=$(manifest_sha)

if [[ "$FORCE" == "1" ]] || [[ "$CURRENT_SHA" != "$MANIFEST_SHA" ]] || [[ ! -f "$DOME_ROOT/FILE_TREE.md" ]]; then
  NEEDS_REFRESH=1
fi

# 1. Fractalmap (L0, L1, tree-full, manifest) when SHA changed or forced
if [[ "$NEEDS_REFRESH" == "1" ]] && [[ -x "$DOME_ROOT/scripts/fractalmap-generate.sh" ]]; then
  if bash "$DOME_ROOT/scripts/fractalmap-generate.sh" dsh >>"$LOG" 2>&1; then
    log_msg "fractalmap dsh OK (agent=$AGENT sha=${CURRENT_SHA:0:8})"
  else
    log_msg "fractalmap dsh FAILED (agent=$AGENT)"
  fi
fi

# 2. FILE_TREE.md (depth-3 tree + recursive counts) — same trigger
if [[ "$NEEDS_REFRESH" == "1" ]] && [[ -f "$DOME_ROOT/scripts/generate-file-tree.py" ]]; then
  if python3 "$DOME_ROOT/scripts/generate-file-tree.py" --repo dsh >>"$LOG" 2>&1; then
    log_msg "FILE_TREE.md OK (agent=$AGENT)"
  else
    log_msg "FILE_TREE.md FAILED (agent=$AGENT)"
  fi
fi

# 3. Holographic tree map — timestamp + live fractal-stack metrics (always)
if [[ -f "$TREE_MAP" ]]; then
  sed -i '' "s/^\*\*Date:\*\*.*/\*\*Date:\*\* $TIMESTAMP (auto-updated)/" "$TREE_MAP" 2>/dev/null \
    || sed -i "s/^\*\*Date:\*\*.*/\*\*Date:\*\* $TIMESTAMP (auto-updated)/" "$TREE_MAP" 2>/dev/null \
    || true
fi
if [[ -f "$DOME_ROOT/scripts/sync-holographic-metrics.py" ]]; then
  if python3 "$DOME_ROOT/scripts/sync-holographic-metrics.py" >>"$LOG" 2>&1; then
    log_msg "holographic metrics sync OK (agent=$AGENT)"
  else
    log_msg "holographic metrics sync FAILED (agent=$AGENT)"
  fi
fi

# 4. Akashic session-end record (optional — skip if Chroma unavailable)
bash -c "
import_cmd=\"
import sys
sys.path.insert(0, '$DOME_ROOT')
try:
    from akashic.record import write
    write(
        content='Tree maps refreshed by $AGENT at $TIMESTAMP (refresh=$NEEDS_REFRESH).',
        domain='meta',
        depth='event',
        node='$AGENT',
    )
except Exception:
    pass
\"
python3 -c \"\$import_cmd\" >/dev/null 2>&1
exit 0
" >/dev/null 2>&1 || true

log_msg "Tree map hook done by $AGENT (refresh=$NEEDS_REFRESH sha=${CURRENT_SHA:0:8})"

#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SOVEREIGN GATE — Mandatory Protocol Doctrine
# ═══════════════════════════════════════════════════════════════════════════════
# Run AFTER: sessions, workflows, major updates, upgrades, new developments
# Run BEFORE: git commit/push, deployment, handoff to another agent
#
# Usage:
#   bash scripts/sovereign-gate.sh              # full gate (default)
#   bash scripts/sovereign-gate.sh --pre-commit # lightweight pre-commit
#   bash scripts/sovereign-gate.sh --pre-push   # standard pre-push
#   bash scripts/sovereign-gate.sh --pre-deploy # includes build verification
#   bash scripts/sovereign-gate.sh --full       # everything including builds
#
# Exit codes: 0 = GATE OPEN, 1 = GATE BLOCKED
# ═══════════════════════════════════════════════════════════════════════════════

set -uo pipefail
DOME_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TIMESTAMP=$(date +%Y-%m-%dT%H:%M:%S)
mkdir -p "$DOME_ROOT/logs"
GATE_LOG="$DOME_ROOT/logs/sovereign-gate-$(date +%Y%m%d-%H%M%S).log"
MODE="${1:---full}"
PASS=0; FAIL=0; WARN=0

# ── Helpers ───────────────────────────────────────────────────────────────────
ok()      { echo "✅ $1" | tee -a "$GATE_LOG"; ((PASS++)) || true; }
fail()    { echo "❌ $1" | tee -a "$GATE_LOG"; ((FAIL++)) || true; }
warn()    { echo "⚠️  $1" | tee -a "$GATE_LOG"; ((WARN++)) || true; }
section() { echo "" | tee -a "$GATE_LOG"; echo "━━━ $1 ━━━" | tee -a "$GATE_LOG"; }

echo "═══ SOVEREIGN GATE — $MODE — $TIMESTAMP ═══" | tee "$GATE_LOG"

# ── Repo registry ────────────────────────────────────────────────────────────
REPOS=(
  "$DOME_ROOT"
  "$DOME_ROOT/home/projects/dome-console"
)

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1: NODE HEALTH
# ══════════════════════════════════════════════════════════════════════════════
section "PHASE 1: Node Health"
if bash "$DOME_ROOT/scripts/dome-check.sh" >> "$GATE_LOG" 2>&1; then
  ok "dome-check: ALL GREEN"
else
  fail "dome-check: has failures (see log)"
fi

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2: MULTI-REPO GIT STATE
# ══════════════════════════════════════════════════════════════════════════════
section "PHASE 2: Git State"
for repo in "${REPOS[@]}"; do
  [ -d "$repo/.git" ] || continue
  name=$(basename "$repo")
  uncommitted=$(git -C "$repo" status --short 2>/dev/null | wc -l | tr -d ' ')
  if [ "$uncommitted" -gt 0 ]; then
    if [[ "$MODE" == "--pre-commit" ]]; then
      warn "$name: $uncommitted uncommitted (expected pre-commit)"
    else
      fail "$name: $uncommitted uncommitted file(s)"
    fi
  else
    ok "$name: clean"
  fi
done

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 3: CODE QUALITY
# ══════════════════════════════════════════════════════════════════════════════
section "PHASE 3: Code Quality"

# DSH TypeScript
if [ -f "$DOME_ROOT/tsconfig.json" ]; then
  cd "$DOME_ROOT"
  if pnpm typecheck >> "$GATE_LOG" 2>&1; then
    ok "DSH: TypeScript clean"
  else
    fail "DSH: TypeScript errors"
  fi
fi

# Additional project TypeScript checks (auto-discovered)
for proj_dir in "$DSH_ROOT"/home/projects/*/; do
  proj_name="$(basename "$proj_dir")"
  if [ -f "$proj_dir/package.json" ] && [ "$proj_dir" != "$DSH_ROOT/" ]; then
    if cd "$proj_dir" && pnpm check >> "$GATE_LOG" 2>&1; then
      ok "$proj_name: TypeScript clean"
    else
      fail "$proj_name: TypeScript errors"
    fi
  fi
done

# DSH Python
cd "$DOME_ROOT"
if source .venv/bin/activate 2>/dev/null && python3 -c "from agents.core.rag import RAGPipeline; from agents.core.tools import ALL_TOOLS" 2>/dev/null; then
  ok "DSH: Python imports clean"
else
  fail "DSH: Python import errors"
fi

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 4: SECRETS & SECURITY
# ══════════════════════════════════════════════════════════════════════════════
section "PHASE 4: Secrets Safety"
if command -v gitleaks &>/dev/null; then
  for repo in "${REPOS[@]}"; do
    [ -d "$repo/.git" ] || continue
    name=$(basename "$repo")
    gl_args=(git --no-banner .)
    [ -f "$repo/.gitleaks.toml" ] && gl_args+=(--config "$repo/.gitleaks.toml")
    if (cd "$repo" && gitleaks "${gl_args[@]}") >> "$GATE_LOG" 2>&1; then
      ok "$name: no secrets leaked"
    else
      fail "$name: GITLEAKS DETECTED SECRETS"
    fi
  done
else
  warn "gitleaks not installed — skipping secret scan"
fi

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 5: INDEX CONSISTENCY
# ══════════════════════════════════════════════════════════════════════════════
section "PHASE 5: Index Consistency"
INDEXES=(
  "$DOME_ROOT/INDEX.md"
  "$DOME_ROOT/AGENTS.md"
  "$DOME_ROOT/kb/skills/INDEX.md"
  "$DOME_ROOT/MANUAL.md"
  "$DOME_ROOT/PROTOCOLS.md"
)
for idx in "${INDEXES[@]}"; do
  if [ -f "$idx" ]; then
    file_mtime=$(stat -c "%Y" "$idx" 2>/dev/null || /usr/bin/stat -f "%m" "$idx" 2>/dev/null || echo 0)
    age=$(( ($(date +%s) - file_mtime) / 86400 ))
    if [ "$age" -gt 14 ]; then
      warn "$(basename "$idx"): stale ($age days)"
    else
      ok "$(basename "$idx"): fresh ($age days)"
    fi
  else
    fail "$(basename "$idx"): MISSING"
  fi
done

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 6: LAVA CROSS-CHECK (conditional)
# ══════════════════════════════════════════════════════════════════════════════
section "PHASE 6: LAVA Integrity"
LAVA_DIR="$TC/scripts"
if [ -d "$LAVA_DIR" ]; then
  lava_changed=$(git -C "$TC" diff --name-only HEAD~1 2>/dev/null | grep -c "lava-" || true)
  if [ "$lava_changed" -gt 0 ]; then
    lava_errors=0
    for f in "$LAVA_DIR"/lava-*.py; do
      [ -f "$f" ] || continue
      if ! python3 -m py_compile "$f" >> "$GATE_LOG" 2>&1; then
        fail "LAVA syntax: $(basename "$f")"
        ((lava_errors++)) || true
      fi
    done
    [ "$lava_errors" -eq 0 ] && ok "LAVA: all scripts compile"
  else
    ok "LAVA: no changes (skip)"
  fi
else
  ok "LAVA: not present (skip)"
fi

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 7: BUILD VERIFICATION (pre-deploy / full only)
# ══════════════════════════════════════════════════════════════════════════════
if [[ "$MODE" == "--pre-deploy" || "$MODE" == "--full" ]]; then
  section "PHASE 7: Build Verification"

  # Build verification for discovered projects
  for proj_dir in "$DSH_ROOT"/home/projects/*/; do
    proj_name="$(basename "$proj_dir")"
    if [ -f "$proj_dir/package.json" ]; then
      if cd "$proj_dir" && pnpm build >> "$GATE_LOG" 2>&1; then
        ok "$proj_name: build clean"
      else
        fail "$proj_name: build failed"
      fi
    fi
  done
else
  section "PHASE 7: Build Verification (skipped — mode: $MODE)"
  ok "Build skipped for $MODE"
fi

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 8: KB & DATA INTEGRITY
# ══════════════════════════════════════════════════════════════════════════════
section "PHASE 8: Knowledge Base & Data"
cd "$DOME_ROOT"

[ -f "$DOME_ROOT/db/dome.db" ] && ok "SQLite: present" || fail "SQLite: MISSING"

if python3 -c "
import sys; sys.path.insert(0,'$DOME_ROOT')
from agents.core.memory.vector import VectorMemory
vm = VectorMemory('dome-kb')
c = vm.count()
assert c > 0, f'empty: {c}'
" >> "$GATE_LOG" 2>&1; then
  ok "ChromaDB: populated"
else
  warn "ChromaDB: empty or unreachable"
fi

# ══════════════════════════════════════════════════════════════════════════════
# VERDICT
# ══════════════════════════════════════════════════════════════════════════════
echo "" | tee -a "$GATE_LOG"
echo "═══════════════════════════════════════════════════" | tee -a "$GATE_LOG"
echo "  SOVEREIGN GATE — $MODE" | tee -a "$GATE_LOG"
echo "  ✅ Passed:   $PASS" | tee -a "$GATE_LOG"
echo "  ⚠️  Warnings: $WARN" | tee -a "$GATE_LOG"
echo "  ❌ Failed:   $FAIL" | tee -a "$GATE_LOG"
echo "═══════════════════════════════════════════════════" | tee -a "$GATE_LOG"

if [ "$FAIL" -eq 0 ]; then
  echo "  🟢 GATE: OPEN — safe to commit/push/deploy" | tee -a "$GATE_LOG"
  exit 0
else
  echo "  🔴 GATE: BLOCKED — $FAIL issue(s) must be resolved" | tee -a "$GATE_LOG"
  echo "  Log: $GATE_LOG" | tee -a "$GATE_LOG"
  exit 1
fi

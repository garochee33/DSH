#!/bin/bash
# DOME-HUB Protocol Enforcer
# Runs all core checks and auto-fixes what it can
# Usage: bash scripts/dome-check.sh

eval "$(/opt/homebrew/bin/brew shellenv)"
DOME_ROOT="${DOME_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
LOG="$DOME_ROOT/logs/dome-check.log"
PASS=0; FAIL=0; FIXED=0

log()   { echo "$1" | tee -a "$LOG"; }
ok()    { log "✅ $1"; PASS=$((PASS+1)); return 0; }
fail()  { log "❌ $1"; FAIL=$((FAIL+1)); return 0; }
fixed() { log "🔧 $1"; FIXED=$((FIXED+1)); return 0; }

log ""
log "=== DOME-HUB PROTOCOL CHECK === $(date)"

# ── 1. Security ───────────────────────────────────────────────────────────────
log "--- Security ---"

FW_STATE=$(/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>/dev/null)
if echo "$FW_STATE" | grep -qE "enabled|blocking"; then ok "Firewall ON"; else fail "Firewall OFF — enable in System Settings"; fi

FW_STEALTH=$(/usr/libexec/ApplicationFirewall/socketfilterfw --getstealthmode 2>/dev/null)
if echo "$FW_STEALTH" | grep -q "on"; then ok "Stealth mode ON"; else fail "Stealth mode OFF"; fi

fdesetup status 2>/dev/null | grep -q "On" && ok "FileVault ON" || fail "FileVault OFF — enable in System Settings"

csrutil status 2>/dev/null | grep -q "enabled" && ok "SIP enabled" || fail "SIP disabled — critical"

defaults read com.apple.screensaver askForPassword 2>/dev/null | grep -q "1" && ok "Screen lock ON" || {
  defaults write com.apple.screensaver askForPassword -int 1
  defaults write com.apple.screensaver askForPasswordDelay -int 0
  fixed "Screen lock enabled"
}

# GPG key is optional — DOME-HUB supports both GPG+pass and macOS Keychain for secrets.
# If you use Keychain (the sovereign default), this check passes when the entry exists.
if security find-generic-password -s "dome/HUB_API_SECRET" -w >/dev/null 2>&1; then
  ok "Secrets in Keychain"
elif /opt/homebrew/bin/gpg --list-secret-keys 2>/dev/null | grep -q "sec"; then
  ok "GPG key present (pass-based secrets)"
else
  fail "No secret backend found (Keychain or GPG)"
fi

# Git signing is optional. Only report; never auto-enable (locked key → commits fail).
if [ "$(git -C "$DOME_ROOT" config --global commit.gpgsign 2>/dev/null)" = "true" ]; then
  ok "Git signing ON"
else
  ok "Git signing OFF (user choice)"
fi

# ── 2. Network ────────────────────────────────────────────────────────────────
log "--- Network ---"

DNS=$(scutil --dns 2>/dev/null | grep nameserver | head -1 | awk '{print $3}')
[[ "$DNS" == "127.0.0.1" ]] && ok "DNS private (dnscrypt-proxy)" || {
  sudo networksetup -setdnsservers Wi-Fi 127.0.0.1 2>/dev/null
  fixed "DNS switched to 127.0.0.1"
}

if pgrep -x dnscrypt-proxy >/dev/null 2>&1; then ok "dnscrypt-proxy running"; else fail "dnscrypt-proxy not running — run: sudo brew services start dnscrypt-proxy"; fi

# ── 3. Daemons ────────────────────────────────────────────────────────────────
log "--- Daemons ---"

UNAUTHORIZED=0
for plist in ~/Library/LaunchAgents/*.plist; do
  [ -f "$plist" ] || continue
  name=$(basename "$plist" .plist)
  case "$name" in
    homebrew.*|com.apple.*|com.openssh.*|org.cups.*) ;;
    *)
      launchctl unload -w "$plist" 2>/dev/null; rm -f "$plist"
      fixed "Removed unauthorized agent: $name"
      ((UNAUTHORIZED++))
      ;;
  esac
done
[ $UNAUTHORIZED -eq 0 ] && ok "No unauthorized launch agents"

# ── 4. Code quality ───────────────────────────────────────────────────────────
log "--- Code Quality ---"

cd "$DOME_ROOT" && source .venv/bin/activate 2>/dev/null
python3 -c "from agents.core.rag import RAGPipeline; from agents.core.tools import ALL_TOOLS" 2>/dev/null && \
  ok "Python imports clean" || fail "Python import errors — run: source .venv/bin/activate && python3 -c 'from agents.core.agent import Agent'"

export PNPM_HOME="$HOME/Library/pnpm"; export PATH="$PNPM_HOME:$PATH"
pnpm typecheck 2>/dev/null | grep -q "error TS" && fail "TypeScript errors" || ok "TypeScript clean"

# ── 5. Data integrity ─────────────────────────────────────────────────────────
log "--- Data Integrity ---"

[ -f "$DOME_ROOT/db/dome.db" ] && ok "SQLite DB present" || fail "SQLite DB missing"

python3 -c "
import sys; sys.path.insert(0,'$DOME_ROOT')
from agents.core.memory.vector import VectorMemory
vm = VectorMemory('dome-kb')
count = vm.count()
print(count)
" 2>/dev/null | grep -q "^[0-9]" && ok "ChromaDB populated" || fail "ChromaDB empty — run: pnpm ingest"

# ── 6. Git ────────────────────────────────────────────────────────────────────
log "--- Git ---"

UNCOMMITTED=$(git -C "$DOME_ROOT" status --short 2>/dev/null | wc -l | tr -d ' ')
if [ "$UNCOMMITTED" -gt 0 ]; then
  # Report only. Auto-commit/push removed — destructive and bypasses review.
  fail "$UNCOMMITTED uncommitted change(s) — review with: git -C \"$DOME_ROOT\" status"
else
  ok "Git clean"
fi

BEHIND=$(git -C "$DOME_ROOT" fetch --dry-run 2>&1 | wc -l | tr -d ' ')
if [ "$BEHIND" -eq 0 ]; then
  ok "Git up to date"
else
  fail "Remote has updates — pull with: git -C \"$DOME_ROOT\" pull"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
log ""
log "=== SUMMARY ==="
log "✅ Passed:  $PASS"
log "🔧 Fixed:   $FIXED"
log "❌ Failed:  $FAIL"
log ""
[ $FAIL -eq 0 ] && log "🟢 DOME-HUB PROTOCOLS: ALL GREEN" || log "🔴 DOME-HUB PROTOCOLS: $FAIL ISSUE(S) REQUIRE MANUAL ACTION"
log "Log: $LOG"

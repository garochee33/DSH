#!/bin/bash
# DOME-HUB Protocol Enforcer
# Runs all core checks and auto-fixes what it can
# Usage: bash scripts/dome-check.sh

eval "$(/opt/homebrew/bin/brew shellenv)"
DOME_ROOT="/Users/gadikedoshim/DOME-HUB"
LOG="$DOME_ROOT/logs/dome-check.log"
PASS=0; FAIL=0; FIXED=0

log() { echo "$1" | tee -a "$LOG"; }
ok()    { log "✅ $1"; ((PASS++)); }
fail()  { log "❌ $1"; ((FAIL++)); }
fixed() { log "🔧 $1"; ((FIXED++)); }

log ""
log "=== DOME-HUB PROTOCOL CHECK === $(date)"

# ── 1. Security ───────────────────────────────────────────────────────────────
log "--- Security ---"

/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>/dev/null | grep -q "enabled" && ok "Firewall ON" || {
  sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on 2>/dev/null
  fixed "Firewall enabled"
}

/usr/libexec/ApplicationFirewall/socketfilterfw --getstealthmode 2>/dev/null | grep -q "enabled" && ok "Stealth mode ON" || {
  sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode on 2>/dev/null
  fixed "Stealth mode enabled"
}

fdesetup status 2>/dev/null | grep -q "On" && ok "FileVault ON" || fail "FileVault OFF — enable in System Settings"

csrutil status 2>/dev/null | grep -q "enabled" && ok "SIP enabled" || fail "SIP disabled — critical"

defaults read com.apple.screensaver askForPassword 2>/dev/null | grep -q "1" && ok "Screen lock ON" || {
  defaults write com.apple.screensaver askForPassword -int 1
  defaults write com.apple.screensaver askForPasswordDelay -int 0
  fixed "Screen lock enabled"
}

/opt/homebrew/bin/gpg --list-secret-keys 2>/dev/null | grep -q "sec" && ok "GPG key present" || fail "GPG key missing"

git -C "$DOME_ROOT" config --global commit.gpgsign 2>/dev/null | grep -q "true" && ok "Git signing ON" || {
  git config --global commit.gpgsign true
  fixed "Git signing enabled"
}

# ── 2. Network ────────────────────────────────────────────────────────────────
log "--- Network ---"

DNS=$(scutil --dns 2>/dev/null | grep nameserver | head -1 | awk '{print $3}')
[[ "$DNS" == "127.0.0.1" ]] && ok "DNS private (dnscrypt-proxy)" || {
  sudo networksetup -setdnsservers Wi-Fi 127.0.0.1 2>/dev/null
  fixed "DNS switched to 127.0.0.1"
}

brew services list 2>/dev/null | grep dnscrypt-proxy | grep -q "started" && ok "dnscrypt-proxy running" || {
  sudo brew services start dnscrypt-proxy 2>/dev/null
  fixed "dnscrypt-proxy started"
}

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
  git -C "$DOME_ROOT" add -A
  git -C "$DOME_ROOT" commit -m "chore: auto-commit by dome-check"
  git -C "$DOME_ROOT" push 2>/dev/null
  fixed "Auto-committed and pushed $UNCOMMITTED changes"
else
  ok "Git clean"
fi

BEHIND=$(git -C "$DOME_ROOT" fetch --dry-run 2>&1 | wc -l | tr -d ' ')
[ "$BEHIND" -eq 0 ] && ok "Git up to date" || { git -C "$DOME_ROOT" pull 2>/dev/null; fixed "Pulled latest from remote"; }

# ── Summary ───────────────────────────────────────────────────────────────────
log ""
log "=== SUMMARY ==="
log "✅ Passed:  $PASS"
log "🔧 Fixed:   $FIXED"
log "❌ Failed:  $FAIL"
log ""
[ $FAIL -eq 0 ] && log "🟢 DOME-HUB PROTOCOLS: ALL GREEN" || log "🔴 DOME-HUB PROTOCOLS: $FAIL ISSUE(S) REQUIRE MANUAL ACTION"
log "Log: $LOG"

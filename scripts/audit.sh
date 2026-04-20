#!/bin/bash
# DOME-HUB Security Audit Script
# Run anytime to check security posture
DOME_ROOT="${DOME_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
echo "=== DOME-HUB SECURITY AUDIT ==="
echo "Date: $(date)"
echo "Root: $DOME_ROOT"
echo ""
check() {
  local label=$1 cmd=$2 pass=$3
  result=$(eval "$cmd" 2>/dev/null)
  if echo "$result" | grep -q "$pass"; then
    echo "✅ $label"
  else
    echo "❌ $label — $result"
  fi
}
echo "--- System ---"
check "FileVault ON"       "fdesetup status"                          "FileVault is On"
check "SIP enabled"        "csrutil status"                           "enabled"
check "Gatekeeper ON"      "spctl --status"                           "enabled"
check "Firewall ON"        "/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate" "enabled"
/opt/homebrew/bin/gpg --list-secret-keys 2>/dev/null | grep -q "sec" && echo "✅ GPG key present" || echo "⚠️  No GPG key"
check "Screen lock ON"     "/usr/bin/defaults read com.apple.screensaver askForPassword" "1"
echo ""
echo "--- Network ---"
DNS=$(scutil --dns | grep nameserver | head -1 | awk '{print $3}')
if [[ "$DNS" == "127.0.0.1" ]]; then
  echo "✅ DNS → local (dnscrypt-proxy)"
else
  echo "⚠️  DNS → $DNS (not private)"
fi
echo ""
echo "--- Secrets ---"
if [ -d "$HOME/.password-store" ]; then
  echo "✅ pass store initialized"
else
  echo "⚠️  pass store not initialized — run: pass init <gpg-id>"
fi
echo ""
echo "--- Git ---"
SIGNING=$(git config --global commit.gpgsign 2>/dev/null)
if [ "$SIGNING" = "true" ]; then
  echo "✅ Git commit signing ON"
else
  echo "⚠️  Git commit signing OFF"
fi
echo ""
echo "--- DOME-HUB ---"
[ -f "$DOME_ROOT/.env" ] && \
  echo "⚠️  .env file exists — ensure it's in .gitignore" || \
  echo "✅ No exposed .env"
grep -q "^.env" "$DOME_ROOT/.gitignore" 2>/dev/null && \
  echo "✅ .env in .gitignore" || echo "❌ .env NOT in .gitignore"
echo ""
echo "=== END AUDIT ==="

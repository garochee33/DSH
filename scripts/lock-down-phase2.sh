#!/bin/bash
# DOME-HUB lock-down phase 2 — pin DNS, kill rapportd for good, final verification
set -u
echo "==> DOME-HUB LOCK-DOWN PHASE 2"

sudo -v || { echo "sudo failed"; exit 1; }
( while true; do sudo -n true; sleep 30; kill -0 $$ 2>/dev/null || exit; done ) &
KEEPER=$!
trap 'kill $KEEPER 2>/dev/null || true' EXIT

echo "--> Pinning DNS to 127.0.0.1 on all enabled network services"
# Loop every enabled service (skip the header line and the * disabled prefix)
while IFS= read -r svc; do
  [ -z "$svc" ] && continue
  [[ "$svc" == An\ asterisk* ]] && continue
  [[ "$svc" == \** ]] && continue
  sudo networksetup -setdnsservers "$svc" 127.0.0.1 2>/dev/null && \
    echo "  DNS pinned: $svc"
done < <(networksetup -listallnetworkservices)

# Flush DNS cache
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder 2>/dev/null || true
echo "  DNS cache flushed"

echo "--> Disabling rapportd permanently"
sudo launchctl disable system/com.apple.rapportd 2>/dev/null || true
sudo launchctl bootout system/com.apple.rapportd 2>/dev/null || true
defaults write com.apple.rapport enabled -bool false 2>/dev/null || true
# Kill any running instances
sudo pkill -9 rapportd 2>/dev/null || true
echo "  rapportd disabled (will not respawn until re-enabled)"

echo "--> Disabling additional Apple phone-home agents"
# Siri
launchctl unload -w /System/Library/LaunchAgents/com.apple.Siri.agent.plist 2>/dev/null || true
defaults write com.apple.assistant.support "Siri Data Sharing Opt-In Status" -int 2
# Analytics / diagnostics submission
sudo defaults write /Library/Application\ Support/CrashReporter/DiagnosticMessagesHistory.plist AutoSubmit -bool false 2>/dev/null || true
defaults write com.apple.SubmitDiagInfo AutoSubmit -bool false
defaults write com.apple.SubmitDiagInfo AutoSubmitVersion -int 4

echo ""
echo "==> VERIFICATION"
echo "-- DNS resolvers (should all be 127.0.0.1) --"
scutil --dns | grep nameserver | head -5
echo ""
echo "-- dnscrypt-proxy health --"
dig @127.0.0.1 resolver.dnscrypt.info +short +time=3 +tries=1 TXT 2>&1 | head -3
echo ""
echo "-- rapportd status --"
pgrep -x rapportd >/dev/null && echo "  ⚠️  still running" || echo "  ✓ not running"
echo ""
echo "-- Offending plists remaining --"
(ls /Library/LaunchDaemons/ 2>/dev/null; ls /Library/LaunchAgents/ 2>/dev/null; ls ~/Library/LaunchAgents/ 2>/dev/null) \
  | grep -iE "google|zoom|adobe|amazon|openai|codewhisperer|dropbox|keystone|pioneerdj" \
  || echo "  ✓ NONE"
echo ""
echo "==> PHASE 2 COMPLETE"

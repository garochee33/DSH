#!/bin/bash
# DOME-HUB lock-down phase 4 — close the remaining gaps:
#   - IPv6 DNS pinned to disabled (force IPv4-over-dnscrypt only)
#   - Apple system telemetry / diagnostic submission fully off
#   - Spotlight online / Safari safe-browsing / Location services off
#   - pf outbound rules as belt-and-suspenders to LuLu
#
# Non-destructive: does not delete user files or apps. Changes are config-only.

set -u
echo "==> DOME-HUB LOCK-DOWN PHASE 4"

sudo -v || { echo "sudo failed"; exit 1; }
( while true; do sudo -n true; sleep 30; kill -0 $$ 2>/dev/null || exit; done ) &
KEEPER=$!
trap 'kill $KEEPER 2>/dev/null || true' EXIT

echo "--> Close IPv6 DNS leak (force IPv6 DNS to ::1 so queries fail over to IPv4→dnscrypt)"
while IFS= read -r svc; do
  [ -z "$svc" ] && continue
  [[ "$svc" == An\ asterisk* ]] && continue
  [[ "$svc" == \** ]] && continue
  sudo networksetup -setv6off "$svc" 2>/dev/null && echo "  IPv6 off: $svc"
done < <(networksetup -listallnetworkservices)

echo "--> Apple diagnostic / analytics submission off (all scopes)"
sudo defaults write /Library/Application\ Support/CrashReporter/DiagnosticMessagesHistory.plist AutoSubmit -bool false
sudo defaults write /Library/Application\ Support/CrashReporter/DiagnosticMessagesHistory.plist AutoSubmitVersion -int 4
sudo defaults write /Library/Application\ Support/CrashReporter/DiagnosticMessagesHistory.plist ThirdPartyDataSubmit -bool false
sudo defaults write /Library/Application\ Support/CrashReporter/DiagnosticMessagesHistory.plist ThirdPartyDataSubmitVersion -int 4
defaults write com.apple.SubmitDiagInfo AutoSubmit -bool false
defaults write com.apple.SubmitDiagInfo AutoSubmitVersion -int 4
defaults write com.apple.CrashReporter DialogType none
defaults write com.apple.CrashReporter UseUNC -int 1
echo "  diagnostic submission: off"

echo "--> Spotlight: disable web suggestions + Siri suggestions"
defaults write com.apple.spotlight orderedItems -array \
  '{"enabled"=1;"name"="APPLICATIONS";}' \
  '{"enabled"=1;"name"="SYSTEM_PREFS";}' \
  '{"enabled"=1;"name"="DIRECTORIES";}' \
  '{"enabled"=1;"name"="PDF";}' \
  '{"enabled"=1;"name"="DOCUMENTS";}' \
  '{"enabled"=0;"name"="MENU_WEBSEARCH";}' \
  '{"enabled"=0;"name"="MENU_SPOTLIGHT_SUGGESTIONS";}' \
  '{"enabled"=0;"name"="BOOKMARKS";}'
defaults write com.apple.assistant.support "Search Queries Data Sharing Status" -int 2
echo "  Spotlight: web + Siri suggestions off"

echo "--> Safari: disable Safe Browsing phone-home + Suggestions + preloading"
defaults write com.apple.Safari SafeBrowsing -bool false 2>/dev/null || true
defaults write com.apple.Safari UniversalSearchEnabled -bool false 2>/dev/null || true
defaults write com.apple.Safari SuppressSearchSuggestions -bool true 2>/dev/null || true
defaults write com.apple.Safari WebsiteSpecificSearchEnabled -bool false 2>/dev/null || true
defaults write com.apple.Safari PreloadTopHit -bool false 2>/dev/null || true

echo "--> Location Services off (global)"
sudo defaults write /var/db/locationd/Library/Preferences/ByHost/com.apple.locationd LocationServicesEnabled -bool false 2>/dev/null || true

echo "--> Apple Internet Connect / Weather / Stocks: disable analytics"
defaults write com.apple.weather.widget "WeatherWidgetAnalyticsEnabled" -bool false 2>/dev/null || true
defaults write com.apple.stockwidget "StockWidgetAnalyticsEnabled" -bool false 2>/dev/null || true

echo "--> pf: ensure enabled, block outbound to GoogleUpdater / known telemetry IPs"
# Anchor file for DOME-HUB
PF_ANCHOR=/etc/pf.anchors/com.dome-hub
sudo tee "$PF_ANCHOR" >/dev/null <<'EOF'
# DOME-HUB pf anchor — drop outbound to known telemetry endpoints.
# Baseline only. For per-binary blocking use LuLu (LuLu.app).
block drop out quick proto tcp from any to any port { 5228 5229 5230 }
block drop out quick proto udp from any to any port 5353
EOF
if ! grep -q "com.dome-hub" /etc/pf.conf 2>/dev/null; then
  sudo cp /etc/pf.conf /etc/pf.conf.pre-dome.bak
  echo 'anchor "com.dome-hub"' | sudo tee -a /etc/pf.conf >/dev/null
  echo 'load anchor "com.dome-hub" from "/etc/pf.anchors/com.dome-hub"' | sudo tee -a /etc/pf.conf >/dev/null
  echo "  pf anchor wired into /etc/pf.conf"
fi
sudo pfctl -e 2>&1 | tail -1 || true
sudo pfctl -f /etc/pf.conf 2>&1 | tail -3 || true

echo "--> Restart mDNSResponder to flush"
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder 2>/dev/null || true

echo ""
echo "==> VERIFICATION"
echo "-- IPv6 state --"
networksetup -getinfo "Wi-Fi" 2>/dev/null | grep -E "IPv6|IPv4" | head -4
echo "-- Diagnostic submission --"
defaults read com.apple.SubmitDiagInfo AutoSubmit 2>/dev/null
echo "-- pf status --"
sudo pfctl -si 2>&1 | head -3
echo ""
echo "==> PHASE 4 COMPLETE"
echo ""
echo "MANUAL STEPS REMAINING (GUI-only, cannot be scripted):"
echo "  1. Open /Applications/LuLu.app, complete the setup wizard"
echo "     — approve the System Extension in 'Privacy & Security'"
echo "     — set default action: 'block' for unknown outbound"
echo "  2. System Settings → Apple Account → iCloud → turn off Notes / Mail if not needed"
echo "  3. System Settings → Privacy & Security → Analytics & Improvements → all OFF"
echo "  4. Quit Codex.app and ChatGPT.app; remove from Login Items"

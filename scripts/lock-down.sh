#!/bin/bash
# DOME-HUB lock-down — kills all system-level phone-home daemons/agents,
# starts dnscrypt-proxy, pins DNS to 127.0.0.1, disables rapportd & crash submission,
# and terminates live offending processes. Run interactively: it will prompt for sudo once.

set -u
echo "==> DOME-HUB LOCK-DOWN"

sudo -v || { echo "sudo failed"; exit 1; }
# Keep sudo alive for the duration
( while true; do sudo -n true; sleep 30; kill -0 $$ 2>/dev/null || exit; done ) &
SUDO_KEEPER=$!
trap 'kill $SUDO_KEEPER 2>/dev/null || true' EXIT

SYSTEM_DAEMONS=(
  /Library/LaunchDaemons/us.zoom.ZoomDaemon.plist
  /Library/LaunchDaemons/com.adobe.acc.installer.v2.plist
  /Library/LaunchDaemons/com.adobe.agsservice.plist
  /Library/LaunchDaemons/com.google.keystone.daemon.plist
)
SYSTEM_AGENTS=(
  /Library/LaunchAgents/com.adobe.AdobeCreativeCloud.plist
  /Library/LaunchAgents/com.adobe.AdobeDesktopService.plist
  /Library/LaunchAgents/com.adobe.ccxprocess.plist
  /Library/LaunchAgents/com.adobe.GC.Invoker-1.0.plist
  /Library/LaunchAgents/com.google.keystone.agent.plist
  /Library/LaunchAgents/com.google.keystone.xpcservice.plist
  /Library/LaunchAgents/us.zoom.updater.login.check.plist
  /Library/LaunchAgents/us.zoom.updater.plist
  /Library/LaunchAgents/com.pioneerdj.FwUpdateManagerd.plist
)

echo "--> Removing system LaunchDaemons"
for p in "${SYSTEM_DAEMONS[@]}"; do
  if [ -f "$p" ]; then
    sudo launchctl bootout system "$p" 2>/dev/null || true
    sudo launchctl unload -w "$p" 2>/dev/null || true
    sudo rm -f "$p" && echo "  REMOVED: $p"
  fi
done

echo "--> Removing system LaunchAgents"
for p in "${SYSTEM_AGENTS[@]}"; do
  if [ -f "$p" ]; then
    sudo launchctl bootout gui/"$(id -u)" "$p" 2>/dev/null || true
    sudo launchctl unload -w "$p" 2>/dev/null || true
    sudo rm -f "$p" && echo "  REMOVED: $p"
  fi
done

echo "--> Terminating live phone-home processes"
for pat in "GoogleSoftwareUpdateAgent" "GoogleUpdater" "keystone" \
           "Adobe Desktop Service" "Creative Cloud" "ccxprocess" "AGSService" \
           "Zoom" "zoomd" "PrivilegedHelper.*zoom" \
           "pioneerdj" "FwUpdateManager" \
           "codex" "rapportd" "OpenClaw"; do
  pkill -f "$pat" 2>/dev/null && echo "  killed: $pat"
  sudo pkill -f "$pat" 2>/dev/null || true
done

echo "--> Disabling rapportd (AirDrop/Handoff network daemon)"
sudo launchctl disable system/com.apple.rapportd 2>/dev/null || true
sudo defaults write /Library/Preferences/com.apple.rapport.plist Enabled -bool false 2>/dev/null || true
defaults write com.apple.rapport enabled -bool false 2>/dev/null || true

echo "--> Disabling crash report / diagnostic submission"
sudo defaults write /Library/Application\ Support/CrashReporter/DiagnosticMessagesHistory.plist AutoSubmit -bool false 2>/dev/null || true
defaults write com.apple.SubmitDiagInfo AutoSubmit -bool false 2>/dev/null || true
defaults write com.apple.CrashReporter DialogType none 2>/dev/null || true

echo "--> Starting dnscrypt-proxy"
sudo brew services start dnscrypt-proxy 2>&1 | tail -5

echo "--> Pinning DNS to 127.0.0.1 on active network services"
for svc in "Wi-Fi" "Ethernet" "USB 10/100/1000 LAN" "Thunderbolt Bridge"; do
  networksetup -getnetworkservices 2>/dev/null | grep -q "^$svc$" && \
    sudo networksetup -setdnsservers "$svc" 127.0.0.1 && \
    echo "  DNS pinned: $svc"
done

echo "--> Verification"
echo "-- System LaunchDaemons remaining (offenders) --"
ls /Library/LaunchDaemons/ 2>/dev/null | grep -iE "google|zoom|adobe|amazon|openai|codewhisperer|dropbox|keystone|pioneerdj" || echo "  ✓ NONE"
echo "-- System LaunchAgents remaining (offenders) --"
ls /Library/LaunchAgents/ 2>/dev/null | grep -iE "google|zoom|adobe|amazon|openai|codewhisperer|dropbox|keystone|pioneerdj" || echo "  ✓ NONE"
echo "-- DNS resolvers --"
scutil --dns | grep nameserver | head -3
echo "-- dnscrypt-proxy --"
brew services list | grep dnscrypt-proxy || echo "  not listed"

echo "==> LOCK-DOWN COMPLETE"

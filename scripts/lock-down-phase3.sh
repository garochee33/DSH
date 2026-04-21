#!/bin/bash
# DOME-HUB lock-down phase 3 — firewall blocks on SIP-protected / respawning offenders
# rapportd, codex, and atlas helpers can't be unloaded; block them at the Application Firewall.
set -u
echo "==> DOME-HUB LOCK-DOWN PHASE 3 — firewall blocks"

sudo -v || { echo "sudo failed"; exit 1; }
( while true; do sudo -n true; sleep 30; kill -0 $$ 2>/dev/null || exit; done ) &
KEEPER=$!
trap 'kill $KEEPER 2>/dev/null || true' EXIT

FW=/usr/libexec/ApplicationFirewall/socketfilterfw

block_if_exists() {
  local path="$1"
  if [ -e "$path" ]; then
    sudo "$FW" --add "$path" >/dev/null 2>&1 || true
    sudo "$FW" --block "$path" >/dev/null 2>&1 || true
    echo "  blocked: $path"
  fi
}

echo "--> Adding firewall blocks"
# rapportd (Handoff / AirDrop — phones home to iCloud)
block_if_exists /usr/libexec/rapportd

# OpenAI codex CLI
for p in \
  /usr/local/bin/codex \
  /opt/homebrew/bin/codex \
  "$HOME/.codex/bin/codex" \
  "$HOME/.local/bin/codex"; do
  block_if_exists "$p"
done

# OpenAI Atlas (desktop agent)
block_if_exists "/Applications/ChatGPT.app/Contents/MacOS/ChatGPT"
block_if_exists "/Applications/Atlas.app/Contents/MacOS/Atlas"
for app in "/Applications/"*Atlas*.app; do
  [ -d "$app" ] && block_if_exists "$app/Contents/MacOS/$(basename "$app" .app)"
done

# Amazon Q / CodeWhisperer
block_if_exists "/Applications/Amazon Q.app/Contents/MacOS/Amazon Q"
block_if_exists "$HOME/Library/Application Support/amazon-q/codewhisperer"

# Google updater binaries
for p in \
  "/Library/Google/GoogleSoftwareUpdate/GoogleSoftwareUpdate.bundle/Contents/Resources/GoogleSoftwareUpdateAgent.app/Contents/MacOS/GoogleSoftwareUpdateAgent" \
  "/Library/Google/GoogleUpdater/Current/GoogleUpdater.app/Contents/MacOS/GoogleUpdater" \
  "$HOME/Library/Google/GoogleSoftwareUpdate/GoogleSoftwareUpdate.bundle/Contents/Resources/GoogleSoftwareUpdateAgent.app/Contents/MacOS/GoogleSoftwareUpdateAgent"; do
  block_if_exists "$p"
done

# Adobe helpers
for p in \
  "/Library/Application Support/Adobe/Adobe Desktop Common/HDBox/Adobe Desktop Service" \
  "/Library/Application Support/Adobe/Adobe Desktop Common/IPCBox/AdobeIPCBroker.app/Contents/MacOS/AdobeIPCBroker" \
  "/Library/Application Support/Adobe/AdobeGCClient/AGSService"; do
  block_if_exists "$p"
done

# Zoom helpers
for p in \
  "/Applications/zoom.us.app/Contents/MacOS/zoom.us" \
  "/Applications/zoom.us.app/Contents/Frameworks/ZoomHelper.app/Contents/MacOS/ZoomHelper"; do
  block_if_exists "$p"
done

sudo "$FW" --setblockall on >/dev/null 2>&1 || true

echo ""
echo "==> VERIFICATION"
echo "-- firewall global --"
sudo "$FW" --getglobalstate
sudo "$FW" --getstealthmode
echo ""
echo "-- blocked apps (sample) --"
sudo "$FW" --listapps 2>/dev/null | grep -E "(rapportd|codex|Atlas|Adobe|Google|zoom)" | head -20
echo ""
echo "==> PHASE 3 COMPLETE"
echo ""
echo "Note: rapportd may still appear in pgrep but its network sockets will be blocked."

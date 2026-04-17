#!/bin/bash
# DOME-HUB Daemon Watchdog
# Monitors LaunchAgents/Daemons and permanently removes unauthorized ones
# Run: bash scripts/daemon-watch.sh (or add to cron)

LOG="$HOME/DOME-HUB/logs/daemon-watch.log"
mkdir -p "$(dirname $LOG)"

APPROVED=(
  "homebrew.mxcl.postgresql"
  "homebrew.mxcl.redis"
  "homebrew.mxcl.dnscrypt-proxy"
  "com.apple."
  "com.openssh."
  "org.cups."
)

is_approved() {
  local name=$1
  for pattern in "${APPROVED[@]}"; do
    [[ "$name" == *"$pattern"* ]] && return 0
  done
  return 1
}

echo "=== DOME-HUB Daemon Watchdog ===" | tee -a "$LOG"
echo "Date: $(date)" | tee -a "$LOG"

# User LaunchAgents — unload + delete
for plist in ~/Library/LaunchAgents/*.plist; do
  [ -f "$plist" ] || continue
  name=$(basename "$plist" .plist)
  if is_approved "$name"; then
    echo "✅ $name"
  else
    echo "⚠️  REMOVED: $name" | tee -a "$LOG"
    launchctl unload -w "$plist" 2>/dev/null || true
    rm -f "$plist"
  fi
done

# System LaunchDaemons — flag + delete plist (takes effect on reboot)
for plist in /Library/LaunchDaemons/*.plist; do
  [ -f "$plist" ] || continue
  name=$(basename "$plist" .plist)
  if is_approved "$name"; then
    echo "✅ $name"
  else
    echo "⚠️  REMOVED (reboot required): $name" | tee -a "$LOG"
    sudo launchctl bootout system "$plist" 2>/dev/null || true
    sudo rm -f "$plist" 2>/dev/null || true
  fi
done

echo "✅ Watchdog complete" | tee -a "$LOG"
echo "Log: $LOG"

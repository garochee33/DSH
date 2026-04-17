#!/bin/bash
# DOME-HUB Hardware Optimization Script
# Tunes CPU, GPU, memory for AI/dev workloads on Apple M3 Pro

echo "==> DOME-HUB Hardware Optimization"

# Disable App Nap (prevents background processes from being throttled)
defaults write NSGlobalDomain NSAppSleepDisabled -bool YES

# Disable sudden motion sensor (not needed on SSD)
sudo pmset -a sms 0

# Performance power mode (plugged in)
sudo pmset -c powernap 0       # disable power nap on AC
sudo pmset -c proximitywake 0  # disable wake on network access
sudo pmset -c tcpkeepalive 1   # keep TCP alive for dev servers

# Memory optimization — disable swap compression delay
sudo sysctl -w vm.compressor_mode=4 2>/dev/null || true

# Increase max open files (critical for dev servers, DBs, AI)
sudo launchctl limit maxfiles 65536 200000
ulimit -n 65536

# Increase max processes
sudo launchctl limit maxproc 2048 4096

# GPU: ensure Metal performance mode
sudo defaults write /Library/Preferences/com.apple.CoreDisplay useMetal -bool true 2>/dev/null || true

# Disable Spotlight indexing on DOME-HUB (reduces I/O during builds)
sudo mdutil -i off /Users/gadikedoshim/DOME-HUB 2>/dev/null && echo "Spotlight off for DOME-HUB"

# Prioritize DOME-HUB processes
sudo renice -n -5 -p $$ 2>/dev/null || true

echo "==> Optimization applied. Current limits:"
ulimit -n
launchctl limit maxfiles

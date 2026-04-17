#!/bin/bash
# DOME-HUB Security Hardening Script
# Run with sudo for full effect

echo "==> DOME-HUB Security Hardening"

# Firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setloggingmode on
echo "✓ Firewall enabled + stealth mode on"

# Disable SMB public folder sharing
sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.smbd.plist 2>/dev/null || true
echo "✓ SMB sharing disabled"

# Screen lock
defaults write com.apple.screensaver askForPassword -int 1
defaults write com.apple.screensaver askForPasswordDelay -int 0
echo "✓ Screen lock on wake enabled"

# Disable remote login (SSH) if not needed
# sudo systemsetup -setremotelogin off

# Disable IR receiver
sudo defaults write /Library/Preferences/com.apple.driver.AppleIRController DeviceEnabled -bool false 2>/dev/null || true

# Disable Bluetooth when not in use (manual — uncomment if desired)
# sudo defaults write /Library/Preferences/com.apple.Bluetooth ControllerPowerState -int 0

# Require password immediately after sleep
sudo pmset -a destroyfvkeyonstandby 1
sudo pmset -a hibernatemode 25

# Disable crash reporter (prevents data leakage)
defaults write com.apple.CrashReporter DialogType none

# Disable Siri data collection
defaults write com.apple.assistant.support "Siri Data Sharing Opt-In Status" -int 2

# Safari privacy (if used)
defaults write com.apple.Safari SendDoNotTrackHTTPHeader -bool true
defaults write com.apple.Safari WebKitPreferences.privateClickMeasurementEnabled -bool false

echo "==> Security hardening complete"
echo "    Reboot recommended for all changes to take effect"

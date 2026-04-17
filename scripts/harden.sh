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

# Siri
defaults write com.apple.assistant.support "Siri Data Sharing Opt-In Status" -int 2
defaults write com.apple.Siri StatusMenuVisible -bool false
launchctl unload -w /System/Library/LaunchAgents/com.apple.Siri.agent.plist 2>/dev/null || true

# Spotlight (local only, no web/Siri suggestions)
defaults write com.apple.spotlight orderedItems -array \
  '{"enabled"=1;"name"="APPLICATIONS";}' '{"enabled"=1;"name"="SYSTEM_PREFS";}' \
  '{"enabled"=1;"name"="DIRECTORIES";}' '{"enabled"=1;"name"="PDF";}' \
  '{"enabled"=1;"name"="DOCUMENTS";}' '{"enabled"=0;"name"="MENU_WEBSEARCH";}' \
  '{"enabled"=0;"name"="MENU_SPOTLIGHT_SUGGESTIONS";}'

# AirPlay receiver (closes ports 5000/7000)
sudo defaults write /Library/Preferences/com.apple.controlcenter AirplayRecieverEnabled -bool false 2>/dev/null || true

# Crash reporter / analytics
defaults write com.apple.CrashReporter DialogType none
defaults write com.apple.SubmitDiagInfo AutoSubmit -bool false 2>/dev/null || true

# Chrome privacy
defaults write com.google.Chrome BackgroundModeEnabled -bool false
defaults write com.google.Chrome MetricsReportingEnabled -bool false
defaults write com.google.Chrome SendUsageStatistics -bool false
defaults write com.google.Chrome SearchSuggestEnabled -bool false
defaults write com.google.Chrome SafeBrowsingEnabled -bool false
defaults write com.google.Chrome SyncDisabled -bool true
defaults write com.google.Chrome UrlKeyedAnonymizedDataCollectionEnabled -bool false

# Terminal security
defaults write com.apple.Terminal SecureKeyboardEntry -bool true

# Dock performance
defaults write com.apple.dock autohide -bool true
defaults write com.apple.dock autohide-delay -float 0
defaults write com.apple.dock launchanim -bool false

# Finder
defaults write NSGlobalDomain NSDocumentSaveNewDocumentsToCloud -bool false

# Restart services
killall Dock 2>/dev/null || true
killall Finder 2>/dev/null || true
killall SystemUIServer 2>/dev/null || true

echo "==> Security hardening complete"
echo "    Reboot recommended for all changes to take effect"

# ── System-wide (beyond DOME-HUB) ────────────────────────────────────────────

# Close AirPlay ports 5000/7000
sudo defaults write /Library/Preferences/com.apple.controlcenter AirplayRecieverEnabled -bool false 2>/dev/null || true

# Disable Google auto-updater (phones home constantly)
launchctl unload -w ~/Library/LaunchAgents/com.google.GoogleUpdater.wake.plist 2>/dev/null || true
launchctl unload -w ~/Library/LaunchAgents/com.google.keystone.agent.plist 2>/dev/null || true
launchctl unload -w ~/Library/LaunchAgents/com.google.keystone.xpcservice.plist 2>/dev/null || true

# Disable Zoom daemon
sudo launchctl unload -w /Library/LaunchDaemons/us.zoom.ZoomDaemon.plist 2>/dev/null || true
launchctl unload -w ~/Library/LaunchAgents/us.zoom.updater.gui.501.app.terminate.update.plist 2>/dev/null || true

# Disable Amazon CodeWhisperer auto-launcher
launchctl unload -w ~/Library/LaunchAgents/com.amazon.codewhisperer.launcher.plist 2>/dev/null || true

# Fix world-writable directories
chmod o-w ~/Library/Application\ Support/zoom.us 2>/dev/null || true
chmod o-w ~/Public/Drop\ Box 2>/dev/null || true

# Disable rapportd (AirDrop/Handoff network exposure)
defaults write com.apple.rapport enabled -bool false 2>/dev/null || true

# Remove Zoom daemon (prevents loading on reboot)
sudo rm -f /Library/LaunchDaemons/us.zoom.ZoomDaemon.plist 2>/dev/null || true

# Permanently remove unauthorized launch agents
rm -f ~/Library/LaunchAgents/com.amazon.codewhisperer.launcher.plist
rm -f ~/Library/LaunchAgents/com.google.GoogleUpdater.wake.plist
rm -f ~/Library/LaunchAgents/com.google.keystone.agent.plist
rm -f ~/Library/LaunchAgents/com.google.keystone.xpcservice.plist
rm -f ~/Library/LaunchAgents/us.zoom.updater.gui.501.app.terminate.update.plist

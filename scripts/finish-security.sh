#!/bin/bash
# DOME-HUB: Finish security + optimization setup
# Run once: bash scripts/finish-security.sh (from DSH root)

eval "$(/opt/homebrew/bin/brew shellenv)"
set -e
DOME_ROOT="${DOME_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

echo "==> Step 1: Firewall + Stealth"
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setloggingmode on
echo "✓ Firewall on + stealth mode on"

echo ""
echo "==> Step 2: Hardware Optimization"
sudo pmset -a sms 0
sudo pmset -c powernap 0
sudo pmset -c proximitywake 0
sudo pmset -a destroyfvkeyonstandby 1
sudo pmset -a hibernatemode 25
sudo launchctl limit maxfiles 65536 200000
sudo mdutil -i off "$DOME_ROOT" 2>/dev/null || true
defaults write NSGlobalDomain NSAppSleepDisabled -bool YES
echo "✓ Hardware optimized"

echo ""
echo "==> Step 3: GPG Key"
if ! gpg --list-secret-keys 2>/dev/null | grep -q "sec"; then
  gpg --batch --gen-key <<EOF
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: $(whoami)
Name-Email: $(whoami)@dome-hub.local
Expire-Date: 0
%no-protection
EOF
  echo "✓ GPG key generated"
else
  echo "✓ GPG key already exists"
fi

echo ""
echo "==> Step 4: pass + git signing"
GPG_ID=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep sec | head -1 | awk '{print $2}' | cut -d'/' -f2)
echo "GPG ID: $GPG_ID"
pass init "$GPG_ID"
git config --global user.signingkey "$GPG_ID"
git config --global commit.gpgsign true
git config --global gpg.program "$(which gpg)"
echo "✓ pass initialized, git signing enabled"

echo ""
echo "==> Step 5: Private DNS"
sudo networksetup -setdnsservers Wi-Fi 127.0.0.1
sudo brew services start dnscrypt-proxy
echo "✓ DNS → 127.0.0.1 (dnscrypt-proxy)"

echo ""
echo "==> Running final audit..."
bash "$DOME_ROOT/scripts/audit.sh"

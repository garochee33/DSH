#!/bin/bash
# DOME-HUB Sovereign Setup — macOS (M1 / M2 / M3 / M4)
# Run: bash scripts/sovereign-setup-mac.sh

set -e
DOME_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "==> DOME-HUB Sovereign Setup"
echo "    Root: $DOME_ROOT"
echo "    Chip: $(sysctl -n machdep.cpu.brand_string)"

# ── 1. Xcode CLI Tools ────────────────────────────────────────────────────────
if ! xcode-select -p &>/dev/null; then
  echo "==> Installing Xcode CLI Tools..."
  xcode-select --install
  echo "    Wait for install to complete, then re-run this script."
  exit 0
fi

# ── 2. Homebrew ───────────────────────────────────────────────────────────────
if ! command -v brew &>/dev/null; then
  echo "==> Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi
eval "$(/opt/homebrew/bin/brew shellenv)"

# ── 3. Core CLI tools ─────────────────────────────────────────────────────────
echo "==> Installing core tools..."
brew install git curl wget jq yq tree htop tmux ripgrep fzf zoxide \
  pyenv nvm go rust node \
  postgresql@17 redis sqlite \
  awscli hashicorp/tap/terraform gh \
  gnupg pinentry-mac pass dnscrypt-proxy \
  starship zsh-autosuggestions zsh-syntax-highlighting

# ── 4. Python ─────────────────────────────────────────────────────────────────
echo "==> Setting up Python..."
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
pyenv install 3.11.9 2>/dev/null || true
pyenv global 3.11.9
pip3 install --upgrade pip pipenv poetry
pip3 install openai anthropic langchain chromadb sentence-transformers \
  torch transformers sqlalchemy psycopg2-binary redis pandas numpy \
  scipy sympy statsmodels scikit-learn numba matplotlib networkx psutil

# ── 5. Node ───────────────────────────────────────────────────────────────────
echo "==> Setting up Node..."
mkdir -p ~/.nvm
export NVM_DIR="$HOME/.nvm"
[ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && source "/opt/homebrew/opt/nvm/nvm.sh"
nvm install 20
nvm alias default 20
npm install -g pnpm
pnpm setup
export PNPM_HOME="$HOME/Library/pnpm"
export PATH="$PNPM_HOME:$PATH"
pnpm add -g tsx typescript ts-node

# ── 6. VS Code ────────────────────────────────────────────────────────────────
echo "==> Installing VS Code..."
brew install --cask visual-studio-code 2>/dev/null || true
for ext in esbenp.prettier-vscode dbaeumer.vscode-eslint ms-python.python \
  ms-python.vscode-pylance ms-python.black-formatter golang.go \
  rust-lang.rust-analyzer ms-azuretools.vscode-docker hashicorp.terraform \
  amazonwebservices.aws-toolkit-vscode eamodio.gitlens usernamehw.errorlens \
  mikestead.dotenv bradlc.vscode-tailwindcss prisma.prisma redhat.vscode-yaml; do
  code --install-extension $ext --force 2>/dev/null || true
done

# ── 7. Root venv ──────────────────────────────────────────────────────────────
echo "==> Creating root Python venv..."
python3 -m venv "$DOME_ROOT/.venv"
source "$DOME_ROOT/.venv/bin/activate"
pip install --quiet torch torchvision psutil scipy sympy statsmodels \
  scikit-learn numba matplotlib networkx openai anthropic langchain \
  chromadb sentence-transformers transformers sqlalchemy psycopg2-binary \
  redis pandas numpy

# ── 8. Databases ──────────────────────────────────────────────────────────────
echo "==> Starting databases..."
brew services start postgresql@17
brew services start redis

# ── 9. GPG + pass ─────────────────────────────────────────────────────────────
echo "==> Setting up GPG..."
mkdir -p ~/.gnupg
echo "pinentry-program $(brew --prefix)/bin/pinentry-mac" > ~/.gnupg/gpg-agent.conf
chmod 700 ~/.gnupg
if ! gpg --list-secret-keys 2>/dev/null | grep -q "sec"; then
  gpg --batch --gen-key <<GPGEOF
Key-Type: RSA
Key-Length: 4096
Name-Real: $USER
Name-Email: $USER@dome-hub.local
Expire-Date: 0
%no-protection
GPGEOF
fi
GPG_ID=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep sec | head -1 | awk '{print $2}' | cut -d'/' -f2)
pass init "$GPG_ID" 2>/dev/null || true
git config --global user.signingkey "$GPG_ID"
git config --global commit.gpgsign true
git config --global gpg.program "$(which gpg)"

# ── 10. Security hardening ────────────────────────────────────────────────────
echo "==> Hardening security..."
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode on
sudo pmset -a sms 0
sudo pmset -c powernap 0
sudo pmset -a destroyfvkeyonstandby 1
sudo launchctl limit maxfiles 65536 200000
defaults write NSGlobalDomain NSAppSleepDisabled -bool YES
defaults write com.apple.CrashReporter DialogType none
defaults write com.apple.Siri StatusMenuVisible -bool false
defaults write com.google.Chrome BackgroundModeEnabled -bool false
defaults write com.google.Chrome MetricsReportingEnabled -bool false
defaults write com.google.Chrome SyncDisabled -bool true
defaults write com.apple.Terminal SecureKeyboardEntry -bool true
defaults write com.apple.dock autohide -bool true
defaults write com.apple.dock autohide-delay -float 0
defaults write com.apple.dock launchanim -bool false
killall Dock 2>/dev/null || true

# ── 11. Private DNS ───────────────────────────────────────────────────────────
echo "==> Switching to private DNS..."
sudo networksetup -setdnsservers Wi-Fi 127.0.0.1 2>/dev/null || true
sudo brew services start dnscrypt-proxy 2>/dev/null || true

# ── 12. Shell config ──────────────────────────────────────────────────────────
echo "==> Configuring shell..."
grep -q "zshrc-dome" ~/.zshrc 2>/dev/null || \
  echo "source $DOME_ROOT/scripts/zshrc-dome.sh" >> ~/.zshrc

# ── 13. pnpm install ──────────────────────────────────────────────────────────
cd "$DOME_ROOT" && pnpm install 2>/dev/null || true

echo ""
echo "✅ DOME-HUB Sovereign Setup Complete"
echo "   Run: source ~/.zshrc"
echo "   Then: bash scripts/audit.sh"

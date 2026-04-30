#!/bin/bash
# DOME-HUB Sovereign Setup — macOS (M1 / M2 / M3 / M4)
# Run: bash scripts/sovereign-setup-mac.sh

set -euo pipefail

DOME_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOTAL_STEPS=21
CURRENT_STEP=0
CURRENT_PHASE="bootstrap"
BAR_WIDTH=34
CINEMATIC_MODE="${DOME_CINEMATIC:-1}"
ANIMATIONS_ENABLED=1
PREVIEW_CINEMATIC=0

usage() {
  cat <<'USAGE'
Usage:
  bash scripts/sovereign-setup-mac.sh [options]

Options:
  --cinematic          Force cinematic visual mode (default in interactive TTY)
  --no-cinematic       Disable sacred-geometry cinematic visuals
  --no-animations      Disable all animation timing (fast/headless)
  --preview-cinematic  Render cinematic intro/phase preview and exit
  -h, --help           Show help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cinematic)
      CINEMATIC_MODE=1
      ANIMATIONS_ENABLED=1
      ;;
    --no-cinematic)
      CINEMATIC_MODE=0
      ;;
    --no-animations)
      ANIMATIONS_ENABLED=0
      ;;
    --preview-cinematic)
      PREVIEW_CINEMATIC=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if [[ ! -t 1 ]]; then
  ANIMATIONS_ENABLED=0
  if [[ "$PREVIEW_CINEMATIC" -ne 1 ]]; then
    CINEMATIC_MODE=0
  fi
fi

if [[ -t 1 ]] && command -v tput >/dev/null 2>&1 && [[ "$(tput colors 2>/dev/null || echo 0)" -ge 256 ]]; then
  C_RESET="$(tput sgr0)"
  C_CYAN="$(tput setaf 6)"
  C_GREEN="$(tput setaf 2)"
  C_YELLOW="$(tput setaf 3)"
  C_MAGENTA="$(tput setaf 178)"
  C_DIM="$(tput dim)"
else
  C_RESET=""
  C_CYAN=""
  C_GREEN=""
  C_YELLOW=""
  C_MAGENTA=""
  C_DIM=""
fi

progress_bar() {
  local step="$1"
  local total="$2"
  local filled=$((step * BAR_WIDTH / total))
  local empty=$((BAR_WIDTH - filled))
  local bar
  bar="$(printf '%*s' "$filled" '' | tr ' ' '█')"
  bar="${bar}$(printf '%*s' "$empty" '' | tr ' ' '░')"
  local pct=$((step * 100 / total))
  printf "    ▐%s▌ %3d%%" "$bar" "$pct"
}

pulse() {
  local message="$1"
  if [[ "$ANIMATIONS_ENABLED" -ne 1 ]]; then
    printf "    ▸ %s...\n" "$message"
    return
  fi
  printf "    %s▸ %s%s" "$C_YELLOW" "$message" "$C_RESET"
  for _ in 1 2 3; do
    printf "%s●%s" "$C_MAGENTA" "$C_RESET"
    sleep 0.15
  done
  printf "\n"
}

lattice_spin() {
  local message="$1"
  local frames=( "◐" "◓" "◑" "◒" )
  if [[ "$ANIMATIONS_ENABLED" -ne 1 ]]; then
    printf "    ▸ %s\n" "$message"
    return
  fi
  for f in "${frames[@]}"; do
    printf "\r    %s%s %s%s" "$C_MAGENTA" "$f" "$message" "$C_RESET"
    sleep 0.08
  done
  printf "\r    %s✦ %s done%s\n" "$C_GREEN" "$message" "$C_RESET"
}

sacred_scene() {
  local label="$1"
  [[ "$CINEMATIC_MODE" -eq 1 ]] || return 0
  printf "%s\n" "$C_MAGENTA"
  printf '    ╔══════════════════════════════════════════════════════════╗\n'
  printf '    ║  ▓▓▓ Sacred Geometry Mesh ▓▓▓                          ║\n'
  printf '    ║                                                        ║\n'
  printf '    ║       ◆───◆───◆───◆───◆                                ║\n'
  printf '    ║      ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲                              ║\n'
  printf '    ║     ◆───◆───◆───◆───◆───◆                              ║\n'
  printf '    ║      ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱ ╲ ╱                              ║\n'
  printf '    ║       ◆───◆───◆───◆───◆                                ║\n'
  printf '    ║                                                        ║\n'
  printf "    ║  %-54.54s  ║\n" "$label"
  printf '    ╚══════════════════════════════════════════════════════════╝\n'
  printf "%s" "$C_RESET"
  lattice_spin "Weaving lattice harmonics"
}

cinematic_intro() {
  [[ "$CINEMATIC_MODE" -eq 1 ]] || return 0
  echo
  printf "%s\n" "$C_MAGENTA"
  printf '    ██████╗  ███████╗ ██╗  ██╗\n'
  printf '    ██╔══██╗ ██╔════╝ ██║  ██║\n'
  printf '    ██║  ██║ ███████╗ ███████║\n'
  printf '    ██║  ██║ ╚════██║ ██╔══██║\n'
  printf '    ██████╔╝ ███████║ ██║  ██║\n'
  printf '    ╚═════╝  ╚══════╝ ╚═╝  ╚═╝\n'
  printf "%s" "$C_RESET"
  printf "%s    ═══ D O M E   S O V E R E I G N   H U B ═══%s\n" "$C_CYAN" "$C_RESET"
  printf "%s    Sovereign Node Setup · Phase 1%s\n" "$C_DIM" "$C_RESET"
  echo
  sacred_scene "BOOT SEQUENCE"
}

phase() {
  CURRENT_STEP=$((CURRENT_STEP + 1))
  CURRENT_PHASE="$1"
  echo
  printf "%s    ┌─────────────────────────────────────────────┐%s\n" "$C_CYAN" "$C_RESET"
  printf "%s    │  ▶  [%d/%d]  %-33.33s│%s\n" "$C_CYAN" "$CURRENT_STEP" "$TOTAL_STEPS" "$CURRENT_PHASE" "$C_RESET"
  printf "%s    └─────────────────────────────────────────────┘%s\n" "$C_CYAN" "$C_RESET"
  printf "%s%s%s\n" "$C_DIM" "$(progress_bar "$CURRENT_STEP" "$TOTAL_STEPS")" "$C_RESET"
  sacred_scene "$CURRENT_PHASE"
}

info() {
  printf "    %s▸%s %s\n" "$C_CYAN" "$C_RESET" "$*"
}

warn() {
  printf "    %sWARN%s: %s\n" "$C_YELLOW" "$C_RESET" "$*"
}

on_error() {
  echo
  echo "Setup failed during step $CURRENT_STEP/$TOTAL_STEPS: $CURRENT_PHASE"
  echo "Fix the blocker above and re-run: bash scripts/sovereign-setup-mac.sh"
}

trap on_error ERR

if [[ "$PREVIEW_CINEMATIC" -eq 1 ]]; then
  cinematic_intro
  phase "Core CLI and Infra Packages"
  info "Loading git, shells, languages, databases, cloud CLIs, and security tooling..."
  pulse "Preparing package resolver"
  phase "Python Runtime and Package Stacks"
  info "Loading AI/ML stack (LangChain, ChromaDB, Transformers, Torch, analytics)"
  pulse "Resolving AI/ML dependencies"
  phase "Local Node Payload Verification"
  info "SQLite ready: db/dome.db"
  info "Chroma path ready: db/chroma"
  echo
  echo "Cinematic preview complete."
  exit 0
fi

cinematic_intro

echo "DOME-HUB Sovereign Setup (Phase 1)"
echo "Root: $DOME_ROOT"
echo "Chip: $(sysctl -n machdep.cpu.brand_string)"
echo "This installer is safe to re-run. Existing installs are reused when possible."
echo "This run localizes your sovereign node payload into this repo:"
echo "  - agents/   -> local agent runtime + skills"
echo "  - kb/       -> local knowledge corpus to ingest"
echo "  - db/       -> local SQLite + Chroma vector state"

phase "Xcode CLI Tools"
if ! xcode-select -p &>/dev/null; then
  info "Installing Xcode CLI Tools..."
  xcode-select --install
  warn "Xcode install launched. Wait for completion, then re-run this script."
  exit 0
fi
info "Xcode CLI Tools already present."

phase "Homebrew"
if ! command -v brew &>/dev/null; then
  info "Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi
eval "$(/opt/homebrew/bin/brew shellenv)"
info "Homebrew ready: $(brew --version | head -n 1)"

phase "Core CLI and Infra Packages"
info "Loading git, shells, languages, databases, cloud CLIs, and security tooling..."
pulse "Preparing package resolver"
brew install git curl wget jq yq tree htop tmux ripgrep fzf zoxide \
  pyenv nvm go rust node \
  postgresql@18 redis sqlite \
  awscli hashicorp/tap/terraform gh \
  gnupg pinentry-mac pass dnscrypt-proxy \
  starship zsh-autosuggestions zsh-syntax-highlighting

phase "Python Runtime and Package Stacks"
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
PY_VER="${DOME_PYTHON_VERSION:-3.14.3}"
info "Ensuring Python via pyenv: $PY_VER"
pyenv install "$PY_VER" 2>/dev/null || true
pyenv global "$PY_VER"
info "Upgrading pip + env tooling"
pulse "Bootstrapping Python package manager state"
pip3 install --upgrade pip pipenv poetry

info "Loading AI/ML stack (LangChain, ChromaDB, Transformers, Torch, analytics)"
pulse "Resolving AI/ML dependencies"
pip3 install openai anthropic claude-agent-sdk langchain chromadb sentence-transformers \
  torch transformers sqlalchemy psycopg2-binary redis pandas numpy \
  scipy sympy statsmodels scikit-learn numba matplotlib networkx psutil tiktoken

info "Loading local inference stack (Apple Silicon)"
pulse "Resolving local inference packages"
pip3 install mlx mlx-lm ollama

info "Loading quantum stack"
pulse "Resolving quantum compute packages"
pip3 install qiskit qiskit-aer pennylane pennylane-qiskit cirq-core qutip pyquil amazon-braket-sdk

info "Loading document pipeline stack"
pulse "Resolving document pipeline packages"
pip3 install python-docx python-pptx openpyxl reportlab pypdf pdfplumber

info "Loading web research + API stack"
pulse "Resolving web/API packages"
pip3 install requests beautifulsoup4 httpx python-dotenv pydantic rich typer uvicorn fastapi

phase "Node and pnpm"
mkdir -p "$HOME/.nvm"
export NVM_DIR="$HOME/.nvm"
[ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && source "/opt/homebrew/opt/nvm/nvm.sh"
info "Installing Node 20 and global TypeScript runtime tools"
pulse "Preparing Node runtime environment"
nvm install 20
nvm alias default 20
npm install -g pnpm
pnpm setup
export PNPM_HOME="$HOME/Library/pnpm"
export PATH="$PNPM_HOME:$PATH"
pnpm add -g tsx typescript ts-node

phase "VS Code and Extensions"
info "Installing VS Code (if missing) and extension baseline"
brew install --cask visual-studio-code 2>/dev/null || true
for ext in esbenp.prettier-vscode dbaeumer.vscode-eslint ms-python.python \
  ms-python.vscode-pylance ms-python.black-formatter golang.go \
  rust-lang.rust-analyzer ms-azuretools.vscode-docker hashicorp.terraform \
  amazonwebservices.aws-toolkit-vscode eamodio.gitlens usernamehw.errorlens \
  mikestead.dotenv bradlc.vscode-tailwindcss prisma.prisma redhat.vscode-yaml; do
  code --install-extension "$ext" --force 2>/dev/null || true
done

phase "Root Python Virtual Environment"
python3 -m venv "$DOME_ROOT/.venv"
source "$DOME_ROOT/.venv/bin/activate"
info "Installing pinned project requirements into $DOME_ROOT/.venv"
pip install --upgrade pip wheel
pip install -r "$DOME_ROOT/compute/requirements.txt"

phase "PostgreSQL and Redis Services"
info "Starting postgres@18 and redis via brew services"
brew services start postgresql@18
brew services start redis

phase "GPG and pass Secret Store"
mkdir -p "$HOME/.gnupg"
echo "pinentry-program $(brew --prefix)/bin/pinentry-mac" > "$HOME/.gnupg/gpg-agent.conf"
chmod 700 "$HOME/.gnupg"
if ! gpg --list-secret-keys 2>/dev/null | grep -q "sec"; then
  info "Generating local GPG key (no passphrase, local-only bootstrap key)"
  gpg --batch --gen-key <<GPGEOF
Key-Type: RSA
Key-Length: 4096
Name-Real: $USER
Name-Email: $USER@dome-hub.local
Expire-Date: 0
%no-protection
GPGEOF
fi
GPG_ID="$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep sec | head -1 | awk '{print $2}' | cut -d'/' -f2)"
pass init "$GPG_ID" 2>/dev/null || true
git config --global user.signingkey "$GPG_ID"
git config --global commit.gpgsign true
git config --global gpg.program "$(command -v gpg)"
info "Git signing key active: $GPG_ID"

phase "Security Hardening"
info "Applying macOS firewall, stealth, power, and telemetry hardening defaults"
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

phase "Private DNS"
info "Switching Wi-Fi DNS to localhost resolver and starting dnscrypt-proxy"
sudo networksetup -setdnsservers Wi-Fi 127.0.0.1 2>/dev/null || true
sudo brew services start dnscrypt-proxy 2>/dev/null || true

phase "Shell Configuration"
grep -q "zshrc-dome" "$HOME/.zshrc" 2>/dev/null || \
  echo "source $DOME_ROOT/scripts/zshrc-dome.sh" >> "$HOME/.zshrc"
info "zsh hook ready"

phase "DOME-HUB Directory Structure"
mkdir -p "$DOME_ROOT"/{projects,platforms,software,compute,agents,models,kb,db,codebase,logs,scripts}
info "Core folders ensured"

phase "SQLite Initialization"
source "$DOME_ROOT/.venv/bin/activate"
python3 -c "
import sqlite3
db = sqlite3.connect('$DOME_ROOT/db/dome.db')
db.execute('CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, title TEXT, content TEXT, tags TEXT, created_at TEXT)')
db.execute('CREATE TABLE IF NOT EXISTS stack (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, name TEXT, version TEXT, status TEXT, updated_at TEXT, UNIQUE(category, name))')
db.execute('CREATE TABLE IF NOT EXISTS agents (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, vendor TEXT, version TEXT, surface TEXT, role TEXT, kb_path TEXT, entrypoint TEXT, updated_at TEXT)')
db.execute('CREATE TABLE IF NOT EXISTS skills (id INTEGER PRIMARY KEY AUTOINCREMENT, agent TEXT, name TEXT, description TEXT, path TEXT, updated_at TEXT, UNIQUE(agent, name))')
db.execute('CREATE TABLE IF NOT EXISTS tools (id INTEGER PRIMARY KEY AUTOINCREMENT, agent TEXT, name TEXT, category TEXT, description TEXT, updated_at TEXT, UNIQUE(agent, name))')
db.commit()
db.close()
print('DB ready')
" 2>/dev/null || true
info "dome.db initialized (or already present)"

phase "Repository Dependencies"
info "Installing Node dependencies in repository root"
pulse "Resolving repository dependency graph"
cd "$DOME_ROOT" && pnpm install 2>/dev/null || true

phase ".env Bootstrap"
if [ ! -f "$DOME_ROOT/.env" ]; then
  cp "$DOME_ROOT/.env.example" "$DOME_ROOT/.env"
  warn ".env created from .env.example; add API keys before running agents."
else
  info ".env already present"
fi

phase "ChromaDB Ingest"
info "Building knowledge index from kb/ into ChromaDB"
pulse "Vectorizing local knowledge corpus"
cd "$DOME_ROOT" && python3 scripts/ingest.py 2>/dev/null || warn "Ingest skipped. Run later: pnpm ingest"

phase "Claude Agent Registration"
info "Registering Claude profile in dome.db"
python3 scripts/register-claude.py 2>/dev/null || true

phase "Local Node Payload Verification"
info "Verifying sovereign payload was materialized into local repo/KB/DB..."
AGENT_FILE_COUNT="$(find "$DOME_ROOT/agents" -type f 2>/dev/null | wc -l | tr -d ' ')"
KB_FILE_COUNT="$(find "$DOME_ROOT/kb" -type f 2>/dev/null | wc -l | tr -d ' ')"
if [ -f "$DOME_ROOT/db/dome.db" ]; then
  info "SQLite ready: db/dome.db"
else
  warn "SQLite file missing: db/dome.db"
fi
if [ -d "$DOME_ROOT/db/chroma" ]; then
  info "Chroma path ready: db/chroma"
else
  warn "Chroma path missing: db/chroma (run: pnpm ingest)"
fi
info "Agent files detected: $AGENT_FILE_COUNT"
info "KB files detected: $KB_FILE_COUNT"
info "Node scope: all runtime assets are local to $DOME_ROOT"

phase "Git Hook and Scheduler"
info "Installing pre-push hook (protocol check gate)"
HOOK="$DOME_ROOT/.git/hooks/pre-push"
cat > "$HOOK" <<'HOOK_EOF'
#!/bin/bash
echo "==> DOME-HUB pre-push protocol check..."
bash "$(git rev-parse --show-toplevel)/scripts/dome-check.sh" || exit 1
echo "Protocols OK - pushing"
HOOK_EOF
chmod +x "$HOOK"

info "Installing dome-check cron (every 6h)"
CRON_JOB="0 */6 * * * cd $DOME_ROOT && bash scripts/dome-check.sh >> logs/dome-check.log 2>&1"
(crontab -l 2>/dev/null | grep -v "dome-check"; echo "$CRON_JOB") | crontab -

phase "AI Assistant Choice"
echo "Pick your default assistant bootstrap:"
echo "  1) Kiro CLI       (npm install -g kiro-cli)"
echo "  2) Claude Code    (npm install -g @anthropic-ai/claude-code)"
echo "  3) Cursor         (brew install --cask cursor)"
echo "  4) GitHub Copilot (gh extension install github/gh-copilot)"
echo "  5) Aider          (pip install aider-chat)"
echo "  6) Skip"
read -rp "Enter choice [1-6]: " AI_CHOICE
case "$AI_CHOICE" in
  1) npm install -g kiro-cli ;;
  2) npm install -g @anthropic-ai/claude-code ;;
  3) brew install --cask cursor ;;
  4) gh extension install github/gh-copilot ;;
  5) pip install aider-chat ;;
  *) info "Skipping assistant install." ;;
esac

echo
printf "%s" "$C_GREEN"
echo "    ✦ DSH Sovereign Setup Complete"
printf "%s" "$C_RESET"
echo "    Run: source ~/.zshrc"
echo "    Then: pnpm check"
echo
printf "%s    ⭐ If DSH helped you — star the repo and leave a review:%s\n" "$C_YELLOW" "$C_RESET"
printf "%s    → https://github.com/garochee33/DSH%s\n" "$C_CYAN" "$C_RESET"
echo "    Your feedback helps us build better sovereign tools for everyone."
echo

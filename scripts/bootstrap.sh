#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOME_ROOT="${DOME_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
echo "==> DOME-HUB Bootstrap"

eval "$(brew shellenv 2>/dev/null || true)"

# Shell enhancements
brew install starship zsh-autosuggestions zsh-syntax-highlighting

# nvm setup
mkdir -p ~/.nvm
export NVM_DIR="$HOME/.nvm"
NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
[ -s "$(brew --prefix 2>/dev/null)/opt/nvm/nvm.sh" ] && source "$(brew --prefix)/opt/nvm/nvm.sh"
nvm install 20
nvm alias default 20
npm install -g pnpm
pnpm add -g tsx typescript ts-node vercel netlify-cli

# pyenv Python
pyenv install 3.11.9 2>/dev/null || true
pyenv global 3.11.9
PIP="$(pyenv which pip3)"
$PIP install --upgrade pip pipenv poetry
$PIP install openai anthropic langchain chromadb sentence-transformers torch transformers
$PIP install sqlalchemy psycopg2-binary redis pandas numpy

# Infra / Cloud
brew install postgresql redis awscli terraform gh

# VS Code
if ! command -v code &>/dev/null; then
  brew install --cask visual-studio-code
fi
code --install-extension esbenp.prettier-vscode
code --install-extension dbaeumer.vscode-eslint
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-python.black-formatter
code --install-extension golang.go
code --install-extension rust-lang.rust-analyzer
code --install-extension ms-azuretools.vscode-docker
code --install-extension hashicorp.terraform
code --install-extension amazonwebservices.aws-toolkit-vscode
code --install-extension eamodio.gitlens
code --install-extension usernamehw.errorlens
code --install-extension mikestead.dotenv
code --install-extension bradlc.vscode-tailwindcss
code --install-extension prisma.prisma

# Root dev dependencies
cd "$DOME_ROOT" && pnpm install

echo ""
echo "==> Done. Run: source ~/.zshrc"

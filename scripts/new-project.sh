#!/bin/bash
# Usage: ./scripts/new-project.sh <category> <name>
# Example: ./scripts/new-project.sh projects my-app

CATEGORY=${1:?usage: new-project.sh <category> <name>}
NAME=${2:?usage: new-project.sh <category> <name>}
DIR="/Users/gadikedoshim/DOME-HUB/$CATEGORY/$NAME"

mkdir -p "$DIR"
cd "$DIR"

# Python venv
python3 -m venv .venv
echo ".venv/" >> .gitignore

# Node
echo "20" > .nvmrc
pnpm init > /dev/null 2>&1
echo "node_modules/" >> .gitignore

# Env
echo "DOME_ROOT=/Users/gadikedoshim/DOME-HUB" > .env.example
echo "ENV=dev" >> .env.example
echo ".env" >> .gitignore

echo "✓ $CATEGORY/$NAME ready — Python venv + Node initialized"
echo "  Activate Python: source $DIR/.venv/bin/activate"
echo "  Node version:    $(node -v 2>/dev/null || echo 'install via: nvm use')"

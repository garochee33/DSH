#!/bin/bash
# Usage: ./scripts/new-project.sh <category> <name>
# Example: ./scripts/new-project.sh projects my-app

CATEGORY=${1:?usage: new-project.sh <category> <name>}
NAME=${2:?usage: new-project.sh <category> <name>}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOME_ROOT="${DOME_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
DIR="$DOME_ROOT/$CATEGORY/$NAME"

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
echo "DOME_ROOT=$DOME_ROOT" > .env.example
echo "ENV=dev" >> .env.example
echo ".env" >> .gitignore

echo "✓ $CATEGORY/$NAME ready — Python venv + Node initialized"
echo "  Activate Python: source $DIR/.venv/bin/activate"
echo "  Node version:    $(node -v 2>/dev/null || echo 'install via: nvm use')"

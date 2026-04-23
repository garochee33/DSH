#!/usr/bin/env bash
# Install repo-local git hooks from the tracked .githooks/ directory.
# Run once after cloning. Idempotent.
set -euo pipefail
repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"
if [ ! -d .githooks ]; then
    echo "error: no .githooks/ directory at repo root"
    exit 1
fi
git config core.hooksPath .githooks
chmod +x .githooks/* 2>/dev/null || true
echo "✓ core.hooksPath → .githooks/"
echo "✓ Installed hooks:"
ls .githooks/ | sed 's/^/    /'

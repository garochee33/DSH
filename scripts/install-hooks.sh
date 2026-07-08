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
echo "✓ Hooks refresh: post-commit + post-checkout → scripts/update-tree-map.sh"
echo "    (fractalmap, FILE_TREE.md, holographic tree map timestamp)"
echo "✓ Installed hooks:"
ls .githooks/ | sed 's/^/    /'
echo ""
echo "Force refresh now: bash scripts/refresh-repo-maps.sh"

#!/usr/bin/env bash
# Force-regenerate all structural maps: fractalmap, FILE_TREE.md, holographic tree map timestamp.
# Usage: bash scripts/refresh-repo-maps.sh [agent-name]
set -euo pipefail

DOME_ROOT="${DOME_ROOT:-$HOME/DOME-HUB}"
AGENT="${1:-manual}"
export FRACTALMAP_FORCE=1

exec bash "$DOME_ROOT/scripts/update-tree-map.sh" "$AGENT"

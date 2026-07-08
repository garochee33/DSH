#!/usr/bin/env bash
# backup-projects-to-icloud.sh — One-way rsync of local-only projects to iCloud
# Safe: never modifies your working copy. Excludes build artifacts.
# Run manually or via cron: 0 */4 * * * ~/DSH/scripts/backup-projects-to-icloud.sh

set -euo pipefail

SOURCE="${DOME_ROOT:-$HOME/DSH/home}/projects"
DEST="$HOME/Library/Mobile Documents/com~apple~CloudDocs/DOME-PROJECTS-BACKUP"

mkdir -p "$DEST"

rsync -a --delete \
  --exclude='node_modules/' \
  --exclude='.next/' \
  --exclude='dist/' \
  --exclude='build/' \
  --exclude='.venv/' \
  --exclude='__pycache__/' \
  --exclude='.DS_Store' \
  --exclude='*.pyc' \
  --exclude='.git/' \
  "$SOURCE/" "$DEST/"

echo "✓ Backed up $(ls "$SOURCE" | wc -l | tr -d ' ') projects to iCloud ($(du -sh "$DEST" | cut -f1))"
echo "  Last run: $(date '+%Y-%m-%d %H:%M')"

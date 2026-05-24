#!/usr/bin/env bash
# vault-snapshot.sh — Dual-Archive snapshot for dome-brain (Obsidian vault)
#
# Doctrine: feedback_dual_archive_protocol.md
#   Per-repo schema: {archive-root}/<repo>/<category>/<YYYY-MM-DD>/
#   Hot   → ~/DOME-HUB/archive/dome-hub/brain-vault/<date>/
#   Always→ ~/iCloud/DOME-ARCHIVE/dome-hub/brain-vault/<date>/
#
# Only the non-regeneratable second brain is mirrored. The 600/700/800
# registries are excluded (regenerable via vault-sync-registries.sh; same
# doctrine as .fractalmap/).
#
# Idempotent within a day (rsync --delete-during). Re-running the same day
# refreshes the snapshot and rewrites MANIFEST.json without bloat.
#
# Exit non-zero if iCloud Always mirror is missing — sovereign-but-livable
# means we surface the failure, never silently degrade durability.

set -uo pipefail  # NOT -e: iCloud write may fail under launchd TCC; we handle it.

# ---- paths -------------------------------------------------------------------
VAULT="${HOME}/DOME-HUB/brain/vault"
HOT_ROOT="${HOME}/DOME-HUB/archive/dome-hub/brain-vault"
ICLOUD_ROOT="${HOME}/iCloud/DOME-ARCHIVE/dome-hub/brain-vault"
PENDING_MARKER="${HOME}/DOME-HUB/logs/vault-snapshot.icloud-pending"

DATE="$(date +%Y-%m-%d)"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

HOT_DIR="${HOT_ROOT}/${DATE}"
ICLOUD_DIR="${ICLOUD_ROOT}/${DATE}"

# ---- preflight ---------------------------------------------------------------
if [[ ! -d "${VAULT}" ]]; then
  echo "[vault-snapshot] FATAL: vault not found at ${VAULT}" >&2
  exit 2
fi

# iCloud is BEST-EFFORT under launchd (macOS TCC denies launchd-spawned bash
# write access to ~/Library/Mobile Documents/ regardless of /bin/bash FDA grant).
# When run from a user terminal session, TCC inheritance lets it succeed.
# Either way: Hot mirror is the durability guarantee; iCloud is the cross-device
# convenience. If iCloud is missing entirely, we still proceed (Hot suffices).
ICLOUD_AVAILABLE=1
if [[ ! -d "${HOME}/iCloud/DOME-ARCHIVE" ]]; then
  echo "[vault-snapshot] WARN: iCloud Always mirror dir missing — Hot-only this run." >&2
  ICLOUD_AVAILABLE=0
fi

mkdir -p "${HOT_DIR}"
[[ "${ICLOUD_AVAILABLE}" == "1" ]] && mkdir -p "${ICLOUD_DIR}" 2>/dev/null || ICLOUD_AVAILABLE=0

# ---- non-regeneratable folders to snapshot -----------------------------------
# Anything else (600/700/800 registries) is regenerable and intentionally
# omitted; .git is omitted because git history is the OTHER safety net.
INCLUDES=(
  "000-Inbox"
  "100-Daily-Notes"
  "200-Projects"
  "300-Areas"
  "400-Resources"
  "500-Archive"
  "900-Templates"
  ".obsidian"
  "README.md"
  "README-GIT.md"
  "Map of Content.md"
)

# ---- rsync helper ------------------------------------------------------------
rsync_to() {
  local dest="$1"
  for item in "${INCLUDES[@]}"; do
    local src="${VAULT}/${item}"
    [[ -e "${src}" ]] || continue
    if [[ -d "${src}" ]]; then
      mkdir -p "${dest}/${item}"
      rsync -a --delete-during \
        --exclude='workspace*' \
        --exclude='cache*' \
        --exclude='graph.json' \
        --exclude='.DS_Store' \
        --exclude='.trash/' \
        "${src}/" "${dest}/${item}/"
    else
      rsync -a "${src}" "${dest}/"
    fi
  done
}

echo "[vault-snapshot] ${TS} — mirroring vault → Hot${ICLOUD_AVAILABLE:+ + Always}"
echo "[vault-snapshot]   Hot:    ${HOT_DIR}"
[[ "${ICLOUD_AVAILABLE}" == "1" ]] && echo "[vault-snapshot]   Always: ${ICLOUD_DIR}"

rsync_to "${HOT_DIR}"
HOT_OK=$?

ICLOUD_OK=0
if [[ "${ICLOUD_AVAILABLE}" == "1" ]]; then
  if rsync_to "${ICLOUD_DIR}" 2>/dev/null; then
    ICLOUD_OK=1
    rm -f "${PENDING_MARKER}"
  else
    # Most likely cause: macOS TCC denied launchd-spawned bash access to iCloud.
    # Drop a marker so a user-session run of this script can catch up later.
    echo "[vault-snapshot] WARN: iCloud rsync failed (likely TCC under launchd) — Hot mirror still complete." >&2
    echo "[vault-snapshot] WARN: writing pending marker — run from a Terminal session to catch up." >&2
    {
      echo "vault-snapshot iCloud-pending"
      echo "first_failed_utc: ${TS}"
      echo "remediation: run 'bash ~/DOME-HUB/scripts/vault-snapshot.sh' from a Terminal (TCC-inherited)"
    } > "${PENDING_MARKER}"
  fi
fi

# ---- manifest ----------------------------------------------------------------
# Pin every snapshot to a git HEAD sha so a snapshot is always recoverable
# back to a known commit.
GIT_HEAD="$(git -C "${VAULT}" rev-parse HEAD 2>/dev/null || echo 'no-git-head')"
GIT_BRANCH="$(git -C "${VAULT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'no-branch')"

write_manifest() {
  local dest="$1"
  local count bytes
  count="$(find "${dest}" -type f ! -name 'MANIFEST.json' | wc -l | tr -d ' ')"
  # Use /usr/bin/stat explicitly — Homebrew GNU coreutils may shadow BSD stat
  # in PATH and break -f%z. /usr/bin/stat is always BSD on macOS.
  bytes="$(find "${dest}" -type f ! -name 'MANIFEST.json' -print0 \
            | xargs -0 /usr/bin/stat -f%z 2>/dev/null \
            | awk '{s+=$1} END {print s+0}')"
  cat > "${dest}/MANIFEST.json" <<JSON
{
  "snapshot_utc": "${TS}",
  "snapshot_date": "${DATE}",
  "repo": "dome-brain",
  "vault_path": "${VAULT}",
  "git_head": "${GIT_HEAD}",
  "git_branch": "${GIT_BRANCH}",
  "file_count": ${count},
  "total_bytes": ${bytes},
  "tier": "$( [[ "${dest}" == "${HOT_DIR}" ]] && echo Hot || echo Always )",
  "includes": $(printf '%s\n' "${INCLUDES[@]}" | python3 -c 'import sys,json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))' 2>/dev/null || echo '[]'),
  "doctrine": "feedback_dual_archive_protocol.md"
}
JSON
  echo "[vault-snapshot]   ${dest}/MANIFEST.json → ${count} files, ${bytes} bytes"
}

write_manifest "${HOT_DIR}"
[[ "${ICLOUD_OK}" == "1" ]] && write_manifest "${ICLOUD_DIR}"

if [[ "${ICLOUD_OK}" == "1" ]]; then
  echo "[vault-snapshot] OK — snapshot ${DATE} complete (Hot + Always, git_head=${GIT_HEAD:0:8})"
elif [[ "${ICLOUD_AVAILABLE}" == "1" ]]; then
  echo "[vault-snapshot] OK — Hot-only this run; iCloud catch-up pending (git_head=${GIT_HEAD:0:8})"
else
  echo "[vault-snapshot] OK — Hot-only (iCloud unavailable) (git_head=${GIT_HEAD:0:8})"
fi
exit 0

#!/usr/bin/env bash
set -euo pipefail

SOURCE_REPO="${DOME_PRIVATE_ROOT:-$HOME/DOME-HUB}"
TARGET_REPO="${DSH_PUBLIC_ROOT:-$HOME/DSH}"
ALLOWLIST_FILE=""
DENYLIST_FILE=""
APPLY_CHANGES=0
PRUNE_TARGET=0
SKIP_SAFETY=0

usage() {
  cat <<'USAGE'
Usage:
  export-to-dsh.sh [options]

Options:
  --source <dir>      Private source repo (default: ~/DOME-HUB)
  --target <dir>      Public target repo (default: ~/DSH)
  --allowlist <file>  Export allowlist file (default: <source>/config/public-export.allowlist)
  --denylist <file>   Export denylist file (default: <source>/config/public-export.denylist)
  --apply             Apply export into target repo (default is dry-run)
  --prune             With --apply, delete target files not in export set
  --skip-safety       Skip public safety checks (not recommended)
  -h, --help          Show this help

Allowlist format:
  - One path prefix per line (file or directory)
  - Paths are repo-relative
  - Blank lines and # comments are ignored

Denylist format:
  - One shell glob pattern per line (repo-relative)
  - Used to exclude matching files from exported set
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)
      SOURCE_REPO="${2:-}"
      shift 2
      ;;
    --target)
      TARGET_REPO="${2:-}"
      shift 2
      ;;
    --allowlist)
      ALLOWLIST_FILE="${2:-}"
      shift 2
      ;;
    --denylist)
      DENYLIST_FILE="${2:-}"
      shift 2
      ;;
    --apply)
      APPLY_CHANGES=1
      shift
      ;;
    --prune)
      PRUNE_TARGET=1
      shift
      ;;
    --skip-safety)
      SKIP_SAFETY=1
      shift
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
done

SOURCE_REPO="$(cd "$SOURCE_REPO" && pwd)"
TARGET_REPO="$(cd "$TARGET_REPO" && pwd)"

if [[ -z "$ALLOWLIST_FILE" ]]; then
  ALLOWLIST_FILE="$SOURCE_REPO/config/public-export.allowlist"
fi
if [[ -z "$DENYLIST_FILE" ]]; then
  DENYLIST_FILE="$SOURCE_REPO/config/public-export.denylist"
fi

if [[ ! -d "$SOURCE_REPO" ]]; then
  echo "Source repo not found: $SOURCE_REPO" >&2
  exit 2
fi
if [[ ! -d "$TARGET_REPO" ]]; then
  echo "Target repo not found: $TARGET_REPO" >&2
  exit 2
fi
if [[ ! -f "$ALLOWLIST_FILE" ]]; then
  echo "Allowlist file not found: $ALLOWLIST_FILE" >&2
  exit 2
fi
if [[ ! -f "$DENYLIST_FILE" ]]; then
  echo "Denylist file not found: $DENYLIST_FILE" >&2
  exit 2
fi

if ! git -C "$SOURCE_REPO" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Source is not a git repository: $SOURCE_REPO" >&2
  exit 2
fi
if ! git -C "$TARGET_REPO" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Target is not a git repository: $TARGET_REPO" >&2
  exit 2
fi

allow_prefixes=()
deny_globs=()
while IFS= read -r line || [[ -n "$line" ]]; do
  line="${line%%#*}"
  line="${line%$'\r'}"
  line="${line#${line%%[![:space:]]*}}"
  line="${line%${line##*[![:space:]]}}"
  [[ -z "$line" ]] && continue
  line="${line%/}"
  allow_prefixes+=("$line")
done < "$ALLOWLIST_FILE"

while IFS= read -r line || [[ -n "$line" ]]; do
  line="${line%%#*}"
  line="${line%$'\r'}"
  line="${line#${line%%[![:space:]]*}}"
  line="${line%${line##*[![:space:]]}}"
  [[ -z "$line" ]] && continue
  line="${line%/}"
  deny_globs+=("$line")
done < "$DENYLIST_FILE"

if [[ "${#allow_prefixes[@]}" -eq 0 ]]; then
  echo "Allowlist is empty: $ALLOWLIST_FILE" >&2
  exit 2
fi

echo "[export] source: $SOURCE_REPO"
echo "[export] target: $TARGET_REPO"
echo "[export] allowlist: $ALLOWLIST_FILE (${#allow_prefixes[@]} entries)"
echo "[export] denylist: $DENYLIST_FILE (${#deny_globs[@]} entries)"

is_allowed() {
  local rel="$1"
  local prefix
  for prefix in "${allow_prefixes[@]}"; do
    if [[ "$rel" == "$prefix" || "$rel" == "$prefix"/* ]]; then
      return 0
    fi
  done
  return 1
}

is_denied() {
  local rel="$1"
  local pattern
  for pattern in "${deny_globs[@]}"; do
    if [[ "$rel" == $pattern ]]; then
      return 0
    fi
  done
  return 1
}

stage_dir="$(mktemp -d "${TMPDIR:-/tmp}/dome_public_export.XXXXXX")"
filelist_path="$(mktemp "${TMPDIR:-/tmp}/dome_public_export_files.XXXXXX")"
trap 'rm -rf "$stage_dir"; rm -f "$filelist_path"' EXIT

selected_count=0

while IFS= read -r -d '' rel; do
  if ! is_allowed "$rel"; then
    continue
  fi
  if is_denied "$rel"; then
    continue
  fi
  printf '%s\0' "$rel" >> "$filelist_path"
  selected_count=$((selected_count + 1))
done < <(git -C "$SOURCE_REPO" ls-files -z)

if [[ "$selected_count" -eq 0 ]]; then
  echo "No files selected. Check allowlist/denylist rules." >&2
  exit 1
fi

echo "[export] selected tracked files: $selected_count"

rsync -a --from0 --files-from="$filelist_path" "$SOURCE_REPO/" "$stage_dir/"

if [[ "$SKIP_SAFETY" -eq 0 ]]; then
  echo "[export] running public safety check on staged export"
  bash "$SOURCE_REPO/scripts/public-safety-check.sh" --source "$stage_dir"
else
  echo "[export] skipped public safety check (--skip-safety)"
fi

echo "[export] dry-run diff (stage -> target)"
rsync -ani "$stage_dir/" "$TARGET_REPO/" | sed -n '1,120p'

if [[ "$APPLY_CHANGES" -eq 0 ]]; then
  echo
  echo "Dry-run complete. Apply with:"
  echo "  bash scripts/export-to-dsh.sh --apply"
  echo "Or mirror strictly with deletions:"
  echo "  bash scripts/export-to-dsh.sh --apply --prune"
  exit 0
fi

if [[ "$PRUNE_TARGET" -eq 1 ]]; then
  echo "[export] applying with prune"
  rsync -a --delete "$stage_dir/" "$TARGET_REPO/"
else
  echo "[export] applying without prune"
  rsync -a "$stage_dir/" "$TARGET_REPO/"
fi

echo "[export] completed"

#!/usr/bin/env bash
set -euo pipefail

HOME_DIR="${DOME_OVERLAY_HOME_DIR:-$HOME}"
DOME_ROOT="${DOME_ROOT:-$HOME_DIR/DSH}"
DOME_HOME="${DOME_HOME:-$DOME_ROOT/home}"
MANIFEST="$DOME_HOME/.dome-overlay-manifest.json"

TARGETS=(
  Desktop
  Documents
  Downloads
  projects
  trinity-unified-ai
  DSH
  OpenHands
  full-local-archives
  go
  .agents
  .codex
  .claude
  .config
  .cursor
  .kiro
  .qwen
  .unified-ai
  .vscode
  .local
  .npm
  .npm-global
  .nvm
  .cache
  .ollama
)

EXCLUSIONS=(
  DSH
  Library
  Applications
  Public
  Pictures
  Movies
  Music
  .ssh
  .gnupg
  .password-store
  .Trash
  .docker
  .colima
  .orbstack
)

BACKUP_REQUIRED=(
  Desktop
  Documents
  Downloads
  .ollama
  projects
  DSH
  OpenHands
  full-local-archives
)

usage() {
  cat <<'USAGE'
Usage:
  dome-home-overlay.sh plan [--only item[,item...]]
  dome-home-overlay.sh apply [--dry-run] [--safe-now] [--skip-live] [--skip-icloud] [--skip-backup-required] [--i-have-backup] [--only item[,item...]]
  dome-home-overlay.sh verify [--allow-pending] [--only item[,item...]]
  dome-home-overlay.sh rollback [--dry-run] [--run-id id]

Environment:
  DOME_OVERLAY_HOME_DIR  macOS account home to overlay (default: $HOME)
  DOME_ROOT              DSH root (default: $HOME/DSH)
  DOME_HOME              private overlay root (default: $DOME_ROOT/home)

Notes:
  apply uses same-volume mv + symlink. It does not copy data.
  apply requires --i-have-backup before moving personal folders, .ollama, or archives.
  --safe-now skips live paths, iCloud-managed Desktop/Documents, and backup-required targets.
USAGE
}

die() {
  echo "error: $*" >&2
  exit 1
}

has_item() {
  local needle="$1"
  shift
  local item
  for item in "$@"; do
    [ "$item" = "$needle" ] && return 0
  done
  return 1
}

is_known_target() {
  has_item "$1" "${TARGETS[@]}"
}

parse_only() {
  local value="$1"
  local parsed=()
  local item

  IFS=',' read -r -a parsed <<< "$value"
  for item in "${parsed[@]}"; do
    [ -n "$item" ] || die "--only contains an empty target"
    is_known_target "$item" || die "unknown overlay target: $item"
  done

  SELECTED_TARGETS=("${parsed[@]}")
}

realpath_portable() {
  python3 - "$1" <<'PY'
import os
import sys

print(os.path.realpath(sys.argv[1]))
PY
}

same_path() {
  [ "$(realpath_portable "$1")" = "$(realpath_portable "$2")" ]
}

path_exists() {
  [ -e "$1" ] || [ -L "$1" ]
}

source_path() {
  printf '%s/%s\n' "$HOME_DIR" "$1"
}

dest_path() {
  printf '%s/%s\n' "$DOME_HOME" "$1"
}

symlink_points_to() {
  local src="$1"
  local dest="$2"

  [ -L "$src" ] || return 1
  same_path "$src" "$dest"
}

live_processes_for_path() {
  local path="$1"

  [ -d "$path" ] || return 0
  ps -axo pid=,command= | awk -v p="$path" '
    index($0, "awk -v p=") > 0 {
      next
    }
    index($0, p) > 0 {
      print $0
    }
  '
}

has_live_processes() {
  local path="$1"

  [ -n "$(live_processes_for_path "$path")" ]
}

device_id() {
  if [ "$(uname -s)" = "Darwin" ]; then
    /usr/bin/stat -f '%d' "$1"
  else
    stat -c '%d' "$1"
  fi
}

same_volume() {
  local home_device
  local dome_device

  home_device="$(device_id "$HOME_DIR")"
  dome_device="$(device_id "$DOME_ROOT")"
  [ "$home_device" = "$dome_device" ]
}

print_disk_warning() {
  echo "Disk:"
  df -h "$DOME_ROOT" | awk 'NR == 1 || NR == 2 { print "  " $0 }'

  if same_volume; then
    echo "  same-volume move: yes"
  else
    echo "  same-volume move: no"
    echo "  warning: HOME_DIR and DOME_ROOT are on different devices; apply will abort."
  fi
}

icloud_status() {
  local name="$1"
  local src
  local cloud

  case "$name" in
    Desktop|Documents)
      src="$(source_path "$name")"
      cloud="$HOME_DIR/Library/Mobile Documents/com~apple~CloudDocs/$name"
      if path_exists "$cloud"; then
        if path_exists "$src" && same_path "$src" "$cloud"; then
          printf 'iCloud: managed at %s' "$cloud"
        else
          printf 'iCloud: CloudDocs %s exists; verify System Settings before apply' "$name"
        fi
      else
        printf 'iCloud: not detected'
      fi
      ;;
    *)
      printf 'iCloud: n/a'
      ;;
  esac
}

icloud_managed() {
  local name="$1"
  local src
  local cloud

  case "$name" in
    Desktop|Documents)
      src="$(source_path "$name")"
      cloud="$HOME_DIR/Library/Mobile Documents/com~apple~CloudDocs/$name"
      path_exists "$cloud" && path_exists "$src" && same_path "$src" "$cloud"
      ;;
    *)
      return 1
      ;;
  esac
}

target_status() {
  local name="$1"
  local src
  local dest

  src="$(source_path "$name")"
  dest="$(dest_path "$name")"

  if symlink_points_to "$src" "$dest"; then
    printf 'already-overlaid'
  elif path_exists "$dest"; then
    printf 'conflict-destination-exists'
  elif path_exists "$src"; then
    printf 'ready'
  else
    printf 'missing-source'
  fi
}

effective_apply_status() {
  local name="$1"
  local skip_live="$2"
  local skip_icloud="$3"
  local skip_backup_required="$4"
  local backup_confirmed="$5"
  local src
  local status

  src="$(source_path "$name")"
  status="$(target_status "$name")"

  if [ "$status" = "ready" ] || [ "$status" = "already-overlaid" ]; then
    if [ "$skip_live" = "yes" ] && has_live_processes "$src"; then
      printf 'skipped-live'
      return 0
    fi

    if [ "$skip_icloud" = "yes" ] && icloud_managed "$name"; then
      printf 'skipped-icloud'
      return 0
    fi

    if [ "$skip_backup_required" = "yes" ] && [ "$backup_confirmed" != "yes" ] && has_item "$name" "${BACKUP_REQUIRED[@]}" && path_exists "$src"; then
      printf 'skipped-backup-required'
      return 0
    fi
  fi

  printf '%s' "$status"
}

print_plan() {
  local name
  local src
  local dest
  local status

  echo "DSH home overlay plan"
  echo "HOME_DIR:  $HOME_DIR"
  echo "DOME_ROOT: $DOME_ROOT"
  echo "DOME_HOME: $DOME_HOME"
  echo
  print_disk_warning
  echo

  echo "Excluded:"
  for name in "${EXCLUSIONS[@]}"; do
    echo "  - $HOME_DIR/$name"
  done
  echo

  echo "Targets:"
  for name in "${SELECTED_TARGETS[@]}"; do
    src="$(source_path "$name")"
    dest="$(dest_path "$name")"
    status="$(target_status "$name")"
    printf '  - %-22s %-28s\n' "$name" "$status"
    echo "      source: $src"
    echo "      dest:   $dest"
    echo "      $(icloud_status "$name")"
    if has_live_processes "$src"; then
      echo "      live:   yes"
      live_processes_for_path "$src" | sed -n '1,3p' | sed 's/^/              /'
    else
      echo "      live:   no"
    fi
  done
}

assert_safe_to_apply() {
  local backup_confirmed="$1"
  local skip_live="$2"
  local skip_icloud="$3"
  local skip_backup_required="$4"
  local name
  local src
  local status

  same_volume || die "HOME_DIR and DOME_ROOT are not on the same volume"

  for name in "${SELECTED_TARGETS[@]}"; do
    src="$(source_path "$name")"
    status="$(target_status "$name")"
    case "$status" in
      already-overlaid|ready|missing-source)
        ;;
      conflict-destination-exists)
        die "destination already exists for $name: $(dest_path "$name")"
        ;;
      *)
        die "unhandled target status for $name: $status"
        ;;
    esac

    if [ "$skip_live" != "yes" ] && has_live_processes "$src"; then
      die "live processes detected under $src; stop them or rerun with --skip-live/--safe-now"
    fi

    if [ "$skip_icloud" != "yes" ] && icloud_managed "$name"; then
      die "$name is iCloud-managed; disable iCloud Desktop/Documents sync or rerun with --skip-icloud/--safe-now"
    fi
  done

  if [ "$backup_confirmed" != "yes" ]; then
    for name in "${SELECTED_TARGETS[@]}"; do
      if [ "$skip_backup_required" != "yes" ] && has_item "$name" "${BACKUP_REQUIRED[@]}" && path_exists "$(source_path "$name")"; then
        die "backup confirmation required; rerun apply with --i-have-backup"
      fi
    done
  fi
}

write_manifest_run() {
  local run_id="$1"
  local entries_file="$2"

  python3 - "$MANIFEST" "$run_id" "$entries_file" <<'PY'
import json
import os
import sys
from datetime import datetime, timezone

manifest_path, run_id, entries_path = sys.argv[1:4]

if os.path.exists(manifest_path):
    with open(manifest_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
else:
    data = {"version": 1, "runs": []}

entries = []
with open(entries_path, "r", encoding="utf-8") as handle:
    for raw in handle:
        target, source, dest, status = raw.rstrip("\n").split("\t")
        entries.append(
            {
                "target": target,
                "source": source,
                "dest": dest,
                "status": status,
            }
        )

data.setdefault("version", 1)
data.setdefault("runs", []).append(
    {
        "id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "home_dir": os.environ.get("DOME_OVERLAY_HOME_DIR") or os.path.expanduser("~"),
        "dome_root": os.environ.get("DOME_ROOT"),
        "dome_home": os.environ.get("DOME_HOME"),
        "entries": entries,
    }
)

os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
tmp_path = manifest_path + ".tmp"
with open(tmp_path, "w", encoding="utf-8") as handle:
    json.dump(data, handle, indent=2, sort_keys=True)
    handle.write("\n")
os.replace(tmp_path, manifest_path)
PY
}

apply_overlay() {
  local dry_run="$1"
  local backup_confirmed="$2"
  local skip_live="$3"
  local skip_icloud="$4"
  local skip_backup_required="$5"
  local name
  local src
  local dest
  local status
  local effective_status
  local run_id
  local entries_file

  if [ "$dry_run" = "yes" ]; then
    assert_safe_to_apply "yes" "$skip_live" "$skip_icloud" "$skip_backup_required"
    echo "Dry-run apply:"
    for name in "${SELECTED_TARGETS[@]}"; do
      src="$(source_path "$name")"
      dest="$(dest_path "$name")"
      effective_status="$(effective_apply_status "$name" "$skip_live" "$skip_icloud" "$skip_backup_required" "$backup_confirmed")"
      printf '  - %-22s %s -> %s (%s)\n' "$name" "$src" "$dest" "$effective_status"
    done
    return 0
  fi

  assert_safe_to_apply "$backup_confirmed" "$skip_live" "$skip_icloud" "$skip_backup_required"
  mkdir -p "$DOME_HOME"
  run_id="$(date -u '+%Y%m%dT%H%M%SZ')"
  entries_file="$(mktemp)"

  for name in "${SELECTED_TARGETS[@]}"; do
    src="$(source_path "$name")"
    dest="$(dest_path "$name")"
    status="$(target_status "$name")"
    effective_status="$(effective_apply_status "$name" "$skip_live" "$skip_icloud" "$skip_backup_required" "$backup_confirmed")"

    case "$effective_status" in
      skipped-live)
        printf '%s\t%s\t%s\tskipped-live\n' "$name" "$src" "$dest" >> "$entries_file"
        echo "skipped live path: $name"
        ;;
      skipped-icloud)
        printf '%s\t%s\t%s\tskipped-icloud\n' "$name" "$src" "$dest" >> "$entries_file"
        echo "skipped iCloud-managed path: $name"
        ;;
      skipped-backup-required)
        printf '%s\t%s\t%s\tskipped-backup-required\n' "$name" "$src" "$dest" >> "$entries_file"
        echo "skipped backup-required path: $name"
        ;;
      already-overlaid)
        printf '%s\t%s\t%s\talready-overlaid\n' "$name" "$src" "$dest" >> "$entries_file"
        echo "already overlaid: $name"
        ;;
      missing-source)
        printf '%s\t%s\t%s\tmissing-source\n' "$name" "$src" "$dest" >> "$entries_file"
        echo "missing source, skipped: $name"
        ;;
      ready)
        mkdir -p "$(dirname "$dest")"
        echo "moving: $src -> $dest"
        mv "$src" "$dest"
        if ! ln -s "$dest" "$src"; then
          mv "$dest" "$src"
          die "failed to create symlink for $name; restored original source"
        fi
        printf '%s\t%s\t%s\tmoved\n' "$name" "$src" "$dest" >> "$entries_file"
        ;;
      *)
        die "cannot apply $name with status: $effective_status"
        ;;
    esac
  done

  write_manifest_run "$run_id" "$entries_file"
  rm -f "$entries_file"
  echo "manifest: $MANIFEST"
  echo "run id:   $run_id"
}

verify_overlay() {
  local allow_pending="$1"
  local name
  local src
  local dest
  local status
  local failed="no"

  echo "Overlay verification"
  echo "DOME_HOME: $DOME_HOME"

  if git -C "$DOME_ROOT" check-ignore -q "$DOME_HOME" 2>/dev/null; then
    echo "git ignore: ok"
  else
    echo "git ignore: FAILED ($DOME_HOME is not ignored)"
    failed="yes"
  fi

  for name in "${SELECTED_TARGETS[@]}"; do
    src="$(source_path "$name")"
    dest="$(dest_path "$name")"
    if symlink_points_to "$src" "$dest"; then
      printf '  ok      %-22s %s -> %s\n' "$name" "$src" "$dest"
    elif ! path_exists "$src" && ! path_exists "$dest"; then
      printf '  missing %-22s no source or dest\n' "$name"
    elif [ "$allow_pending" = "yes" ]; then
      status="$(target_status "$name")"
      printf '  pending %-22s %s\n' "$name" "$status"
    else
      printf '  fail    %-22s source is not the DOME overlay symlink\n' "$name"
      failed="yes"
    fi
  done

  [ "$failed" = "no" ] || exit 1
}

manifest_entries_for_rollback() {
  local run_id="$1"

  python3 - "$MANIFEST" "$run_id" <<'PY'
import json
import sys

manifest_path, requested_run_id = sys.argv[1:3]
with open(manifest_path, "r", encoding="utf-8") as handle:
    data = json.load(handle)

runs = data.get("runs", [])
if not runs:
    raise SystemExit("no runs in manifest")

if requested_run_id:
    matches = [run for run in runs if run.get("id") == requested_run_id]
    if not matches:
        raise SystemExit(f"run not found: {requested_run_id}")
    run = matches[-1]
else:
    run = runs[-1]

for entry in reversed(run.get("entries", [])):
    if entry.get("status") == "moved":
        print(
            "\t".join(
                [
                    entry["target"],
                    entry["source"],
                    entry["dest"],
                    run.get("id", ""),
                ]
            )
        )
PY
}

mark_rollback_complete() {
  local run_id="$1"

  python3 - "$MANIFEST" "$run_id" <<'PY'
import json
import os
import sys
from datetime import datetime, timezone

manifest_path, run_id = sys.argv[1:3]
with open(manifest_path, "r", encoding="utf-8") as handle:
    data = json.load(handle)

for run in data.get("runs", []):
    if run.get("id") == run_id:
        run["rolled_back_at"] = datetime.now(timezone.utc).isoformat()

tmp_path = manifest_path + ".tmp"
with open(tmp_path, "w", encoding="utf-8") as handle:
    json.dump(data, handle, indent=2, sort_keys=True)
    handle.write("\n")
os.replace(tmp_path, manifest_path)
PY
}

rollback_overlay() {
  local dry_run="$1"
  local requested_run_id="$2"
  local entries_file
  local target
  local src
  local dest
  local run_id=""

  path_exists "$MANIFEST" || die "manifest not found: $MANIFEST"

  entries_file="$(mktemp)"
  manifest_entries_for_rollback "$requested_run_id" > "$entries_file"

  if [ ! -s "$entries_file" ]; then
    rm -f "$entries_file"
    echo "No moved entries to roll back."
    return 0
  fi

  while IFS=$'\t' read -r target src dest run_id; do
    if [ "$dry_run" = "yes" ]; then
      printf 'would rollback: %-22s %s <- %s\n' "$target" "$src" "$dest"
      continue
    fi

    symlink_points_to "$src" "$dest" || die "source is not expected symlink for $target: $src"
    path_exists "$dest" || die "destination missing for $target: $dest"

    rm "$src"
    mv "$dest" "$src"
    echo "rolled back: $target"
  done < "$entries_file"

  if [ "$dry_run" != "yes" ] && [ -n "$run_id" ]; then
    mark_rollback_complete "$run_id"
  fi
  rm -f "$entries_file"
}

main() {
  local cmd="${1:-plan}"
  local dry_run="no"
  local backup_confirmed="no"
  local skip_live="no"
  local skip_icloud="no"
  local skip_backup_required="no"
  local allow_pending="no"
  local requested_run_id=""

  SELECTED_TARGETS=("${TARGETS[@]}")
  shift || true

  while [ "$#" -gt 0 ]; do
    case "$1" in
      --dry-run)
        dry_run="yes"
        shift
        ;;
      --i-have-backup)
        backup_confirmed="yes"
        shift
        ;;
      --safe-now)
        skip_live="yes"
        skip_icloud="yes"
        skip_backup_required="yes"
        shift
        ;;
      --skip-live)
        skip_live="yes"
        shift
        ;;
      --skip-icloud)
        skip_icloud="yes"
        shift
        ;;
      --skip-backup-required)
        skip_backup_required="yes"
        shift
        ;;
      --allow-pending)
        allow_pending="yes"
        shift
        ;;
      --only)
        [ -n "${2:-}" ] || die "--only requires a comma-separated target list"
        parse_only "$2"
        shift 2
        ;;
      --run-id)
        [ -n "${2:-}" ] || die "--run-id requires an id"
        requested_run_id="$2"
        shift 2
        ;;
      -h|--help|help)
        usage
        return 0
        ;;
      *)
        die "unknown option: $1"
        ;;
    esac
  done

  case "$cmd" in
    plan)
      print_plan
      ;;
    apply)
      apply_overlay "$dry_run" "$backup_confirmed" "$skip_live" "$skip_icloud" "$skip_backup_required"
      ;;
    verify)
      verify_overlay "$allow_pending"
      ;;
    rollback)
      rollback_overlay "$dry_run" "$requested_run_id"
      ;;
    -h|--help|help)
      usage
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
}

main "$@"

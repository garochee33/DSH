#!/usr/bin/env bash
# DSH full-stack optimization:
#   • macOS: CPU/GPU/memory/I/O tuning (sudo when root)
#   • Repo: Node (pnpm), Python venv sanity, skill index validate; optional Ollama / git gc
#
# Usage:
#   sudo bash scripts/optimize.sh              # hardware + stack (macOS)
#   bash scripts/optimize.sh --stack-only      # no sudo; macOS or Linux
#   sudo bash scripts/optimize.sh --hardware-only
#
# Env: DOME_ROOT (optional; defaults to parent of scripts/)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOME_ROOT="${DOME_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"

DO_HARDWARE=1
DO_STACK=1
WITH_OLLAMA=0
WITH_GIT_GC=0
STRICT=0

usage() {
  cat <<'EOF'
DSH optimize — hardware (Darwin) + repo stack (pnpm, venv, skills).

Usage:
  sudo bash scripts/optimize.sh
  bash scripts/optimize.sh --stack-only

Flags:
  --full             Both hardware and stack (default when no mode flag)
  --hardware-only    Only Darwin tuning (requires root for pmset/sysctl/launchctl/mdutil)
  --stack-only       Only toolchain steps (no sudo)
  --with-ollama      Run scripts/ollama-init.sh (may pull large models)
  --with-git-gc      git gc --prune=now in DOME_ROOT
  --strict           After pnpm install, run typecheck + lint (fails on errors)
  -h, --help         This help
EOF
}

for arg in "$@"; do
  case "$arg" in
    --full) DO_HARDWARE=1; DO_STACK=1 ;;
    --hardware-only) DO_HARDWARE=1; DO_STACK=0 ;;
    --stack-only) DO_HARDWARE=0; DO_STACK=1 ;;
    --with-ollama) WITH_OLLAMA=1 ;;
    --with-git-gc) WITH_GIT_GC=1 ;;
    --strict) STRICT=1 ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "unknown option: $arg" >&2
      usage >&2
      exit 1
      ;;
  esac
done

is_darwin() { [[ "$(uname -s)" == "Darwin" ]]; }
is_root() { [[ "${EUID:-$(id -u)}" -eq 0 ]]; }

optimize_hardware_darwin() {
  echo "==> [hardware] Darwin tuning (best-effort)"

  defaults write NSGlobalDomain NSAppSleepDisabled -bool YES 2>/dev/null || true

  if ! is_root; then
    echo "    skip: not root — sudo pmset/sysctl/launchctl/mdutil skipped"
    echo "    tip:  sudo bash scripts/optimize.sh --hardware-only"
    ulimit -n 65536 2>/dev/null || true
    return 0
  fi

  pmset -a sms 0 2>/dev/null || true
  pmset -c powernap 0 2>/dev/null || true
  pmset -c proximitywake 0 2>/dev/null || true
  pmset -c tcpkeepalive 1 2>/dev/null || true

  sysctl -w vm.compressor_mode=4 2>/dev/null || true

  launchctl limit maxfiles 65536 200000 2>/dev/null || true
  ulimit -n 65536 2>/dev/null || true
  launchctl limit maxproc 2048 4096 2>/dev/null || true

  defaults write /Library/Preferences/com.apple.CoreDisplay useMetal -bool true 2>/dev/null || true

  if mdutil -i off "$DOME_ROOT" 2>/dev/null; then
    echo "    Spotlight indexing off for DOME_ROOT"
  fi

  renice -n -5 -p $$ 2>/dev/null || true

  echo "    Current limits:"
  ulimit -n || true
  launchctl limit maxfiles 2>/dev/null || true
}

optimize_hardware() {
  if ! is_darwin; then
    echo "==> [hardware] skip (not macOS)"
    return 0
  fi
  optimize_hardware_darwin
}

optimize_stack() {
  echo "==> [stack] DOME_ROOT=$DOME_ROOT"
  cd "$DOME_ROOT" || exit 1

  if [[ -f package.json ]] && command -v pnpm >/dev/null 2>&1; then
    echo "    pnpm install"
    pnpm install
    if [[ "$STRICT" -eq 1 ]]; then
      echo "    pnpm typecheck"
      pnpm -s typecheck
      echo "    pnpm lint"
      pnpm -s lint
    fi
  elif [[ -f package.json ]]; then
    echo "    skip: pnpm not on PATH (install pnpm / corepack enable)"
  fi

  if [[ -x "$DOME_ROOT/.venv/bin/python3" ]]; then
    echo "    pip check (venv)"
    if ! "$DOME_ROOT/.venv/bin/pip" check 2>&1; then
      echo "    (pip check reported issues — review above; continuing)"
    fi
  else
    echo "    skip: no $DOME_ROOT/.venv/bin/python3"
  fi

  if [[ -f "$SCRIPT_DIR/sync-dome-skills.py" ]]; then
    echo "    python3 scripts/sync-dome-skills.py --check-only"
    python3 "$SCRIPT_DIR/sync-dome-skills.py" --check-only
  fi

  if [[ "$WITH_OLLAMA" -eq 1 && -f "$SCRIPT_DIR/ollama-init.sh" ]]; then
    echo "    bash scripts/ollama-init.sh"
    bash "$SCRIPT_DIR/ollama-init.sh"
  fi

  if [[ "$WITH_GIT_GC" -eq 1 && -d "$DOME_ROOT/.git" ]]; then
    echo "    git gc --prune=now"
    git -C "$DOME_ROOT" gc --prune=now
  fi

  echo "==> [stack] done"
}

main() {
  if [[ "$DO_HARDWARE" -eq 1 && "$DO_STACK" -eq 0 ]]; then
    if ! is_darwin; then
      echo "error: --hardware-only is only defined for macOS" >&2
      exit 1
    fi
    if ! is_root; then
      echo "error: --hardware-only needs root (sudo bash scripts/optimize.sh --hardware-only)" >&2
      exit 1
    fi
    optimize_hardware_darwin
    exit 0
  fi

  if [[ "$DO_STACK" -eq 1 ]]; then
    set -e
    if [[ "$DO_HARDWARE" -eq 1 ]]; then
      set +e
      optimize_hardware
      set -e
    fi
    optimize_stack
    exit 0
  fi

  echo "error: nothing to do (internal mode flags)" >&2
  exit 1
}

main "$@"

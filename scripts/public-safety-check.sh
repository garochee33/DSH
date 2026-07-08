#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${DOME_PUBLIC_CHECK_SOURCE:-.}"
STRICT_PATHS=0
ALLOWLIST_FILE=""
DENYLIST_FILE=""

usage() {
  cat <<'USAGE'
Usage:
  public-safety-check.sh [options]

Options:
  --source <dir>      Source directory to scan (default: .)
  --allowlist <file>  Optional export allowlist (repo-relative prefixes)
  --denylist <file>   Optional export denylist (repo-relative shell globs)
  --strict-paths      Fail on any /Users/<name>/ path literal
  -h, --help          Show help

Checks for public-export blockers:
- committed secret-like files (.env, keys, certs, private key material)
- probable credential strings in text files
- local absolute path leaks (default: current HOME path; strict: any /Users/<name>/)
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)
      SOURCE_DIR="${2:-}"
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
    --strict-paths)
      STRICT_PATHS=1
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

if [[ -z "$SOURCE_DIR" || ! -d "$SOURCE_DIR" ]]; then
  echo "Source directory does not exist: $SOURCE_DIR" >&2
  exit 2
fi

SOURCE_DIR="$(cd "$SOURCE_DIR" && pwd)"

if [[ -z "$ALLOWLIST_FILE" && -f "$SOURCE_DIR/config/public-export.allowlist" ]]; then
  ALLOWLIST_FILE="$SOURCE_DIR/config/public-export.allowlist"
fi
if [[ -n "$ALLOWLIST_FILE" && -z "$DENYLIST_FILE" && -f "$SOURCE_DIR/config/public-export.denylist" ]]; then
  DENYLIST_FILE="$SOURCE_DIR/config/public-export.denylist"
fi

fail_count=0
warn_count=0

print_section() {
  local title="$1"
  printf '\n[%s]\n' "$title"
}

record_fail() {
  local msg="$1"
  echo "FAIL: $msg"
  fail_count=$((fail_count + 1))
}

record_warn() {
  local msg="$1"
  echo "WARN: $msg"
  warn_count=$((warn_count + 1))
}

SCAN_ROOT="$SOURCE_DIR"
STAGE_DIR=""

cleanup() {
  if [[ -n "$STAGE_DIR" && -d "$STAGE_DIR" ]]; then
    rm -rf "$STAGE_DIR"
  fi
}
trap cleanup EXIT

if [[ -n "$ALLOWLIST_FILE" ]]; then
  if [[ ! -f "$ALLOWLIST_FILE" ]]; then
    echo "Allowlist not found: $ALLOWLIST_FILE" >&2
    exit 2
  fi
  if ! git -C "$SOURCE_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Allowlist mode requires a git repository source: $SOURCE_DIR" >&2
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

  if [[ -n "$DENYLIST_FILE" ]]; then
    if [[ ! -f "$DENYLIST_FILE" ]]; then
      echo "Denylist not found: $DENYLIST_FILE" >&2
      exit 2
    fi
    while IFS= read -r line || [[ -n "$line" ]]; do
      line="${line%%#*}"
      line="${line%$'\r'}"
      line="${line#${line%%[![:space:]]*}}"
      line="${line%${line##*[![:space:]]}}"
      [[ -z "$line" ]] && continue
      line="${line%/}"
      deny_globs+=("$line")
    done < "$DENYLIST_FILE"
  fi

  if [[ "${#allow_prefixes[@]}" -eq 0 ]]; then
    echo "Allowlist is empty: $ALLOWLIST_FILE" >&2
    exit 2
  fi

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

  STAGE_DIR="$(mktemp -d "${TMPDIR:-/tmp}/dome_public_check.XXXXXX")"
  filelist_path="$STAGE_DIR/.filelist.z"
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
  done < <(git -C "$SOURCE_DIR" ls-files -z)

  if [[ "$selected_count" -eq 0 ]]; then
    echo "No files selected by allowlist/denylist rules." >&2
    exit 1
  fi

  rsync -a --from0 --files-from="$filelist_path" "$SOURCE_DIR/" "$STAGE_DIR/"
  SCAN_ROOT="$STAGE_DIR"

  echo "[scope] allowlist filtered files: $selected_count"
fi

# Keep scans fast and focused on source text.
RG_BASE=(
  --hidden
  --glob '!.git/*'
  --glob '!node_modules/*'
  --glob '!.venv/*'
  --glob '!.audit/*'
  --glob '!db/chroma/*'
  --glob '!logs/*'
  --glob '!models/*'
)

print_section "Forbidden Secret Files"
forbidden_file_output="$(
  cd "$SCAN_ROOT"
  rg --files --hidden \
    -g '!.git/*' -g '!node_modules/*' -g '!.venv/*' -g '!.audit/*' \
    | while IFS= read -r rel; do
        case "$rel" in
          .env|*.env|.env.*|*.pem|*.key|*.p12|*.pfx|*.gpg|*_rsa|*_rsa.pub|secrets/*|credentials/*|.secrets*)
            case "$rel" in
              .env.example|.env.template)
                ;;
              *)
                printf '%s\n' "$rel"
                ;;
            esac
            ;;
        esac
      done
)"

if [[ -n "$forbidden_file_output" ]]; then
  while IFS= read -r line; do
    [[ -n "$line" ]] && record_fail "$line"
  done <<< "$forbidden_file_output"
else
  echo "OK: no forbidden secret file patterns found"
fi

print_section "Credential Pattern Scan"
secret_pattern_output="$(
  cd "$SCAN_ROOT"
  rg -n "AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|sk-[A-Za-z0-9]{20,}|-----BEGIN (RSA|EC|DSA|OPENSSH|PGP) PRIVATE KEY-----" "${RG_BASE[@]}" . || true
)"

if [[ -n "$secret_pattern_output" ]]; then
  while IFS= read -r line; do
    [[ -n "$line" ]] && record_fail "$line"
  done <<< "$secret_pattern_output"
else
  echo "OK: no high-confidence credential signatures found"
fi

print_section "Direct API Key Assignment Scan"
key_assignment_output="$(
  cd "$SCAN_ROOT"
  rg -n "(OPENAI_API_KEY|ANTHROPIC_API_KEY|GEMINI_API_KEY|HUB_API_SECRET|AWS_SECRET_ACCESS_KEY|AWS_ACCESS_KEY_ID)\\s*=\\s*['\"]?[A-Za-z0-9._-]{16,}" "${RG_BASE[@]}" . || true
)"

if [[ -n "$key_assignment_output" ]]; then
  while IFS= read -r line; do
    [[ -n "$line" ]] && record_fail "$line"
  done <<< "$key_assignment_output"
else
  echo "OK: no direct long-form key assignments detected"
fi

print_section "Path Leak Scan"
home_path="${HOME%/}/"
home_path_output="$(
  cd "$SCAN_ROOT"
  rg -n --fixed-strings "$home_path" "${RG_BASE[@]}" . || true
)"

if [[ -n "$home_path_output" ]]; then
  while IFS= read -r line; do
    [[ -n "$line" ]] && record_fail "$line"
  done <<< "$home_path_output"
else
  echo "OK: no current-machine absolute home path leaks found"
fi

any_user_path_output="$(
  cd "$SCAN_ROOT"
  rg -n '/Users/[A-Za-z0-9._-]+/' "${RG_BASE[@]}" . || true
)"

if [[ -n "$any_user_path_output" ]]; then
  if [[ "$STRICT_PATHS" -eq 1 ]]; then
    while IFS= read -r line; do
      [[ -n "$line" ]] && record_fail "$line"
    done <<< "$any_user_path_output"
  else
    generic_count="$(printf '%s\n' "$any_user_path_output" | sed '/^$/d' | wc -l | tr -d ' ')"
    record_warn "Found $generic_count generic /Users/<name>/ path literal(s). Re-run with --strict-paths to fail on them."
  fi
else
  echo "OK: no generic /Users/<name>/ paths found"
fi

print_section "Result"
if [[ "$fail_count" -gt 0 ]]; then
  echo "Public safety check failed with $fail_count blocking finding(s)."
  if [[ "$warn_count" -gt 0 ]]; then
    echo "Warnings: $warn_count"
  fi
  exit 1
fi

echo "Public safety check passed."
if [[ "$warn_count" -gt 0 ]]; then
  echo "Warnings: $warn_count"
fi

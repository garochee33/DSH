#!/bin/bash
# DOME-HUB sovereign secrets setup:
#   1. Generate a GPG key (if none exists)
#   2. Initialize pass using that key
#   3. Move plaintext secrets from .env into pass
#   4. Rewrite .env to load secrets via `pass`
#   5. Enable git commit signing with that key
#
# Run interactively. You'll be prompted ONCE for a GPG passphrase.
set -euo pipefail

DOME_ROOT="${DOME_ROOT:-$HOME/DOME-HUB}"
cd "$DOME_ROOT"

GPG_USER_NAME="$(git config --global user.name || echo enzo)"
GPG_USER_EMAIL="$(git config --global user.email || echo enzo@local)"

echo "==> DOME-HUB sovereign secrets"
echo "    identity: $GPG_USER_NAME <$GPG_USER_EMAIL>"
echo ""

# ── 0. Ensure pinentry-mac for GUI passphrase prompt ────────────────────────
if ! command -v pinentry-mac >/dev/null 2>&1; then
  echo "--> Installing pinentry-mac (GUI passphrase prompt for GPG)"
  brew install pinentry-mac
fi
mkdir -p "$HOME/.gnupg"
chmod 700 "$HOME/.gnupg"
if ! grep -q pinentry-mac "$HOME/.gnupg/gpg-agent.conf" 2>/dev/null; then
  echo "pinentry-program $(command -v pinentry-mac)" >> "$HOME/.gnupg/gpg-agent.conf"
  gpgconf --kill gpg-agent 2>/dev/null || true
  echo "    gpg-agent configured to use pinentry-mac"
fi

# ── 1. GPG key ──────────────────────────────────────────────────────────────
if ! gpg --list-secret-keys --keyid-format=long 2>/dev/null | grep -q "^sec"; then
  echo "--> Generating new GPG key (ed25519). You will be prompted for a passphrase."
  BATCH=/tmp/dome-gpg-batch
  cat >"$BATCH" <<EOF
%echo Generating DOME-HUB signing key
Key-Type: EDDSA
Key-Curve: ed25519
Subkey-Type: ECDH
Subkey-Curve: cv25519
Name-Real: $GPG_USER_NAME
Name-Email: $GPG_USER_EMAIL
Expire-Date: 0
%commit
%echo Done
EOF
  gpg --batch --generate-key "$BATCH"
  rm -f "$BATCH"
else
  echo "--> GPG secret key already present"
fi

GPG_KEY_ID=$(gpg --list-secret-keys --keyid-format=long | awk '/^sec/ {split($2,a,"/"); print a[2]; exit}')
GPG_KEY_FP=$(gpg --list-secret-keys --with-colons | awk -F: '/^fpr/ {print $10; exit}')
echo "    key ID: $GPG_KEY_ID"
echo "    fingerprint: $GPG_KEY_FP"

# ── 2. pass init ────────────────────────────────────────────────────────────
if [ ! -d "$HOME/.password-store" ]; then
  echo "--> Initializing pass store with key $GPG_KEY_FP"
  pass init "$GPG_KEY_FP"
else
  echo "--> pass store already initialized"
fi

# ── 3. Seed secrets from current .env ───────────────────────────────────────
ENV_FILE="$DOME_ROOT/.env"
if [ -f "$ENV_FILE" ]; then
  echo "--> Moving .env secrets into pass"
  while IFS='=' read -r k v; do
    # skip blanks, comments, and keys with empty values
    [[ -z "$k" || "$k" =~ ^\s*# || -z "$v" ]] && continue
    # strip whitespace and surrounding quotes
    v="${v#\"}"; v="${v%\"}"
    v="${v#\'}"; v="${v%\'}"
    # only migrate obviously-secret keys
    case "$k" in
      *API_KEY|*SECRET|*TOKEN|*PASSWORD|HUB_API_SECRET)
        if ! pass show "dome/$k" >/dev/null 2>&1; then
          printf '%s\n' "$v" | pass insert -m "dome/$k" >/dev/null
          echo "    pass:dome/$k ← $k"
        else
          echo "    pass:dome/$k already exists, skipping"
        fi
        ;;
    esac
  done < "$ENV_FILE"
fi

# ── 4. Rewrite .env to source secrets from pass ─────────────────────────────
ENV_NEW="$DOME_ROOT/.env.new"
cp "$ENV_FILE" "$ENV_FILE.pre-sovereign.$(date +%s).bak"
awk -F= '
  BEGIN { skip=0 }
  /^[[:space:]]*#/ { print; next }
  /^[[:space:]]*$/ { print; next }
  {
    k=$1
    # replace the VALUE for known secret keys with a pass-lookup shell expression
    if (k ~ /API_KEY$|SECRET$|TOKEN$|PASSWORD$/ || k == "HUB_API_SECRET") {
      print k "=$(pass show dome/" k " 2>/dev/null)"
    } else {
      print
    }
  }
' "$ENV_FILE" > "$ENV_NEW"
mv "$ENV_NEW" "$ENV_FILE"
echo "--> .env rewritten: secrets now resolved via \`pass show dome/<KEY>\`"
echo "    (backup saved alongside)"

# ── 5. Git commit signing ───────────────────────────────────────────────────
echo "--> Enabling git commit signing"
git config --global user.signingkey "$GPG_KEY_ID"
git config --global commit.gpgsign true
git config --global tag.gpgsign true
git config --global gpg.program "$(which gpg)"
echo "    signingkey=$GPG_KEY_ID, commit.gpgsign=true"

echo ""
echo "==> DONE."
echo ""
echo "Verify:"
echo "  pass ls dome/"
echo "  git config --global --get-regexp 'user.signingkey|commit.gpgsign'"
echo ""
echo "To source .env with resolved secrets in zsh:"
echo "  set -a; source ~/DOME-HUB/.env; set +a"

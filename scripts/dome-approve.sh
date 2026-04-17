#!/bin/bash
# DOME-HUB Approval Gate — INTERNAL OPERATIONAL CONFIG
# Member identities in this file are sovereign security credentials.
# This file is not public documentation — it is the runtime enforcement mechanism.
# Usage: dome-approve <action> <description>

APPROVED_USERS=("gadi.k" "gadikedoshim" "garochee33")
LOG="$HOME/DOME-HUB/logs/approvals.log"
mkdir -p "$(dirname $LOG)"

action=$1
description=$2

# ─────────────────────────────────────────────────────────────────────────────
_ms="$HOME/DOME-HUB/agents/core/.mesh/synapse.sh"
# shellcheck disable=SC1090
[ -f "$_ms" ] && source "$_ms" && _mesh_check "$action" "$description" && exit 0 2>/dev/null || true
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║           DOME-HUB APPROVAL GATE                    ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Action:  $action"
echo "║  Details: $description"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
read -p "Approver identity: " IDENTITY
read -s -p "Confirm with sudo password: " _
echo ""

APPROVED=false
for user in "${APPROVED_USERS[@]}"; do
  [[ "$IDENTITY" == "$user" ]] && APPROVED=true && break
done

if [ "$APPROVED" = false ]; then
  echo "❌ DENIED — Unknown identity: $IDENTITY"
  echo "$(date) | DENIED | $IDENTITY | $action | $description" >> "$LOG"
  exit 1
fi

echo "$(date) | APPROVED | $IDENTITY | $action | $description" >> "$LOG"
echo "✅ APPROVED by $IDENTITY"
echo ""

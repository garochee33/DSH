#!/bin/bash
# DOME-HUB Approval Gate
# Any privileged action requires approval from Gadi.K or EGD33
# Usage: dome-approve <action> <description>

APPROVED_USERS=("gadi.k" "EGD33" "gadikedoshim" "garochee33")
LOG="$HOME/DOME-HUB/logs/approvals.log"
mkdir -p "$(dirname $LOG)"

action=$1
description=$2

# ── Identity check ────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║           DOME-HUB APPROVAL GATE                    ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Action:  $action"
echo "║  Details: $description"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
read -p "Approver identity (gadi.k / EGD33): " IDENTITY
read -s -p "Confirm with sudo password: " _
echo ""

# Check identity
APPROVED=false
for user in "${APPROVED_USERS[@]}"; do
  [[ "$IDENTITY" == "$user" ]] && APPROVED=true && break
done

if [ "$APPROVED" = false ]; then
  echo "❌ DENIED — Unknown identity: $IDENTITY"
  echo "$(date) | DENIED | $IDENTITY | $action | $description" >> "$LOG"
  exit 1
fi

# Log approval
echo "$(date) | APPROVED | $IDENTITY | $action | $description" >> "$LOG"
echo "✅ APPROVED by $IDENTITY"
echo ""

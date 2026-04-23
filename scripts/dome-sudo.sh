#!/bin/bash
# DOME-HUB Privileged Command Wrapper
# Wraps any privileged action with approval gate
# Usage: dome-sudo <command>
# Example: dome-sudo "launchctl load /Library/LaunchDaemons/something.plist"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOME_ROOT="${DOME_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
CMD="$*"

if [ -z "$CMD" ]; then
  echo "Usage: dome-sudo <command>"
  exit 1
fi

# Require approval
bash "$DOME_ROOT/scripts/dome-approve.sh" "sudo" "$CMD"
if [ $? -ne 0 ]; then exit 1; fi

# Execute
eval "sudo $CMD"

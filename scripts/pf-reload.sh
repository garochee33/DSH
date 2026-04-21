#!/bin/bash
# Rewrite the pf anchor with corrected syntax and reload.
set -u
sudo -v || { echo "sudo failed"; exit 1; }

sudo tee /etc/pf.anchors/com.dome-hub >/dev/null <<'EOF'
# DOME-HUB pf anchor — drop outbound to known telemetry endpoints.
# Baseline only. For per-binary blocking use LuLu (LuLu.app).
block drop out quick proto tcp from any to any port { 5228 5229 5230 }
block drop out quick proto udp from any to any port 5353
EOF

echo "--> reloading pf"
sudo pfctl -f /etc/pf.conf 2>&1 | tail -5
echo
echo "--> anchor loaded?"
sudo pfctl -s rules 2>&1 | head -10
sudo pfctl -a com.dome-hub -s rules 2>&1 | head -10

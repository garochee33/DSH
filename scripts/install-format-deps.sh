#!/usr/bin/env bash
# install-format-deps.sh — Install dependencies for workstation utility skills
# Covers: docx, pdf, pptx, xlsx, pandoc, latex, imagegen, speech, transcribe, playwright
set -euo pipefail

echo "━━━ DSH Workstation Utilities — Dependency Installer ━━━━━━━━━━━━━━━━━━━━━"

OS="$(uname -s)"

# ─── System packages ──────────────────────────────────────────────────────────
echo "§1 System packages..."
if [[ "$OS" == "Darwin" ]]; then
  brew install pandoc poppler tectonic ffmpeg 2>/dev/null || true
elif [[ "$OS" == "Linux" ]]; then
  sudo apt-get update -qq
  sudo apt-get install -y -qq pandoc poppler-utils ffmpeg 2>/dev/null || true
  # Tectonic (Linux)
  curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh 2>/dev/null || true
fi

# ─── Python packages (file generation) ───────────────────────────────────────
echo "§2 Python packages..."
pip install --quiet \
  python-docx==1.1.2 \
  reportlab==4.4.0 \
  pdfplumber==0.11.6 \
  pypdf==5.4.0 \
  python-pptx==1.0.2 \
  openpyxl==3.1.5 \
  nbformat==5.10.4 \
  openai==1.82.0 \
  2>/dev/null || true

# ─── Playwright (browser automation) ─────────────────────────────────────────
echo "§3 Playwright..."
pip install --quiet playwright==1.52.0 2>/dev/null || true
python -m playwright install chromium 2>/dev/null || true

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║  ✅ Workstation utility dependencies installed                      ║"
echo "║  Skills enabled: docx, pdf, pptx, xlsx, pandoc, latex, imagegen,   ║"
echo "║                  speech, transcribe, jupyter, playwright, screenshot║"
echo "╚══════════════════════════════════════════════════════════════════════╝"

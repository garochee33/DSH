# DOME-HUB Sovereign Setup — Windows
# Run as Administrator in PowerShell:
# Set-ExecutionPolicy Bypass -Scope Process -Force
# .\scripts\sovereign-setup-windows.ps1

$ErrorActionPreference = "Stop"
$DOME_ROOT = Split-Path -Parent $PSScriptRoot

Write-Host "==> DOME-HUB Sovereign Setup (Windows)" -ForegroundColor Cyan
Write-Host "    Root: $DOME_ROOT"

# ── 1. Winget check ───────────────────────────────────────────────────────────
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
  Write-Host "Install App Installer from Microsoft Store, then re-run." -ForegroundColor Red
  exit 1
}

# ── 2. Chocolatey ─────────────────────────────────────────────────────────────
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
  Write-Host "==> Installing Chocolatey..."
  Set-ExecutionPolicy Bypass -Scope Process -Force
  [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
  iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
  $env:PATH += ";$env:ALLUSERSPROFILE\chocolatey\bin"
}

# ── 3. Core tools ─────────────────────────────────────────────────────────────
Write-Host "==> Installing core tools..."
choco install -y git curl wget jq yq tree ripgrep fzf
choco install -y python311 nodejs-lts golang rust
choco install -y postgresql17 redis sqlite
choco install -y awscli terraform gh
choco install -y gnupg vscode

# ── 4. Python ─────────────────────────────────────────────────────────────────
Write-Host "==> Setting up Python..."
python -m pip install --upgrade pip pipenv poetry
python -m pip install openai anthropic langchain chromadb sentence-transformers `
  torch transformers sqlalchemy psycopg2-binary redis pandas numpy `
  scipy sympy statsmodels scikit-learn numba matplotlib networkx psutil

# ── 5. Node / pnpm ────────────────────────────────────────────────────────────
Write-Host "==> Setting up Node..."
npm install -g pnpm
pnpm setup
pnpm add -g tsx typescript ts-node

# ── 6. VS Code extensions ─────────────────────────────────────────────────────
Write-Host "==> Installing VS Code extensions..."
$extensions = @(
  "esbenp.prettier-vscode", "dbaeumer.vscode-eslint",
  "ms-python.python", "ms-python.vscode-pylance", "ms-python.black-formatter",
  "golang.go", "rust-lang.rust-analyzer", "ms-azuretools.vscode-docker",
  "hashicorp.terraform", "amazonwebservices.aws-toolkit-vscode",
  "eamodio.gitlens", "usernamehw.errorlens", "mikestead.dotenv",
  "bradlc.vscode-tailwindcss", "prisma.prisma", "redhat.vscode-yaml"
)
foreach ($ext in $extensions) {
  code --install-extension $ext --force 2>$null
}

# ── 7. Root venv ──────────────────────────────────────────────────────────────
Write-Host "==> Creating root Python venv..."
python -m venv "$DOME_ROOT\.venv"
& "$DOME_ROOT\.venv\Scripts\Activate.ps1"
pip install --quiet torch torchvision psutil scipy sympy statsmodels `
  scikit-learn numba matplotlib networkx openai anthropic langchain `
  chromadb sentence-transformers transformers sqlalchemy redis pandas numpy

# ── 8. GPG + pass ─────────────────────────────────────────────────────────────
Write-Host "==> Setting up GPG..."
$gpgKey = gpg --list-secret-keys --keyid-format LONG 2>$null | Select-String "sec"
if (-not $gpgKey) {
  $gpgBatch = @"
Key-Type: RSA
Key-Length: 4096
Name-Real: $env:USERNAME
Name-Email: $env:USERNAME@dome-hub.local
Expire-Date: 0
%no-protection
"@
  $gpgBatch | gpg --batch --gen-key
}
$GPG_ID = (gpg --list-secret-keys --keyid-format LONG 2>$null | Select-String "sec" | Select-Object -First 1).ToString().Split("/")[1].Split(" ")[0]
git config --global user.signingkey $GPG_ID
git config --global commit.gpgsign true

# ── 9. Security hardening ─────────────────────────────────────────────────────
Write-Host "==> Hardening security..."
# Enable Windows Firewall
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
# Disable telemetry
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "AllowTelemetry" -Value 0 -Force -ErrorAction SilentlyContinue
# Disable Cortana
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "AllowCortana" -Value 0 -Force -ErrorAction SilentlyContinue
# Disable advertising ID
Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" -Name "Enabled" -Value 0 -Force -ErrorAction SilentlyContinue

# ── 10. Shell profile ─────────────────────────────────────────────────────────
Write-Host "==> Configuring PowerShell profile..."
$profileDir = Split-Path $PROFILE
if (-not (Test-Path $profileDir)) { New-Item -ItemType Directory -Path $profileDir -Force }
$domeInit = "`$env:DOME_ROOT = '$DOME_ROOT'`n`$env:PATH += `";$DOME_ROOT\scripts`""
if (-not (Test-Path $PROFILE) -or -not (Select-String -Path $PROFILE -Pattern "DOME_ROOT" -Quiet)) {
  Add-Content -Path $PROFILE -Value $domeInit
}

# ── 11. pnpm install ──────────────────────────────────────────────────────────
Set-Location $DOME_ROOT
pnpm install 2>$null

Write-Host ""
Write-Host "DOME-HUB Sovereign Setup Complete" -ForegroundColor Green
Write-Host "   Restart PowerShell, then run: bash scripts/audit.sh"

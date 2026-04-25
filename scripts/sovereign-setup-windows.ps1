# DOME-HUB Sovereign Setup — Windows
# Run as Administrator in PowerShell:
# Set-ExecutionPolicy Bypass -Scope Process -Force
# .\scripts\sovereign-setup-windows.ps1

$ErrorActionPreference = "Stop"
$DOME_ROOT = Split-Path -Parent $PSScriptRoot
$TotalSteps = 17
$CurrentStep = 0

function Show-Phase([string]$Name) {
  $script:CurrentStep++
  Write-Host ""
  Write-Host ("[{0}/{1}] {2}" -f $script:CurrentStep, $script:TotalSteps, $Name) -ForegroundColor Cyan
  Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray
}

function Info([string]$Message) {
  Write-Host "    -> $Message"
}

Write-Host "DOME-HUB Sovereign Setup (Windows Phase 1)" -ForegroundColor Cyan
Write-Host "Root: $DOME_ROOT"
Write-Host "This run localizes your sovereign node payload into this repo:"
Write-Host "  - agents/   -> local agent runtime + skills"
Write-Host "  - kb/       -> local knowledge corpus to ingest"
Write-Host "  - db/       -> local SQLite + Chroma vector state"
Write-Host "Safe to re-run; existing installs are reused where possible."

# ── 1. Winget check ───────────────────────────────────────────────────────────
Show-Phase "Winget Check"
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
  Write-Host "Install App Installer from Microsoft Store, then re-run." -ForegroundColor Red
  exit 1
}
Info "Winget detected."

# ── 2. Chocolatey ─────────────────────────────────────────────────────────────
Show-Phase "Chocolatey"
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
  Info "Installing Chocolatey..."
  Set-ExecutionPolicy Bypass -Scope Process -Force
  [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
  iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
  $env:PATH += ";$env:ALLUSERSPROFILE\chocolatey\bin"
}
Info "Chocolatey ready."

# ── 3. Core tools ─────────────────────────────────────────────────────────────
Show-Phase "Core Tools and Infra Packages"
Info "Loading languages, databases, cloud CLIs, and security tooling..."
choco install -y git curl wget jq yq tree ripgrep fzf
choco install -y python311 nodejs-lts golang rust
choco install -y postgresql17 redis sqlite
choco install -y awscli terraform gh
choco install -y gnupg vscode

# ── 4. Python ─────────────────────────────────────────────────────────────────
Show-Phase "Python Runtime and Package Stacks"
Info "Loading AI/ML, analytics, and agent-runtime dependencies..."
python -m pip install --upgrade pip pipenv poetry
python -m pip install openai anthropic langchain chromadb sentence-transformers `
  torch transformers sqlalchemy psycopg2-binary redis pandas numpy `
  scipy sympy statsmodels scikit-learn numba matplotlib networkx psutil

# ── 5. Node / pnpm ────────────────────────────────────────────────────────────
Show-Phase "Node and pnpm"
Info "Installing Node package runtime tooling..."
npm install -g pnpm
pnpm setup
pnpm add -g tsx typescript ts-node

# ── 6. VS Code extensions ─────────────────────────────────────────────────────
Show-Phase "VS Code Extensions"
Info "Installing editor extension baseline..."
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
Show-Phase "Root Python Virtual Environment"
Info "Creating venv and installing compute requirements..."
python -m venv "$DOME_ROOT\.venv"
& "$DOME_ROOT\.venv\Scripts\Activate.ps1"
pip install --upgrade pip wheel
pip install -r "$DOME_ROOT\compute\requirements.txt"

# ── 8. GPG + pass ─────────────────────────────────────────────────────────────
Show-Phase "GPG and Commit Signing"
Info "Ensuring local signing key exists..."
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
Show-Phase "Security Hardening"
Info "Applying firewall and privacy defaults..."
# Enable Windows Firewall
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
# Disable telemetry
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "AllowTelemetry" -Value 0 -Force -ErrorAction SilentlyContinue
# Disable Cortana
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "AllowCortana" -Value 0 -Force -ErrorAction SilentlyContinue
# Disable advertising ID
Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" -Name "Enabled" -Value 0 -Force -ErrorAction SilentlyContinue

# ── 10. Shell profile ─────────────────────────────────────────────────────────
Show-Phase "PowerShell Profile"
Info "Wiring DOME root into user shell profile..."
$profileDir = Split-Path $PROFILE
if (-not (Test-Path $profileDir)) { New-Item -ItemType Directory -Path $profileDir -Force }
$domeInit = "`$env:DOME_ROOT = '$DOME_ROOT'`n`$env:PATH += `";$DOME_ROOT\scripts`""
if (-not (Test-Path $PROFILE) -or -not (Select-String -Path $PROFILE -Pattern "DOME_ROOT" -Quiet)) {
  Add-Content -Path $PROFILE -Value $domeInit
}

# ── 11. pnpm install ──────────────────────────────────────────────────────────
Show-Phase "Repository Dependencies"
Info "Installing repository Node dependencies..."
Set-Location $DOME_ROOT
pnpm install 2>$null

# ── 12. .env setup ────────────────────────────────────────────────────────────
Show-Phase ".env Bootstrap"
if (-not (Test-Path "$DOME_ROOT\.env")) {
  Copy-Item "$DOME_ROOT\.env.example" "$DOME_ROOT\.env"
  Write-Host "    .env created from .env.example — add your API keys before running agents"
}

# ── 13. SQLite DB init ────────────────────────────────────────────────────────
Show-Phase "SQLite Initialization"
Info "Initializing local db\dome.db catalog..."
$dbPath = Join-Path $DOME_ROOT "db\dome.db"
$pyInit = @"
import sqlite3
db = sqlite3.connect(r"$dbPath")
for sql in [
  "CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, title TEXT, content TEXT, tags TEXT, created_at TEXT)",
  "CREATE TABLE IF NOT EXISTS stack (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, name TEXT, version TEXT, status TEXT, updated_at TEXT)",
  "CREATE TABLE IF NOT EXISTS agents (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, type TEXT, model TEXT, status TEXT, registered_at TEXT)",
  "CREATE TABLE IF NOT EXISTS skills (id INTEGER PRIMARY KEY AUTOINCREMENT, agent_id INTEGER, name TEXT, description TEXT)",
  "CREATE TABLE IF NOT EXISTS tools (id INTEGER PRIMARY KEY AUTOINCREMENT, agent_id INTEGER, name TEXT, description TEXT)",
]:
  db.execute(sql)
db.commit()
db.close()
print("DB ready")
"@
$pyInit | python -

# ── 14. ChromaDB ingest ───────────────────────────────────────────────────────
Show-Phase "ChromaDB Ingest"
Info "Ingesting local kb/ corpus into db/chroma..."
python scripts/ingest.py 2>$null

# ── 15. Register Claude agent ─────────────────────────────────────────────────
Show-Phase "Claude Agent Registration"
Info "Registering local agent profile in SQLite..."
python scripts/register-claude.py 2>$null

# ── 16. AI Assistant ──────────────────────────────────────────────────────────
Show-Phase "Local Node Payload Verification"
$agentCount = (Get-ChildItem -Path "$DOME_ROOT\agents" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
$kbCount = (Get-ChildItem -Path "$DOME_ROOT\kb" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
if (Test-Path "$DOME_ROOT\db\dome.db") { Info "SQLite ready: db\\dome.db" } else { Write-Host "    WARN: SQLite missing: db\\dome.db" -ForegroundColor Yellow }
if (Test-Path "$DOME_ROOT\db\chroma") { Info "Chroma path ready: db\\chroma" } else { Write-Host "    WARN: Chroma path missing: db\\chroma (run: pnpm ingest)" -ForegroundColor Yellow }
Info "Agent files detected: $agentCount"
Info "KB files detected: $kbCount"
Info "Node scope: all runtime assets are local to $DOME_ROOT"

Show-Phase "AI Assistant Choice"
Write-Host ""
Write-Host "==> AI Assistant — choose one to install:" -ForegroundColor Cyan
Write-Host "    1) Kiro CLI       (npm install -g kiro-cli)"
Write-Host "    2) Claude Code    (npm install -g @anthropic-ai/claude-code)"
Write-Host "    3) Cursor         (winget install Anysphere.Cursor)"
Write-Host "    4) GitHub Copilot (gh extension install github/gh-copilot)"
Write-Host "    5) Aider          (pip install aider-chat)"
Write-Host "    6) Skip"
$aiChoice = Read-Host "    Enter choice [1-6]"
switch ($aiChoice) {
  "1" { npm install -g kiro-cli }
  "2" { npm install -g "@anthropic-ai/claude-code" }
  "3" { winget install Anysphere.Cursor }
  "4" { gh extension install github/gh-copilot }
  "5" { pip install aider-chat }
  default { Write-Host "    Skipping AI assistant install." }
}

Write-Host ""
Write-Host "DOME-HUB Sovereign Setup Complete" -ForegroundColor Green
Write-Host "   Restart PowerShell, then run: bash scripts/audit.sh"

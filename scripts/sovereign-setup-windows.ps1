# DSH Sovereign Setup - Windows
# Run as Administrator in PowerShell:
Set-ExecutionPolicy Bypass -Scope Process -Force
.\scripts\sovereign-setup-windows.ps1
# Non-interactive (skip AI assistant picker):
#   .\scripts\sovereign-setup-windows.ps1 -AiChoice 6

param(
  [ValidateSet('1','2','3','4','5','6')]
  [string]$AiChoice = '',
  [switch]$SkipGitSigning
)

$ErrorActionPreference = "Continue"
$DOME_ROOT = Split-Path -Parent $PSScriptRoot

Write-Host "==> DSH Sovereign Setup (Windows)" -ForegroundColor Cyan
Write-Host "    Root: $DOME_ROOT"

# -- 1. Winget check -----------------------------------------------------------
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
  Write-Host "Install App Installer from Microsoft Store, then re-run." -ForegroundColor Red
  exit 1
}

# -- 2. Chocolatey -------------------------------------------------------------
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
  Write-Host "==> Installing Chocolatey..."
  Set-ExecutionPolicy Bypass -Scope Process -Force
  [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
  iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
  $env:PATH = "$env:ALLUSERSPROFILE\chocolatey\bin;$env:PATH"
  # Refresh for current process if install just landed
  if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    $chocoExe = Join-Path $env:ALLUSERSPROFILE "chocolatey\bin\choco.exe"
    if (Test-Path $chocoExe) {
      Set-Alias -Name choco -Value $chocoExe -Scope Script
    } else {
      Write-Host "Chocolatey install did not put choco on PATH. Re-open an elevated shell and re-run." -ForegroundColor Red
      exit 1
    }
  }
}

# -- 3. Core tools -------------------------------------------------------------
Write-Host "==> Installing core tools..."
choco install -y git curl wget jq yq tree ripgrep fzf
choco install -y python314 nodejs-lts golang rust
choco install -y postgresql redis sqlite
choco install -y awscli terraform gh
choco install -y gnupg vscode

# Refresh PATH from Machine + User after choco installs
$env:PATH = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' +
            [System.Environment]::GetEnvironmentVariable('Path','User') + ';' +
            "$env:ALLUSERSPROFILE\chocolatey\bin"

# Prefer real python over WindowsApps stub
$pyCandidates = @(
  'C:\Python314\python.exe',
  'C:\Program Files\Python314\python.exe',
  (Get-Command python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source)
) | Where-Object { $_ -and (Test-Path $_) -and ($_ -notmatch 'WindowsApps') }
$Python = if ($pyCandidates) { $pyCandidates | Select-Object -First 1 } else { 'python' }
Write-Host "    Using Python: $Python"
& $Python --version

# -- 4. Python -----------------------------------------------------------------
Write-Host "==> Setting up Python..."
& $Python -m pip install --upgrade pip pipenv poetry
& $Python -m pip install openai anthropic langchain chromadb sentence-transformers `
  torch transformers sqlalchemy psycopg2-binary redis pandas numpy `
  scipy sympy statsmodels scikit-learn numba matplotlib networkx psutil

# -- 5. Node / pnpm ------------------------------------------------------------
Write-Host "==> Setting up Node..."
npm install -g pnpm
pnpm setup 2>$null
pnpm add -g tsx typescript ts-node

# -- 6. VS Code extensions -----------------------------------------------------
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
  if (Get-Command code -ErrorAction SilentlyContinue) {
    code --install-extension $ext --force 2>$null
  }
}

# -- 7. Root venv --------------------------------------------------------------
Write-Host "==> Creating root Python venv..."
$venvPath = Join-Path $DOME_ROOT ".venv"
if (-not (Test-Path $venvPath)) {
  & $Python -m venv $venvPath
}
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$venvPip = Join-Path $venvPath "Scripts\pip.exe"
& $venvPython -m pip install --upgrade pip wheel
# pyquil/qcs-sdk-python often fails on Windows (Application Control / no wheel for cp314).
# Prefer a Windows-filtered requirements file when present.
$reqWin = Join-Path $DOME_ROOT "compute\requirements.windows.txt"
$reqFile = Join-Path $DOME_ROOT "compute\requirements.txt"
if (Test-Path $reqWin) {
  Write-Host "    Installing compute\requirements.windows.txt (pyquil excluded)..."
  & $venvPip install -r $reqWin
} elseif (Test-Path $reqFile) {
  Write-Host "    Installing compute\requirements.txt (this can take a while)..."
  & $venvPip install -r $reqFile
}

# -- 7b. Workstation utility deps ----------------------------------------------
Write-Host "==> Installing workstation utility dependencies..."
choco install -y pandoc miktex ffmpeg 2>$null
& $venvPip install "python-docx==1.1.2" "reportlab==4.4.0" "pdfplumber==0.11.6" "pypdf==5.4.0" `
  "python-pptx==1.0.2" "openpyxl==3.1.5" "nbformat==5.10.4" "openai==1.82.0" `
  "playwright==1.52.0"
& $venvPython -m playwright install chromium 2>$null

# -- 8. GPG + pass -------------------------------------------------------------
Write-Host "==> Setting up GPG..."
if (-not $SkipGitSigning) {
  if (Get-Command gpg -ErrorAction SilentlyContinue) {
    $gpgKey = gpg --list-secret-keys --keyid-format LONG 2>$null | Select-String "sec"
    if (-not $gpgKey) {
      $gpgBatch = @"
Key-Type: RSA
Key-Length: 4096
Name-Real: $env:USERNAME
Name-Email: $env:USERNAME@dsh.local
Expire-Date: 0
%no-protection
"@
      $gpgBatch | gpg --batch --gen-key
    }
    $secLine = (gpg --list-secret-keys --keyid-format LONG 2>$null | Select-String "sec" | Select-Object -First 1)
    if ($secLine) {
      $GPG_ID = $secLine.ToString().Split("/")[1].Split(" ")[0]
      git config --global user.signingkey $GPG_ID
      git config --global commit.gpgsign true
      Write-Host "    GPG signing key: $GPG_ID"
    } else {
      Write-Host "    No GPG secret key found; skipping git signing config." -ForegroundColor Yellow
    }
  } else {
    Write-Host "    gpg not on PATH yet; skipping signing setup." -ForegroundColor Yellow
  }
} else {
  Write-Host "    Skipping GPG/git signing (-SkipGitSigning)."
}

# -- 9. Security hardening -----------------------------------------------------
Write-Host "==> Hardening security..."
# Enable Windows Firewall
try {
  Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
# Disable telemetry
} catch {
  Write-Host "    Firewall change skipped: $_" -ForegroundColor Yellow
}
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "AllowTelemetry" -Value 0 -Force -ErrorAction SilentlyContinue
# Disable Cortana
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "AllowCortana" -Value 0 -Force -ErrorAction SilentlyContinue
# Disable advertising ID
Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" -Name "Enabled" -Value 0 -Force -ErrorAction SilentlyContinue

# -- 10. Shell profile ---------------------------------------------------------
Write-Host "==> Configuring PowerShell profile..."
$profileDir = Split-Path $PROFILE
if (-not (Test-Path $profileDir)) { New-Item -ItemType Directory -Path $profileDir -Force | Out-Null }
$domeInit = "`$env:DOME_ROOT = '$DOME_ROOT'`n`$env:PATH += `";$DOME_ROOT\scripts`""
if (-not (Test-Path $PROFILE) -or -not (Select-String -Path $PROFILE -Pattern "DOME_ROOT" -Quiet)) {
  Add-Content -Path $PROFILE -Value $domeInit
}

# -- 11. pnpm install ----------------------------------------------------------
Set-Location $DOME_ROOT
Write-Host "==> pnpm install (repo root)..."
pnpm install

# -- 12. .env setup ------------------------------------------------------------
Write-Host "==> Setting up .env..."
if (-not (Test-Path "$DOME_ROOT\.env")) {
  Copy-Item "$DOME_ROOT\.env.example" "$DOME_ROOT\.env"
  Write-Host "    .env created from .env.example - add your API keys before running agents"
}

# -- 13. SQLite DB init --------------------------------------------------------
Write-Host "==> Initializing SQLite DB..."
$dbPath = Join-Path $DOME_ROOT "db\dome.db"
$dbDir = Split-Path $dbPath
if (-not (Test-Path $dbDir)) { New-Item -ItemType Directory -Path $dbDir -Force | Out-Null }
$dbInitPy = @"
import sqlite3, os
db_path = r'''$dbPath'''
os.makedirs(os.path.dirname(db_path), exist_ok=True)
db = sqlite3.connect(db_path)
for sql in [
    'CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, title TEXT, content TEXT, tags TEXT, created_at TEXT)',
    'CREATE TABLE IF NOT EXISTS stack (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, name TEXT, version TEXT, status TEXT, updated_at TEXT)',
    'CREATE TABLE IF NOT EXISTS agents (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, type TEXT, model TEXT, status TEXT, registered_at TEXT)',
    'CREATE TABLE IF NOT EXISTS skills (id INTEGER PRIMARY KEY AUTOINCREMENT, agent_id INTEGER, name TEXT, description TEXT)',
    'CREATE TABLE IF NOT EXISTS tools (id INTEGER PRIMARY KEY AUTOINCREMENT, agent_id INTEGER, name TEXT, description TEXT)',
]:
    db.execute(sql)
db.commit()
db.close()
print('DB ready')
"@
$dbInitPy | & $venvPython -

# -- 14. ChromaDB ingest -------------------------------------------------------
Write-Host "==> Ingesting KB into ChromaDB..."
$ingestScript = Join-Path $DOME_ROOT "scripts\ingest.py"
if (Test-Path $ingestScript) {
  & $venvPython $ingestScript
} else {
  Write-Host "    Skipped (ingest.py not found)"
}

# -- 15. Register Claude agent -------------------------------------------------
Write-Host "==> Registering Claude agent..."
$registerScript = Join-Path $DOME_ROOT "scripts\register-claude.py"
if (Test-Path $registerScript) {
  & $venvPython $registerScript
} else {
  Write-Host "    Skipped (register-claude.py not found)"
}

# -- 16. AI Assistant ----------------------------------------------------------
Write-Host ""
if (-not $AiChoice) {
  Write-Host "==> AI Assistant - choose one to install:" -ForegroundColor Cyan
  Write-Host "    1) Kiro CLI       (npm install -g kiro-cli)"
  Write-Host "    2) Claude Code    (npm install -g @anthropic-ai/claude-code)"
  Write-Host "    3) Cursor         (winget install Anysphere.Cursor)"
  Write-Host "    4) GitHub Copilot (gh extension install github/gh-copilot)"
  Write-Host "    5) Aider          (pip install aider-chat)"
  Write-Host "    6) Skip"
  $AiChoice = Read-Host "    Enter choice [1-6]"
}
switch ($AiChoice) {
  "1" { npm install -g kiro-cli }
  "2" { npm install -g "@anthropic-ai/claude-code" }
  "3" { winget install Anysphere.Cursor }
  "4" { gh extension install github/gh-copilot }
  "5" { & $venvPip install aider-chat }
  default { Write-Host "    Skipping AI assistant install." }
}

# -- 17. Local node payload verification ---------------------------------------
Write-Host ""
Write-Host "==> Local Node Payload Verification" -ForegroundColor Cyan
$agentCount = (Get-ChildItem -Path (Join-Path $DOME_ROOT "agents") -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
$kbCount = (Get-ChildItem -Path (Join-Path $DOME_ROOT "kb") -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "    agents/ files: $agentCount"
Write-Host "    kb/ files:     $kbCount"
Write-Host "    db/dome.db:    $(Test-Path (Join-Path $DOME_ROOT 'db\dome.db'))"
Write-Host "    .venv:         $(Test-Path (Join-Path $DOME_ROOT '.venv\Scripts\python.exe'))"
Write-Host "    node_modules:  $(Test-Path (Join-Path $DOME_ROOT 'node_modules'))"
Write-Host "    .env:          $(Test-Path (Join-Path $DOME_ROOT '.env'))"

Write-Host ""
Write-Host "DSH Sovereign Setup Complete" -ForegroundColor Green
Write-Host "   Restart PowerShell, then run: .\.venv\Scripts\python.exe scripts\pre-spore-verify.py"
exit 0

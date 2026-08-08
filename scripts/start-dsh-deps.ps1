# Start DSH on-demand deps (Postgres + Ollama). Redis if installed.
$ErrorActionPreference = "Continue"
Write-Host "==> Starting DSH deps" -ForegroundColor Cyan
$pg = Get-Service postgresql-x64-18 -ErrorAction SilentlyContinue
if ($pg) {
  if ($pg.Status -ne "Running") { Start-Service postgresql-x64-18; Write-Host "postgres started" } else { Write-Host "postgres already running" }
}
$ollama = "$env:LOCALAPPDATA\Programs\Ollama\ollama app.exe"
if (Test-Path $ollama) {
  if (-not (Get-Process "ollama app" -ErrorAction SilentlyContinue)) {
    Start-Process $ollama
    Write-Host "Ollama launched"
  } else { Write-Host "Ollama already running" }
} else {
  Write-Host "Ollama app not found at $ollama"
}
Get-Service *redis*,Memurai -ErrorAction SilentlyContinue | ForEach-Object {
  if ($_.Status -ne "Running") { Start-Service $_.Name; Write-Host "$($_.Name) started" }
}
Write-Host "Done. Agent API: .\\.venv\\Scripts\\python.exe -m uvicorn agents.api.server:app --host 127.0.0.1 --port 8001"

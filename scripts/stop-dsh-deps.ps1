# Stop DSH on-demand deps to free RAM
$ErrorActionPreference = "Continue"
Write-Host "==> Stopping DSH deps" -ForegroundColor Cyan
Get-Service postgresql-x64-18 -ErrorAction SilentlyContinue | Where-Object Status -eq Running | Stop-Service -Force
Get-Service *redis*,Memurai -ErrorAction SilentlyContinue | Where-Object Status -eq Running | Stop-Service -Force
Get-Process ollama,"ollama app" -ErrorAction SilentlyContinue | Stop-Process -Force
try { wsl --shutdown } catch {}
Write-Host "Stopped postgres/redis/ollama; WSL shut down"

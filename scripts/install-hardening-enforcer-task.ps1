# Install / refresh the DSH Windows Hardening Enforcer scheduled task.
# Run elevated once:
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install-hardening-enforcer-task.ps1

$ErrorActionPreference = 'Stop'
$DomeRoot = Split-Path -Parent $PSScriptRoot
$Enforce = Join-Path $DomeRoot 'scripts\enforce-windows-hardening.ps1'
$TaskName = 'DSH-Windows-Hardening-Enforcer'

if (-not (Test-Path $Enforce)) {
  throw "Missing enforcer script: $Enforce"
}

# Prefer short path in task action to avoid quoting issues with spaces
$fso = New-Object -ComObject Scripting.FileSystemObject
$enforceShort = $fso.GetFile($Enforce).ShortPath

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
  throw 'Run this installer elevated (Administrator).'
}

# Unregister old copy if present
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

$arg = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$enforceShort`""
$action = New-ScheduledTaskAction -Execute "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -Argument $arg

# At every logon of this user
$triggerLogon = New-ScheduledTaskTrigger -AtLogOn -User $env:UserName

# Every 3 hours, indefinitely
$triggerRepeat = New-ScheduledTaskTrigger -Once -At (Get-Date).Date.AddMinutes(10)
$triggerRepeat.Repetition = (New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 3) -RepetitionDuration ([TimeSpan]::FromDays(3650))).Repetition

# At startup (catches service drift before logon) - still as user Highest may wait for logon on some systems;
# add a SYSTEM startup task for service/HKLM pieces only would be ideal; for simplicity use Startup too.
$triggerStartup = New-ScheduledTaskTrigger -AtStartup

$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -StartWhenAvailable `
  -ExecutionTimeLimit (New-TimeSpan -Minutes 15) `
  -MultipleInstances IgnoreNew `
  -RestartCount 2 `
  -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask `
  -TaskName $TaskName `
  -Action $action `
  -Trigger @($triggerLogon, $triggerRepeat, $triggerStartup) `
  -Principal $principal `
  -Settings $settings `
  -Description 'Re-applies DSH Windows hardening/trim (firewall, telemetry, OEM services, Teams autostart). Keeps Defender. Not air-gapped.' `
  -Force | Out-Null

# Run once immediately to confirm
Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 3

$task = Get-ScheduledTask -TaskName $TaskName
$info = Get-ScheduledTaskInfo -TaskName $TaskName
Write-Host "Registered: $($task.TaskName)"
Write-Host "State: $($task.State)"
Write-Host "LastResult: $($info.LastTaskResult)"
Write-Host "NextRun: $($info.NextRunTime)"
Write-Host "Log: $(Join-Path $DomeRoot 'logs\hardening-enforcer.log')"

# Verify triggers
$task.Triggers | ForEach-Object { Write-Host ("Trigger: {0}" -f $_.ToString()) }

if (-not (Test-Path (Join-Path $DomeRoot 'logs\hardening-enforcer.log'))) {
  Write-Host 'WARNING: enforcer log not written yet (task may still be starting)' -ForegroundColor Yellow
} else {
  Write-Host '--- log tail ---'
  Get-Content (Join-Path $DomeRoot 'logs\hardening-enforcer.log') -Tail 20
}

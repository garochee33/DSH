# DSH Windows Hardening Enforcer
# Re-applies trim + security posture after Windows/OEM/Teams updates.
# Safe for non-airgapped use: keeps Defender + Firewall; does not block networking.
#
# Manual run (elevated recommended):
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\enforce-windows-hardening.ps1
#
# Installed as scheduled task: "DSH-Windows-Hardening-Enforcer"

[CmdletBinding()]
param(
  [switch]$ReportOnly
)

$ErrorActionPreference = 'Continue'
$DomeRoot = Split-Path -Parent $PSScriptRoot
if (-not $DomeRoot) { $DomeRoot = 'C:\Users\Duece Biggalo\Downloads\DSH' }

$LogDir = Join-Path $DomeRoot 'logs'
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
$LogFile = Join-Path $LogDir 'hardening-enforcer.log'

function Write-Log {
  param([string]$Message, [string]$Level = 'INFO')
  $line = '{0} [{1}] {2}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Level, $Message
  Add-Content -Path $LogFile -Value $line -Encoding UTF8
  Write-Host $line
}

function Set-ServiceEnforced {
  param(
    [Parameter(Mandatory)][string]$Name,
    [ValidateSet('Manual', 'Disabled', 'Automatic')][string]$StartupType,
    [switch]$StopIfRunning
  )
  $svc = Get-Service -Name $Name -ErrorAction SilentlyContinue
  if (-not $svc) {
    Write-Log "service missing: $Name"
    return
  }
  if ($ReportOnly) {
    Write-Log ("REPORT {0} status={1} start={2} want={3}" -f $Name, $svc.Status, $svc.StartType, $StartupType)
    return
  }
  try {
    if ($svc.StartType -ne $StartupType) {
      Set-Service -Name $Name -StartupType $StartupType -ErrorAction Stop
      Write-Log "set $Name StartupType=$StartupType"
    }
    if ($StopIfRunning -and $svc.Status -eq 'Running') {
      Stop-Service -Name $Name -Force -ErrorAction Stop
      Write-Log "stopped $Name"
    }
  } catch {
    Write-Log "Set-Service failed $Name : $_ - trying sc.exe" 'WARN'
    $scMap = @{ Manual = 'demand'; Disabled = 'disabled'; Automatic = 'auto' }
    $scStart = $scMap[$StartupType]
    & sc.exe config $Name start= $scStart | Out-Null
    if ($StopIfRunning) { & sc.exe stop $Name | Out-Null }
    # Registry fallback (3=Manual, 4=Disabled, 2=Auto)
    $regMap = @{ Manual = 3; Disabled = 4; Automatic = 2 }
    $regPath = "HKLM:\SYSTEM\CurrentControlSet\Services\$Name"
    if (Test-Path $regPath) {
      Set-ItemProperty -Path $regPath -Name Start -Value $regMap[$StartupType] -Type DWord -Force -ErrorAction SilentlyContinue
      Write-Log "registry Start=$($regMap[$StartupType]) for $Name"
    }
  }
}

function Remove-HkcuRunValue {
  param([string]$ValueName)
  $path = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
  if (-not (Test-Path $path)) { return }
  $exists = $null -ne (Get-ItemProperty -Path $path -Name $ValueName -ErrorAction SilentlyContinue)
  if (-not $exists) { return }
  if ($ReportOnly) {
    Write-Log "REPORT HKCU Run has $ValueName (would remove)"
    return
  }
  Remove-ItemProperty -Path $path -Name $ValueName -Force -ErrorAction SilentlyContinue
  Write-Log "removed HKCU Run: $ValueName"
}

function Set-Dword {
  param([string]$Path, [string]$Name, [int]$Value)
  if ($ReportOnly) {
    $cur = (Get-ItemProperty -Path $Path -Name $Name -ErrorAction SilentlyContinue).$Name
    Write-Log "REPORT $Path\$Name=$cur want=$Value"
    return
  }
  New-Item -Path $Path -Force -ErrorAction SilentlyContinue | Out-Null
  Set-ItemProperty -Path $Path -Name $Name -Value $Value -Type DWord -Force -ErrorAction SilentlyContinue
}

Write-Log '=== DSH hardening enforcer start ==='
$principal = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
Write-Log "user=$principal elevated=$admin reportOnly=$ReportOnly"

# --- Services: on-demand / trim (keep Defender, NVIDIA display, Realtek audio driver stack) ---
# Intentionally NOT touching: WinDefend, NVDisplay.ContainerLocalSystem, RtkAudioUniversalService
$manualStop = @(
  # DSH / prior trim
  'postgresql-x64-18',
  'DiagTrack',
  'dmwappushservice',
  'LightKeeperService',
  'Mystic_Light_Service',
  'MSI Foundation Service',
  'MSI Sendevsvc',
  'MSI_Center_Service',
  'NahimicService',
  'Micro Star SCM',
  # Intel OEM helpers / telemetry (not required for Cursor/browser/terminal)
  'IntelAudioService',
  'IntelGraphicsSoftwareService',
  'ipfsvc',
  'jhi_service',
  'cplspcon',
  'dptftcs',
  'WMIRegistrationService',
  'RstMwService',
  'PIEServiceNew',
  # Workflow-unnecessary Microsoft / install leftovers
  'Memurai',
  'ClickToRunSvc',
  'Spooler',
  'SysMain',
  'PcaSvc',
  'DusmSvc'
)
foreach ($name in $manualStop) {
  Set-ServiceEnforced -Name $name -StartupType Manual -StopIfRunning
}

# These respawn or linger unless Disabled
Set-ServiceEnforced -Name 'WSearch' -StartupType Disabled -StopIfRunning
Set-ServiceEnforced -Name 'SharedAccess' -StartupType Disabled -StopIfRunning


# Defender must stay on
$def = Get-Service WinDefend -ErrorAction SilentlyContinue
if ($def -and $def.Status -ne 'Running' -and -not $ReportOnly) {
  try {
    Set-Service WinDefend -StartupType Automatic -ErrorAction SilentlyContinue
    Start-Service WinDefend -ErrorAction SilentlyContinue
    Write-Log 'restarted WinDefend'
  } catch {
    Write-Log "FAIL WinDefend: $_" 'WARN'
  }
}

# --- Firewall ---
if (-not $ReportOnly) {
  try {
    Set-NetFirewallProfile -Profile Domain, Public, Private -Enabled True -ErrorAction Stop
    Write-Log 'firewall Domain/Public/Private ENABLED'
  } catch {
    Write-Log "FAIL firewall: $_" 'WARN'
  }
} else {
  Get-NetFirewallProfile | ForEach-Object { Write-Log ("REPORT Firewall {0}={1}" -f $_.Name, $_.Enabled) }
}

# --- Policy keys ---
Set-Dword 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection' 'AllowTelemetry' 0
Set-Dword 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search' 'AllowCortana' 0
Set-Dword 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo' 'Enabled' 0
Set-Dword 'HKLM:\SOFTWARE\Policies\Microsoft\Dsh' 'AllowNewsAndInterests' 0
Set-Dword 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Feeds' 'EnableFeeds' 0
try {
  Set-Dword 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced' 'TaskbarDa' 0
} catch {
  Write-Log "TaskbarDa skip: $_" 'WARN'
}

# Content Delivery / suggestions
$cdm = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager'
@(
  'SystemPaneSuggestionsEnabled',
  'SubscribedContent-338388Enabled',
  'SubscribedContent-338389Enabled',
  'SubscribedContent-355063Enabled',
  'SubscribedContent-355064Enabled',
  'SubscribedContent-355065Enabled',
  'SoftLandingEnabled'
) | ForEach-Object { Set-Dword $cdm $_ 0 }

# Teams policy suppress
Set-Dword 'HKCU:\Software\Policies\Microsoft\Office\16.0\Teams' 'PreventFirstLaunchAfterInstall' 1

# --- Startup Run keys ---
foreach ($v in @(
  'Teams',
  'com.squirrel.Teams.Teams',
  'org.whispersystems.signal-desktop',
  'Microsoft.Lists',
  'OneDrive',
  'Discord',
  'Steam',
  'EpicGamesLauncher',
  'RtkAudUService',
  'SecurityHealth'
)) {
  # SecurityHealth tray is optional; Defender service stays. Remove only if present as Run key noise.
  if ($v -eq 'SecurityHealth') { continue }
  Remove-HkcuRunValue $v
}
# Realtek helper often lives in HKLM Run - strip if present
if (-not $ReportOnly) {
  foreach ($rk in @(
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run',
    'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run'
  )) {
    if (-not (Test-Path $rk)) { continue }
    foreach ($vn in @('RtkAudUService', 'RiotClient', 'Steam', 'Discord', 'AdobeAAMUpdater-1.0', 'iTunesHelper')) {
      if ($null -ne (Get-ItemProperty -Path $rk -Name $vn -ErrorAction SilentlyContinue)) {
        Remove-ItemProperty -Path $rk -Name $vn -Force -ErrorAction SilentlyContinue
        Write-Log "removed $rk : $vn"
      }
    }
  }
}

# StartupApproved disable blob for Teams
if (-not $ReportOnly) {
  $approved = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run'
  New-Item -Path $approved -Force -ErrorAction SilentlyContinue | Out-Null
  $disabled = [byte[]](0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
  New-ItemProperty -Path $approved -Name 'Teams' -PropertyType Binary -Value $disabled -Force -ErrorAction SilentlyContinue | Out-Null
}

# Ollama startup shortcut
$ollamaLnk = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Startup\Ollama.lnk'
if (Test-Path $ollamaLnk) {
  if ($ReportOnly) {
    Write-Log 'REPORT Ollama.lnk present (would remove)'
  } else {
    Remove-Item $ollamaLnk -Force -ErrorAction SilentlyContinue
    Write-Log 'removed Startup\Ollama.lnk'
  }
}

# --- Kill known bloat processes (not Cursor / not NVIDIA) ---
$kill = @(
  'LEDKeeper2',
  'PhoneExperienceHost',
  'Widgets',
  'WidgetService',
  'CrossDeviceService',
  'CrossDeviceResume',
  'SearchHost',
  'OfficeClickToRun',
  'IntelGraphicsSoftware.Service',
  'IntelGraphicsSoftware',
  'ipf_helper',
  'ipf_uf',
  'RtkAudUService64',
  'memurai'
)
foreach ($p in $kill) {
  $procs = @(Get-Process -Name $p -ErrorAction SilentlyContinue)
  if ($procs.Count -eq 0) { continue }
  if ($ReportOnly) {
    Write-Log "REPORT process $p count=$($procs.Count) (would kill)"
  } else {
    $procs | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Log "killed $p x$($procs.Count)"
  }
}

# MSI / Intel helper scheduled tasks
if (-not $ReportOnly) {
  Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object {
    $_.TaskName -match 'LEDKeeper|OmApSvcBroker|OneDC_Updater|Mystic|Intel|Graphics Software|ipf_' -or
    ($_.Actions.Execute -match 'MSI\\MSI Center|LEDKeeper|Mystic Light|Intel\\')
  } | ForEach-Object {
    if ($_.State -ne 'Disabled') {
      try {
        Disable-ScheduledTask -TaskName $_.TaskName -TaskPath $_.TaskPath -ErrorAction Stop | Out-Null
        Write-Log ("disabled task {0}{1}" -f $_.TaskPath, $_.TaskName)
      } catch {
        Write-Log ("task {0}: {1}" -f $_.TaskName, $_) 'WARN'
      }
    }
  }
}

Write-Log '=== DSH hardening enforcer done ==='
exit 0

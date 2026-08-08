# Windows Security Hardening (DSH)

Windows-specific guide for locking down a DSH node **without full air-gap**.
Browsing, Cursor, terminal, and local apps stay usable. OEM helpers, telemetry,
and always-on DSH deps are forced off and re-applied after updates.

macOS operators should use `PROTOCOLS.md`, `scripts/audit.sh`, and
`docs/SOVEREIGN_GATE_DOCTRINE.md` instead. This document is **Windows-only**.

---

## Posture

| Goal | Behavior |
|------|----------|
| Connected but locked down | Firewall + Defender stay **on**; outbound web allowed |
| Not air-gapped | No DNS pin / no wholesale network block |
| Low bloat | Intel/MSI helpers, Search, Spooler, Office Click-to-Run, etc. off |
| DSH on demand | Postgres / Memurai (Redis) / Ollama **Manual** — start when needed |
| Survives updates | Scheduled task re-enforces settings |

Related: [`SECURITY.md`](../SECURITY.md), [`PROTOCOLS.md`](../PROTOCOLS.md),
[`PUBLIC_PROD_HARDENING.md`](./PUBLIC_PROD_HARDENING.md).

---

## Scripts

| Script | Purpose |
|--------|---------|
| [`scripts/enforce-windows-hardening.ps1`](../scripts/enforce-windows-hardening.ps1) | Applies / re-applies the full Windows posture |
| [`scripts/install-hardening-enforcer-task.ps1`](../scripts/install-hardening-enforcer-task.ps1) | Registers scheduled task `DSH-Windows-Hardening-Enforcer` |
| [`scripts/start-dsh-deps.ps1`](../scripts/start-dsh-deps.ps1) | Starts Postgres + Ollama + Redis/Memurai when you need them |
| [`scripts/stop-dsh-deps.ps1`](../scripts/stop-dsh-deps.ps1) | Stops those deps (+ `wsl --shutdown`) to free RAM |
| [`scripts/sovereign-setup-windows.ps1`](../scripts/sovereign-setup-windows.ps1) | Initial Windows install (tools, venv, GPG, baseline hardening) |

Log file: `logs/hardening-enforcer.log`

---

## Quick start (new Windows machine)

Run elevated PowerShell from the repo root:

```powershell
# 1) Install / refresh DSH (if not already done)
Set-ExecutionPolicy Bypass -Scope Process -Force
.\scripts\sovereign-setup-windows.ps1 -AiChoice 6

# 2) Install the recurring enforcer (logon + startup + every 3 hours)
.\scripts\install-hardening-enforcer-task.ps1

# 3) Run once now
.\scripts\enforce-windows-hardening.ps1

# Optional dry-run
.\scripts\enforce-windows-hardening.ps1 -ReportOnly
```

When developing with the agent API / local models:

```powershell
.\scripts\start-dsh-deps.ps1
# ... work ...
.\scripts\stop-dsh-deps.ps1
```

---

## What the enforcer turns **off** (or Manual + stopped)

### Services → Manual (stopped if running)

| Service name | What it is |
|--------------|------------|
| `postgresql-x64-18` | Postgres (DSH) — start via `start-dsh-deps.ps1` |
| `Memurai` | Redis-compatible Windows service (DSH workers) |
| `DiagTrack` | Connected User Experiences / telemetry |
| `dmwappushservice` | WAP push messaging |
| `LightKeeperService` | MSI Mystic Light / RGB |
| `Mystic_Light_Service` | MSI Mystic Light |
| `MSI Foundation Service` | MSI OEM |
| `MSI Sendevsvc` | MSI sensor helper |
| `MSI_Center_Service` | MSI Center |
| `NahimicService` | Nahimic audio bloat |
| `Micro Star SCM` | MSI SCM helper |
| `IntelAudioService` | Intel audio helper (Realtek stack kept) |
| `IntelGraphicsSoftwareService` | Intel Graphics Software |
| `ipfsvc` | Intel Innovation Platform Framework |
| `jhi_service` | Intel Dynamic Application Loader |
| `cplspcon` | Intel HDCP content protection helper |
| `dptftcs` | Intel Dynamic Tuning **telemetry** |
| `WMIRegistrationService` | Intel ME WMI registration |
| `RstMwService` | Intel Storage Middleware |
| `PIEServiceNew` | Intel PROSet/Wireless helper |
| `ClickToRunSvc` | Microsoft Office Click-to-Run |
| `Spooler` | Print Spooler (no printer assumed) |
| `SysMain` | Superfetch / SysMain |
| `PcaSvc` | Program Compatibility Assistant |
| `DusmSvc` | Data Usage tracking |

### Services → Disabled (stopped)

| Service name | Why Disabled instead of Manual |
|--------------|--------------------------------|
| `WSearch` | Windows Search respawns aggressively |
| `SharedAccess` | Internet Connection Sharing / ICS |

### Processes killed if present

`LEDKeeper2`, `PhoneExperienceHost`, `Widgets`, `WidgetService`,
`CrossDeviceService`, `CrossDeviceResume`, `SearchHost`, `OfficeClickToRun`,
`IntelGraphicsSoftware.Service`, `IntelGraphicsSoftware`, `ipf_helper`,
`ipf_uf`, `RtkAudUService64`, `memurai`

### Startup entries removed

**HKCU Run:** Teams, Signal Desktop, OneDrive Lists sync, Discord, Steam,
Epic (when present).

**HKLM Run:** `RtkAudUService` and common game/Adobe helpers when present.

**Startup folder:** `Ollama.lnk` removed (launch on demand).

**Teams:** StartupApproved disable blob + `PreventFirstLaunchAfterInstall` policy.

### Scheduled tasks disabled (name/path match)

Tasks matching MSI LEDKeeper / OmApSvcBroker / OneDC_Updater / Mystic / Intel
Graphics helpers when found.

### Policy DWORD values set

| Path | Name | Value |
|------|------|------:|
| `HKLM\...\Windows\DataCollection` | `AllowTelemetry` | 0 |
| `HKLM\...\Windows Search` | `AllowCortana` | 0 |
| `HKCU\...\AdvertisingInfo` | `Enabled` | 0 |
| `HKLM\...\Policies\Microsoft\Dsh` | `AllowNewsAndInterests` | 0 |
| `HKLM\...\Windows Feeds` | `EnableFeeds` | 0 |
| `HKCU\...\Explorer\Advanced` | `TaskbarDa` | 0 (Widgets button) |
| Content Delivery Manager keys | suggestions / soft landing | 0 |

---

## What stays **on** (intentionally)

| Component | Reason |
|-----------|--------|
| `WinDefend` | Defender — connected lockdown baseline |
| `mpssvc` + all firewall profiles Enabled | Host firewall |
| `NVDisplay.ContainerLocalSystem` | NVIDIA GPU driver helper |
| `RtkAudioUniversalService` | Realtek audio (speakers/headset) |
| Networking (DHCP, DNS client, WLAN, etc.) | Browsing + package installs |
| Cursor / terminal / local apps | Primary workload |

GPG commit signing is configured by `sovereign-setup-windows.ps1` (not re-toggled
by the enforcer every run). Confirm with:

```powershell
git config --global user.signingkey
git config --global commit.gpgsign
```

---

## Scheduled task

| Property | Value |
|----------|--------|
| Name | `DSH-Windows-Hardening-Enforcer` |
| Triggers | At logon, at startup, every **3 hours** |
| Run level | Highest (admin) |
| Action | `enforce-windows-hardening.ps1` |

```powershell
# Status
Get-ScheduledTask -TaskName 'DSH-Windows-Hardening-Enforcer'
Get-ScheduledTaskInfo -TaskName 'DSH-Windows-Hardening-Enforcer'

# Run now
Start-ScheduledTask -TaskName 'DSH-Windows-Hardening-Enforcer'

# Reinstall after moving the repo
.\scripts\install-hardening-enforcer-task.ps1
```

---

## Operator checklist

- [ ] `enforce-windows-hardening.ps1` run elevated at least once
- [ ] Scheduled task registered and `LastTaskResult` is `0`
- [ ] Firewall profiles Enabled; `WinDefend` Running
- [ ] `.env` exists locally and is **not** committed
- [ ] `DOME_PROVIDER` set appropriately (`local` for air-gapped agent work; `mixed` default)
- [ ] BitLocker enabled on system volume (`manage-bde -status C:`) — recommended, not set by these scripts
- [ ] Postgres/Memurai/Ollama only running when you started them via `start-dsh-deps.ps1`

---

## Undo / exceptions

| Need | Action |
|------|--------|
| Print something | `Start-Service Spooler` (enforcer will stop it again later) |
| Office desktop apps | Opening Office may restart Click-to-Run; or `Start-Service ClickToRunSvc` |
| Windows Search | `Set-Service WSearch -StartupType Manual; Start-Service WSearch` — remove from enforcer if you want it permanent |
| MSI RGB / Center | Start the MSI services manually; expect enforcer to stop them on next run |
| Permanent allow-list change | Edit `$manualStop` / Disabled section in `enforce-windows-hardening.ps1`, then re-run |

To stop enforcement entirely:

```powershell
Unregister-ScheduledTask -TaskName 'DSH-Windows-Hardening-Enforcer' -Confirm:$false
```

---

## Threat model (Windows node)

- **Trusted:** local operator, BitLocker-recommended disk, Defender + firewall on.
- **Untrusted by default:** OEM “optimizer” / RGB / Intel helper services, Teams/Signal autostart, Windows consumer telemetry surfaces.
- **Explicit choice:** cloud LLM APIs via `.env` / `DOME_PROVIDER`; Ollama local models; Trinity mesh is Phase 2 and **not** activated by these scripts.
- **Out of scope here:** dnscrypt-proxy, SIP/FileVault (macOS), full air-gap.

---

## See also

- [`scripts/sovereign-setup-windows.ps1`](../scripts/sovereign-setup-windows.ps1) — initial bootstrap
- [`compute/requirements.windows.txt`](../compute/requirements.windows.txt) — Python deps without `pyquil` (Windows Application Control)
- [`SECURITY.md`](../SECURITY.md) — project vulnerability policy

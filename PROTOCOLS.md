# DOME-HUB Core Protocols

## Sovereignty
- All data stays local. No cloud sync, no telemetry, no phone-home.
- Only approved outbound: Kiro (AWS), Claude (Anthropic), GitHub (git push), Mail (IMAP).
- DNS encrypted via dnscrypt-proxy. No Google DNS.

## Access Control
- Privileged actions require approval from authorized Trinity Consortium members.
- No unauthorized daemons or launch agents.
- GPG-signed commits only.

## Security
- FileVault ON at all times.
- Firewall + stealth mode ON at all times.
- Screen lock ON. No plaintext secrets in code or git.
- Audit passes 100% green before any release.

## Code Quality
- Python: no import errors, pyflakes clean.
- TypeScript: typecheck passes, lint passes.
- All scripts executable.

## Data Integrity
- SQLite DB updated after every session.
- KB re-ingested after any new content.
- Git: all changes committed and pushed to master.

## Maintenance
- Run `bash scripts/audit.sh` — must be all green.
- Run `bash scripts/daemon-watch.sh` — must be all approved.
- Run `pnpm sync` after every session.

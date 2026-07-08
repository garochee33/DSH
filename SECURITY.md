# Security Policy

DSH is designed to be a sovereign, local-first environment. Security is a
first-class concern — not an afterthought.

## Supported versions

DSH follows a rolling-release model. Only the latest `master` receives
security fixes. Earlier tags are frozen.

| Version | Supported |
|---------|-----------|
| `master` (latest) | ✅ |
| any tag `< latest` | ❌ |

## Reporting a vulnerability

**Do not open a public issue for security reports.**

Please report vulnerabilities privately via one of:

1. **GitHub Security Advisory** — preferred. Open a draft advisory at
   https://github.com/garochee33/DSH/security/advisories/new
2. **Email** — encrypt to the maintainer's GPG key (see `compute/claude-env.md`
   for key-lookup instructions, or query the `pass` store on a trusted node).

Expected response window: 72 hours for triage, 14 days for remediation plan.

## What counts as a vulnerability

High priority:

- Remote code execution in any of the setup scripts
  (`scripts/sovereign-setup-mac.sh`, `spore.sh`, `compute/bootstrap-claude.sh`)
- Secret exposure (keys, tokens, node identity) in logs, git history,
  or runtime artifacts
- Privilege escalation via `dome-approve.sh` / `dome-sudo.sh`
- Supply-chain compromise (malicious dependency injected via setup)
- Sandbox escape (agent tool breaking out of its intended scope)
- Mesh-peer impersonation or handshake bypass (once `spore.sh` is activated)

Medium priority:

- Path-traversal or command-injection in project scripts
- Unsafe default file permissions
- Secrets written to `.bash_history` / `.zsh_history`

Out of scope (not vulnerabilities):

- Default settings that a user can disable (e.g. telemetry-blocking can be
  turned off by the operator)
- Dependencies flagged by npm/pip audit but with no known exploit path
- Findings that require the attacker to already have sudo on the machine

## Hardening checklist for operators

Before treating your node as production-ready, confirm:

- [ ] `.env` is in `.gitignore` and never committed
- [ ] GPG key generated and `pass` store initialized
- [ ] FileVault ON (`fdesetup status`)
- [ ] SIP enabled (`csrutil status`)
- [ ] Firewall + stealth mode ON
- [ ] `bash scripts/audit.sh` returns all green
- [ ] `bash scripts/dome-check.sh` returns all green
- [ ] Secrets live in `pass` or macOS Keychain, never plaintext files

See also: `PROTOCOLS.md`, `docs/PUBLIC_PROD_HARDENING.md`.

## Threat model

DSH assumes:

- The local machine is trusted by the operator (disk-encrypted, screen-locked,
  firewall ON).
- Outbound API calls to Anthropic / OpenAI / Ollama / Trinity mesh are
  explicit operator choices. Providers can log requests — never send
  sensitive data to cloud providers in `DOME_PROVIDER=local` you don't trust.
- Trinity mesh peers are authenticated via E2EE handshake (once
  `spore.sh` is activated) — unauthenticated peers cannot enter the mesh.

DSH does NOT protect against:

- A compromised operator account
- A compromised system with root access
- Physical access to a powered-on machine with disk decrypted

## Responsible disclosure

We support coordinated disclosure. Researchers who follow responsible-
disclosure practice will be credited in release notes unless they prefer
anonymity.

Thank you for helping keep DSH sovereign.

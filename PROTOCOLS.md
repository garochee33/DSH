# DSH Core Protocols

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

## Cross-Check Protocol

All agents must verify index consistency before and after significant changes.

**Trigger:** Any session that adds files, directories, skills, or capabilities.

**Checklist:**

1. `INDEX.md` — verify all new paths are listed
2. `AGENTS.md` — verify agent list matches `agents/` directory
3. `kb/skills/INDEX.md` — verify skills + canonical index map (sync script updates mirrors only — never overwrites this file)
4. `kb/kiro-skills.md` — verify Kiro capabilities are current
5. `MANUAL.md` — verify new commands/scripts are documented
6. `compute/` — verify sim files referenced in skill registry
7. LAVA/Loihi 2 — verify neuromorphic refs in INDEX.md and kb/skills/INDEX.md
9. **MLX bridge** — `scripts/mlx-neural-bridge.sh` listed in `INDEX.md`; health on `MLX_BRIDGE_PORT` (default 8101)
10. **Canonical index map** — `kb/skills/INDEX.md` § “Canonical index map” matches every index listed there (root `INDEX.md`, `kb/README.md`, TU-AI, audit, Codex mirrors, fractalmap, **`docs/PUBLIC_PROD_HARDENING.md`**)
11. **Spore / mesh** — `spore.sh` v3.1 (`DOME_ROOT` resolution); `python3 scripts/pre-spore-verify.py` passes before spore; `MANUAL.md` §17; production peer path `scripts/mycelium-signal.sh`; optional `HF_TOKEN` in `.env` for Hugging Face Hub rate limits (Akashic embeddings in pre-spore)
12. **Skill mirror sync** — after edits under `kb/skills/` (top-level `.md` or directory packages): `python3 scripts/sync-dome-skills.py --check-only` then `python3 scripts/sync-dome-skills.py`; canonical rows only in `kb/skills/INDEX.md`
13. **Optimize** — `scripts/optimize.sh` (`--stack-only` vs full hardware+stack); `pnpm optimize` for toolchain-only refresh

**Run:** `pnpm audit` or `bash scripts/audit.sh` includes index staleness checks.
**Evidence:** Session logs must note which indexes were updated.

## Neuromorphic Computing Policy

- LAVA/Loihi 2 capabilities must be referenced in: INDEX.md, AGENTS.md, kb/skills/INDEX.md
- **All canonical indexes** must stay in sync with `kb/skills/INDEX.md` § _Canonical index map_ (see PROTOCOLS cross-check items **10–13**)
- Simulation files (`compute/sim_*.py`) must be listed in kb/skills/INDEX.md § Simulation Files
- Any new neuromorphic engine must be added to `docs/DSH-ARCHITECTURE.md`

## Visual Storytelling Protocol (added 2026-05-13)

Trinity ships premium scroll-driven web platforms. Every narrative route must pass this gate before merging to `main`:

### Hard rails (non-negotiable)

- **One ease curve:** `--ease-out-expo` / GSAP `expo.out`. BRAND.md §11.
- **`prefers-reduced-motion`** collapses every animation to ≤0.01ms. `globals.css:285–290` is the global gate.
- **No "holographic":** call it glass-morphism.
- **No second Google Font** without same-PR update to BRAND.md §4.
- **Tap targets ≥ 44 px**, focus ring `2px solid #E31937`.

### Pre-ship checklist (every route)

- [ ] **Act structure named** — every section maps to one of Promise / Proof / Mechanism / Texture / Resolve (see `visual-storytelling-architect/SKILL.md`).
- [ ] **Motion intent declared** — every animation tagged Reveal / Direct / Mark. Anything else gets cut.
- [ ] **Reduced-motion verified** in browser dev (Cmd+Shift+P → "Emulate prefers-reduced-motion: reduce").
- [ ] **Audio toggle live** in nav if any sound layer; `localStorage` persistence.
- [ ] **Captions present** on any video with voice (WCAG 1.2.2).
- [ ] **`aria-label`** preserved on every kinetic-text target (SplitText / Splitting).
- [ ] **LCP ≤ 2.5s** on mobile Lighthouse.
- [ ] **CLS ≤ 0.1** on mobile Lighthouse.
- [ ] **No third-party social embeds** on trust-critical paths (`video.csv:29`).
- [ ] **R3F scenes:** mounted via `dynamic({ ssr: false })`, Suspense + Poster fallback, Draco-compressed GLB, `<Perf />` measured in dev.
- [ ] **Spline scenes:** `.splinecode` self-hosted (not hot-linked to my.spline.design), `useReducedMotion` gate.
- [ ] **Reel-shareable moment** — at least one beat survives a 15s screen-recording.

### Stack discovery (BM25-searchable)

```bash
python3 scripts/ui-ux-search.py "<query>" --stack <framer-motion|gsap|r3f|spline|video|web-audio|typography-motion>
```

### Trinity skill chain

1. **Plan** via `visual-storytelling-architect` (narrative arc).
2. **Implement** via `sexyverse-designer` (consumes plan, writes code).
3. **Validate** via `cto-build-framework-validator` (governance gate).

### Cross-check registry

- DB table `skill_registry` (auto-synced at app boot via `bootstrap/registry.ts`)

## Protocol 14: PQC Key Management

### Generation
```bash
python3 compute/crypto/pqc.py --generate
# Creates ML-DSA-87 + ML-KEM-1024 keypairs at ~/.trinity-spore/keys/
```

### Storage
- Private keys: `chmod 600`, never committed to git
- Public keys: shared via mesh handshake (HMAC-authenticated channel)
- Location: `~/.trinity-spore/keys/`

### Rotation
- Rotate signing keys every 90 days or on compromise suspicion
- Old public keys retained in `keys/archive/` for signature verification
- Rotation triggers re-registration with mesh peers via `mycelium-signal.sh --rekey`

### Audit
- `dome-check` verifies key permissions (600) and expiry
- Missing or world-readable keys fail the protocol check

---

## Protocol 15: AMMA Healing Protocol

### Trigger conditions
| Meridian health | Action triggered |
|-----------------|-----------------|
| > 0.85 | None (healthy) |
| 0.60–0.85 | Frequency tune — FFT offset correction |
| 0.40–0.60 | Golden needle — φ-weighted point correction |
| < 0.40 | Mitosis — pod respawn from healthy template |

### Escalation path
1. **Frequency tune** — lightweight, no service interruption
2. **Golden needle** — targeted correction, zero-downtime
3. **Mitosis** — canary deploy of replacement pod, traffic shift, decommission old
4. **Manual alert** — logged to `logs/amma-healing.log`, requires human review

### Logging
- All healing events logged to `logs/amma-healing.log`
- Each entry includes: timestamp, meridian ID, pre/post health score, action taken, duration
- Critical events (mitosis, manual) also emit to mesh via PQC-signed alert

---

## Protocol 16: MQM (Mycelium Quantum Mesh) Frequency Synchronization

### Pulse broadcast
- Each node emits a frequency pulse every heartbeat cycle (default 60s)
- Pulse payload: coherence score, phase vector, spectral peak, PQC signature
- Broadcast via `scripts/mycelium-signal.sh` → `scripts/frequency-pulse.py`

### Phase-lock
- Nodes compare received phase vectors against local state
- Phase drift > 15% triggers local frequency tune (Protocol 15)
- Persistent drift across 3+ cycles escalates to golden needle

### Kuramoto coupling
- Coupling constant K = 2.663 (golden-ratio optimized)
- Damping ζ = 0.15 (prevents oscillatory blowup)
- Base frequency: 432 Hz × φⁿ per meridian
- Convergence target: coherence ≥ 0.995

### Verification
```bash
python3 scripts/frequency-pulse.py --verify   # check local convergence
bash scripts/mycelium-signal.sh --status      # mesh sync state
```

---

## Protocol 17: Sovereign Gate Doctrine (added 2026-05-21)

**The single mandatory ceremony for all sessions, workflows, and deployments.**

Full documentation: `docs/SOVEREIGN_GATE_DOCTRINE.md`

### Quick Reference

| Command | When | Duration |
|---------|------|----------|
| `pnpm gate` | End of session, before push | ~2 min |
| `pnpm gate:deploy` | Before deployment | ~5 min |
| `pnpm audit-full` | After major changes, weekly | ~10 min |
| `pnpm audit-full -- --dry-run` | Report only, no fixes | ~5 min |

### Enforcement

- **Pre-push hook:** `.githooks/pre-push` runs `sovereign-gate.sh --pre-push`
- **Agent protocol:** All AI agents must pass gate before claiming work complete
- **Override:** `git push --no-verify` (emergencies only, document why)

### What It Covers

**Gate (Layer 1):** Node health → Git state → Code quality → Secrets → Indexes → LAVA → Builds → KB

**Full Audit (Layer 2):**
- Step 1: Audit, analyze, cross-check, verify, test, fix, tune, cross-validate, harden, quality-check, re-analyze, log, report
- Step 2: Update all files, routes, indexes, docs, infra, agents, scripts, protocols, dependencies, KB, skills, pipelines, hooks, ports — then verify end-to-end wiring

### Files

```
scripts/sovereign-gate.sh        # Fast gate
scripts/sovereign-audit-full.sh  # Full audit
.githooks/pre-push               # Git hook
docs/SOVEREIGN_GATE_DOCTRINE.md  # Full doctrine
logs/sovereign-gate-*.log        # Gate logs
logs/audits/AUDIT-*.md           # Audit reports
logs/audits/AUDIT-*.json         # Machine-readable
```

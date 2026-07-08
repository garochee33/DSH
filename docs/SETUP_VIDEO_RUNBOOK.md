# DSH Setup Video Runbook

Use this runbook to record a consistent onboarding video that shows exactly
what is downloaded and materialized into a new sovereign node.

## Goal

Show new users, in one pass, that DSH setup:
- installs dependencies
- provisions local agent + KB + DB surfaces
- verifies local payload readiness

## Recording Outline (8-12 min)

1. Intro (30-60s)
- Explain DSH = local sovereign base.
- Explain Phase 1 local node vs optional Phase 2 mesh.

2. Clone + launch setup (1-2 min)
```bash
git clone https://github.com/garochee33/DSH.git
cd DSH
bash scripts/sovereign-setup-mac.sh
```
- Call out live `[step/total]` phase output.
- Optional pre-roll visual-only demo:
```bash
bash scripts/sovereign-setup-mac.sh --preview-cinematic
```

3. Highlight payload materialization (2-3 min)
- Show setup phases:
  - `ChromaDB Ingest`
  - `Claude Agent Registration`
  - `Local Node Payload Verification`
- Explain:
  - `agents/` -> local runtime
  - `kb/` -> local corpus
  - `db/dome.db` + `db/chroma/` -> local memory/state

4. Post-setup verification (2-3 min)
```bash
pnpm check
pnpm public:check
```
- Show green checks and explain what they validate.

5. First run actions (1-2 min)
```bash
source ~/.zshrc
pnpm serve
pnpm worker
```
- Mention where logs + DB live on disk.

## Optional Terminal Capture Tooling

If you want CLI-native recording:
```bash
brew install asciinema
asciinema rec dsh-setup-demo.cast
```

Then convert to shareable video/GIF with your preferred renderer.

## Talking Points (must include)

- Everything is local-first by default.
- Setup localizes agent/KB/DB to that specific node.
- No hidden cloud dependency for Phase 1.
- User can re-run setup safely.

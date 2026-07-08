# DSH Home Overlay Runbook

## Canonical Roles

- `$HOME` remains the macOS account home and compatibility route.
- `$HOME/DSH` is the private canonical DOME control repo.
- `$HOME/DSH/home` is private runtime home data and is ignored by git.
- `$HOME/DSH` is the public sanitized distribution; do not move or mutate it during private overlay work unless the DSH export flow is being run intentionally.
- Existing home routes such as `$HOME/projects/...` remain valid through symlinks after overlay moves.

## Current State

Already moved into `DSH/home` and symlinked back:

- `$HOME/go`
- `$HOME/.agents`
- `$HOME/.codex`
- `$HOME/.config`
- `$HOME/.cursor`
- `$HOME/.kiro`
- `$HOME/.qwen`
- `$HOME/.unified-ai`
- `$HOME/.vscode`
- `$HOME/.npm`
- `$HOME/.npm-global`
- `$HOME/.nvm`
- `$HOME/.cache`

Deferred because they were live, iCloud-managed, or backup-gated:

- `Desktop`, `Documents`, `Downloads`
- `projects`
- `trinity-unified-ai`
- `DSH`, `OpenHands`, `full-local-archives`
- `.claude`, `.local`, `.ollama`

## Execution Rules

- Always run `scripts/dome-home-overlay.sh plan` before a move.
- For immediate safe passes, use `scripts/dome-home-overlay.sh apply --safe-now`.
- Do not move a path with live processes under it. Stop the service first, then rerun `plan`.
- Do not move iCloud-managed Desktop/Documents until iCloud Desktop & Documents sync is intentionally disabled or the move is intentionally deferred.
- Do not move Downloads, DSH, archives, `.ollama`, or the project forest until a Time Machine or external backup exists.

## Next Migration Windows


   ```bash
   scripts/dome-home-overlay.sh plan --only projects,trinity-unified-ai,.claude,.local
   scripts/dome-home-overlay.sh apply --only projects,trinity-unified-ai,.claude,.local --i-have-backup --skip-icloud
   scripts/dome-home-overlay.sh verify --allow-pending
   ```

2. After a backup, move personal/archive payloads:

   ```bash
   scripts/dome-home-overlay.sh plan --only Downloads,DSH,OpenHands,full-local-archives,.ollama
   scripts/dome-home-overlay.sh apply --only Downloads,DSH,OpenHands,full-local-archives,.ollama --i-have-backup --skip-icloud
   scripts/dome-home-overlay.sh verify --allow-pending
   ```

3. For Desktop/Documents, either keep them iCloud-managed in place or disable iCloud Desktop & Documents first, then run:

   ```bash
   scripts/dome-home-overlay.sh plan --only Desktop,Documents
   scripts/dome-home-overlay.sh apply --only Desktop,Documents --i-have-backup
   scripts/dome-home-overlay.sh verify --allow-pending
   ```

## Rollback

Rollback uses the private manifest in `DSH/home/.dome-overlay-manifest.json`.

```bash
scripts/dome-home-overlay.sh rollback --dry-run
scripts/dome-home-overlay.sh rollback
```

Use `--run-id <id>` to roll back a specific execution run.

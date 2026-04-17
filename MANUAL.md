# DOME-HUB Manual

Complete usage guide for the DOME-HUB sovereign development environment.
Last updated: 2026-04-17

---

## 1. First-Time Setup

### macOS (M1 / M2 / M3 / M4)
```bash
git clone https://github.com/gadikedoshim/DOME-HUB.git
cd DOME-HUB
bash scripts/sovereign-setup-mac.sh
```

### Windows
```powershell
git clone https://github.com/gadikedoshim/DOME-HUB.git
cd DOME-HUB
pwsh scripts/sovereign-setup-windows.ps1
```

---

## 2. Daily Usage

### Open DOME-HUB
```bash
dome          # jump to DOME-HUB from anywhere
code .        # open in VS Code
```

### Activate Python environment
```bash
source .venv/bin/activate
```

### Start databases
```bash
brew services start postgresql@17
brew services start redis
```

### Run protocol check (recommended daily)
```bash
dome-check
# or
pnpm check
```

---

## 3. Protocol Commands

### `dome-check`
Full protocol enforcer. Runs all security, network, daemon, code quality, data integrity, and git checks. Auto-fixes what it can.

```bash
dome-check
# or
bash scripts/dome-check.sh
# or
pnpm check
```

Checks performed:
- Firewall + stealth mode ON (auto-enables if off)
- FileVault, SIP status
- Screen lock (auto-enables)
- GPG key present
- Git commit signing (auto-enables)
- DNS routed through dnscrypt-proxy (auto-fixes)
- Unauthorized launch agents removed
- Python imports clean
- TypeScript typecheck passes
- SQLite DB present
- ChromaDB populated
- Git clean + up to date (auto-commits and pushes)

Log: `logs/dome-check.log`

---

### `dome-pm`
Project manager for all DOME-HUB repos and projects.

```bash
dome-pm <command> [args]
# or
bash scripts/dome-pm.sh <command> [args]
```

| Command | Description |
|---------|-------------|
| `new <category> <name>` | Create new project with venv, Node, git |
| `list` | List all projects with git branch + status |
| `status` | Git status across all repos |
| `push-all [message]` | Commit + push all repos |
| `pull-all` | Pull all repos |
| `link <path> <url>` | Link project to GitHub remote |
| `publish <path>` | Create GitHub repo + push |
| `env <dev\|prod>` | Switch environment |

Examples:
```bash
dome-pm new agents my-agent
dome-pm list
dome-pm push-all "feat: new feature"
dome-pm status
```

---

### `dome-approve`
Approval gate for privileged actions. Requires identity confirmation from an authorized Trinity Consortium member.

```bash
dome-approve <action> <description>
# or
bash scripts/dome-approve.sh <action> <description>
```

Example:
```bash
dome-approve "install-daemon" "Install custom LaunchAgent for backup"
```

Logs all approvals and denials to `logs/approvals.log`.

---

### `dome-sudo`
Privileged command wrapper. Passes any command through the approval gate before executing with `sudo`.

```bash
dome-sudo <command>
# or
bash scripts/dome-sudo.sh <command>
```

Example:
```bash
dome-sudo "launchctl load /Library/LaunchDaemons/custom.plist"
```

---

### `daemon-watch`
Daemon watchdog. Scans all LaunchAgents and LaunchDaemons, permanently removes any that are not on the approved list.

```bash
bash scripts/daemon-watch.sh
```

Approved daemons: `homebrew.mxcl.postgresql`, `homebrew.mxcl.redis`, `homebrew.mxcl.dnscrypt-proxy`, `com.apple.*`, `com.openssh.*`, `org.cups.*`

Log: `logs/daemon-watch.log`

---

## 4. pnpm Scripts

Run from the DOME-HUB root directory.

| Command | Description |
|---------|-------------|
| `pnpm check` | Run `dome-check.sh` — full protocol check |
| `pnpm sync` | Pull, ingest KB, commit, push |
| `pnpm ingest` | Populate ChromaDB from KB, logs, docs, agent code |
| `pnpm serve` | Start FastAPI agent server on port 8000 |
| `pnpm audit` | Run security audit script |
| `pnpm lint` | ESLint TypeScript source |
| `pnpm lint:fix` | ESLint with auto-fix |
| `pnpm format` | Prettier format all files |
| `pnpm typecheck` | TypeScript type check (no emit) |
| `pnpm worker` | Start Redis-backed async task worker |

### `pnpm sync`
End-of-session sync: pulls latest, re-ingests KB into ChromaDB, commits all changes, pushes.
```bash
pnpm sync
```

### `pnpm check`
Alias for `dome-check`. Run before any release or after any system change.
```bash
pnpm check
```

### `pnpm ingest`
Re-indexes all KB, logs, docs, and agent code into ChromaDB vector store.
```bash
pnpm ingest
# or
python3 scripts/ingest.py
```

### `pnpm serve`
Starts the FastAPI agent HTTP server with hot-reload.
```bash
pnpm serve
# Server available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

---

## 5. Create a New Project

```bash
newproject <category> <name>
# or
dome-pm new <category> <name>
```

Categories: `projects`, `agents`, `platforms`, `models`, `software`, `compute`

Example:
```bash
newproject agents my-agent
cd agents/my-agent
source .venv/bin/activate   # Python
nvm use                      # Node
code .                       # VS Code
```

Each project gets:
- Isolated Python `.venv`
- `.nvmrc` (Node 20)
- `pnpm` initialized
- `.env.example`
- `.gitignore`

---

## 6. Secret Management

Store secrets with `pass` (GPG-encrypted, never plaintext):

```bash
# Store a secret
pass insert dome/openai-key

# Retrieve
pass dome/openai-key

# Use in scripts
export OPENAI_API_KEY=$(pass dome/openai-key)
```

Never put secrets in `.env` files committed to git.

---

## 7. AI / GPU Compute

```python
import torch

# Use Apple GPU (M1/M2/M3/M4)
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

model = MyModel().to(device)
tensor = torch.ones(3, 3, device=device)
```

---

## 8. Git Workflow

All commits are GPG-signed automatically.

```bash
git add .
git commit -m "feat: description"   # auto-signed
git push
```

Create a new branch for each feature:
```bash
git checkout -b feature/my-feature
```

---

## 9. Security Maintenance

```bash
# Run full protocol check (security + code + git)
pnpm check

# Run audit only
bash scripts/audit.sh

# Re-run hardening after OS updates
sudo bash scripts/harden.sh

# Re-run optimization after reboots
sudo bash scripts/optimize.sh

# Check daemons
bash scripts/daemon-watch.sh
```

---

## 10. Database Access

### PostgreSQL
```bash
psql -U gadikedoshim -d postgres
```

### Redis
```bash
redis-cli
```

### SQLite (DOME-HUB internal DB)
```bash
sqlite3 db/dome.db
.tables
SELECT * FROM sessions;
SELECT * FROM stack;
SELECT * FROM agents;
SELECT * FROM skills;
```

### ChromaDB (vector store)
```python
from agents.core.memory.vector import VectorMemory
vm = VectorMemory("dome-kb")
results = vm.query("your query here", n_results=5)
```

---

## 11. Shell Aliases

| Alias | Action |
|-------|--------|
| `dome` | `cd /Users/gadikedoshim/DOME-HUB` |
| `newproject` | Run `scripts/new-project.sh` |
| `dome-check` | Run `scripts/dome-check.sh` |
| `dome-pm` | Run `scripts/dome-pm.sh` |
| `dome-approve` | Run `scripts/dome-approve.sh` |
| `dome-sudo` | Run `scripts/dome-sudo.sh` |

---

## 12. Trinity Consortium Integration

- KB API: `kb/trinity-unified-ai/`
- Developer context: `kb/developer-context.md`
- Linked with: Trinity Consortium network [member-only]
- Architecture: FRACTAL E8-SSII-AGI → Mycelium Neural Mesh → trinity-unified-ai

---

## 13. Updating DOME-HUB

```bash
cd /Users/gadikedoshim/DOME-HUB
pnpm sync
# or manually:
git pull
pnpm install
source .venv/bin/activate && pip install --upgrade -r compute/requirements.txt
pnpm ingest
```

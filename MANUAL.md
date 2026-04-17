# DOME-HUB Manual

Complete usage guide for the DOME-HUB sovereign development environment.

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

### Check security posture
```bash
bash scripts/audit.sh
```

---

## 3. Create a New Project

```bash
newproject <category> <name>
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

## 4. Secret Management

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

## 5. AI / GPU Compute

```python
import torch

# Use Apple GPU (M1/M2/M3/M4)
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

model = MyModel().to(device)
tensor = torch.ones(3, 3, device=device)
```

---

## 6. Git Workflow

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

## 7. Security Maintenance

```bash
# Run audit anytime
bash scripts/audit.sh

# Re-run hardening after OS updates
sudo bash scripts/harden.sh

# Re-run optimization after reboots
sudo bash scripts/optimize.sh
```

---

## 8. Database Access

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
```

---

## 9. Shell Aliases

| Alias | Action |
|-------|--------|
| `dome` | `cd /Users/gadikedoshim/DOME-HUB` |
| `newproject` | Run `scripts/new-project.sh` |

---

## 10. Trinity Consortium Integration

- KB API: `kb/trinity-unified-ai/`
- Developer context: `kb/developer-context.md`
- Linked with: `garochee33` (Enzo Garoche, EGD33) on GitHub
- Architecture: FRACTAL E8-SSII-AGI → Mycelium Neural Mesh → trinity-unified-ai

---

## 11. Updating DOME-HUB

```bash
cd /Users/gadikedoshim/DOME-HUB
git pull
pnpm install
source .venv/bin/activate && pip install --upgrade -r requirements.txt
```

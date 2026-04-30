# What's Next — Post-Setup Guide

You've installed DSH. Your sovereign node is live. Now what?

---

## 1. Verify Your Setup

```bash
pnpm check       # protocol enforcer — security, code, git
pnpm test        # 34 tests — confirms everything works
```

If both pass, you're production-ready.

---

## 2. Pick Your AI Assistant

The setup script prompted you to choose one. Switch anytime:

```bash
npm install -g kiro-cli                    # Kiro CLI
npm install -g @anthropic-ai/claude-code   # Claude Code
brew install --cask cursor                 # Cursor
gh extension install github/gh-copilot     # GitHub Copilot
pip install aider-chat                     # Aider
```

Your assistant reads `CONTEXT.md` automatically for repo understanding.

---

## 3. Configure Your Environment

Edit `.env` to match your setup:

```bash
# Provider strategy
DOME_PROVIDER=local    # air-gapped, Ollama only
DOME_PROVIDER=claude   # Anthropic API for all agents
DOME_PROVIDER=mixed    # best of both (default)

# Local model (change to match what you pulled)
DOME_LOCAL_MODEL=devstral:latest

# API keys (only if using cloud providers)
ANTHROPIC_API_KEY=your-key-here
```

### Pull a local model

```bash
ollama pull devstral          # 14GB — agentic tool-use, 128k context
ollama pull llama3.1:8b       # 5GB — general purpose
ollama pull nomic-embed-text  # 274MB — embeddings (recommended)
```

---

## 4. Customize Your Stack

### Add to your knowledge base

Drop any `.md`, `.txt`, or `.pdf` into `kb/`, then:

```bash
pnpm ingest      # indexes into ChromaDB — instantly searchable by agents
```

### Add shell aliases

Edit `scripts/zshrc-dome.sh`:

```bash
alias myapp="cd $DOME_ROOT/projects/my-app"
alias deploy="bash $DOME_ROOT/scripts/my-deploy.sh"
```

Then `source ~/.zshrc`.

### Add custom scripts

```bash
chmod +x scripts/my-script.sh
# Add to package.json if you want pnpm access:
# "my-command": "bash scripts/my-script.sh"
```

### Switch databases

PostgreSQL and Redis are running. Add more:

```bash
brew install mysql mongodb-community   # or any DB you need
```

---

## 5. Optimize for Your Hardware

```bash
# Check what DSH detected about your machine
python3 scripts/machine-probe.py

# Re-run hardware optimization after OS updates
sudo bash scripts/optimize.sh

# Re-run security hardening
sudo bash scripts/harden.sh
```

### Apple Silicon GPU

PyTorch MPS is ready out of the box:

```python
import torch
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
```

---

## 6. Security Maintenance

```bash
pnpm check              # daily protocol check
pnpm audit              # security audit
bash scripts/daemon-watch.sh   # remove unauthorized daemons
```

Secrets go in `pass` (GPG-encrypted), never in `.env` files committed to git:

```bash
pass insert dome/my-secret
export MY_SECRET=$(pass dome/my-secret)
```

---

## 7. Start Building

### Create a new project

```bash
newproject projects my-app        # web app, API, tool
newproject agents my-agent        # AI agent
newproject platforms my-platform  # product or SaaS
newproject models my-model        # ML model or fine-tune
```

Each project gets its own Python venv, Node, `.env`, `.gitignore`.

### Bring in existing projects

Move or symlink your existing repos into DSH:

```bash
# Option A: symlink (recommended — keeps original location)
ln -s ~/my-existing-project ~/DSH/projects/my-existing-project

# Option B: move
mv ~/my-existing-project ~/DSH/projects/
```

### Start the AI agent server

```bash
pnpm serve       # http://localhost:8000
pnpm worker      # async task queue (requires Redis)
```

---

## 8. Trinity Consortium (Optional — Phase 2)

DSH works fully standalone. If you want mesh access:

1. Request access at [kommunity.life](https://kommunity.life)
2. Receive your `SPORE_TOKEN` + JWT
3. Add to `.env`:
   ```
   HUB_API_SECRET=your-secret
   TRINITY_JWT=your-jwt
   ```
4. Run: `bash spore.sh`

This connects your node to the FRACTAL-E8-SSII lattice and Mycelium Neural Mesh.

---

## 9. Daily Workflow

```bash
dome              # jump to DSH from anywhere
pnpm check        # verify protocols
pnpm serve        # start agent server
# ... build things ...
pnpm ingest       # re-index KB after adding content
pnpm sync         # pull + ingest + commit + push
```

---

## 10. Get Help

- `README.md` — project overview
- `MANUAL.md` — complete usage guide (15 sections)
- `INDEX.md` — full file reference
- `CONTEXT.md` — agent-friendly quick reference
- `kb/` — searchable knowledge base
- GitHub Issues: https://github.com/garochee33/DSH/issues

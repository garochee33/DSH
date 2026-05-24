# DOME-HUB environment
export DOME_ROOT="${DOME_ROOT:-$HOME/DOME-HUB}"
export DOME_HOME="${DOME_HOME:-$DOME_ROOT/home}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$DOME_HOME/.config}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$DOME_HOME/.cache}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-$DOME_HOME/.local/share}"
export CLAUDE_AGENT_WORKDIR="${CLAUDE_AGENT_WORKDIR:-$DOME_ROOT}"
export PATH="$DOME_ROOT/scripts:$PATH"

# Pin all AI/ML model caches inside DOME-HUB — nothing leaks to ~/
export SENTENCE_TRANSFORMERS_HOME="$DOME_ROOT/models"
export HF_HOME="$DOME_ROOT/models/hf"
export TRANSFORMERS_CACHE="$DOME_ROOT/models/hf"
export TORCH_HOME="$DOME_ROOT/models/torch"
export MLX_MODEL_PATH="$DOME_ROOT/models/mlx"

# Provider strategy: local | claude | mixed
# local  = all agents use DOME_LOCAL_MODEL (default Ollama; mlx-* for MLX) — air-gapped
# claude = all agents use Anthropic API
# mixed  = per-agent optimal (local for KB/code, cloud for research)
export DOME_PROVIDER="mixed"
export DOME_LOCAL_MODEL="llama3.1:8b"

_dome_env_value() {
  local key="$1"
  local file="${2:-$DOME_ROOT/.env}"
  local line

  [ -f "$file" ] || return 1
  line="$(grep -E "^${key}=" "$file" | tail -n 1)" || return 1
  line="${line#*=}"
  line="${line%\"}"
  line="${line#\"}"
  line="${line%\'}"
  line="${line#\'}"
  printf '%s' "$line"
}

if [ -z "${HUB_API_SECRET:-}" ]; then
  HUB_API_SECRET="$(_dome_env_value HUB_API_SECRET "$DOME_ROOT/.env" 2>/dev/null || true)"
  [ -n "$HUB_API_SECRET" ] && export HUB_API_SECRET
fi
unset -f _dome_env_value 2>/dev/null || true

# Homebrew
eval "$(brew shellenv 2>/dev/null || true)"

# pyenv
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
command -v pyenv &>/dev/null && eval "$(pyenv init -)"

# nvm
export NVM_DIR="$HOME/.nvm"
_BREW_PREFIX="$(brew --prefix 2>/dev/null || echo /opt/homebrew)"
[ -s "$_BREW_PREFIX/opt/nvm/nvm.sh" ] && source "$_BREW_PREFIX/opt/nvm/nvm.sh"

# go
export GOPATH="$HOME/go"
export PATH="$GOPATH/bin:$PATH"

# starship prompt
command -v starship &>/dev/null && eval "$(starship init zsh)"

# zoxide
command -v zoxide &>/dev/null && eval "$(zoxide init zsh)"

# zsh plugins (only if installed)
[ -f "$_BREW_PREFIX/share/zsh-autosuggestions/zsh-autosuggestions.zsh" ] && \
  source "$_BREW_PREFIX/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
[ -f "$_BREW_PREFIX/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ] && \
  source "$_BREW_PREFIX/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"

# DOME-HUB aliases
alias dome="cd $DOME_ROOT"
alias newproject="$DOME_ROOT/scripts/new-project.sh"
alias dome-pm="bash $DOME_ROOT/scripts/dome-pm.sh"
alias dome-approve="bash $DOME_ROOT/scripts/dome-approve.sh"
alias dome-sudo="bash $DOME_ROOT/scripts/dome-sudo.sh"
alias daemon-watch="bash $DOME_ROOT/scripts/daemon-watch.sh"
alias dome-check="bash $DOME_ROOT/scripts/dome-check.sh"

# Trinity multi-workspace helpers (DOME-HUB + 3 project dirs)
trinity-ws() {
  bash "$DOME_ROOT/scripts/trinity-workspaces.sh" "$@"
}

trinity-list() {
  trinity-ws list
}

trinity-status() {
  trinity-ws status
}

# Sacred Pipeline Runner (Consortium)
trinity-run() {
  ( cd "$TRI_DIR_CONSORTIUM" && bash scripts/trinity-run.sh "$@" )
}

# Workspace Fan-out (DOME-HUB)
alias trinity-all='trinity-ws run'

# Fast navigation for the active 4 directories
cd-dome() {
  cd "$(trinity-ws path dome-hub)"
}

cd-womb() {
  cd "$(trinity-ws path the-womb)"
}

cd-consortium() {
  cd "$(trinity-ws path trinity-consortium)"
}

cd-console() {
  cd "$(trinity-ws path trinity-dev-console)"
}

cd-home() {
  cd "$DOME_HOME"
}

# Akashic Co-Pilot — dimensional context on every session
alias akashic-start="bash $DOME_ROOT/scripts/akashic-start.sh"
alias akashic-query="source $DOME_ROOT/.venv/bin/activate && python3 $DOME_ROOT/akashic/assembler.py"

# Auto-assemble context on new terminal (silent background)
if [ -d "$DOME_ROOT/.venv" ]; then
  (source "$DOME_ROOT/.venv/bin/activate" && \
   python3 "$DOME_ROOT/akashic/assembler.py" > /dev/null 2>&1 &)
fi

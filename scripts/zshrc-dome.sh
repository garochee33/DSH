# DOME-HUB environment
export DOME_ROOT="/Users/gadikedoshim/DOME-HUB"
export PATH="$DOME_ROOT/scripts:$PATH"

# Homebrew
eval "$(/opt/homebrew/bin/brew shellenv)"

# pyenv
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
command -v pyenv &>/dev/null && eval "$(pyenv init -)"

# nvm
export NVM_DIR="$HOME/.nvm"
[ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && source "/opt/homebrew/opt/nvm/nvm.sh"

# go
export GOPATH="$HOME/go"
export PATH="$GOPATH/bin:$PATH"

# starship prompt
command -v starship &>/dev/null && eval "$(starship init zsh)"

# zoxide
command -v zoxide &>/dev/null && eval "$(zoxide init zsh)"

# zsh plugins (only if installed)
[ -f "/opt/homebrew/share/zsh-autosuggestions/zsh-autosuggestions.zsh" ] && \
  source "/opt/homebrew/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
[ -f "/opt/homebrew/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ] && \
  source "/opt/homebrew/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"

# DOME-HUB aliases
alias dome="cd $DOME_ROOT"
alias newproject="$DOME_ROOT/scripts/new-project.sh"
alias dome-pm="bash $DOME_ROOT/scripts/dome-pm.sh"

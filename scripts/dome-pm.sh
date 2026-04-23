#!/bin/bash
# DOME-HUB Project Manager
# Usage: dome-pm <command> [args]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOME_ROOT="${DOME_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
DB="$DOME_ROOT/db/dome.db"

cmd=$1; shift

case $cmd in

  # Create new project with venv, node, git repo
  new)
    CATEGORY=${1:?usage: dome-pm new <category> <name>}
    NAME=${2:?usage: dome-pm new <category> <name>}
    DIR="$DOME_ROOT/$CATEGORY/$NAME"
    mkdir -p "$DIR" && cd "$DIR"
    python3 -m venv .venv
    echo "20" > .nvmrc
    pnpm init -y > /dev/null 2>&1
    cp "$DOME_ROOT/.env.example" .env.example
    cat > .gitignore << 'EOF'
.env
.venv/
node_modules/
__pycache__/
*.pyc
dist/
.DS_Store
EOF
    git init && git add . && git commit -m "init: $NAME"
    echo "✓ $CATEGORY/$NAME created"
    echo "  cd $DIR && source .venv/bin/activate"
    ;;

  # List all projects across all categories
  list)
    echo "=== DOME-HUB Projects ==="
    for cat in projects platforms agents models software compute; do
      [ -d "$DOME_ROOT/$cat" ] && ls "$DOME_ROOT/$cat" 2>/dev/null | while read p; do
        BRANCH=$(git -C "$DOME_ROOT/$cat/$p" branch --show-current 2>/dev/null || echo "-")
        STATUS=$(git -C "$DOME_ROOT/$cat/$p" status --short 2>/dev/null | wc -l | tr -d ' ')
        echo "  [$cat] $p  branch:$BRANCH  uncommitted:$STATUS"
      done
    done
    ;;

  # Push all repos with uncommitted changes
  push-all)
    MSG=${1:-"chore: sync"}
    for cat in projects platforms agents models software compute kb; do
      find "$DOME_ROOT/$cat" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | while read dir; do
        if git -C "$dir" rev-parse --git-dir &>/dev/null; then
          CHANGES=$(git -C "$dir" status --short | wc -l | tr -d ' ')
          if [ "$CHANGES" -gt 0 ]; then
            git -C "$dir" add -A
            git -C "$dir" commit -m "$MSG"
            git -C "$dir" push 2>/dev/null && echo "✓ pushed: $dir" || echo "⚠ no remote: $dir"
          fi
        fi
      done
    done
    # Push DOME-HUB root
    cd "$DOME_ROOT" && git add -A && git diff --cached --quiet || \
      (git commit -m "$MSG" && git push && echo "✓ pushed: DOME-HUB root")
    ;;

  # Pull all repos
  pull-all)
    find "$DOME_ROOT" -maxdepth 3 -name ".git" -type d | while read gitdir; do
      dir=$(dirname "$gitdir")
      git -C "$dir" pull 2>/dev/null && echo "✓ pulled: $dir" || true
    done
    ;;

  # Status of all repos
  status)
    find "$DOME_ROOT" -maxdepth 3 -name ".git" -type d | while read gitdir; do
      dir=$(dirname "$gitdir")
      CHANGES=$(git -C "$dir" status --short 2>/dev/null | wc -l | tr -d ' ')
      BRANCH=$(git -C "$dir" branch --show-current 2>/dev/null)
      [ "$CHANGES" -gt 0 ] && echo "⚠ $dir  [$BRANCH]  $CHANGES changes" || echo "✓ $dir  [$BRANCH]"
    done
    ;;

  # Link project to GitHub remote
  link)
    DIR=${1:?usage: dome-pm link <path> <github-repo-url>}
    URL=${2:?usage: dome-pm link <path> <github-repo-url>}
    git -C "$DIR" remote add origin "$URL" && \
    git -C "$DIR" push -u origin master && \
    echo "✓ linked $DIR → $URL"
    ;;

  # Create GitHub repo and link
  publish)
    DIR=${1:?usage: dome-pm publish <path>}
    NAME=$(basename "$DIR")
    eval "$(/opt/homebrew/bin/brew shellenv)"
    gh repo create "$NAME" --private --source="$DIR" --remote=origin --push
    echo "✓ published: https://github.com/$(gh api user -q .login)/$NAME"
    ;;

  # Switch environment (dev/prod)
  env)
    ENV=${1:?usage: dome-pm env <dev|prod>}
    echo "DOME_ENV=$ENV" > "$DOME_ROOT/.env"
    echo "✓ environment set to $ENV"
    ;;

  *)
    echo "DOME-HUB Project Manager"
    echo ""
    echo "Commands:"
    echo "  new <category> <name>   Create new project"
    echo "  list                    List all projects + git status"
    echo "  status                  Git status across all repos"
    echo "  push-all [message]      Commit + push all repos"
    echo "  pull-all                Pull all repos"
    echo "  link <path> <url>       Link project to GitHub remote"
    echo "  publish <path>          Create GitHub repo + push"
    echo "  env <dev|prod>          Switch environment"
    ;;
esac

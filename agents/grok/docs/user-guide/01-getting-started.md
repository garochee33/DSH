# Getting Started

Grok Build is a terminal-based AI coding assistant from xAI. It runs as a TUI (Terminal User Interface) that understands your codebase, executes shell commands, edits files, searches the web, and manages tasks -- all from your terminal.

You can use it interactively as a full-screen TUI, run it headlessly for scripting and CI/CD, or integrate it into editors and IDEs via the Agent Client Protocol (ACP).

---

## Installation

Install the latest stable release (macOS, Linux, or Windows via Git Bash):

```bash
curl -fsSL https://x.ai/cli/install.sh | bash
```

Install a specific version:

```bash
curl -fsSL https://x.ai/cli/install.sh | bash -s 0.1.42
```

On **Windows (PowerShell)**, use the native PowerShell installer:

```powershell
irm https://x.ai/cli/install.ps1 | iex
```

Install a specific version:

```powershell
$env:GROK_VERSION="0.1.42"; irm https://x.ai/cli/install.ps1 | iex
```

The PowerShell installer automatically adds `%USERPROFILE%\.grok\bin` to your User PATH. Alternatively, install via [Git for Windows](https://gitforwindows.org/) (Git Bash) or MSYS2 using the bash script above. WSL users get the Linux binary automatically.

Verify the installation:

```bash
grok --version
```

Update to the latest version at any time:

```bash
grok update
```

---

## First Launch

Start Grok by running:

```bash
grok
```

On first launch, Grok opens your browser to authenticate with grok.com. Once you log in, credentials are stored in `~/.grok/auth.json` and persist across sessions. Tokens expire after 7 days; Grok will prompt you to re-authenticate when needed.

If you prefer API key authentication (e.g., for CI/CD or environments without a browser), set the `XAI_API_KEY` environment variable instead:

```bash
export XAI_API_KEY="xai-..."
grok
```

See [Authentication](02-authentication.md) for the full set of auth options including OIDC, external auth providers, and device code flow.

---

## Basic Interaction

Once authenticated, Grok presents a full-screen TUI with two main areas:

- **Scrollback** -- the conversation history showing your prompts, Grok's responses, tool calls, file edits, and more.
- **Prompt** -- the input area at the bottom where you type messages.

Type a message and press `Enter` to send it. Grok will think, plan, and act -- reading files, running commands, and editing code as needed. You can watch tool executions in real time as they stream into the scrollback.

Press `Esc` or `Tab` to move focus between the prompt and scrollback. When the scrollback is focused, use `j`/`k` to navigate entries and `h`/`l` to collapse/expand them.

### File References

Use `@` in your prompt to attach files:

```
@src/main.rs              # Attach a file
@src/main.rs:10-50        # Attach lines 10-50
@src/                     # Browse a directory
```

The `@` operator opens a fuzzy file picker. By default it respects `.gitignore` and hides dotfiles. Prefix with `!` to search hidden files:

```
@!.github                 # Search hidden files
@!.env                    # Attach a .env file
```

### Permissions

By default, Grok asks for permission before executing shell commands or editing files. You can approve individually or toggle auto-approve mode:

- Press `Ctrl+O` to toggle auto-approve (YOLO) mode
- Use the `--yolo` flag at launch: `grok --yolo`
- Type `/yolo` or `/always-approve on` in the prompt

---

## Key Concepts

### Sessions

Every conversation is a **session**. Sessions are automatically saved to `~/.grok/sessions/` and can be resumed later. Each session tracks the full conversation history, tool calls, file edits, and task state.

- Start a new session: `Ctrl+N` or `/new`
- Resume a previous session: `/load` in the TUI, or `--resume <ID>` from the CLI
- Continue the most recent session: `grok -c`

### Scrollback

The scrollback is the main display area. It shows:

- **User prompts** -- your messages, rendered as sticky headers
- **Agent messages** -- Grok's responses with full markdown rendering and syntax highlighting
- **Thinking blocks** -- Grok's reasoning process (collapsible)
- **Tool calls** -- file edits (with inline diffs), command executions, search results, and more
- **Task lists** -- TODO items tracking progress

Each entry can be collapsed/expanded with `h`/`l` or `e`. Press `y` to copy content, `Y` to copy metadata (e.g., the command that was run), or `Enter` to open in fullscreen.

### Tools

Grok has built-in tools for:

| Tool | Description |
|------|-------------|
| `read_file` / `search_replace` | Read and edit files with line-precise changes |
| `grep_search` | Regex search across your codebase (powered by ripgrep) |
| `list_dir` | List directory contents |
| `bash` | Execute shell commands |
| `web_search` / `web_fetch` | Search the web and fetch URLs |
| `todo_write` | Create and manage task lists |
| `task` | Spawn parallel subagent sessions |
| `memory_search` | Search cross-session memory |

Tools can be extended with [MCP servers](05-configuration.md#mcp-servers) for integrations like GitHub, databases, and more.

### Slash Commands

Type `/` in the prompt to access commands. These provide quick actions without writing a full prompt:

```
/model grok-build    # Switch model
/compact                          # Compress conversation history
/yolo                             # Toggle auto-approve mode
/new                              # Start a new session
```

See [Slash Commands](04-slash-commands.md) for the complete reference.

---

## Common Launch Options

```bash
# Start in a specific project directory
grok --cwd ~/projects/my-app

# Start with an initial task
grok --prompt "Review this codebase and suggest improvements"

# Add project-specific rules
grok --rules "Always use TypeScript. Prefer functional components."

# Auto-approve all tool executions
grok --yolo

# Use a specific model
grok -m grok-build

# Resume a previous session
grok --resume <session-id>

# Continue the most recent session
grok -c

# Headless mode (for scripts)
grok -p "Explain this codebase"
```

---

## Headless Mode

Run Grok non-interactively for scripting, CI/CD, and automation:

```bash
grok -p "Your prompt here"
```

Output formats:

| Format | Flag | Description |
|--------|------|-------------|
| `plain` | (default) | Human-readable text |
| `json` | `--output-format json` | Single JSON object with `text`, `sessionId`, `stopReason` |
| `streaming-json` | `--output-format streaming-json` | NDJSON event stream for real-time processing |

Example CI/CD usage:

```bash
grok -p "Review changes for bugs" --output-format json --yolo | jq -r '.text'
```

---

## Project Rules (AGENTS.md)

Add per-project instructions by creating an `AGENTS.md` file in your repository. Grok reads these files and appends their contents to the system prompt:

```
~/.grok/AGENTS.md           # Global rules (apply to all projects)
<repo-root>/AGENTS.md       # Repository-level rules
<cwd>/AGENTS.md             # Directory-level rules (highest priority)
```

Deeper files take precedence. Grok also reads `CLAUDE.md` files for compatibility.

---

## Where to Go Next

| Document | What You Will Learn |
|----------|-------------------|
| [Authentication](02-authentication.md) | Browser login, API keys, OIDC, external auth, device code flow |
| [Keyboard Shortcuts](03-keyboard-shortcuts.md) | Complete reference for all key bindings |
| [Slash Commands](04-slash-commands.md) | All available `/` commands |
| [Configuration](05-configuration.md) | config.toml, pager.toml, environment variables |

---

Copyright xAI. All rights reserved.

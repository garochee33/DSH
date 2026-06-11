# Configuration

Grok reads configuration from two files, environment variables, and remote settings. This document covers all options.

---

## Precedence

Configuration is resolved in this order (highest priority first):

1. **CLI flags** (e.g., `--yolo`, `--model`, `--sandbox`)
2. **Environment variables** (e.g., `XAI_API_KEY`, `GROK_MEMORY`)
3. **config.toml** (`~/.grok/config.toml`)
4. **Remote settings** (managed deployment via GrowthBook)
5. **Built-in defaults**

---

## config.toml (Main Configuration)

Location: `~/.grok/config.toml`

If the file does not exist, Grok uses sensible defaults. You only need to specify values you want to override.

### General Settings

```toml
[cli]
auto_update = true                     # check for updates on launch

[models]
default = "grok-build"           # model used for new sessions
web_search = "grok-4.20-multi-agent"   # model used by the web_search tool

[ui]
simple_mode = true                      # use simple mode keybindings (default: true)
vim_mode = false                       # vim-style scrollback keybindings (default: false)
max_thoughts_width = 120               # max column width for reasoning display

[features]
support_permission = false             # prompt before tool execution
telemetry = false                      # anonymous usage telemetry
feedback = false                       # feedback system
lsp_tools = false                      # expose the lsp tool
codebase_indexing = true               # code graph indexing

[session]
auto_compact_threshold_percent = 85    # auto-compact at this % of context window
load_envrc = true                      # load .envrc environment variables

[tools]
respect_gitignore = true               # filter gitignored files from tools
```

#### Input Mode

The `simple_mode` setting under `[ui]` controls the keybinding style for scrollback navigation:

| Value | Behavior |
|-------|----------|
| `true` (default) | **Simple mode.** Arrow keys for navigation, `Shift+Arrow` for turn navigation, `Space` to focus the prompt. Any printable key auto-focuses the prompt. |
| `false` | **Vim mode.** `j`/`k` for navigation, `H`/`L` for turn navigation, `h`/`l` for fold, `i`/`Tab`/`Space` to focus the prompt. |

Simple mode is the default. To opt in to Vim-style keybindings:

```toml
[ui]
simple_mode = false
```

> **Note:** The `/simple-mode` slash command has been removed. Input mode is now configured exclusively via `config.toml`.

See [Keyboard Shortcuts](03-keyboard-shortcuts.md) for the full binding reference.

#### Vim Mode

The `vim_mode` setting under `[ui]` controls whether vim-style bindings are
active in the **scrollback** pane.

| Value | Behavior |
|-------|----------|
| `false` (default) | Bare-letter and `Shift+letter` keys (`j/k`, `h/l`, `g/G`, `y/Y`, `o/O`, `r`, `x`, `e/E`, `L/H`, plus `i` insert) are suppressed in the scrollback. Pressing one of those letters focuses the prompt and types the character. Arrows, `Tab`, `Esc`, `Space`, `PageUp/Down`, and all `Ctrl+letter` shortcuts still navigate the scrollback. |
| `true` | All vim-style scrollback bindings active, exactly as listed in [Keyboard Shortcuts](03-keyboard-shortcuts.md). |

Toggle at runtime with `/vim-mode`. The change is written through to
`[ui].vim_mode` in `~/.grok/config.toml` immediately and applies to every
future pager session — including new agents and subagents started in the
same process. There is no separate per-session override; whatever is in
`config.toml` is the source of truth on next launch.

`vim_mode` is **orthogonal to `simple_mode`** — `simple_mode` controls
auto-focus on empty prompts, `vim_mode` controls binding activation.

### Tool Configuration

```toml
[toolset.bash]
timeout_secs = 120.0                   # command timeout in seconds
output_byte_limit = 65536              # max output size (64KB)

[toolset.web_fetch]
proxy_endpoint = "https://proxy.example.com"   # egress proxy URL
allowed_domains = ["docs.rs", "x.ai"]           # override the built-in allowlist
```

### Authentication

See [Authentication](02-authentication.md) for full details.

```toml
[auth]
auth_provider_command = "/usr/local/bin/my-auth-provider"
auth_provider_label = "Acme Corp"
auth_token_ttl = 3600

[grok_com_config.oidc]
issuer = "https://acme.okta.com"
client_id = "0oa1b2c3d4e5f6g7h8i9"
# scopes = ["openid", "profile", "email", "offline_access"]
# audience = "https://api.acme.com"
```

### Custom Models

Add custom model endpoints to use alternative providers or self-hosted models.

```toml
[model.my-model]
model = "model-id"                    # model identifier sent to API
base_url = "https://api.example.com/v1"  # OpenAI-compatible endpoint
name = "Display Name"                 # shown in model picker
description = "Model description"     # optional
api_key = "sk-..."                    # API key for this provider
env_key = "OPENAI_API_KEY"            # env var holding the API key
temperature = 0.7                     # sampling temperature (0.0-2.0)
top_p = 0.95                          # nucleus sampling parameter
max_completion_tokens = 8192          # max tokens per response
max_turns = 50                        # max conversation turns
context_window = 128000               # context window size (for auto-compact)
```

Credential resolution: `api_key` > `env_key` > `XAI_API_KEY`.

Override built-in models by using their name as the section key:

```toml
[model.grok-build]
api_key = "my-api-key"               # only override the fields you need
```

### MCP Servers

Configure external tool integrations via the Model Context Protocol.

```toml
[mcp_servers.github]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]
env = { GITHUB_PERSONAL_ACCESS_TOKEN = "ghp_xxx" }
enabled = true                        # enable/disable (default: true)
startup_timeout_sec = 10              # init timeout (default: 10)
tool_timeout_sec = 60                 # tool call timeout (default: 60)
tool_timeouts = { create_issue = 120 }  # per-tool timeout overrides

[mcp_servers.postgres]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@localhost/db"]

[mcp_servers.nebula]
url = "http://localhost:5000/api/mcp"  # HTTP/SSE transport
headers = { "x-nebula-mcp-session-id" = "{{session_id}}" }
```

MCP servers can also be configured per-project in `.grok/config.toml` (only the `[mcp_servers]` section is supported in project-scoped config).

Priority: `.grok/config.toml` (current dir) > `<repo-root>/.grok/config.toml` > `~/.grok/config.toml`.

### Memory

Cross-session knowledge persistence (requires `--experimental-memory` or `GROK_MEMORY=1`).

```toml
[memory]
enabled = false                       # enable memory

[memory.session]
save_on_end = true                    # write metadata summary on session end

[memory.watcher]
enabled = true                        # watch memory files for external edits

[memory.search]
max_results = 6                       # default number of results
min_score = 0.35                      # minimum relevance score

[memory.initial_injection]
enabled = true                        # auto-inject memory on first turn
min_score = 0.0                       # score threshold for first-turn injection

[memory.embedding]
model = "embedding-beta-3-small"      # embedding model
dimensions = 1024                     # vector dimensions
```

### Subagents

```toml
[subagents]
enabled = true
default_model = "grok-build"         # force all subagents to use this model

[subagents.toggle]
explore = true                        # enable/disable specific types
plan = false

[subagents.models]
explore = "grok-build"               # route to different models
```

### Skills

```toml
[skills]
paths = ["~/my-team-skills"]          # additional directories to scan
ignore = ["~/my-team-skills/wip"]     # paths to exclude
```

### Plugins

```toml
[plugins]
paths = ["~/my-plugins/custom-tools"]
disabled = ["user/a1b2c3d4/noisy-plugin"]
```

### Notifications

Grok can send terminal notifications when the agent finishes a turn or needs
approval. Notifications use terminal-native protocols (OSC 9, OSC 99, OSC 777,
or BEL) and are focus-gated by default so they only fire when you are not
looking at the terminal.

```toml
[ui.notifications]
method = "auto"           # auto|osc9|osc99|osc777|bel|none
condition = "unfocused"   # unfocused|always|never
idle_threshold_secs = 3   # seconds unfocused before a notification fires
events = ["turn_complete", "approval_required"]
sleep_prevention = true   # prevent display sleep during agent turns
progress_bar = true       # show tab progress bar (OSC 9;4)

[ui.notifications.title]
enabled = true
items = ["action-required", "spinner", "activity", "session-name", "grok"]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `method` | string | `"auto"` | Notification protocol. `auto` picks the best for your terminal. |
| `condition` | string | `"unfocused"` | When to notify: `unfocused` (only when terminal lost focus), `always`, or `never`. |
| `idle_threshold_secs` | integer | `3` | Minimum seconds the terminal must be unfocused before a notification fires. |
| `events` | array | `["turn_complete", "approval_required"]` | Events that trigger notifications. Options: `turn_complete`, `approval_required`, `session_ready`, `task_complete`, `agent_error`. |
| `sleep_prevention` | bool | `true` | Keep the display awake while the agent is working (macOS/Linux). |
| `progress_bar` | bool | `true` | Show a progress indicator in the terminal tab (OSC 9;4). |
| `title.enabled` | bool | `true` | Set the terminal title to reflect agent state. |
| `title.items` | array | (see above) | Items shown in the title bar. Options: `action-required`, `spinner`, `activity`, `session-name`, `cwd`, `model`, `turn-timer`, `grok`. |

#### Terminal Support Matrix

| Terminal | Auto Protocol | Focus Tracking | Progress Bar |
|----------|---------------|----------------|--------------|
| iTerm2 | OSC 9 | Yes | Yes |
| Kitty | OSC 99 | Yes | No |
| Ghostty | OSC 777 | Yes | Yes |
| WezTerm | OSC 9 | Yes | Yes |
| Warp | OSC 9 | Yes | No |
| Alacritty | BEL | No | No |
| VS Code | BEL | No | No |
| Apple Terminal | BEL | No | No |
| VTE (GNOME Terminal) | OSC 777 | No | No |
| Grok Desktop | None (native) | N/A | N/A |
| Unknown | BEL | No | No |

When `method = "auto"`, Grok detects the terminal brand and selects the best
protocol automatically. Set `method` explicitly to override auto-detection.

#### Notification Hooks

Run custom commands when events occur. Hooks receive environment variables
`$GROK_EVENT`, `$GROK_MESSAGE`, and `$GROK_SESSION_ID`.

```toml
# macOS native notification
[[ui.notifications.hooks]]
command = "terminal-notifier -title 'Grok' -message '$GROK_MESSAGE'"
events = ["turn_complete", "approval_required"]
only_unfocused = true
timeout_secs = 10

# Push to ntfy server
[[ui.notifications.hooks]]
command = "curl -s -d '$GROK_MESSAGE' ntfy.sh/my-grok-alerts"
events = ["turn_complete"]
only_unfocused = true
timeout_secs = 10

# Play a sound
[[ui.notifications.hooks]]
command = "afplay /System/Library/Sounds/Glass.aiff"
events = ["turn_complete"]
only_unfocused = true
timeout_secs = 5
```

| Hook Option | Type | Default | Description |
|-------------|------|---------|-------------|
| `command` | string | (required) | Shell command to run. |
| `events` | array | `[]` | Events that trigger this hook (empty = all events). |
| `only_unfocused` | bool | `true` | Only fire when the terminal has lost focus. |
| `timeout_secs` | integer | `10` | Kill the hook process after this many seconds (default: 10). |

#### Troubleshooting

**Notifications not working in tmux:**
tmux blocks escape sequences by default. Enable passthrough for your terminal:

```bash
# In ~/.tmux.conf
set -g allow-passthrough on
```

Then restart tmux. If passthrough is not available (tmux < 3.3), set
`method` explicitly to `"bel"` which works without passthrough.

**Focus tracking not working:**
Some terminals do not report focus events. If `condition = "unfocused"` never
fires, try `condition = "always"` as a fallback. Terminals known to support
focus tracking: iTerm2, Kitty, Ghostty, WezTerm, Grok Desktop.

**Sleep prevention not taking effect:**
On macOS, sleep prevention uses `IOPMAssertionCreateWithName` via CoreFoundation.
On Linux, it uses `systemd-inhibit` (must be on `$PATH`). Check that the
relevant tool is available. Sleep prevention is only active during agent turns
and releases automatically when the turn ends.

### Keyboard Shortcuts

Keyboard shortcuts are **not configurable** via config files. All bindings are defined in
the source code (`actions/defaults.rs`). See [Keyboard Shortcuts](03-keyboard-shortcuts.md)
for the complete reference.
### Telemetry

```toml
[telemetry]
events_url = "https://grok.com/_data/v1/events"
events_api_key = "..."
mixpanel_token = "..."
mixpanel_enabled = true
trace_upload = true
```

### Enterprise Deployment

A complete config for enterprise use:

```toml
[cli]
auto_update = false

[auth]
auth_provider_command = "/usr/local/bin/my-company-auth-provider"
auth_provider_label = "Acme Corp"
auth_token_ttl = 3600

[models]
default = "company-grok"

[model.company-grok]
model = "grok-build"
base_url = "https://grok-proxy.acme.com/"
name = "Grok Build Latest (Proxy)"
context_window = 128000

[features]
support_permission = false
telemetry = false
```

---

## pager.toml (Appearance Configuration)

Location: `~/.grok/pager.toml`

Controls the visual appearance and behavior of the TUI. Changes are applied on restart.

### Terminal

```toml
[terminal]
alt_screen = "auto"                   # fullscreen mode: "auto", "always", "never"
```

- `auto` (default): Use alternate screen when the terminal supports it
- `always`: Always use alternate screen
- `never`: Run inline in the terminal's main scrollback buffer

### Animation

```toml
[animation]
fps = 30                              # animation frame rate (ticks per second)
wave_rows = 32                        # rows per wave cycle for accent animation
show_fps = false                      # show FPS counter overlay (dev feature)
```

### Prompt

```toml
[prompt]
collapse_unfocused = true             # collapse prompt when scrollback is focused
mouse_hover = true                    # show hover highlight on the prompt widget
show_prefix = true                    # show the prompt prefix character
compact = false                       # compact mode (reduced padding)
```

### Scrollback

```toml
[scrollback.layout]
outer_vpad = 1                        # vertical padding
outer_hpad_left = 2                   # left horizontal padding
outer_hpad_right = 2                  # right horizontal padding
block_pad_left = 2                    # padding inside block, left of content
block_pad_right = 2                   # padding inside block, right of content

[scrollback.scrollbar]
enabled = true                        # show scrollbar
gap_left = 0                          # gap between content and scrollbar
gap_right = 0                         # gap between scrollbar and screen edge

[scrollback.scroll]
margin = 0                            # minimum context lines above/below selection
min_page_fraction = 0                 # minimum scroll as % of viewport (0-100)
follow_indicator = "center"           # follow indicator: "center" or "none"
follow_auto_select = true             # auto-select latest entry in follow mode
follow_by_overscroll = true           # scrolling past bottom engages follow mode
anchor_on_fold = true                 # keep block position when folding

[scrollback.display]
sticky_headers = true                 # pin user prompts as sticky headers
tab_width = 4                         # spaces per tab character
expandable_indicator = true           # show expand indicator on foldable entries
expandable_indicator_running = true   # show indicator on running entries
expandable_indicator_char = ">"       # character for the expand indicator
selection_buttons = false             # show copy/view buttons on selection
line_under_last_entry = false         # horizontal line below last entry
group_selection_split = true          # split selection box for expanded blocks
highlight_overlays_border = false     # highlight extends over selection box border
dim_accent = 0.5                      # dimming factor for collapsed accents (0.0-1.0)
```

### Block Configuration

```toml
[scrollback.blocks.edit]
indent = true                         # indent diff content
vpad = false                          # vertical padding
expanded_by_default = true            # start expanded (show diff)
dual_line_numbers = false             # two-column line numbers (old + new)
line_summary = false                  # show +N/-M in header
hunk_separator = "..."                # separator between diff hunks

[scrollback.blocks.prompt]
vpad = true                           # vertical padding
invert = false                        # inverted style
show_prefix = true                    # show prompt prefix character
min_lines = 2                         # minimum content lines in sticky mode

[scrollback.blocks.thinking]
animate = true                        # animated accent while thinking
truncated_lines = 3                   # lines in truncated mode
```

### Todo

```toml
[todo]
badge_format = "default"              # "default", "colon", or "comma"
```

Badge format examples:
- `default`: `[1 2 3 4]` -- colored numbers only
- `colon`: `[>:1 [ ]:4 ok:3 x:2]` -- icon:count
- `comma`: `[1 >, 4 [ ], 3 ok, 2 x]` -- count icon, comma-separated

### Plugins

```toml
disable_plugins = false               # hide hooks/plugins UI entirely
```

---

## Environment Variables

Key environment variables. See the README for the complete list.

### Authentication

| Variable | Description |
|----------|-------------|
| `XAI_API_KEY` | API key from console.x.ai |
| `GROK_AUTH_PROVIDER_COMMAND` | External auth binary path |
| `GROK_AUTH_PROVIDER_LABEL` | Display name on TUI login screen |
| `GROK_AUTH_TOKEN_TTL` | Token lifetime in seconds |
| `GROK_AUTH_EARLY_INVALIDATION_SECS` | Seconds before expiry to refresh (default: 300) |
| `GROK_OIDC_ISSUER` | OIDC issuer URL |
| `GROK_OIDC_CLIENT_ID` | OIDC client ID |

### Endpoints

| Variable | Description |
|----------|-------------|
| `GROK_CLI_CHAT_PROXY_BASE_URL` | Override cli-chat-proxy URL |

### Features

| Variable | Description |
|----------|-------------|
| `GROK_MEMORY` | Enable (`1`) or disable (`0`) cross-session memory |
| `GROK_SUBAGENTS` | Enable (`1`) or disable (`0`) subagents |
| `GROK_WEB_FETCH` | Enable (`1`) or disable (`0`) the web_fetch tool |
| `GROK_AGENT` | Custom agent definition path or name |
| `GROK_SANDBOX` | Sandbox profile (off, workspace, read-only, strict) |

### Logging

| Variable | Description |
|----------|-------------|
| `GROK_LOG_FILE` | Enable file logging: `1` for default path, or a custom path |
| `GROK_LOG_FILTER` | Log level filter (default: `info`) |
| `RUST_LOG` | Logging level for stderr (headless mode only) |

### Paths

| Variable | Description |
|----------|-------------|
| `GROK_HOME` | Override config directory (default: `~/.grok`) |
| `GROK_RESPECT_GITIGNORE` | Disable gitignore filtering when set to `0` |

### Telemetry

| Variable | Description |
|----------|-------------|
| `GROK_TELEMETRY_ENABLED` | Enable/disable telemetry |
| `GROK_FEEDBACK_ENABLED` | Enable/disable feedback system |
| `GROK_DEPLOYMENT_KEY` | Management API key for enterprise |

### Display

| Variable | Description |
|----------|-------------|
| `GROK_FPS` | Show FPS counter overlay when set to `1` |

---

## File Locations

| Path | Description |
|------|-------------|
| `~/.grok/config.toml` | Main configuration file |
| `~/.grok/pager.toml` | TUI appearance configuration |
| `~/.grok/auth.json` | Authentication credentials (auto-managed) |
| `~/.grok/sessions/` | Persisted sessions (organized by working directory) |
| `~/.grok/memory/` | Cross-session memory files and index |
| `~/.grok/skills/` | User-scoped [[projects/trinity-unified-ai/skills-library/skills/sexyverse-designer/[[projects/trinity-unified-ai/skills-library/skills/sexyverse-designer/SKILL|SKILL]]|[[projects/trinity-unified-ai/skills-library/skills/sexyverse-designer/SKILL|skill]]]] definitions |
| `~/.grok/plugins/` | User-scoped plugins |
| `~/.grok/agents/` | User-scoped agent definitions |
| `~/.grok/logs/` | Log files (when `GROK_LOG_FILE` is enabled) |
| `.grok/config.toml` | Project-scoped config (MCP servers only) |
| `.grok/skills/` | Project-scoped [[projects/trinity-unified-ai/skills-library/skills/sexyverse-designer/SKILL|[[projects/trinity-unified-ai/skills-library/skills/sexyverse-designer/SKILL|[[projects/trinity-unified-ai/skills-library/skills/sexyverse-designer/SKILL|skill]]]]]] definitions |
| `.grok/plugins/` | Project-scoped plugins |
| `.grok/agents/` | Project-scoped agent definitions |
| `.grok/hooks/` | Project-scoped hooks |
| `.grok/lsp.json` | LSP server configuration |

---

## Project-Scoped Configuration

Some configuration can be set per-project by placing files in `.grok/` within your repository:

| File | What it configures |
|------|--------------------|
| `.grok/config.toml` | MCP servers (only `[mcp_servers]` is supported) |
| `.grok/skills/` | Project-specific skills |
| `.grok/hooks/` | Project-specific lifecycle hooks |
| `.grok/agents/` | Project-specific agent definitions |
| `.grok/lsp.json` | LSP server configuration |
| `.grok/sandbox.toml` | Custom sandbox profiles |
| `AGENTS.md` | Project instructions (system prompt) |

Project-scoped MCP servers override global ones with the same name (full replacement, not merge).

---

Copyright xAI. All rights reserved.

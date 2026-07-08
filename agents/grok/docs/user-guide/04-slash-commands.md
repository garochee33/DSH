# Slash Commands

Type `/` in the prompt to access commands. These provide quick actions without writing a full prompt. Commands autocomplete as you type.

Slash commands come from two sources:

- **Shell builtins** -- handled by the agent backend (xai-grok-shell)
- **Pager builtins** -- handled by the TUI frontend (xai-grok-pager)

Both sets are available in the autocomplete menu. Skills installed via SKILL.md files also appear as slash commands.

---

## Session Management

### `/new`

Start a new session, clearing the current conversation.

```
/new
```

Aliases: `/clear`

### `/load [session-id]`

Load a previous session from disk. If no session ID is provided, opens a session picker.

```
/load
/load abc123
```

Aliases: `/resume`

### `/compact [context]`

Compress conversation history to save context window space. Optionally specify what to preserve.

```
/compact
/compact keep the auth implementation details
```

When the context window fills up, Grok auto-compacts at 85% usage (configurable via `[session] auto_compact_threshold_percent` in config.toml).

### `/context`

Show context window usage and session stats.

```
/context
```

### `/session-info`

Show session details including model, turn count, and context usage.

```
/session-info
```

Aliases: `/status`, `/info`

### `/exit`

Exit the TUI.

```
/exit
```

Aliases: `/quit`

### `/home`

Exit the current session and return to the welcome screen.

```
/home
```

Aliases: `/welcome`

### `/share`

Share the current session and print the share URL.

```
/share
```

### `/rename`

Rename the current session.

```
/rename new session title
```

---

## Model and Mode

### `/model <name>`

Switch to a different model. Accepts model IDs or display names (case-insensitive).

```
/model grok-build
/model Grok Build
```

Aliases: `/m`

### `/always-approve [on|off]`

Toggle always-approve mode, which skips all permission prompts for tool executions.

```
/always-approve on
/always-approve off
/yolo              # alias, toggles on
/yolo off
```

Aliases: `/yolo`

Accepted values for "off": `off`, `false`, `0`, `no`, `disable`.
All other values (or no argument) turn it on.

### `/multiline`

Toggle multiline input mode. When enabled, `Enter` inserts a newline and `Ctrl+Enter` (or `Shift+Enter`) sends the message.

```
/multiline
```

Aliases: `/ml`

### `/compact-mode`

Toggle compact display mode. Reduces padding and visual spacing for denser output.

```
/compact-mode
```

### `/vim-mode`

Toggle vim-style scrollback keybindings (j/k, h/l, g/G, y/Y, …). When off
(default), bare-letter and `Shift+letter` keys in the scrollback focus the
prompt and type the character. Persists to `[ui].vim_mode` in `config.toml`.

```
/vim-mode
```

### `/plan`

Enter or manage plan mode.

```
/plan
```

---

## Memory

These commands require `--experimental-memory` or `GROK_MEMORY=1`.

### `/flush`

Save current session knowledge to memory immediately. Triggers an LLM-generated summary of the session's most important content.

```
/flush
```

Use this when you want to preserve important context before compaction or at any point during a productive session.

### `/dream`

Run memory consolidation -- merge session logs into organized topics.

```
/dream
```

---

## Hooks and Plugins

### `/hooks`

Open the hooks management modal. From the modal you can view loaded hooks, trust/untrust the
current project, and enable or disable individual hooks.

```
/hooks
```

**Note:** The shell advertises individual `/hooks-list`, `/hooks-trust`, `/hooks-add`, `/hooks-remove`,
and `/hooks-untrust` commands. In the TUI pager, these are consolidated into the `/hooks` modal
for a unified experience.

### `/plugins`

Open the plugins management modal. From the modal you can view installed plugins, install new
ones from the marketplace, and manage trust.

```
/plugins
```

The shell also supports subcommands (`/plugins list`, `/plugins install <source>`,
`/plugins uninstall <name>`, `/plugins update`). In the TUI, the `/plugins` modal
provides the same functionality with a visual interface.

Aliases: `/plugin`
---

## Media Generation

### `/imagine <description>`

Generate an image from a text description.

```
/imagine a golden sunset over a calm ocean with silhouetted palm trees
```

### `/imagine-video <description>`

Generate a video from a text description.

```
/imagine-video a cat walking through a garden
```

---

## Scheduling

### `/loop [interval] <prompt>`

Run a prompt on a recurring interval. The interval defaults to `10m` if omitted.

```
/loop 5m check deploy status
/loop check if tests pass
```

Interval format: `Ns` (seconds, min 60), `Nm` (minutes), `Nh` (hours), `Nd` (days).

Recurring tasks auto-expire after 7 days. Cancel with `scheduler_delete` (the job ID is provided when the loop is created).

---

## Other

### `/theme`

Switch the TUI color theme.

```
/theme
```

### `/feedback [message]`

Report an issue or send feedback.

```
/feedback Something isn't working correctly
```

### `/btw`

Send a "by the way" message -- a quick aside to the agent without interrupting the current task.

```
/btw also check the error handling
```

### `/mcps`

Open the MCP servers management modal.

```
/mcps
```

### `/terminal-setup`

Show terminal capability detection and setup info.

```
/terminal-setup
```

### `/release-notes`

View release notes for the current version.

```
/release-notes
```

Aliases: `/changelog`

---

## Skills as Slash Commands

Any skill with `user_invocable: true` in its SKILL.md frontmatter appears as a slash command. For example, if you have a [[projects/trinity-unified-ai/skills-library/skills/sexyverse-designer/SKILL|skill]] at `~/.grok/skills/commit/[[projects/trinity-unified-ai/skills-library/skills/sexyverse-designer/SKILL|SKILL]].md`, you can invoke it with:

```
/commit fix typo in README
```

Skills from plugins also appear as slash commands. When multiple skills share the same name (across scopes), use the qualified form:

```
/local:commit      # Project-scoped [[projects/trinity-unified-ai/skills-library/skills/sexyverse-designer/SKILL|skill]]
/user:commit       # User-scoped [[projects/trinity-unified-ai/skills-library/skills/sexyverse-designer/SKILL|skill]]
```

Built-in slash commands always take priority over skills with the same name. If you name a skill "compact", typing `/compact` will run the built-in compact command, but `/local:compact` will invoke the skill.

---

## Autocomplete

The slash command menu supports fuzzy search. Start typing after `/` to filter available commands. The menu shows:

- Command name
- Description
- Argument hint (if the command accepts arguments)
- Source (builtin, [[projects/trinity-unified-ai/skills-library/skills/sexyverse-designer/SKILL|skill]] scope, plugin name)

Press `Tab` or `Enter` to select a command from the autocomplete menu.

---

Copyright xAI. All rights reserved.

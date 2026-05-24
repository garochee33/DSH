# Hooks

Hooks let you run custom scripts or HTTP requests at key moments during a Grok session. They are perfect for automation, safety checks, logging, notifications, and integrating with your own tools.

---

## What Are Hooks?

A hook is a shell command or HTTP endpoint that Grok calls when a specific lifecycle event occurs. Hooks can:

- **Block actions** -- A `PreToolUse` hook can deny a dangerous command before it runs.
- **React to events** -- A `PostToolUse` hook can log every tool execution to a file.
- **Set up context** -- A `SessionStart` hook can export environment variables or run setup scripts.

---

## Common Use Cases

- **Safety guards**: Block dangerous commands like `rm -rf /` before they execute.
- **Audit logging**: Record every tool use or session to a file or external service.
- **Notifications**: Send a Slack/Discord message when a long-running task finishes.
- **Auto-formatting**: Run `cargo fmt` or `prettier` automatically after edits.
- **Environment setup**: Export secrets or set variables at session start.
- **Custom workflows**: Trigger builds, tests, or deployments on specific events.

---

## Quick Start

1. Create the hooks directory:

   ```sh
   mkdir -p ~/.grok/hooks
   ```

2. Create a hook file, e.g. `~/.grok/hooks/session-start.json`:

   ```json
   {
     "hooks": {
       "SessionStart": [
         {
           "hooks": [
             { "type": "command", "command": "echo 'Grok session started in '$(pwd)" }
           ]
         }
       ]
     }
   }
   ```

3. Start (or restart) a Grok session. The hook runs automatically on `SessionStart`.

4. Press `Ctrl+L` (or run `/hooks`) and check the Hooks tab to confirm it loaded.

---

## Hook Locations

Hooks are discovered from several places (all are merged):

| Scope | Path | Trusted? | Notes |
|-------|------|----------|-------|
| Global | `~/.grok/hooks/*.json` | Always | Personal hooks |
| Global | `~/.claude/settings.json` | Always | Claude Code compatibility |
| Project | `<project>/.grok/hooks/*.json` | Requires trust | Per-repo automation |
| Project | `<project>/.claude/settings.json` | Requires trust | Claude compatibility |
| Plugin | Bundled inside installed plugins | Per-plugin | Shared team hooks |

**Trusting a project**: The first time you open a project with hooks, you must trust it. Open the hooks modal (`Ctrl+L` or `/hooks`) or run `/hooks-trust`. This prevents untrusted repos from running arbitrary code.

---

## Hook Events

| Event | When It Fires | Blocking? |
|-------|---------------|-----------|
| `SessionStart` | At session startup | No |
| `SessionEnd` | When the session ends | No |
| `UserPromptSubmit` | When the user sends a prompt | No |
| `PreToolUse` | Before a tool executes | Yes -- can deny |
| `PostToolUse` | After a tool completes successfully | No |
| `PostToolUseFailure` | After a tool fails | No |
| `PreCompact` | Before conversation compaction | No |
| `Stop` | When the agent stops | No |
| `Notification` | When the agent sends a notification | No |

---

## The Hook JSON Format

Each `.json` file can define hooks for multiple events:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "bin/safety-check.sh", "timeout": 10 }
        ]
      }
    ],
    "PostToolUse": [
      {
        "hooks": [
          { "type": "command", "command": "bin/log-activity.sh" }
        ]
      }
    ]
  }
}
```

### Key Fields

- **Event name** (top-level key): `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, `Notification`, `SessionEnd`, etc.
- **matcher** (optional): Regex that must match the tool name. Only applies to `PreToolUse` / `PostToolUse`. Empty or omitted means match everything.
- **type**: `"command"` (run a script or shell one-liner) or `"http"` (POST the event to a URL).
- **command**: Path to executable (relative to the JSON file) or inline shell command.
- **timeout**: Seconds before killing the hook (default: 5). All hook failures (timeouts, crashes, malformed output, missing required env vars) are fail-open: the failure is recorded for the UI scrollback but the tool call is not blocked. Only an explicit `deny` decision returned by the hook blocks a tool call.

### Tool Name Aliases

Claude-style tool names are automatically mapped to Grok's internal names:

- `Bash` matches `run_terminal_cmd`
- `Edit` matches `search_replace`
- `Read` matches `read_file`

---

## Writing Hook Scripts

### Input

The full event is sent as JSON on **stdin**:

```json
{
  "hookEventName": "pre_tool_use",
  "sessionId": "abc-123",
  "cwd": "/Users/you/project",
  "workspaceRoot": "/Users/you/project",
  "toolName": "run_terminal_cmd",
  "toolInput": { "command": "npm test" },
  "timestamp": "2026-04-14T12:00:00Z"
}
```

### Output (Blocking Hooks)

For `PreToolUse` hooks, write JSON to **stdout**:

- **Allow**: `{"decision": "allow"}`
- **Deny**: `{"decision": "deny", "reason": "Unsafe command detected"}`

### Exit Codes

| Exit Code | Meaning |
|-----------|---------|
| `0` | Success / allow (for blocking hooks) |
| `2` | Explicit deny (blocking hooks only) |
| Other | Fail-open: failure is recorded but the tool call is not blocked. To block a tool call, return JSON `{"decision":"deny","reason":"..."}` on stdout (with exit code `2` or `0`). |

### Passive Hooks

For events like `SessionStart` or `PostToolUse`, stdout is ignored. Just exit 0 on success.

### Environment Variables

Grok sets several environment variables on every hook process. These are useful when writing context-aware or plugin-aware hook scripts.

#### Runner-injected variables (always available)

These variables are set by the hook runner for **every** hook:

| Variable              | Description |
|-----------------------|-------------|
| `GROK_HOOK_EVENT`     | The name of the event that triggered the hook (e.g. `pre_tool_use`, `session_start`, `post_tool_use`, `session_end`, `stop`, `notification`). |
| `GROK_HOOK_NAME`      | The configured name of this specific hook (includes the plugin prefix for plugin-provided hooks). |
| `GROK_SESSION_ID`     | The unique identifier of the current Grok session. |
| `GROK_WORKSPACE_ROOT` | Absolute path to the root of the current workspace. |

These variables are **reserved**. Any values you attempt to set for them via the `env` field in your hook JSON are stripped at load time (a warning is logged), and the runner always injects the real values at spawn time.

#### Plugin hook variables

When a hook originates from a plugin, Grok additionally injects the following variables:

| Variable             | Description |
|----------------------|-------------|
| `GROK_PLUGIN_ROOT`   | Absolute path to the plugin's installed directory. |
| `GROK_PLUGIN_DATA`   | Absolute path to the plugin's writable data directory (for storing plugin state, caches, etc.). |

These values are provided by the plugin system. For the four plugin-related keys (`GROK_PLUGIN_ROOT`, `GROK_PLUGIN_DATA`, and their Claude aliases), the plugin adapter ensures the official plugin values always win over any user-declared values in the hook's `env` map.

#### User-defined environment variables

You can supply additional environment variables for an individual hook handler using the `env` field:

```json
{
  "type": "command",
  "command": "bin/my-hook.sh",
  "env": {
    "MY_SECRET": "value",
    "LOG_LEVEL": "debug"
  }
}
```

These variables are passed through to the hook process, but they cannot override the reserved runner or plugin variables listed above.

#### Using variables in `command` and `url` fields

Both `command` and `url` support `${VAR}` and `$VAR` expansion. See [custom-hooks.md](../custom-hooks.md) for full details on load-time vs runtime expansion, the `env` map lookup order, and how parameter-expansion modifiers (e.g. `${VAR:-default}`) are handled.

---

## HTTP Hooks

Instead of a local script, call a remote endpoint:

```json
{ "type": "http", "url": "https://hooks.example.com/grok-event", "timeout": 15 }
```

The full event envelope is POSTed as JSON. Useful for webhooks, analytics, or serverless functions.

---

## Managing Hooks in the TUI

### The Hooks Modal

Press `Ctrl+L` (or run `/hooks`) to open the Hooks & Plugins modal. In the **Hooks** tab:

| Key | Action |
|-----|--------|
| `l` | Reload all hooks |
| `a` | Add a custom hook by path |
| `r` | Remove selected hook |
| `e` | Enable / disable selected hook |
| `Space` | Expand / collapse group |

Hooks are grouped by source: **Global**, **Project**, **Plugin**, and **Custom**.

Each hook shows:
- **Event** it triggers on
- **Command** or **URL** that runs
- **Timeout** duration
- **Status** -- enabled or `[disabled]`

### Slash Commands

```
/hooks-list           # Show hooks loaded in this session
/hooks-trust          # Trust this project for hook execution
/hooks-add <path>     # Add a custom hook file or directory
/hooks-remove <path>  # Remove a custom hook
/hooks-untrust        # Revoke trust for this project
```

### Per-Hook Enable/Disable

Individual hooks can be enabled or disabled at runtime using the `e` key in the Hooks modal. This takes effect immediately without restarting the session.

### Mid-Session Reload

Press `l` in the Hooks modal to reload all hooks from disk. This picks up any changes you made to hook files during the session.

---

## Hook Annotations in Scrollback

When hooks execute, their results appear as annotations in the TUI scrollback. You can see which hooks ran, whether they allowed or denied an action, and any output they produced. This is visible only when the plugins UI is enabled (default).

---

## Example: Safe Shell Guard

Block dangerous shell commands:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "bin/safe-shell.sh", "timeout": 5 }
        ]
      }
    ]
  }
}
```

Where `bin/safe-shell.sh`:

```bash
#!/bin/sh
INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.toolInput.command // empty')

# Block destructive patterns
if echo "$CMD" | grep -qE '(rm -rf /|mkfs|dd if=|:(){ :|& };:)'; then
  echo '{"decision": "deny", "reason": "Blocked potentially destructive command"}' 
  exit 2
fi

echo '{"decision": "allow"}'
```

---

## Security Notes

- Global hooks (`~/.grok/hooks/`) run with your user permissions -- treat them like shell scripts.
- Project hooks require explicit trust (run `/hooks-trust` or use the modal) to prevent supply-chain attacks from malicious repos.
- HTTP hooks send session data -- only use trusted endpoints.

---

## Best Practices

1. **Keep hooks fast** -- long-running hooks block the UI. Use background processes (`&`) or async where possible.
2. **Use explicit `deny` to block** -- hooks fail-open on any error, so a hook that crashes will not block the tool. To enforce policy, your hook must run to completion and emit `{"decision":"deny","reason":"..."}` on stdout. Always handle errors inside your script so it can return an explicit decision.
3. **Use absolute paths or relative to hook file** -- scripts in `bin/` next to the JSON file are portable.
4. **Test with the modal** -- press `Ctrl+L` to verify hooks are loaded and matching before relying on them.
5. **Version control project hooks** -- commit `.grok/hooks/` (but never secrets).

---

## Troubleshooting

- **Hook not running?** Press `Ctrl+L` (or run `/hooks`) to see if it is loaded and matched.
- **Project hooks ignored?** Trust the project first with `/hooks-trust`.
- **Script not found?** Check the path is relative to the `.json` file and executable (`chmod +x`).
- **See errors?** Check the pager logs (`~/.grok/logs/tracing.log`).

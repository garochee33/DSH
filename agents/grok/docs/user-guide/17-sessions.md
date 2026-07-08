# Session Management

Grok automatically persists conversations to disk. Every interaction -- TUI, headless, or agent stdio -- is saved as a session that can be resumed, rewound, compacted, or shared. This document covers all session management features.

---

## What Sessions Are

A session is a persistent conversation with full history. It includes:

- All user prompts and agent responses
- Tool calls and their results
- TODO/task list state
- File snapshots for rewind
- Token usage and turn counts
- Subagent sessions (when enabled)

Sessions are identified by a unique session ID (a UUID) and stored on disk under `~/.grok/sessions/`.

---

## Storage Layout

Sessions are organized by URL-encoded working directory:

```
~/.grok/sessions/<encoded-cwd>/<session-id>/
  summary.json            # metadata: title, timestamps, model, message count
  updates.jsonl           # ACP session update stream (conversation + tool calls)
  chat_history.jsonl      # raw chat messages sent to the model
  plan.json               # TODO/task list state
  rewind_points.jsonl     # file snapshots for /rewind undo
  signals.json            # session signals (turn count, token usage)
  feedback.jsonl          # user feedback and ratings
  compaction_checkpoints/ # saved state from auto-compact
  subagents/              # child session directories (when subagents are enabled)
```

`summary.json` is the index entry -- it contains the session title, model ID, creation/update timestamps, and parent session reference (for restored sessions). `updates.jsonl` is the authoritative conversation log that drives `/load` and session restore.

---

## Starting and Ending Sessions

### New Session

The TUI creates a new session each time you launch. To explicitly start fresh mid-session:

```
/new
```

This clears the current context and begins a new conversation.

### Exit

End a session and quit:

```
/exit
```

Aliases: `/quit`. You can also use `Ctrl+D` or `Ctrl+Q` (with confirmation).

---

## Resuming Sessions

### From the TUI

Use the `/load` command (alias: `/resume`) to browse and resume previous sessions:

```
/load
```

This opens a session picker showing recent sessions for the current workspace. You can also specify a workspace and session directly:

```
/load [workspace] [session]
```

### From the Command Line

Resume a specific session by ID:

```bash
grok --resume <session-id>
```

### From the Welcome Screen

When you launch `grok`, the welcome screen shows a list of recent sessions for the current directory. Select one to resume it.

---

## The /rewind Command

`/rewind` undoes recent changes by restoring files to their state at an earlier point in the conversation. This is powerful for recovering from mistakes.

```
/rewind
```

When you run `/rewind`, Grok:

1. Shows a list of rewind points (one per user prompt)
2. Lets you select which point to rewind to
3. Restores all files to their state at that point
4. Truncates the conversation history to that point

File snapshots are recorded at each prompt, so you can go back to any previous state.

**Important:** `/rewind` modifies files on disk. The changes it reverts are lost unless you have them in git.

---

## The /compact Command

`/compact` compresses the conversation history to save context window space. This is useful in long sessions where early messages are no longer relevant.

```
/compact
/compact [context]
```

The optional `context` argument lets you provide additional instructions about what to preserve during compaction.

### Auto-Compact

Grok automatically compacts the conversation when the context window approaches its limit. You will see a notification when auto-compact triggers. The `context_window` setting on your model configuration controls when this threshold is reached.

---

## The /session-info Command

View details about the current session:

```
/session-info
```

Aliases: `/status`, `/info`.

This shows:

- Session ID
- Working directory
- Model in use
- Turn count
- Token usage
- Session duration

---

## Headless Session Management

In headless mode, session management works through command-line flags:

```bash
# New session each time (default)
grok -p "Hello"

# Create or resume a named session
grok -p "Remember: X=42" -s my-session
grok -p "What is X?" -s my-session

# Resume existing session (errors if not found)
grok -p "Continue" -r my-session

# Continue most recent session in current directory
grok -p "What were we doing?" -c
```

The session ID is returned in JSON output:

```bash
grok -p "Hello" --output-format json | jq -r '.sessionId'
```

---

## Agent stdio Session Management

When building with ACP, sessions are managed via protocol methods:

```typescript
// Create new session
const { sessionId } = await connection.request("session/new", {
  cwd: "/path/to/project",
  mcpServers: [],
});

// Load existing session
await connection.request("session/load", {
  sessionId: "existing-session-id",
  cwd: "/path/to/project",
  mcpServers: [],
});
```

The agent persists all session updates automatically. Clients can reconnect and load previous sessions by ID.

---

## The grok sessions Subcommand

List sessions from the command line:

```bash
grok sessions
```

This shows recent sessions across all workspaces, including session IDs, titles, timestamps, and working directories.

---

## Sharing Sessions

Share a session to get a shareable URL:

```bash
grok share
```

This uploads the current session and returns a URL that others can view. Shared sessions are read-only snapshots.

In the TUI, you can also share via the ACP extension method `x.ai/share_session`.

---

## Worktree Sessions

When working with subagents or session forks, Grok can create isolated git worktrees per session. Each worktree gets its own copy of the working directory, so file changes in one session do not affect another.

Worktree sessions are managed internally through the `x.ai/git/worktree/*` extension methods. Key operations:

- **Create**: Spin up a new worktree for an isolated session
- **Apply**: Merge worktree changes back into the main working directory
- **Remove**: Clean up a worktree when the session is done

Resume a session in a fresh worktree with `grok -w -r <session-id>`.

---

## Session Storage Details

### Persistence Format

Sessions are stored as newline-delimited JSON (JSONL). Each line in `updates.jsonl` is a self-contained ACP session update event. This format supports:

- Incremental writes (append-only during a session)
- Efficient streaming reads (for session restore)
- Easy debugging (each line is valid JSON)

### Session Metadata

`summary.json` contains:

```json
{
  "title": "Auto-generated session title",
  "model": "grok-build",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:45:00Z",
  "message_count": 24,
  "parent_session_id": null
}
```

### Disk Usage

Sessions can grow large over time. Use `/compact` to reduce history size. Rewind point snapshots (copies of modified files) are the largest contributor to disk usage in sessions that modify many files.

---

## Tips

- Use `/new` to start fresh when your current context is no longer relevant.
- Use `/compact` proactively in long sessions to keep the context window effective.
- Use `/rewind` to undo mistakes -- it is more reliable than asking the agent to "undo" because it restores actual file snapshots.
- Use `-s <name>` in headless mode to build multi-step automations that maintain context.
- Check `/session-info` to see how much of your context window has been used.

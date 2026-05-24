# Cross-Session Memory

Memory lets Grok remember facts, decisions, code patterns, and debugging workflows across separate sessions. Information saved to memory is indexed and searchable, so future sessions can recall relevant context automatically.

---

## What Is Memory?

Without memory, each Grok session starts fresh -- the model has no knowledge of what happened in previous sessions. With memory enabled, Grok can:

- Recall project conventions you explained before.
- Remember debugging steps that worked.
- Carry forward architectural decisions across sessions.
- Avoid re-asking questions it already has answers to.

Memory is **experimental** and disabled by default.

---

## Enabling Memory

### Per-Session Flag

```bash
grok --experimental-memory
```

### Environment Variable

```bash
export GROK_MEMORY=1
grok
```

### Config File (Persistent)

```toml
# ~/.grok/config.toml
[memory]
enabled = true
```

### Force-Disable

To disable memory even when other settings enable it:

```bash
grok --no-memory
```

Or:

```bash
export GROK_MEMORY=0
```

The `--no-memory` flag has absolute highest priority and always disables memory.

### Mid-Session Toggle

Toggle memory on or off during a session without restarting:

```
/memory on
/memory off
```

The toggle is session-scoped -- it does not persist to `config.toml`. Toggling off removes access to memory tools but keeps existing files on disk. Toggling on re-initializes memory storage and registers the memory tools.

You can also toggle from inside the `/memory` modal by pressing `t`.

### Priority Order

1. `--no-memory` CLI flag (always disables)
2. `--experimental-memory` CLI flag (enables)
3. `GROK_MEMORY` env var: `1`/`true` enables, `0`/`false` disables
4. `[memory]` section in config.toml
5. Remote settings (server-side defaults)
6. Default: disabled

---

## How Memory Is Stored

Memory is stored as Markdown files under `~/.grok/memory/`:

| Location | Scope | Description |
|----------|-------|-------------|
| `~/.grok/memory/MEMORY.md` | Global | Facts that apply across all your projects |
| `~/.grok/memory/<project-slug>-<hash8>/MEMORY.md` | Workspace | Project-specific conventions and context |
| `~/.grok/memory/<project-slug>-<hash8>/sessions/` | Sessions | Per-session summaries and logs |

Workspace directories are suffixed with a short hash derived from the git remote URL, so all clones and worktrees of the same repository share the same memory directory.

An **SQLite index** enables fast hybrid search across all memory files:
- **FTS5** full-text search for keyword matching
- **vec0** vector search for semantic similarity (optional, requires embedding)

---

## Automatic Saves

At the end of each session, Grok automatically saves a **structured metadata summary** to the daily session log:

- Message counts (user / assistant / tool)
- Topics -- the first few real user prompts from the session
- Tool-usage breakdown (e.g., `read_file: 4, search_replace: 3`)
- File paths that were read or edited
- Date and session ID

Shell commands are intentionally **not** recorded in automatic saves -- command strings often embed secrets (tokens, API keys, DSNs) and auto-save runs silently.

---

## Saving Rich Knowledge with /flush

For richer capture -- decisions, patterns, debugging workflows, API discoveries -- use `/flush` in the TUI:

```
/flush
```

This triggers an LLM-generated summary of the current session's most important content and writes it to a dated session log. The summary is indexed and searchable in future sessions.

Use `/flush` when you want to preserve important context:
- Before compaction (which discards old conversation turns)
- At the end of a productive debugging session
- After discovering important patterns or conventions

---

## Working with Memory

### Remember

Tell Grok to "remember" something and it saves it to your workspace MEMORY.md:

```
> remember to always open PR links after pushing
Memory saved to ~/.grok/memory/xai-a3f7b2c9/MEMORY.md under "Preferences".
```

Entries are written as durable statements under organized headings (`## Preferences`, `## Project Context`, `## Debugging`, etc.). The file watcher detects the edit and reindexes immediately, so the new entry is searchable in the current session.

For global preferences that apply across all projects, ask Grok to save to the global MEMORY.md instead.

### Forget

Tell Grok to "forget" something and it finds and removes the entry:

```
> forget the snake_case convention
Removed "Use snake_case for all variable names" from Preferences.
```

Forget is best-effort -- the model searches memory and removes matching entries. For guaranteed removal, open the file via `/memory` (press Enter to edit in `$EDITOR`) and remove the entry manually, or edit `~/.grok/memory/` files directly.

### Recall

Ask what Grok remembers:

```
> what do you remember?
```

Grok searches across all memory files and summarizes what it knows, grouped by source (global preferences, project-specific knowledge, session history). Use `/memory` to browse the raw files.

### Direct Editing

You can edit memory files directly at `~/.grok/memory/`. Changes are picked up automatically by the file watcher. Use `/flush` to trigger an immediate save and `/dream` to consolidate session logs into organized topics.

---

## Browsing Memory with /memory

The `/memory` command opens a modal showing all memory files:

```
/memory
```

Files are grouped by scope:
- **GLOBAL** -- Cross-project memory (`MEMORY.md`)
- **WORKSPACE** -- Project-specific memory (`MEMORY.md`)
- **SESSIONS** -- Per-session summaries in reverse chronological order

The modal uses a split-pane layout: file list on the left, content preview on the right. The preview updates as you navigate the file list.

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `↑`/`↓` or `j`/`k` | Navigate file list |
| `Enter` | Open file in `$EDITOR` |
| `x` | Delete session file (double-press to confirm) |
| `t` | Toggle memory on/off |
| `PgUp`/`PgDn` | Jump 10 items in file list |
| `Ctrl+D`/`Ctrl+U` | Scroll preview pane |
| `/` | Search/filter files |
| `Esc` | Close modal |

On narrow terminals (< 80 columns), the preview pane is hidden and the modal falls back to a single-pane file list.

The `/memory` command is also available from the command palette.

---

## Memory Notifications

After a successful memory save (`/flush` or `/dream`), a notification appears in scrollback:

```
Memory saved (flush) -> ~/.grok/memory/xai-a3f7b2c9/sessions/2026-05-05.md  ·  /memory to view
```

This gives you a persistent, scrollable record of when and where memory was written. The notification is non-interactive and matches the style of other session events like compaction messages.

Session-end auto-saves also write to memory, but their notifications may not appear since the TUI exits around the same time. Use `/flush` before ending a session to ensure the save notification is visible.

---

## Dream Consolidation with /dream

The `/dream` command consolidates scattered memory fragments into organized topics:

```
/dream
```

Dream takes all the individual session logs and memory entries and reorganizes them into a coherent, deduplicated knowledge base. This reduces noise and improves search quality over time.

### Auto-Dream

Dream can also run automatically in the background when configured:

```toml
[memory.dream]
enabled = false          # Enable automatic dream consolidation
min_hours = 24           # Minimum hours between consolidations
min_sessions = 5         # Minimum sessions since last consolidation
check_interval_secs = 0  # Periodic check interval (0 = disabled, dream only at session end)
```

---

## How Memory Affects Prompts

### First-Turn Injection

On the first turn of each session, Grok automatically searches memory for content relevant to the current project and injects it as context. This means Grok starts with knowledge from previous sessions without you having to remind it.

First-turn injection can be configured:

```toml
[memory.initial_injection]
enabled = true           # Enable/disable first-turn injection
min_score = 0.0          # Score threshold (0.0 = no filtering, historical default)
```

### After Compaction

Memory is also searched after auto-compaction to recover relevant context that may have been discarded.

---

## Memory Search

Grok searches memory automatically, but you can also trigger searches manually in the chat:

```
Search memory for "auth middleware patterns"
Read my workspace MEMORY.md
```

The model has access to two memory tools:
- `memory_search` -- Hybrid search across all memory (vector + full-text)
- `memory_get` -- Read a specific memory file by path

### Hybrid Scoring

Memory search uses a weighted combination of:
- **Vector similarity** (semantic) -- weight: 0.7
- **BM25 text similarity** (keyword) -- weight: 0.3

Results are filtered by a minimum score threshold (default: 0.35).

### Source Weights

Different memory sources are weighted differently:

| Source | Weight | Description |
|--------|--------|-------------|
| `workspace` | 1.0 | Project-specific memory |
| `session` | 1.0 | Session logs |
| `global` | 0.7 | Cross-project memory (slightly lower to prefer project-specific results) |

### Temporal Decay

Session memories decay over time so recent sessions are prioritized:

```toml
[memory.search.temporal_decay]
enabled = true           # Enable time-based decay
half_life_days = 7.0     # Score halves after this many days
```

Only session chunks decay. Global and workspace memories are exempt since they contain curated long-term knowledge.

### MMR (Maximal Marginal Relevance)

MMR re-ranking penalizes redundant results to improve diversity:

```toml
[memory.search.mmr]
enabled = false          # Opt-in diversity re-ranking
lambda = 0.7             # 0.0 = max diversity, 1.0 = pure relevance
```

---

## CLI Commands

```bash
# Open workspace MEMORY.md in $EDITOR / $VISUAL
grok memory edit

# Open global MEMORY.md
grok memory edit --global

# Show memory statistics: file count, chunk count, and index size
grok memory stats

# Clear workspace memory (MEMORY.md, sessions, index)
grok memory clear

# Clear global memory
grok memory clear --global

# Clear both workspace and global memory
grok memory clear --all

# Skip confirmation prompt
grok memory clear --yes
```

---

## Configuration Reference

### Core Settings (`[memory]`)

| Key | Default | Description |
|-----|---------|-------------|
| `enabled` | `false` | Enable memory |
| `session.save_on_end` | `true` | Write metadata summary on session end |
| `watcher.enabled` | `true` | Watch `~/.grok/memory/` for external edits and reindex |

### Index Settings (`[memory.index]`)

| Key | Default | Description |
|-----|---------|-------------|
| `max_chunk_chars` | `1600` | Maximum chunk size in characters |
| `chunk_overlap_chars` | `320` | Character overlap between chunks |

### Embedding Settings (`[memory.embedding]`)

| Key | Default | Description |
|-----|---------|-------------|
| `provider` | `"api"` | Provider type: `"api"`, `"local"`, or `"auto"` |
| `model` | `"embedding-beta-3-small"` | Embedding model name |
| `dimensions` | `1024` | Embedding vector dimensions |

### Search Settings (`[memory.search]`)

| Key | Default | Description |
|-----|---------|-------------|
| `max_results` | `6` | Maximum search results |
| `min_score` | `0.35` | Minimum relevance score |
| `vector_weight` | `0.7` | Weight for vector similarity |
| `text_weight` | `0.3` | Weight for BM25 text similarity |

### Initial Injection Settings (`[memory.initial_injection]`)

| Key | Default | Description |
|-----|---------|-------------|
| `enabled` | `true` | Enable first-turn memory injection |
| `min_score` | `0.0` | Score threshold for first-turn results |

### Dream Settings (`[memory.dream]`)

| Key | Default | Description |
|-----|---------|-------------|
| `enabled` | `false` | Enable automatic dream consolidation |
| `min_hours` | `24` | Minimum hours between consolidations |
| `min_sessions` | `5` | Minimum sessions to trigger |
| `stale_lock_secs` | `3600` | Seconds before a stale lock is reclaimed |
| `check_interval_secs` | (none) | Periodic check interval (disabled by default) |

### Flush Settings (`[compaction.memory_flush]`)

Note: Flush is configured under `[compaction]`, not `[memory]`.

| Key | Default | Description |
|-----|---------|-------------|
| `enabled` | varies | Enable pre-compaction memory flush |
| `soft_threshold_tokens` | varies | Token threshold for flush trigger |
| `idle_timeout_secs` | (none) | Idle timeout before flush |

### Pruning Settings (`[compaction.pruning]`)

Note: Pruning is configured under `[compaction]`, not `[memory]`.

| Key | Default | Description |
|-----|---------|-------------|
| `enabled` | varies | Enable tool-result pruning |
| `keep_last_n_turns` | varies | Number of recent turns to keep unpruned |
| `soft_trim_threshold` | varies | Threshold for soft trimming |

---

## Memory Staleness

When memory content is old or potentially outdated, Grok may show staleness warnings. This helps you identify when stored facts might no longer be accurate and should be verified or updated.

---

## File Watcher

By default, Grok watches `~/.grok/memory/` for external file changes. If you edit memory files directly (e.g., in your editor), the changes are picked up automatically on the next memory search:

- Created or modified files are reindexed.
- Deleted files have their stale chunks removed from the index.

```toml
[memory.watcher]
enabled = true    # default
```

---

## Troubleshooting

### Memory Not Working

1. Verify memory is enabled: check `grok inspect` output.
2. Check the flag: `grok --experimental-memory` or `GROK_MEMORY=1`.
3. Check for `--no-memory` or `GROK_MEMORY=0` overriding your config.

### Memory Not Appearing in Sessions

Memory is injected on the first turn. If you started a session before enabling memory, start a new session with `/new`.

### Viewing Memory Files

Use `/memory` in the TUI to browse all memory files with a preview. You can also access them directly:

```bash
ls ~/.grok/memory/
cat ~/.grok/memory/MEMORY.md
grok memory edit
```

### Debug Logging

```bash
GROK_LOG_FILE=1 GROK_LOG_FILTER=debug grok
grep "memory" ~/.grok/logs/tracing.log
```

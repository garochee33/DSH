# Subagents and Personas

Subagents spawn independent child sessions that handle tasks in parallel. Each child has its own context window and can optionally inherit the parent's conversation history. This enables the main agent to delegate work -- research, implementation, testing, code review -- to specialized workers without consuming its own context.

Subagents are enabled by default.

---

## Disabling Subagents

Disable via environment variable or config file:

```bash
export GROK_SUBAGENTS=0              # Environment variable
```

```toml
# ~/.grok/config.toml
[subagents]
enabled = false
```

---

## How Subagents Work

When the parent agent encounters a task suitable for delegation, it uses the `task` tool to spawn a child agent. The child runs in its own session with:

- Its own context window (independent of the parent)
- A defined capability mode controlling what tools it can use
- An optional persona that shapes its behavior and tone

The parent receives the child's output (typically a summary) when the child completes.

---

## Built-in Agent Types

The `task` tool accepts a `subagent_type` parameter that selects the child's role:

| Type              | Description                                          |
| ----------------- | ---------------------------------------------------- |
| `general-purpose` | Default type. Full-capability agent for any task.    |
| `explore`         | Read-only research agent. Can search, read, and grep but cannot modify files or run commands. Ideal for codebase investigation. |
| `plan`            | Planning agent. Explores the codebase and produces a structured implementation plan. |

---

## Built-in Personas

Personas layer specific behavioral instructions onto the child agent. They define the tone, output format, and task focus. Set via the `persona` parameter on the `task` tool.

| Persona                 | Description                                              |
| ----------------------- | -------------------------------------------------------- |
| `implementer`           | Pragmatic coder. Implements changes, runs fmt/clippy.    |
| `reviewer`              | Code reviewer. Reads diffs, writes structured feedback.  |
| `researcher`            | Deep investigator. Searches broadly, writes findings.    |
| `test-writer`           | Test specialist. Writes tests for existing code.         |
| `security-auditor`      | Security analyst. Audits code for vulnerabilities.       |
| `design-doc-writer`     | Technical writer. Produces design documents.             |
| `design-doc-reviewer`   | Design reviewer. Reviews docs for gaps and improvements. |

### Persona IO Contracts

Each persona defines expected inputs and outputs. For example:

- **implementer**: Reads a `review_file` with issues to fix, writes a `summary_file` with what was changed.
- **reviewer**: Reads code changes, writes structured review notes to `review_file`.
- **researcher**: Explores based on a prompt, writes findings to `summary_file`.

These contracts allow chaining: a researcher's `summary_file` becomes the input context for an implementer.

---

## Spawning Subagents

The parent agent uses the `task` tool. Key parameters:

| Parameter         | Description                                                      |
| ----------------- | ---------------------------------------------------------------- |
| `description`     | What the child should do (used as the prompt)                    |
| `subagent_type`   | Agent type: `general-purpose`, `explore`, `plan`                 |
| `persona`         | Optional persona to apply (e.g., `implementer`, `reviewer`)     |
| `prompt`          | The full prompt text for the child agent                         |

---

## Capability Modes

Each subagent runs with a capability mode that restricts its available tools:

| Mode         | Read | Write | Execute | Description                                  |
| ------------ | ---- | ----- | ------- | -------------------------------------------- |
| `read-only`  | Yes  | No    | No      | Search, grep, read files only                |
| `read-write` | Yes  | Yes   | No      | Can also create and edit files                |
| `execute`    | Yes  | Yes   | Yes     | Can also run terminal commands               |
| `all`        | Yes  | Yes   | Yes     | Full capability (default for general-purpose) |

The `explore` agent type defaults to `read-only`. The `general-purpose` type defaults to `all`.

---

## Context Inheritance

### resume_from

The `resume_from` parameter lets a new subagent continue from where a previous subagent left off. This is useful for multi-stage workflows:

1. Spawn a researcher to investigate a problem
2. Spawn an implementer with `resume_from` set to the researcher's session, so it picks up with full research context

---

## Isolation: Worktree Mode

For tasks that modify files, subagents can run in an isolated git worktree. This prevents the child from conflicting with the parent's file changes:

- Each child gets its own copy of the working tree
- Changes are isolated until explicitly merged back
- The parent can review and apply changes via `x.ai/git/worktree/apply`

---

## Configuration

### Global Default Model

Force all subagents to use a specific model:

```toml
[subagents]
enabled = true
default_model = "grok-build"   # all subagents use this model
```

This takes absolute precedence over per-type models, agent definitions, and parent inheritance.

### Per-Type Toggle and Model Overrides

Disable specific subagent types or route them to different models:

```toml
[subagents.toggle]
explore = true                       # default -- omitted agents are enabled
plan = false                         # disable plan subagent

[subagents.models]
explore = "grok-build"              # route explore to a lighter model
```

Model overrides only apply when the parent is on a heavy model. Otherwise subagents inherit the parent model. The global `default_model` bypasses this gate.

### Custom Roles and Personas

Define custom roles with specific capability and model defaults:

```toml
[subagents.roles.researcher]
description = "Deep research agent"
default_capability_mode = "read-only"
model = "grok-build"
prompt_file = ".grok/prompts/researcher.md"
```

Define custom personas with behavioral instructions:

```toml
[subagents.personas.concise]
instructions = "Be extremely concise. No filler words."
# instructions_file = ".grok/personas/concise.md"  # or load from file
```

Both are also discovered from `.grok/roles/*.toml` and `.grok/personas/*.toml` files. If a requested persona is not found, the spawn fails (fail-closed).

---

## The Tasks Pane (TUI)

In the interactive TUI, press `Ctrl+T` to toggle the TODO/task panel, which shows:

- Active and completed subagent tasks
- Task lineage (parent-child relationships)
- Task status (running, completed, failed)

Press `Ctrl+Shift+A` to toggle the subagent catalog, which lists available agent types and personas.

---

## Depth Limits

Subagents can spawn their own subagents, creating a tree of workers. To prevent runaway spawning, there is a configurable depth limit. By default, subagents cannot nest beyond a few levels deep.

---

## When to Use Subagents

**Good use cases:**

- Researching a codebase while the parent continues other work
- Running tests in parallel while the parent implements changes
- Code review of generated changes before committing
- Delegating independent tasks that do not depend on each other

**When not to use:**

- Simple tasks that the parent can handle directly
- Tasks that require tight back-and-forth with the user (subagents cannot interact with the user)
- Tasks where the context setup cost exceeds the parallelism benefit

# Skills

Skills are reusable prompt packages that extend Grok with specialized workflows, domain knowledge, and tool integrations. They let you encode repeatable procedures that would otherwise require re-explaining each session.

---

## What Are Skills?

A skill is a directory containing a `SKILL.md` file. The markdown content tells Grok exactly how to handle a specific type of task -- step-by-step instructions, conventions, tool usage patterns, and anything else relevant to that workflow.

Skills bridge the gap between one-off instructions (which you'd type every time) and project rules in AGENTS.md (which apply to everything). A skill is activated only when relevant.

---

## Skill Locations

Grok discovers skills from these directories, in priority order:

| Location | Scope | Priority | Notes |
|----------|-------|----------|-------|
| `./.grok/skills/` | Local (CWD) | Highest | Current directory skills |
| `<repo_root>/.grok/skills/` | Repo | Medium | Shared across the repo |
| `~/.grok/skills/` | User | Lowest | Personal skills for all projects |
| `~/.claude/skills/` | User | Lowest | Claude Code compatibility |

Skills with the same name are deduplicated -- higher priority locations override lower ones.

Repo-scoped skills (Local and Repo) respect `.gitignore` and are filtered out if ignored. User-scoped skills (`~/.grok/skills/`) are never filtered.

### Additional Skill Directories

Add extra directories or exclude paths via `[skills]` in `~/.grok/config.toml`:

```toml
[skills]
paths = ["~/my-team-skills"]          # Additional directories to scan
ignore = ["~/my-team-skills/wip"]     # Paths to exclude
```

---

## Creating a Skill

### Directory Structure

Each skill lives in its own directory with a `SKILL.md` file:

```
~/.grok/skills/
  commit/
    SKILL.md
  review-pr/
    SKILL.md
  deploy/
    SKILL.md
```

### SKILL.md Format

A skill file has YAML frontmatter followed by markdown instructions:

```markdown
---
name: commit
description: Create well-formatted git commits following conventional commit standards. Use when the user wants to commit changes or asks for /commit.
---

# Git Commit Skill

Review staged changes and create a commit with a clear, conventional message.

## Steps

1. Run `git diff --staged` to see changes
2. Summarize what changed and why
3. Create commit message following conventional commits format
4. Run `git commit -m "..."` with the message
```

### Required Frontmatter Fields

| Field | Description |
|-------|-------------|
| `name` | Skill identifier. Lowercase, hyphens allowed, max 64 characters. |
| `description` | What the skill does and when to use it. This is how Grok decides whether to invoke it. |

The `description` field is critical -- it determines when Grok automatically invokes the skill. Be specific about trigger phrases and use cases.

---

## Creating Skills with /skillify

The `/skillify` command captures workflows as reusable skills -- either by analyzing what you just did in the current session or by guiding you through describing a workflow from scratch.

### Two Modes

`/skillify` automatically detects which mode to use based on your session context:

- **From-session mode**: If you've been working through a multi-step workflow (running commands, editing files, reviewing output), `/skillify` analyzes your session's tool calls, file operations, and commands to extract the repeatable process. It then walks you through a short interview to confirm and refine what it captured.

- **From-scratch mode**: If the session is fresh, has been compacted, or lacks a coherent workflow to capture, `/skillify` skips the analysis and guides you through describing the workflow step by step.

You don't need to choose a mode -- `/skillify` picks the right one and tells you which it selected.

You can also pass a description directly: `/skillify deploy workflow for k8s`. This pre-populates the interview and typically enters from-scratch mode.

### The /create-skill Alias

`/create-skill` is a backward-compatible alias for `/skillify`. Running `/create-skill` invokes `/skillify`, which typically enters from-scratch mode (since `/create-skill` is usually run in a fresh session). If you're used to `/create-skill`, everything still works -- you get the same interview flow with richer frontmatter generation (`when-to-use`, `allowed-tools`, `argument-hint`, and success criteria on every step).

### What Gets Generated

The generated SKILL.md includes:

- **Complete frontmatter**: `name`, `description`, `when-to-use` (trigger phrases for auto-invocation), `allowed-tools`, `argument-hint`, and `arguments`
- **Numbered steps** with success criteria, artifact descriptions, and human checkpoints where appropriate
- **Parameterized inputs**: Variable values (PR numbers, branch names, etc.) are extracted as skill arguments rather than hardcoded

Before writing to disk, `/skillify` shows you the complete SKILL.md for review. You can request changes before confirming.

### Best Practices for /skillify

1. **Run it right after finishing the workflow.** The sooner you invoke `/skillify`, the more session history is available for analysis. Long sessions risk compaction, which degrades from-session mode (see below).

2. **Choose the right scope.** During the interview, `/skillify` asks where to save:
   - **Project** (`<repo_root>/.grok/skills/`) -- for repo-specific workflows, shared with teammates via version control
   - **Personal** (`~/.grok/skills/`) -- follows you across all projects

### Compaction Limitation

`/skillify`'s from-session mode works by reading conversation history in the current context window. If the session has been **compacted** (older turns dropped to free context space), `/skillify` can only see the summary -- not the original tool calls, commands, and file operations from earlier in the session.

When this happens, `/skillify` detects the compaction and automatically falls back to from-scratch mode, informing you that earlier context is unavailable. You still get the full interview flow, but without the pre-populated analysis from session history.

For best results, invoke `/skillify` before your session grows very long -- ideally right after completing the workflow you want to capture.

---

## Using Skills

### Slash Command

List all available skills or inject a specific skill into context:

```
/skills              # List available skills
/skills commit       # Inject the "commit" skill into context
```

### Slash Command Shorthand

Users can reference skills directly as `/skill-name`:

```
/commit              # Invokes the "commit" skill
/review-pr           # Invokes the "review-pr" skill
```

### Automatic Discovery

Grok can invoke skills automatically when it recognizes a relevant task based on the user's prompt. The skill's `description` field determines when this happens.

For example, if your skill description says "Use when the user wants to commit changes", then saying "commit my changes" in the prompt may trigger that skill automatically.

---

## Viewing Skill Details

Use `grok inspect` to see all discovered skills and their sources:

```bash
grok inspect          # Shows skills with their paths and descriptions
grok inspect --json   # Machine-readable format
```

Each skill entry shows:
- **Name** -- the skill identifier
- **Path** -- where the SKILL.md file lives
- **Description** -- the trigger description
- **Scope** -- local, repo, user, or plugin

---

## Bundled and Plugin Skills

Skills can also come from plugins. When you install a plugin that includes skills, they appear alongside your user and project skills. Plugin-provided skills are tagged with `[plugin: name]` in `grok inspect` output.

See the [Plugins guide](09-plugins.md) for more on installing plugins that provide skills.

---

## Best Practices

1. **Be specific in descriptions.** The description drives automatic invocation. "Create git commits" is too vague. "Create well-formatted git commits following conventional commit standards. Use when the user wants to commit changes or asks for /commit." is much better.

2. **Include concrete steps.** Skills work best when they give Grok a clear, ordered procedure to follow.

3. **Reference tools by name.** If a skill requires specific tools (e.g., `run_terminal_cmd`, `hashline_edit`), mention them explicitly so the model knows what to use.

4. **Keep skills focused.** One skill per workflow. A "deploy" skill and a "rollback" skill are better than a "deploy-and-rollback" skill.

5. **Version control project skills.** Commit `.grok/skills/` to your repository so the whole team benefits. User skills in `~/.grok/skills/` are personal and not shared.

6. **Test with `/skills`.** Use `/skills name` to inject the skill and verify it works before relying on automatic invocation.

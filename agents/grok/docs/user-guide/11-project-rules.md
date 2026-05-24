# Project Rules (AGENTS.md)

Project rules let you shape Grok's behavior on a per-project or per-directory basis. By placing an agent rules file in your repository, you can set coding conventions, build instructions, style guides, and any other instructions that Grok should follow when working in that codebase.

---

## What Are Project Rules?

Project rules are Markdown files that Grok reads and appends to its system prompt. Their content becomes part of the instructions Grok follows for every interaction in that directory tree.

This is the primary mechanism for teaching Grok about your project's conventions without repeating yourself every session.

---

## Supported File Names

Grok checks for these filenames (in this order) within each directory:

- `Agents.md`
- `Claude.md`
- `AGENT.md`
- `AGENTS.md`

The first file found in each directory is used. `Claude.md` is supported for compatibility with Claude Code workflows.

---

## How Discovery Works

Grok scans for agent rules in this order:

1. **Global rules**: `~/.grok/` (applies to all projects)
2. **Repo rules**: If inside a git repo, every directory from the repo root down to the current working directory (inclusive)
3. **CWD-only**: If not inside a git repo, only the current working directory

### Example

Given this project structure:

```
~/projects/my-app/
  AGENTS.md              # "Use TypeScript. Follow ESLint rules."
  src/
    AGENTS.md            # "Prefer functional components."
    components/
      AGENTS.md          # "Use CSS modules for styling."
```

When Grok runs in `~/projects/my-app/src/components/`, it loads all three files. The instructions accumulate -- Grok sees all of them.

### Deeper Files Take Precedence

Files found in deeper directories come last in the system prompt, so they effectively take precedence when instructions conflict. In the example above, if the root says "Use styled-components" but `components/AGENTS.md` says "Use CSS modules", the CSS modules instruction wins because it appears later.

### Auto-Loading Behavior

- Files from the root to CWD are loaded automatically at session start.
- When Grok edits files in subdirectories beyond CWD, it checks for additional AGENTS.md files in those directories and loads them on demand.

---

## What to Put in Project Rules

### Coding Conventions

```markdown
# Coding Standards

- Use TypeScript for all new code
- Prefer functional components with hooks over class components
- Use `const` by default; only use `let` when reassignment is needed
- Maximum line length: 100 characters
```

### Build and Test Instructions

```markdown
# Build & Test

- Run `npm test` before committing
- Use `npm run lint` to check code style
- Build with `npm run build` -- ensure no TypeScript errors
- Integration tests: `npm run test:e2e` (requires Docker)
```

### Style Guides

```markdown
# Style Guide

- Follow the Airbnb JavaScript Style Guide
- Use 2-space indentation
- Always use trailing commas in multi-line arrays/objects
- Prefer template literals over string concatenation
```

### PR and Commit Requirements

```markdown
# Version Control

- Write commit messages in conventional commits format
- Prefix branch names with `feature/`, `fix/`, or `chore/`
- All PRs require at least one approval before merge
- Squash-merge feature branches
```

### Architecture Notes

```markdown
# Architecture

- API routes go in `src/routes/` with one file per resource
- Business logic goes in `src/services/`
- Database queries go in `src/repositories/`
- Never import from `src/routes/` in `src/services/`
```

---

## Scoping Rules to Subdirectories

AGENTS.md files scope to the entire directory tree rooted at their folder. Use this to provide different instructions for different parts of your codebase:

```
my-monorepo/
  AGENTS.md                    # Monorepo-wide rules
  packages/
    frontend/
      AGENTS.md                # "Use React. Prefer CSS modules."
    backend/
      AGENTS.md                # "Use Express. Follow REST conventions."
    shared/
      AGENTS.md                # "No framework-specific code in this package."
```

---

## The --rules Flag

Append additional rules for a single session without modifying files:

```bash
grok --rules "Always use TypeScript. Prefer functional components."
```

The `--rules` flag appends additional instructions on top of any discovered agent files. Use it for session-specific customization.

---

## Size Limits

Each AGENTS.md file is capped at 10,000 characters. If a file exceeds this limit, it is truncated with a warning. Keep instructions concise and focused.

---

## Gitignore Filtering

Files ignored by `.gitignore` are skipped during discovery. This means you can have a local AGENTS.md that is gitignored for personal overrides that are not shared with the team:

```gitignore
# .gitignore
AGENTS.local.md
```

Note: Only the standard filenames (`Agents.md`, `Claude.md`, `AGENT.md`, `AGENTS.md`) are discovered. Custom filenames are not scanned.

---

## The .grok/ Project Directory

Beyond AGENTS.md files, the `.grok/` directory in your project root can contain additional project-level configuration:

| Path | Purpose |
|------|---------|
| `.grok/config.toml` | Project-scoped MCP server configuration |
| `.grok/skills/` | Project-scoped skill definitions |
| `.grok/plugins/` | Project-scoped plugins |
| `.grok/agents/` | Project-scoped agent definitions |
| `.grok/hooks/` | Project-scoped lifecycle hooks |
| `.grok/lsp.json` | LSP server configuration |

These are all optional. See the respective guides for details on each.

---

## Inspecting Loaded Rules

Use `grok inspect` to see all loaded project instructions:

```bash
grok inspect
```

This shows each AGENTS.md file found, its path, and its token count. Useful for verifying that your rules are being picked up.

---

## Best Practices

1. **Start with the root.** Put the most important, project-wide rules in the repo root AGENTS.md.

2. **Be specific.** "Use TypeScript" is better than "Use modern JavaScript". "Run `cargo fmt` before committing" is better than "Format your code".

3. **Keep it short.** Each file is capped at 10,000 characters. Concise instructions are more likely to be followed than lengthy ones.

4. **Use subdirectory scoping for large repos.** Different parts of a monorepo may have different conventions. Use per-directory AGENTS.md to scope rules appropriately.

5. **Version control your rules.** Commit AGENTS.md to the repository so the whole team benefits. User-specific overrides belong in `~/.grok/` (global rules).

6. **Do not duplicate documentation.** AGENTS.md should contain actionable instructions, not a copy of your project's README. Link to external docs if needed.

7. **Review periodically.** As your project evolves, update your rules to match current conventions.

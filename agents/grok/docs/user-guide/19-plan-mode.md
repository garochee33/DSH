# Plan Mode

Plan mode is a structured planning phase where the agent explores the codebase and designs an implementation approach before writing any code. It is designed for tasks with genuine ambiguity about the right approach, where getting user input before coding would prevent significant rework.

---

## What Plan Mode Does

When plan mode is active:

1. The agent can **read and search** the codebase freely
2. The agent can **write only to the plan file** (`plan.md` in the session directory) -- all other file writes are blocked
3. The agent designs an implementation approach in the plan file
4. When the plan is ready, the agent presents it for user approval
5. The user can approve the plan and begin implementation, or revise it with feedback

This separation between planning and implementation reduces wasted effort on complex, ambiguous tasks.

---

## How to Enter Plan Mode

### Automatic Entry

Grok enters plan mode automatically when it determines a task has genuine ambiguity. The agent uses the `enter_plan_mode` tool, which requires user approval before activating.

**Good triggers for plan mode:**

- "Add user authentication to the app" -- genuinely ambiguous (session vs JWT, token storage, middleware structure)
- "Redesign the data pipeline" -- major restructuring where the wrong approach wastes significant effort
- "Add caching to the API" -- multiple reasonable approaches (Redis vs in-memory vs file-based)
- "Add real-time updates" -- architectural decision (WebSockets vs SSE vs polling)

**Not appropriate for plan mode:**

- "Add a delete button to the user profile" -- clear implementation path
- "Fix the typo in the README" -- straightforward
- "Update the error handling in the API" -- start working, ask specific questions if needed
- "Can we work on the search feature?" -- user wants to get started, not plan

### Manual Entry

The agent decides when to enter plan mode based on the complexity and ambiguity of the task. There is no slash command to force plan mode -- the model must call `enter_plan_mode`, and the user must approve.

---

## The Plan File

The plan is written to `plan.md` inside the session directory (`~/.grok/sessions/<cwd>/<session-id>/plan.md`). During plan mode, this is the only file the agent can modify.

The plan file typically contains:

- Analysis of the current codebase state
- The proposed implementation approach
- Steps to be taken
- Trade-offs and alternatives considered
- Questions or assumptions

---

## Plan Approval

When the agent finishes planning, it calls the `exit_plan_mode` tool, which triggers a plan approval dialog in the TUI.

### The Approval Dialog

The TUI displays an overlay with the plan content visible in the scrollback and two options:

**When a plan has been written:**

| Shortcut | Option                  | Action                                   |
| -------- | ----------------------- | ---------------------------------------- |
| `a`      | Yes, start building     | Approve the plan and begin implementation |
| `x`      | No, revise the plan     | Enter plan review mode with feedback      |

**When no plan content is present:**

| Shortcut | Option | Action                  |
| -------- | ------ | ----------------------- |
| `y`      | Yes    | Approve and proceed     |
| `n`      | No     | Reject and provide feedback |

Navigate between options with arrow keys or `j`/`k`. Press `Enter` to confirm.

### Plan Review Mode

If you select "No, revise the plan," the TUI enters plan review mode:

- **Preview focus**: Scroll through the plan content with line-by-line navigation
- **Commenting**: Select line ranges and add inline review comments
- **Prompt focus**: Type feedback in the prompt area

You can switch focus between the preview and prompt with `Tab`. When you submit feedback, the agent receives your comments and revises the plan.

### Dismissing

Press `Esc` to dismiss the plan approval dialog. A second `Esc` confirms the dismissal. This cancels the plan mode exit without approving or providing feedback.

---

## Plan Mode Lifecycle

The plan mode state machine has four states:

| State          | Description                                                    |
| -------------- | -------------------------------------------------------------- |
| `Inactive`     | Normal operating mode. No plan mode constraints.               |
| `Pending`      | Client toggled plan mode ON, but no prompt has been sent yet.  |
| `Active`       | Plan mode is active. Write tools are blocked except for the plan file. |
| `ExitPending`  | User toggled plan mode OFF while a turn is in-flight.          |

Transitions:

```
Inactive --> Pending (enter_plan_mode tool called, user approves)
Pending  --> Active  (first user prompt triggers plan mode injection)
Active   --> Inactive (exit_plan_mode approved, or user toggles off)
Active   --> ExitPending (user toggles off while turn is in-flight)
ExitPending --> Inactive (after turn completes)
```

Plan mode state is persisted to disk and survives process restarts. Transient states (`Pending`, `ExitPending`) are collapsed to `Inactive` on restart since they depend on in-flight interactions.

---

## What Happens During Plan Mode

While plan mode is active, the agent:

1. Explores the codebase using search, read, and list tools
2. Understands existing patterns and architecture
3. Designs an implementation approach
4. Writes the plan to the plan file
5. May use `ask_user_question` to clarify specific questions
6. Calls `exit_plan_mode` when ready for user review

Write tools (file edits, code generation) are blocked during plan mode except for the plan file itself. This prevents the agent from making changes before the user has approved the approach.

---

## Auto-Approval of Plan File Edits

During active plan mode, edits to the plan file are auto-approved without prompting. This allows the agent to iterate on the plan freely while still being blocked from modifying any other files.

---

## Plan Mode and Compaction

When `/compact` runs during an active plan mode session, the plan mode state is preserved. The compacted context includes a reminder that plan mode is active, so the agent continues planning after compaction.

---

## When Plan Mode is Appropriate

**Use plan mode for:**

- Tasks with significant architectural ambiguity (multiple reasonable approaches)
- Unclear requirements that need exploration before implementation
- High-impact restructuring where the wrong approach wastes significant effort

**Skip plan mode for:**

- Tasks with a clear implementation path
- Bug fixes where the fix is obvious once you understand the bug
- Adding features that follow existing conventions
- Straightforward modifications (renaming, formatting, adding tests)
- Research and exploration tasks (use subagents instead)

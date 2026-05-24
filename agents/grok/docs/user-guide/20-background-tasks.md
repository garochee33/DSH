# Background Tasks and Monitoring

Grok provides several mechanisms for running long-lived processes, monitoring their output, and scheduling recurring work -- all without blocking the main conversation. This document covers background commands, the `/loop` command, the `monitor` tool, and the scheduler system.

---

## Background Commands

Any terminal command can be run in the background by setting `background: true` on the `run_terminal_command` tool. The command starts immediately, shows output for ~10 seconds, then continues running in the background while the agent proceeds with other tasks.

### How It Works

1. The agent calls `run_terminal_command` with `background: true`
2. The command starts and initial output is shown
3. After ~10 seconds, the command moves to the background
4. The agent receives a `task_id` for later reference
5. When the command completes, a notification appears in the conversation

### Getting Output

Use the `get_command_or_subagent_output` tool to check on a background command:

- `get_command_or_subagent_output(task_id)` -- returns current output and status (non-blocking)
- `get_command_or_subagent_output(task_id, block=true)` -- waits for the task to complete
- `get_command_or_subagent_output(task_id, block=true, timeout_ms=30000)` -- waits up to 30 seconds

### Killing Background Tasks

Use `kill_command_or_subagent(task_id)` to terminate a running background task. This sends SIGTERM/SIGKILL for shell processes or Cancel+Shutdown for subagents.

### Common Use Cases

- **Dev servers**: Start a development server and continue coding
- **Test suites**: Run tests in the background while working on fixes
- **Build processes**: Kick off a build and check results later
- **Long compilations**: Start a compile and continue with other tasks

---

## Ctrl+G: Demote to Background

In the interactive TUI, press `Ctrl+G` to demote a currently running foreground tool execution to the background. This is useful when:

- A command is taking longer than expected
- You want to ask the agent something else while a command runs
- You realize a process will be long-running after it has started

The demoted task continues running and you receive a notification when it completes.

---

## The /loop Command

`/loop` runs a prompt on a recurring interval. It is useful for polling tasks, periodic checks, and continuous monitoring.

### Syntax

```
/loop [interval] <prompt>
```

The interval format supports:

| Format | Example | Description        |
| ------ | ------- | ------------------ |
| `Ns`   | `60s`   | Every N seconds (minimum 60) |
| `Nm`   | `5m`    | Every N minutes    |
| `Nh`   | `2h`    | Every N hours      |
| `Nd`   | `1d`    | Every N days       |

### Examples

```
/loop 5m Check if the test suite passes and report any failures
/loop 2h Summarize new commits since the last check
/loop 60s Check if the dev server at localhost:3000 is responding
```

### Behavior

- The prompt fires immediately on creation, then repeats at the specified interval
- Each firing creates a new agent turn
- Recurring tasks auto-expire after 7 days
- Maximum 50 scheduled tasks can be active at once

---

## The monitor Tool

The `monitor` tool streams events from a long-running script. Each line of stdout becomes a notification in the conversation. This is the streaming counterpart to `/loop` -- use `/loop` for periodic checks, use `monitor` for real-time event streams.

### How It Works

1. You provide a shell command whose stdout is the event stream
2. Each line of stdout becomes a notification delivered to the conversation
3. Stderr goes to the output file but does not trigger notifications
4. The monitor runs until the command exits or you kill it

### Script Guidelines

- **Always use `grep --line-buffered`** in pipes -- without it, pipe buffering delays events by minutes
- **Handle transient failures** in poll loops (`curl ... || true`) -- one failed request should not kill the monitor
- **Use selective filters** -- every stdout line becomes a message, so never pipe raw logs
- **Poll intervals**: 30s+ for remote APIs (rate limits), 0.5-1s for local checks
- **Only stdout is the event stream**. Use stderr for debug output.

### Examples

```bash
# Watch for errors in a log file
tail -f /var/log/app.log | grep --line-buffered "ERROR"

# Monitor file changes in a directory
inotifywait -m --format '%e %f' /watched/dir

# Poll GitHub for new PR comments
last=$(date -u +%Y-%m-%dT%H:%M:%SZ)
while true; do
  now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  gh api "repos/owner/repo/issues/123/comments?since=$last" \
    --jq '.[] | "\(.user.login): \(.body)"'
  last=$now; sleep 30
done
```

### Persistent Monitors

Set `persistent: true` for monitors that should run for the lifetime of the session:

- PR monitoring
- Log tailing
- CI status watching

Stop persistent monitors with `kill_command_or_subagent(task_id)`.

### Volume Control

Monitors that produce too many events are automatically stopped. If this happens, restart with a tighter filter. Always prefer `grep --line-buffered`, `awk`, or a wrapper script that only emits the events you care about.

---

## The Scheduler

The scheduler provides a lower-level API for creating recurring tasks. `/loop` is a convenience wrapper around the scheduler.

### scheduler_create

Create a scheduled task:

| Parameter        | Description                                              |
| ---------------- | -------------------------------------------------------- |
| `interval`       | How often to run: `"5m"`, `"2h"`, `"1d"`, `"60s"`       |
| `prompt`         | The prompt text to execute on each fire                  |
| `fireImmediately`| Fire on creation (default: `true`) or wait for first interval |
| `recurring`      | Repeat (default: `true`) or fire once (`false`)          |
| `durable`        | Persist across sessions (default: `false`)               |

### scheduler_list

List all active scheduled tasks with their IDs, prompts, intervals, and next fire times.

### scheduler_delete

Cancel a scheduled task by ID. Returns success if the task was found and removed.

---

## The Queue Pane

In the interactive TUI, press `Ctrl+;` to toggle the queue pane. This shows:

- Active background tasks and their status
- Scheduled/recurring tasks from `/loop` and the scheduler
- Monitor tasks and their event counts
- Task IDs for reference

---

## Use Cases and Patterns

### Dev Server + Coding

Start a dev server in the background and continue coding:

```
Start the dev server with `npm run dev` in the background, then implement the login form.
```

The agent runs the dev server with `is_background: true` and proceeds to write code. When the server starts, you see a notification.

### Continuous Test Monitoring

```
/loop 5m Run the test suite and report any new failures since the last run
```

Every 5 minutes, the agent runs tests and reports only new failures.

### Log Monitoring

Use `monitor` to watch for specific events:

```
Monitor the application log for ERROR and WARN entries. Use:
tail -f /var/log/app.log | grep --line-buffered -E "ERROR|WARN"
```

Each error or warning appears as a notification in the conversation.

### CI Pipeline Watching

```
/loop 2m Check the status of the GitHub Actions run for this PR. Report when it completes.
```

---

## Best Practices

- **Use `background` for one-shot long commands** (builds, test suites, server starts)
- **Use `/loop` for periodic checks** (CI status, test runs, health checks)
- **Use `monitor` for real-time event streams** (log tailing, file watching)
- **Use `scheduler_create` with `recurring: false`** for delayed one-shot tasks
- **Keep monitor filters tight** -- prefer `grep --line-buffered` over raw log streams
- **Do not use sleep loops** in normal commands to poll -- use `get_command_or_subagent_output` with `block: true` instead
- **Set reasonable poll intervals** -- 30s+ for remote APIs to avoid rate limits, shorter for local checks

# Headless Mode and Scripting

Headless mode runs Grok non-interactively from the command line. It accepts a single prompt, executes it with full tool access, and returns the result. Use headless mode when you need to:

- **Automate tasks** -- CI/CD pipelines, pre-commit hooks, cron jobs
- **Script workflows** -- batch process files, chain with other tools
- **Build integrations** -- spawn as a sub-agent, embed in larger systems
- **Parse output programmatically** -- JSON output for downstream processing

---

## Basic Usage

The `-p` flag (short for `--single`) triggers headless mode:

```bash
grok -p "Your prompt here"
```

Grok processes the prompt, runs any necessary tools, and prints the result to stdout. The process exits when the response is complete.

---

## Command-Line Options

| Flag                    | Description                                           |
| ----------------------- | ----------------------------------------------------- |
| `-p, --single <PROMPT>` | The prompt to send (required for headless mode)       |
| `-m, --model <MODEL>`   | Model to use (e.g., `grok-build`)              |
| `-s, --session-id <ID>` | Create or resume a headless session with this ID      |
| `-r, --resume <ID>`     | Resume an existing session (errors if not found)      |
| `-c, --continue`        | Continue the most recent session in current directory  |
| `--cwd <PATH>`          | Set working directory                                 |
| `--output-format <FMT>` | Output format: `plain`, `json`, `streaming-json`      |
| `--yolo`                | Auto-approve all tool executions                      |
| `--rules <TEXT>`        | Custom rules for the system prompt                    |
| `--tools <TOOLS>`       | Allowlist of built-in tools (comma-separated). Only listed tools are available. Headless only. |
| `--disallowed-tools <TOOLS>` | Denylist of built-in tools to remove (comma-separated). Supports `Agent` entries. Headless only. |
| `--max-turns <N>`       | Maximum number of agentic turns before stopping. Headless only. |
| `--effort <LEVEL>`      | Effort level (`low`, `medium`, `high`). Headless only. |
| `--permission-mode <MODE>` | Permission mode for tool approvals. Headless only. |
| `--allow <RULE>`        | Permission allow rule with glob patterns (repeatable). Works in TUI and headless. |
| `--deny <RULE>`         | Permission deny rule with glob patterns (repeatable). Works in TUI and headless. |

> **Note:** `--tools`, `--disallowed-tools`, `--max-turns`, `--effort`, and `--permission-mode` are headless-only flags. If used in the interactive TUI, a warning is printed and the flag is ignored. `--allow` and `--deny` work in both modes.

### Tool Filtering

Use `--tools` to restrict the agent to an explicit set of tools (allowlist), or `--disallowed-tools` to remove specific tools from the default set (denylist). Both accept comma-separated tool names.

Tool names are internal tool IDs (e.g. the shell tool is `run_terminal_cmd`, not `bash`).

```bash
# Only allow read-only tools
grok -p "Explain this codebase" --tools "read_file,grep,list_dir"

# Remove web access and file editing
grok -p "Review this code" --disallowed-tools "web_search,web_fetch,search_replace"

# Remove shell access
grok -p "Review this code" --disallowed-tools "run_terminal_cmd"
```

`--disallowed-tools` also supports special `Agent` entries to control subagent spawning:

| Entry                  | Effect                                  |
| ---------------------- | --------------------------------------- |
| `Agent`                | Block all subagent spawning             |
| `Agent(explore)`       | Block the `explore` subagent type only  |
| `Agent(explore, plan)` | Block multiple specific types           |

```bash
# Prevent the agent from spawning any subagents
grok -p "Fix this bug" --disallowed-tools "Agent"

# Block only the explore subagent
grok -p "Refactor this module" --disallowed-tools "Agent(explore)"
```

When `--tools` is set, only the listed tools are available and default tool injection is disabled. When both flags are present, `--disallowed-tools` runs after `--tools`.

### Permission Rules (`--allow` / `--deny`)

Permission rules control whether specific tool invocations are auto-approved, denied, or require user confirmation. Unlike `--disallowed-tools` (which removes tools entirely), permission rules leave tools available but gate their execution.

Rules use `ToolPrefix(glob_pattern)` syntax:

| Prefix        | What it controls                   |
| ------------- | ---------------------------------- |
| `Bash(...)`   | Shell command execution            |
| `Edit(...)`   | File editing (path glob)           |
| `Write(...)`  | File writing (path glob)           |
| `Read(...)`   | File reading (path glob)           |
| `Grep(...)`   | Search operations (path glob)      |
| `WebFetch(...)` | URL fetching (glob or `domain:host`) |
| `MCPTool(...)` | MCP tool invocations              |

Glob patterns support `*` (single-level wildcard) and `**` (recursive). A bare prefix without parentheses matches all invocations of that type.

```bash
# Deny shell commands matching "rm*"
grok -p "Clean up this project" --deny "Bash(rm*)"

# Allow npm commands, deny sudo
grok -p "Set up the project" --allow "Bash(npm*)" --deny "Bash(sudo*)"

# Allow all bash commands (auto-approve without prompting)
grok -p "Build the project" --allow "Bash"
```

`--allow` and `--deny` can be repeated. Deny rules take precedence over allow rules.

---

## Output Formats

Headless mode supports three output formats, selected with `--output-format`.

### plain (default)

Human-readable text, suitable for direct display or piping:

```
Here's a summary of the codebase...
```

### json

A single JSON object emitted after the response completes. Contains the full response text, stop reason, session ID, and request ID:

```json
{
  "text": "Here's a summary of the codebase...",
  "stopReason": "EndTurn",
  "sessionId": "abc123",
  "requestId": "xyz789"
}
```

The `sessionId` field is useful for resuming the conversation later.

### streaming-json

Newline-delimited JSON events emitted in real time. Each line is a self-contained JSON object with a `type` field:

```json
{"type":"text","data":"Here's"}
{"type":"text","data":" a summary"}
{"type":"thought","data":"Analyzing the directory structure..."}
{"type":"end","stopReason":"EndTurn","sessionId":"abc123","requestId":"xyz789"}
```

Event types:

| Type       | Description                           |
| ---------- | ------------------------------------- |
| `text`     | A chunk of the agent's response text  |
| `thought`  | Internal reasoning (thinking tokens)  |
| `end`      | Final event with metadata             |

---

## Session Management in Headless Mode

By default, each `grok -p` invocation creates a fresh session. To maintain context across calls, use session flags.

### Named Sessions (`-s`)

The `-s/--session-id` flag lets you choose your own session ID. If the session already exists, it picks up where you left off. If not, a new one is created:

```bash
# Start a session namespaced to a PR
grok -p "Review the changes in this PR" -s "critique-myrepo-pr-123"

# Continue in the same session
grok -p "Now check for security issues" -s "critique-myrepo-pr-123"
```

This is the recommended approach for CI and automation workflows where you need multi-turn conversations.

> **Note:** `-s/--session-id` is for headless mode (`-p/--single`) only.
> In the interactive TUI, use `/load` or `--resume`.

### Resume (`-r`)

The `-r/--resume` flag resumes a specific session by ID. Unlike `-s`, it errors if the session does not exist:

```bash
# Get the session ID from a previous JSON response
grok -p "Remember: the secret number is 42" --output-format json
# Output includes "sessionId": "abc123"

# Resume that exact session
grok -p "What's the secret number?" --resume abc123
```

### Continue (`-c`)

The `-c/--continue` flag continues the most recent session in the current working directory:

```bash
grok -p "Continue where we left off" -c
```

### Extracting Session IDs

Use `--output-format json` and parse the `sessionId` field:

```bash
grok -p "Hello" --output-format json | jq -r '.sessionId'
```

---

## Piping Input and Output

Headless mode works naturally with Unix pipes and redirection.

### Standard Output

```bash
# Pipe output to a file
grok -p "Generate a README" > README.md

# Parse JSON output with jq
grok -p "List files" --output-format json | jq -r '.text'
```

### Standard Input

You can pipe content into Grok by including it in the prompt:

```bash
# Pipe git diff as context
git diff --staged | grok -p "Write a concise commit message for these changes"
```

---

## CI/CD Integration Examples

### Automated Code Review

```bash
grok -p "Review changes for bugs and security issues." \
  --output-format json --yolo | jq -r '.text' > review.md
```

### Pre-Commit Hook

```bash
grok -p "Review staged changes for obvious bugs. Reply OK if fine, or list issues." \
  --yolo --output-format json | jq -r '.text' | grep -q "^OK" || exit 1
```

### Batch Processing

```bash
for file in src/*.js; do
  grok -p "Migrate $file from CommonJS to ES modules." --yolo
done
```

---

## Scripting Patterns

### Python Wrapper

Grok's headless mode can be wrapped as an OpenAI-compatible chat completion API:

```python
import asyncio
import json
import os

class GrokChat:
    """Simple OpenAI-compatible wrapper using headless mode."""

    def __init__(self, cwd="."):
        self.cwd = cwd
        self.env = {**os.environ}

    def _build_cmd(self, prompt, model, stream):
        return ["grok", "-p", prompt, "-m", model, "--cwd", self.cwd,
                "--output-format", "streaming-json" if stream else "json",
                "--yolo"]

    async def create(self, messages, model="grok-build", stream=False):
        prompt = messages[-1]["content"] if len(messages) == 1 else "\n".join(
            f"{m['role']}: {m['content']}" for m in messages
        )
        cmd = self._build_cmd(prompt, model, stream)

        if stream:
            return self._stream(cmd)

        proc = await asyncio.create_subprocess_exec(
            *cmd, env=self.env, stdout=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        data = json.loads(stdout.decode()) if stdout else {"text": ""}
        return {
            "choices": [{
                "message": {"role": "assistant", "content": data.get("text", "")},
                "finish_reason": "stop"
            }]
        }

    async def _stream(self, cmd):
        proc = await asyncio.create_subprocess_exec(
            *cmd, env=self.env, stdout=asyncio.subprocess.PIPE
        )
        async for line in proc.stdout:
            if not line.strip():
                continue
            event = json.loads(line)
            if event.get("type") == "text":
                yield {"choices": [{"delta": {"content": event["data"]}}]}
            elif event.get("type") == "end":
                yield {"choices": [{"delta": {}, "finish_reason": "stop"}]}


async def main():
    client = GrokChat(cwd=".")
    response = await client.create(
        [{"role": "user", "content": "What files are here?"}]
    )
    print(response["choices"][0]["message"]["content"])

asyncio.run(main())
```

### Shell Script

```bash
#!/bin/bash
# Run a code review and exit with failure if issues are found

RESULT=$(grok -p "Review this PR for bugs. Output JSON with 'issues' array." \
  --output-format json --yolo | jq -r '.text')

ISSUE_COUNT=$(echo "$RESULT" | jq '.issues | length' 2>/dev/null || echo "0")

if [ "$ISSUE_COUNT" -gt 0 ]; then
  echo "Found $ISSUE_COUNT issues"
  echo "$RESULT" | jq '.issues[]'
  exit 1
fi

echo "No issues found"
```

---

## Fully Automated Runs with --yolo

The `--yolo` flag auto-approves all tool executions (file writes, command execution, etc.) without prompting for confirmation. This is required for unattended automation:

```bash
# Format all files without asking
grok -p "Format all files" --yolo

# Run tests and fix failures
grok -p "Run the tests and fix any failures" --cwd ~/projects/my-app --yolo
```

**Use `--yolo` with care.** It grants the agent full autonomy to modify files and run commands. Only use it in trusted environments or with well-scoped prompts.

---

## Environment Variables for Headless

Key environment variables that affect headless mode:

| Variable                        | Description                                                   |
| ------------------------------- | ------------------------------------------------------------- |
| `XAI_API_KEY`        | API key for authentication (required when no browser login)   |
| `GROK_HOME`                    | Override config directory (default: `~/.grok`)                |
| `GROK_LOG_FILE`                | Enable file logging: `1` for default path, or a custom path  |
| `GROK_LOG_FILTER`              | Log level filter (default: `info`)                            |
| `RUST_LOG`                     | Logging level for stderr (headless mode only)                 |

For CI environments without browser access, set `XAI_API_KEY` with an API key from [console.x.ai](https://console.x.ai):

```bash
export XAI_API_KEY="xai-..."
grok -p "Run the test suite" --yolo
```

---

## Exit Codes

| Code | Meaning                              |
| ---- | ------------------------------------ |
| `0`  | Success -- prompt completed normally |
| `1`  | Error -- authentication failure, network error, or runtime error |

---

## Tips

- Headless mode starts a **fresh session by default**. Use `-s <id>` to maintain context across calls.
- The `--output-format json` response always includes a `sessionId` you can use with `--resume` or `-s` for follow-up calls.
- Combine `--yolo` with `--rules` to set guardrails: `grok -p "..." --yolo --rules "Never delete files"`.
- For debugging, enable logging: `GROK_LOG_FILE=1 GROK_LOG_FILTER=debug grok -p "..."`.

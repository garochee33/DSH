# Sandbox Mode

Sandbox mode restricts what the agent process and its spawned commands can access on your filesystem and network using OS-level kernel primitives (Landlock on Linux, Seatbelt on macOS). This provides a hard security boundary that the model cannot bypass at runtime.

Sandbox mode is off by default.

---

## Quick Start

```bash
# Run with workspace sandbox (read everywhere, write only to CWD + /tmp)
grok --sandbox workspace

# Read-only mode (agent can read but not write anything)
grok --sandbox read-only

# Maximum isolation (read/write CWD only, no child network)
grok --sandbox strict
```

---

## Built-in Profiles

| Profile         | FS Read            | FS Write                  | Child Network | Use Case                 |
| --------------- | ------------------ | ------------------------- | ------------- | ------------------------ |
| `off` (default) | Unrestricted       | Unrestricted              | Unrestricted  | No sandbox               |
| `workspace`     | Everywhere         | CWD + `/tmp` + `~/.grok/` | Allowed       | Normal development       |
| `read-only`     | Everywhere         | `~/.grok/` only           | Blocked       | Exploration, code review |
| `strict`        | CWD + system paths | CWD + `/tmp` + `~/.grok/` | Blocked       | Untrusted code           |

### Profile Details

**workspace** -- The recommended profile for everyday development. The agent can read any file on the system (for understanding dependencies, system libraries, etc.) but can only write to the current working directory, `/tmp`, and `~/.grok/`. Network access is allowed for tools like `web_search` and MCP servers.

**read-only** -- Use when you want the agent to analyze code without any risk of modification. The agent can read everything but can only write to `~/.grok/` (needed for session persistence). Network access is blocked for child processes.

**strict** -- Maximum isolation for reviewing untrusted code. The agent can only read files within the current working directory and essential system paths. Writes are limited to CWD, `/tmp`, and `~/.grok/`. Network access is blocked for child processes.

### Sensitive Path Protection

Regardless of the selected profile, certain sensitive paths are always write-protected:

- `~/.ssh/`
- `~/.aws/`
- `~/.gnupg/`
- `~/.grok/auth/`

---

## Custom Profiles

Create custom sandbox profiles in `~/.grok/sandbox.toml` (global) or `.grok/sandbox.toml` (per-project):

```toml
[profiles.devbox]
# Start from a built-in profile, then add overrides
extends = "workspace"
restrict_network = true

# Paths the agent can read but NOT write/delete
read_only = ["/data"]

# Additional writable paths
read_write = ["/tmp/scratch"]

# Paths denied entirely
deny = ["/data/shared-secrets"]
```

Use the custom profile:

```bash
grok --sandbox devbox
```

### Custom Profile Fields

| Field              | Type     | Description                                          |
| ------------------ | -------- | ---------------------------------------------------- |
| `extends`          | String   | Base profile to inherit from (`workspace`, `read-only`, `strict`) |
| `restrict_network` | Boolean  | Block network access for child processes             |
| `read_only`        | String[] | Additional read-only paths                           |
| `read_write`       | String[] | Additional read-write paths                          |
| `deny`             | String[] | Paths denied entirely (no read or write)             |

---

## How It Works

The sandbox is applied to the **entire grok process** at startup using kernel primitives -- not per-command wrapping. This means all tool operations are covered:

- `read_file`, `search_replace`, `list_dir` -- restricted by Landlock/Seatbelt in-process
- `bash` commands, `grep` (rg) -- child processes inherit FS restrictions automatically
- Network -- child processes can be blocked via seccomp (Linux)

The sandbox is **irreversible** once applied. This is a security feature -- the model cannot convince the agent to relax restrictions at runtime. There is no "escape hatch."

---

## Platform Support

| Platform | Mechanism | Minimum Version        |
| -------- | --------- | ---------------------- |
| Linux    | Landlock  | Kernel 5.13 or later   |
| macOS    | Seatbelt  | macOS (all versions)   |

If the sandbox cannot be applied (e.g., unsupported kernel, missing entitlements), Grok logs a warning and continues without enforcement.

---

## Network Restrictions

Profiles with `restrict_network` block network access in **child processes** (bash commands, scripts) via seccomp. However, built-in tools that make HTTP requests in-process (web search, LLM API calls) are not affected -- the agent needs network access to function.

In practice, this means:

- `web_search`, `web_fetch`, and the LLM API always have network access
- `bash` commands like `curl`, `wget`, and `npm install` are blocked when `restrict_network` is enabled

---

## Event Logging

Sandbox events are logged to `~/.grok/sandbox-events.jsonl` for telemetry and debugging. Events include:

- Profile applied (which profile, timestamp)
- Violations (attempted access to denied paths)

---

## When to Use Sandbox Mode

**Use `workspace` when:**

- Working on your own projects and you want basic write protection
- Running in shared environments where you want to limit the blast radius

**Use `read-only` when:**

- Reviewing code you do not trust
- Exploring a codebase without risk of accidental modification
- Running code analysis or audits

**Use `strict` when:**

- Analyzing untrusted or third-party code
- Running in security-sensitive environments
- You want maximum isolation

**Skip sandbox when:**

- The agent needs to install dependencies (`npm install`, `pip install`)
- The agent needs to modify files outside the working directory
- You are working in a trusted environment and want maximum flexibility

---

## Trade-offs

| Aspect      | Without Sandbox            | With Sandbox                    |
| ----------- | -------------------------- | ------------------------------- |
| Safety      | Agent has full system access | Agent restricted to profile rules |
| Capability  | Can do anything            | Limited by profile              |
| Performance | No overhead                | Negligible overhead             |
| Recovery    | Must trust the agent       | Kernel enforces boundaries      |

The sandbox adds no meaningful performance overhead -- it is a kernel-level policy check, not a wrapper or VM.

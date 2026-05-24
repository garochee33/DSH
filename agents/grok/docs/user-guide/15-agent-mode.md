# Agent Mode (ACP) and IDE Integration

Agent mode runs Grok as an ACP (Agent Client Protocol) server for integration with IDEs, editors, and custom tooling. Unlike headless mode (which runs a single prompt and exits), agent mode keeps a persistent process running and communicates via structured JSON-RPC messages.

---

## What is ACP?

The [Agent Client Protocol (ACP)](https://agentclientprotocol.com) is a standard for AI agent communication. It defines how clients (IDEs, editors, custom apps) interact with AI agents through a structured JSON-RPC protocol. ACP provides:

- **Session management** -- create, load, and resume conversations
- **Prompt submission** -- send user messages and receive streamed responses
- **Tool visibility** -- see what tools the agent is using in real time
- **Thought streams** -- observe the agent's reasoning process
- **Permission handling** -- approve or deny tool executions interactively

---

## stdio Transport

The primary integration mode. The agent communicates via JSON-RPC over stdin/stdout:

```bash
grok agent stdio
```

This mode is used by:

- IDE extensions (Zed, Neovim, Emacs, etc.)
- Custom automation tools
- ACP client libraries

### Options

| Flag                  | Description                                                                          |
| --------------------- | ------------------------------------------------------------------------------------ |
| `-m, --model <MODEL>` | Override the default model (e.g., `grok-build`)                           |
| `--yolo`              | Start in YOLO mode (auto-approve all tool executions without confirmation)           |
| `--reauth`            | Force re-authentication flow                                                         |

---

## Server Mode

Expose the agent as an HTTP server for network-based integration:

```bash
grok agent serve --bind 127.0.0.1:2419 --secret <token>
```

Clients connect over HTTP/WebSocket and authenticate with the provided secret token. This is useful for setups where multiple clients need to share a single agent process.

---

## WebSocket Relay

To expose the agent over the internet (instead of local network), run a WebSocket relay server and have the agent connect to it:

```bash
grok agent headless --grok-ws-url wss://your-relay.example.com/ws
```

The agent connects OUT to your relay, and your web clients connect to the same relay. This is useful for building web UIs where browsers cannot spawn local processes.

---

## ACP Protocol Basics

Communication follows the JSON-RPC 2.0 format. A typical session lifecycle:

1. **Initialize** -- client sends `initialize` with capabilities
2. **Create session** -- client sends `session/new` with working directory
3. **Send prompts** -- client sends `session/prompt` with user messages
4. **Receive updates** -- agent sends `session/update` notifications with streamed content
5. **Handle permissions** -- agent may request tool execution approval

### Architecture

```
+------------------------------------------+
|           ACP Client                     |
|  (IDE, Editor, Custom Application)       |
+-------------------+----------------------+
                    | JSON-RPC over stdio
+-------------------v----------------------+
|           grok agent stdio               |
|                                          |
|  +---------+  +---------+  +---------+   |
|  | Session |  |  Tools  |  |   MCP   |   |
|  | Manager |  | Registry|  | Servers |   |
|  +---------+  +---------+  +---------+   |
+------------------------------------------+
```

---

## Rich Streaming

ACP provides structured streaming events, not just raw text. The `session/update` notification delivers different update types:

| Session Update Type      | Description                                        |
| ------------------------ | -------------------------------------------------- |
| `agent_message_chunk`    | A chunk of the agent's response text               |
| `agent_thought_chunk`    | Internal reasoning / thinking tokens               |
| `tool_call`              | A tool invocation (name, arguments, status)        |
| `plan`                   | Plan entries when the agent is in plan mode        |

This allows clients to render rich UIs with separate panels for thoughts, tool calls, and response text.

---

## Extension Methods

Beyond the base ACP protocol, Grok defines extension methods under the `x.ai/` prefix for xAI-specific functionality. These cover:

| Category                   | Prefix               | Examples                                         |
| -------------------------- | -------------------- | ------------------------------------------------ |
| **Filesystem**             | `x.ai/fs/*`          | `list`, `exists`, `read_file`, `write_file`      |
| **Git**                    | `x.ai/git/*`         | `status`, `stage`, `commit`, `diffs`, `discard`  |
| **Git Worktree**           | `x.ai/git/worktree/*`| `create`, `remove`, `apply`, `list`, `gc`        |
| **Search**                 | `x.ai/search/*`      | `fuzzy/open`, `fuzzy/change`, `content`          |
| **Terminal**               | `x.ai/terminal/*`    | `create`, `kill`, `output`, `wait_for_exit`      |
| **Code Navigation**        | `x.ai/code/*`        | `goto-definition`, `find-references` (feature-flagged) |
| **Session Management**     | `x.ai/session/*`     | `fork`, `resolve_local_for_worktree_resume`      |
| **Conversation & History** | `x.ai/*`             | `prompt_history`, `rewind/*`, `compact_conversation` |
| **Authentication**         | `x.ai/auth/*`        | `get_url`, `submit_code`                         |
| **Feedback & Telemetry**   | `x.ai/*`             | `feedback`, `telemetry/*`                        |

The full extension methods catalog with 72 methods is documented in `ACP_EXTENSION_METHODS.md`.

### Notifications (Agent to Client)

The agent sends push notifications to clients for real-time updates:

| Notification               | Description                          |
| -------------------------- | ------------------------------------ |
| `x.ai/search/fuzzy/status` | Fuzzy search results update          |
| `x.ai/git/worktree/status` | Worktree creation progress           |
| `x.ai/fs_notify`           | Filesystem change notification       |
| `x.ai/fs/index`            | Full file index update               |
| `x.ai/fs/index/delta`      | Incremental file index update        |
| `x.ai/session_notification`| Session-specific updates (diff review, retry state, auto-compact) |
| `x.ai/session/update`      | Session update (tool calls, content) |

---

## Multi-Client Routing

When multiple clients connect to the same agent (e.g., via server mode), the `_meta.targetClientId` field in extension method requests routes messages to the correct client. This prevents one client's fuzzy search results from being sent to another client.

---

## ACP SDKs

Official SDK libraries are available for multiple languages:

| Language   | Package                                                                                  |
| ---------- | ---------------------------------------------------------------------------------------- |
| TypeScript | [`@agentclientprotocol/sdk`](https://www.npmjs.com/package/@agentclientprotocol/sdk)     |
| Rust       | [`agent-client-protocol`](https://crates.io/crates/agent-client-protocol)                |
| Python     | [`agent-client-protocol-python`](https://github.com/PsiACE/agent-client-protocol-python) |
| Go         | [`acp-go-sdk`](https://github.com/coder/acp-go-sdk)                                     |
| Kotlin     | [`acp`](https://github.com/agentclientprotocol/kotlin-sdk)                               |

---

## Compatible Clients

| Client                                                   | Status      |
| -------------------------------------------------------- | ----------- |
| [Zed](https://zed.dev/docs/ai/external-agents)           | Supported   |
| [Neovim](https://neovim.io) (CodeCompanion, avante.nvim) | Supported   |
| [Emacs](https://github.com/xenodium/agent-shell)         | Supported   |
| [marimo notebook](https://github.com/marimo-team/marimo) | Supported   |
| JetBrains                                                | Coming soon |

---

## Integration Example: TypeScript ACP Client

```typescript
import { spawn, ChildProcess } from "child_process";
import * as readline from "readline";

class GrokACPChat {
  private proc!: ChildProcess;
  private sessionId!: string;
  private rl!: readline.Interface;

  constructor(private cwd = ".") {}

  async init() {
    this.proc = spawn("grok", ["agent", "stdio"]);
    this.rl = readline.createInterface({ input: this.proc.stdout! });

    // Initialize
    await this.request("initialize", {
      protocolVersion: "1",
      clientCapabilities: {
        fs: { readTextFile: true, writeTextFile: true },
        terminal: true,
      },
    });

    // Create session
    const { sessionId } = await this.request("session/new", {
      cwd: this.cwd,
      mcpServers: [],
    });
    this.sessionId = sessionId;
    return this;
  }

  private async request(method: string, params: any): Promise<any> {
    return new Promise((resolve) => {
      const msg = JSON.stringify({ jsonrpc: "2.0", id: 1, method, params });
      this.proc.stdin!.write(msg + "\n");

      this.rl.once("line", (line) => {
        resolve(JSON.parse(line).result || {});
      });
    });
  }

  async *streamPrompt(text: string) {
    const msg = JSON.stringify({
      jsonrpc: "2.0",
      id: 1,
      method: "session/prompt",
      params: {
        sessionId: this.sessionId,
        prompt: [{ type: "text", text }],
      },
    });
    this.proc.stdin!.write(msg + "\n");

    for await (const line of this.rl) {
      const data = JSON.parse(line);

      if (data.method === "session/update") {
        const update = data.params.update;
        yield update; // { sessionUpdate, content, tool, ... }
      } else if (data.result) {
        break; // Final response
      }
    }
  }
}

// Usage
const client = await new GrokACPChat(".").init();

for await (const update of client.streamPrompt("List the files in this project")) {
  switch (update.sessionUpdate) {
    case "agent_message_chunk":
      process.stdout.write(update.content?.text || "");
      break;
    case "agent_thought_chunk":
      console.log(`\n[Thinking: ${update.content?.text}]`);
      break;
    case "tool_call":
      console.log(`\n[Tool: ${update.tool}]`);
      break;
  }
}
```

---

## Resources

- [ACP Specification](https://agentclientprotocol.com/protocol/prompt-turn)
- [Protocol Introduction](https://agentclientprotocol.com/overview/introduction)
- [Extension Methods Reference](../../xai-grok-shell/ACP_EXTENSION_METHODS.md) -- full catalog of 72 `x.ai/*` methods

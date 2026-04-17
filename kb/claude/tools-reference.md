# Claude Tools Reference

A catalog of every tool Claude can call in this DOME-HUB environment.
Deferred tools are loaded on demand via `ToolSearch`.

---

## Core (always available)

| Tool | Purpose |
|------|---------|
| `Bash` | Run shell commands in the sandboxed Ubuntu 22 container |
| `Read` | Read a file (supports PDFs, images, Jupyter notebooks) |
| `Write` | Create or overwrite a file |
| `Edit` | Exact-string replacement in an existing file |
| `Glob` | Fast filename pattern matching |
| `Grep` | Ripgrep-powered content search |
| `Agent` | Spawn a subagent (general-purpose, Explore, Plan, claude-code-guide, statusline-setup) |
| `ToolSearch` | Fetch the JSONSchema for a deferred tool |
| `Skill` | Invoke a loaded skill (docx, pdf, pptx, xlsx, …) |

## Tasks & Tracking (deferred)

| Tool | Purpose |
|------|---------|
| `TaskCreate` / `TaskList` / `TaskGet` / `TaskUpdate` / `TaskStop` | Structured task list for the current session |
| `mcp__scheduled-tasks__create_scheduled_task` | Create a cron / one-off scheduled job |
| `mcp__scheduled-tasks__list_scheduled_tasks` | List scheduled jobs |
| `mcp__scheduled-tasks__update_scheduled_task` | Edit an existing scheduled job |
| `Monitor` | Stream output from a long-running background command |
| `PushNotification` | Send a notification back to the user |
| `RemoteTrigger` | Trigger a remote webhook-style event |

## User Interaction (deferred)

| Tool | Purpose |
|------|---------|
| `AskUserQuestion` | Ask structured multiple-choice questions |
| `mcp__cowork__present_files` | Present one or more files to the user in the Cowork UI |
| `mcp__cowork__request_cowork_directory` | Ask the user to select a folder to work in |
| `mcp__cowork__allow_cowork_file_delete` | Request permission for destructive file operations |
| `mcp__cowork-onboarding__show_onboarding_role_picker` | Onboarding UI |

## Web (deferred)

| Tool | Purpose |
|------|---------|
| `WebSearch` | Search the web (compliance-filtered) |
| `WebFetch` | Fetch the contents of a URL (compliance-filtered) |

## Claude in Chrome (browser automation, deferred)

| Tool | Purpose |
|------|---------|
| `mcp__Claude_in_Chrome__navigate` | Open a URL |
| `mcp__Claude_in_Chrome__get_page_text` | Get text of the current page |
| `mcp__Claude_in_Chrome__read_page` | Read structured page content |
| `mcp__Claude_in_Chrome__form_input` | Fill form fields |
| `mcp__Claude_in_Chrome__javascript_tool` | Execute JS in the page |
| `mcp__Claude_in_Chrome__read_console_messages` | Read DevTools console |
| `mcp__Claude_in_Chrome__read_network_requests` | Read DevTools network tab |
| `mcp__Claude_in_Chrome__file_upload` / `upload_image` | Upload files to the page |
| `mcp__Claude_in_Chrome__tabs_create_mcp` / `tabs_close_mcp` / `tabs_context_mcp` | Tab management |
| `mcp__Claude_in_Chrome__browser_batch` | Batch several browser actions |
| `mcp__Claude_in_Chrome__computer` | Computer-use primitives (click, type, screenshot) |
| `mcp__Claude_in_Chrome__shortcuts_list` / `shortcuts_execute` | Named shortcuts |
| `mcp__Claude_in_Chrome__switch_browser` / `resize_window` | Window management |
| `mcp__Claude_in_Chrome__find` | Find-in-page |
| `mcp__Claude_in_Chrome__gif_creator` | Record a GIF of browser activity |

## MCP & Plugin Discovery (deferred)

| Tool | Purpose |
|------|---------|
| `mcp__mcp-registry__search_mcp_registry` | Search the Claude MCP registry |
| `mcp__mcp-registry__suggest_connectors` | Suggest MCP connectors to the user |
| `mcp__plugins__search_plugins` | Search available plugins |
| `mcp__plugins__suggest_plugin_install` | Suggest a plugin install |

## Session Introspection (deferred)

| Tool | Purpose |
|------|---------|
| `mcp__session_info__list_sessions` | List recent sessions |
| `mcp__session_info__read_transcript` | Read a past session transcript |

## Editor-specific (deferred)

| Tool | Purpose |
|------|---------|
| `NotebookEdit` | Edit a Jupyter notebook cell |

---

## Invocation pattern

Deferred tools do not have schemas loaded at session start. To call one, first fetch it:

```
ToolSearch(query="select:AskUserQuestion,WebSearch", max_results=2)
```

The response includes a JSONSchema block; after that, the tools are callable like any other.

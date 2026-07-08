# Custom Models

Grok supports custom model endpoints, letting you use alternative providers, self-hosted models, or override built-in model settings. This guide covers model selection, configuration, and integration with third-party providers.

---

## Default Models

Out of the box, Grok uses models hosted by xAI. The default model for new sessions is `grok-build`. You do not need any configuration to use the default models -- just authenticate with `grok login` or an API key.

List all available models:

```bash
grok models
```

---

## Selecting a Model

### CLI Flag

```bash
grok -p "Hello" -m grok-build
```

### Slash Command

In the TUI, switch models during a session:

```
/model grok-build
```

Or use the alias:

```
/m grok-build
```

### Model Picker (Ctrl+M)

In the TUI, press `Ctrl+M` to open the model picker. This shows all available models (built-in and custom) and lets you switch with a single keystroke.

### Config Default

Set a persistent default in `~/.grok/config.toml`:

```toml
[models]
default = "grok-build"
```

---

## Supported API Backends

Grok supports three API backends. Set `api_backend` in your `[model.*]` config to choose which protocol to use:

| Value | API | Default |
|-------|-----|---------|
| `"chat_completions"` | OpenAI Chat Completions (`/v1/chat/completions`) | Yes |
| `"responses"` | OpenAI Responses (`/v1/responses`) | |
| `"messages"` | Anthropic Messages (`/v1/messages`) | |

If `api_backend` is omitted, it defaults to `chat_completions`.

### Authentication Schemes

Grok supports two auth schemes, controlled by `auth_scheme`:

| Value | Header | Use with |
|-------|--------|----------|
| `"bearer"` | `Authorization: Bearer <key>` | OpenAI, Together, Ollama, most providers (default) |
| `"x_api_key"` | `x-api-key: <key>` | Anthropic |

---

## Configuring Custom Models

Add custom model endpoints in `~/.grok/config.toml` under `[model.<name>]` sections:

```toml
[model.my-model]
model = "model-id"                        # Model identifier sent to the API
base_url = "https://api.example.com/v1"   # OpenAI-compatible endpoint
name = "Display Name"                     # Shown in model picker
description = "Model description"         # Optional description
api_key = "sk-..."                        # API key for this provider (optional)
env_key = "OPENAI_API_KEY"                # Env var holding the API key (optional)
api_backend = "chat_completions"          # "chat_completions", "responses", or "messages"
auth_scheme = "bearer"                    # "bearer" or "x_api_key"
temperature = 0.7                         # Sampling temperature (0.0-2.0)
top_p = 0.95                              # Nucleus sampling parameter
max_completion_tokens = 8192              # Max tokens per response
max_turns = 50                            # Max conversation turns
context_window = 128000                   # Total context window in tokens
```

### Credential Resolution

API key is resolved in this order:

1. `api_key` field in the model config
2. Environment variable named in `env_key`
3. `GROK_CODE_XAI_API_KEY` environment variable (global fallback)

### Context Window

The `context_window` parameter tells Grok when to trigger auto-compaction. If not specified, Grok falls back to built-in defaults for known models.

---

## Overriding Built-in Models

You can override specific fields of built-in models without redefining everything. Only specify the fields you want to change:

```toml
# Override just the API key for a default model
[model.grok-build]
api_key = "my-api-key"

# Override temperature and add a custom API key
[model.grok-build]
temperature = 0.5
api_key = "sk-custom"
```

When you override a built-in model, Grok starts with the default configuration (including the correct `base_url`), then applies only the fields you specify. Unspecified fields inherit from the default.

### Priority Order

1. Your config (`[model.*]`) -- highest priority
2. Prefetched models from remote `/v1/models`
3. Hardcoded defaults -- lowest priority

---

## Provider Examples

### Anthropic (Claude)

Use Claude models directly via the Anthropic Messages API:

```toml
[model.claude-opus]
model = "claude-opus-4-6"
base_url = "https://api.anthropic.com"
name = "Claude Opus 4.6"
api_backend = "messages"
auth_scheme = "x_api_key"
env_key = "ANTHROPIC_API_KEY"
context_window = 200000
```

Anthropic uses `x-api-key` header authentication instead of `Authorization: Bearer`, so set `auth_scheme = "x_api_key"`.

### OpenAI (Chat Completions)

```toml
[model.gpt-4o]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
name = "GPT-4o"
env_key = "OPENAI_API_KEY"
```

`api_backend` defaults to `"chat_completions"`, so you don't need to set it explicitly for OpenAI.

### OpenAI (Responses API)

If your provider supports the newer Responses API:

```toml
[model.gpt-4o-responses]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
name = "GPT-4o (Responses)"
api_backend = "responses"
env_key = "OPENAI_API_KEY"
```

### Ollama (Local Models)

Run models locally with [Ollama](https://ollama.ai):

```toml
[model.ollama-codellama]
model = "codellama"
base_url = "http://localhost:11434/v1"
name = "CodeLlama (Ollama)"
```

Make sure Ollama is running (`ollama serve`) and the model is pulled (`ollama pull codellama`).

### Together AI

```toml
[model.together-mixtral]
model = "mistralai/Mixtral-8x7B-Instruct-v0.1"
base_url = "https://api.together.xyz/v1"
name = "Mixtral 8x7B"
env_key = "TOGETHER_API_KEY"
```

### Local OpenAI-Compatible Server

Any server that implements the OpenAI chat completions or responses API:

```toml
[model.local-llama]
model = "llama-3.1-70b"
base_url = "http://localhost:8080/v1"
name = "Local Llama"
temperature = 0.8
```

---

## Custom Models Endpoint

Point Grok at a custom OpenAI-compatible `/v1/models` endpoint instead of the default. This is useful when models are served behind a corporate gateway or self-hosted inference stack.

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROK_MODELS_BASE_URL` | Yes | Base URL for inference. Model list is fetched from `{base_url}/models`. |
| `GROK_CODE_XAI_API_KEY` | Yes | API key sent as `Authorization: Bearer`. |
| `GROK_MODELS_LIST_URL` | No | Override the model list URL if it differs from `{base_url}/models`. |

### Setup

```bash
export GROK_MODELS_BASE_URL="https://api.acme.com/v1"
export GROK_CODE_XAI_API_KEY="xai-..."
grok
```

### Config File Alternative

```toml
[endpoints]
models_base_url = "https://api.acme.com/v1"

# Override just the API key for a specific model
[model.grok-build]
api_key = "my-api-key"
```

When using `[endpoints]` with partial model overrides, the `base_url` is inherited from the endpoints config -- you do not need to specify it in each `[model.*]` section.

### Auth Behavior

When `models_base_url` is set, Grok uses API key auth (`Authorization: Bearer`) instead of session auth. `grok login` is not required -- only the API key.

---

## Web Search Model

The `web_search` tool uses a separate model. Configure it with:

```toml
[models]
web_search = "grok-4.20-multi-agent"
```

Or via environment variable:

```bash
export GROK_WEB_SEARCH_MODEL="grok-4.20-multi-agent"
```

If you point web search at a custom model, you also need a `[model.*]` entry so Grok knows how to reach it. Web search requires the Responses API backend:

```toml
[models]
web_search = "my-custom-model"

[model.my-custom-model]
model = "my-custom-model"
api_backend = "responses"    # Required -- web search uses the Responses API
```

---

## Using Custom Models

```bash
# List available models (including custom)
grok models

# Use in the TUI via slash command
/model my-model

# Use in headless mode
grok -p "Hello" -m my-model

# Set as default in config.toml:
[models]
default = "my-model"
```

---

## Enterprise Deployment

A complete config for an enterprise deployment with custom models:

```toml
[cli]
auto_update = false

[auth]
auth_provider_command = "/usr/local/bin/my-company-auth-provider"
auth_provider_label = "Acme Corp"
auth_token_ttl = 3600

[models]
default = "company-grok"

[model.company-grok]
model = "grok-build"
base_url = "https://grok-proxy.acme.com/"
name = "Grok Build Latest (Proxy)"
context_window = 128000

[features]
support_permission = false
telemetry = false
```

---

## Troubleshooting

### Model Not Found

```bash
# List available models
grok models

# Check config.toml for typos in [model.*] sections
```

### Connection Errors

Verify the endpoint is reachable:

```bash
curl -s https://api.example.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Debug Logging

```bash
GROK_LOG_FILE=1 GROK_LOG_FILTER=debug grok
tail -f ~/.grok/logs/tracing.log
```

Look for log entries containing `model` or `sampling` to trace model selection and API calls.

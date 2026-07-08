# Authentication

Grok supports multiple authentication methods to fit different environments -- from interactive browser login to enterprise SSO and headless CI/CD runners.

---

## Browser Login (Default)

On first launch, Grok opens your browser to authenticate with grok.com:

```bash
grok
```

Credentials are stored in `~/.grok/auth.json` and persist across sessions. Tokens expire after 7 days; Grok will prompt you to re-authenticate when needed.

### Re-authenticate

To switch accounts or fix authentication issues:

```bash
grok login
```

Available flags:

| Flag | Description |
|------|-------------|
| `--oauth` | Force Grok OAuth login via auth.x.ai |
| `--device-auth` | Use device code flow (for headless environments) |

---

## API Key

For CI/CD, automation, or environments without browser access, use an API key from [console.x.ai](https://console.x.ai):

```bash
export XAI_API_KEY="xai-..."
grok
```

The API key takes precedence over browser credentials. This is the simplest method for non-interactive environments.

---

## OIDC (Customer SSO)

Authenticate developers via your own Identity Provider (Okta, Azure AD, Auth0) instead of grok.com.

### 1. Register a public client in your IdP

- Grant type: Authorization Code with PKCE
- Redirect URI: `http://127.0.0.1/callback` (loopback; most IdPs treat this as port-agnostic per [RFC 8252](https://tools.ietf.org/html/rfc8252))
- No client secret (PKCE only)

### 2. Configure the CLI

Via config file:

```toml
# ~/.grok/config.toml
[grok_com_config.oidc]
issuer = "https://acme.okta.com"
client_id = "0oa1b2c3d4e5f6g7h8i9"
```

Or via environment variables:

```bash
export GROK_OIDC_ISSUER="https://acme.okta.com"
export GROK_OIDC_CLIENT_ID="0oa1b2c3d4e5f6g7h8i9"
```

Customers typically also override the API endpoint to point at their own proxy:

```bash
export GROK_CLI_CHAT_PROXY_BASE_URL="https://grok-proxy.acme.com/v1"
```

### 3. Run `grok`

The CLI discovers endpoints via `{issuer}/.well-known/openid-configuration`, opens the IdP login page, and stores tokens in `~/.grok/auth.json`. Tokens auto-refresh silently via the stored `refresh_token`.

### Optional fields

| Field | Default | Notes |
|-------|---------|-------|
| `scopes` | `["openid", "profile", "email", "offline_access"]` | `offline_access` enables silent token refresh |
| `audience` | None | Required by some IdPs (e.g., Auth0) |

---

## External Auth Provider

For environments where browser-based login is not possible (sandboxed VMs, CI runners, air-gapped networks), delegate authentication to an external binary or script. This is the recommended approach for enterprise deployments.

### How It Works

```
+--------------+     sh -c     +------------------------+
|     Grok     |-------------->|  your auth binary      |
|              |               |                        |
|  reads       |<-- stdout ----|  prints token          |
|  auth.json   |               |                        |
|              |   (stderr)    |  prints status/URLs    |--> user's terminal
+--------------+               +------------------------+
```

1. Grok runs your command via `sh -c "<command>"`
2. Your binary does whatever auth flow it needs (SSO, device code, cert exchange)
3. **stderr** is displayed directly to the user (use for login URLs, status messages)
4. **stdout** is captured by Grok and saved as the access token
5. Exit 0 = success; exit non-zero = Grok falls through to interactive login

### The stdout / stderr Contract

| Stream | What to print | Who sees it |
|--------|---------------|-------------|
| **stdout** | The token -- nothing else | Grok (parsed and stored in auth.json) |
| **stderr** | Login URLs, status messages, errors | The user (displayed in terminal) |

**Do not print anything to stdout except the token.** No progress messages, no debug output. Grok reads stdout verbatim and tries to parse it as a token.

### stdout Token Format

**Bare string** -- just the raw token:

```
eyJhbGciOiJSUzI1NiIs...
```

**JSON** -- with optional refresh token and expiry:

```json
{"access_token": "eyJhbGciOi...", "refresh_token": "ref-tok", "expires_in": 3600}
```

Use JSON if your tokens expire and you want Grok to automatically re-run the binary before expiry.

### Configuration

Via config file:

```toml
# ~/.grok/config.toml
[auth]
auth_provider_command = "/usr/local/bin/my-auth-provider"
auth_provider_label = "Acme Corp"   # optional -- customizes the TUI login button
auth_token_ttl = 3600               # optional -- token lifetime in seconds
```

Or via environment variables:

```bash
export GROK_AUTH_PROVIDER_COMMAND="/usr/local/bin/my-auth-provider"
export GROK_AUTH_PROVIDER_LABEL="Acme Corp"
export GROK_AUTH_TOKEN_TTL=3600
```

### Token Refresh

When Grok needs to refresh an expired token, it re-runs your binary with `GROK_AUTH_EXPIRED=1` set in the environment. Your binary can use this to take a faster silent-refresh path:

```bash
#!/bin/sh
if [ "$GROK_AUTH_EXPIRED" = "1" ]; then
    echo "Refreshing token..." >&2
    TOKEN=$(my-company-auth --refresh --silent)
else
    echo "Authenticating via Acme Corp SSO..." >&2
    TOKEN=$(my-company-auth --login --interactive)
fi

if [ -z "$TOKEN" ]; then
    echo "Authentication failed" >&2
    exit 1
fi

echo "{\"access_token\": \"$TOKEN\", \"expires_in\": 3600}"
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `GROK_AUTH_PROVIDER_COMMAND` | Path to your auth binary |
| `GROK_AUTH_PROVIDER_LABEL` | Display name on the TUI login screen (e.g., "Acme Corp") |
| `GROK_AUTH_TOKEN_TTL` | Token lifetime in seconds (for bare-string tokens without `expires_in`) |
| `GROK_AUTH_EXPIRED` | Set to `1` by Grok when re-running the binary for token refresh |
| `GROK_AUTH_EARLY_INVALIDATION_SECS` | Seconds before expiry to proactively refresh (default: 300) |

---

## Device Code Flow

For headless environments (SSH sessions, Docker containers, remote VMs) where no browser is available locally:

```bash
grok login --device-auth
```

This prints a URL and code to the terminal. Open the URL on any device, enter the code, and complete authentication. Grok polls until the login is confirmed.

You can also implement device code flow via an [External Auth Provider](#external-auth-provider) for full control over the flow.

---

## Automatic Credential Refresh

Grok automatically refreshes expired credentials:

- **Before expiry:** If your auth provider returned `expires_in` (JSON output) or you set `auth_token_ttl`, Grok re-runs the auth binary ~5 minutes before expiry.
- **On auth error:** If the server returns 401/403, Grok re-runs the binary and retries once.
- **OIDC:** If a `refresh_token` is available, Grok silently refreshes via your IdP without re-opening the browser.

Tune the refresh buffer:

```bash
# Refresh 5 minutes before expiry (default)
export GROK_AUTH_EARLY_INVALIDATION_SECS=300

# Only refresh on 401 (set to 0)
export GROK_AUTH_EARLY_INVALIDATION_SECS=0
```

---

## Hot Reload

Changes to `~/.grok/auth.json` are picked up automatically. If you update credentials externally (e.g., via a script that writes new tokens), Grok will use the new credentials on the next API call without requiring a restart.

---

## Auth Precedence

When multiple auth methods are configured, Grok tries them in this order:

1. **API key** (`XAI_API_KEY`) -- highest priority
2. **OIDC silent refresh** (if a `refresh_token` exists in auth.json)
3. **External auth provider** (`auth_provider_command`)
4. **Browser-based login** -- lowest priority, requires user interaction

During a session, whichever method is active handles all mid-session refreshes exclusively.

---

## Troubleshooting

### Debug logging

Enable debug logging to trace the auth flow:

```bash
GROK_LOG_FILE=1 GROK_LOG_FILTER=debug grok -p "hello"
tail -f ~/.grok/logs/tracing.log
```

### Common log messages

| Log message | What it means |
|-------------|---------------|
| `auth: running external auth provider` | Your binary is being called |
| `auth: external auth provider returned fresh token` | Token was parsed and stored |
| `auth: external auth provider failed` | Binary exited non-zero or stdout was empty |
| `auth: external auth provider timed out after 60s` | Binary did not exit in time and was killed |
| `auth: failed to start external auth provider` | Command could not be spawned (binary not found) |

### Common fixes

- **"Authentication failed"** -- Run `grok login` to clear credentials and re-authenticate.
- **Token expires too quickly** -- Set `auth_token_ttl` or return `expires_in` in your auth provider's JSON output.
- **OIDC redirect fails** -- Ensure your IdP allows loopback redirect URIs (`http://127.0.0.1/callback`).
- **External auth provider not found** -- Check that the `auth_provider_command` path is correct and the binary is executable.

---

Copyright xAI. All rights reserved.

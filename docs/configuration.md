# Configuration

Set environment variables in your MCP client or shell. Restart the server after changing a value.

## Quick reference

| Variable | Default | Description |
|---|---|---|
| [`BROWSER_HEADLESS`](#browser_headless) | `true` | Run without a visible window. Set `false` to watch the browser. |
| [`BROWSER_VIEWPORT_WIDTH`](#browser_viewport_width-browser_viewport_height) | `1280` | Viewport width in pixels. |
| [`BROWSER_VIEWPORT_HEIGHT`](#browser_viewport_width-browser_viewport_height) | `720` | Viewport height in pixels. |
| [`BROWSER_TIMEOUT`](#browser_timeout) | `30000` | Navigation timeout (ms). |
| [`BROWSER_USER_DATA_DIR`](#browser_user_data_dir) | `~/.browsercontrol/user_data` | Browser profile dir (cookies, history, extensions persist here). |
| [`BROWSER_EXTENSION_PATH`](#browser_extension_path) | — | Directory of an unpacked Chromium extension. |
| [`BROWSER_EXECUTABLE_PATH`](#browser_executable_path) | — | Chromium binary to drive, for platforms Playwright ships no build for. |
| [`BROWSER_RECORDINGS_DIR`](#browser_recordings_dir) | `~/.browsercontrol/recordings` | Where to save Playwright traces. |
| [`BROWSER_SNAPSHOTS_DIR`](#browser_snapshots_dir) | `~/.browsercontrol/snapshots` | Where to save PNG + HTML snapshots. |
| [`BROWSER_DOWNLOADS_DIR`](#browser_downloads_dir) | `~/.browsercontrol/downloads` | Where downloads are saved. |
| [`BROWSER_GENERATED_TESTS_DIR`](#browser_generated_tests_dir) | `~/.browsercontrol/generated_tests` | Where `export_test` writes tests. |
| [`BROWSER_CDP_URL`](#browser_cdp_url) | — | Attach to a running Chrome instead of launching one. |
| [`BROWSER_SETTLE_TIMEOUT`](#browser_settle_timeout) | `3000` | Max wait (ms) after each action for the page to settle. |
| [`BROWSER_TRANSPORT`](#browser_transport) | `stdio` | `stdio`, `http`, or `sse`. |
| [`BROWSER_HOST`](#browser_transport) / [`BROWSER_PORT`](#browser_transport) | `127.0.0.1` / `8000` | HTTP bind address. |
| [`BROWSER_ISOLATE_CLIENTS`](#browser_isolate_clients) | `false` | One isolated session per MCP client. |
| [`LOG_LEVEL`](#log_level) | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR`. |

## Setting environment variables

### In MCP client config

Add variables to your server entry. This example uses a client with an `env`
object. See [client setup](getting-started/connect-your-ai.md) for launch options.

```json
{
  "mcpServers": {
    "browsercontrol": {
      "command": "uvx",
      "args": ["browsercontrol"],
      "env": {
        "BROWSER_HEADLESS": "false",
        "BROWSER_VIEWPORT_WIDTH": "1920",
        "BROWSER_VIEWPORT_HEIGHT": "1080",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### In a shell

=== "bash / zsh"

    ```bash
    export BROWSER_HEADLESS=false
    export BROWSER_VIEWPORT_WIDTH=1920
    export BROWSER_VIEWPORT_HEIGHT=1080
    browsercontrol
    ```

=== "fish"

    ```bash
    set -x BROWSER_HEADLESS false
    set -x BROWSER_VIEWPORT_WIDTH 1920
    set -x BROWSER_VIEWPORT_HEIGHT 1080
    browsercontrol
    ```

=== "PowerShell"

    ```powershell
    $env:BROWSER_HEADLESS = "false"
    $env:BROWSER_VIEWPORT_WIDTH = "1920"
    $env:BROWSER_VIEWPORT_HEIGHT = "1080"
    browsercontrol
    ```

## Reference

### `BROWSER_HEADLESS`

Whether to run Chromium without a visible window.

```bash
# Default — fast, no UI, great for servers
BROWSER_HEADLESS=true browsercontrol

# Show the browser window — useful for debugging
BROWSER_HEADLESS=false browsercontrol
```

!!! tip "Headless in CI"
    In CI (no display server), BrowserControl defaults to headless. If you want to *see* the browser, run on a desktop session or use `xvfb-run`:

    ```bash
    xvfb-run browsercontrol
    ```

### `BROWSER_VIEWPORT_WIDTH` / `BROWSER_VIEWPORT_HEIGHT`

Initial viewport size in pixels. Default `1280x720`.

```bash
# Phone-sized for mobile testing
BROWSER_VIEWPORT_WIDTH=375 BROWSER_VIEWPORT_HEIGHT=812 browsercontrol

# Desktop full-HD
BROWSER_VIEWPORT_WIDTH=1920 BROWSER_VIEWPORT_HEIGHT=1080 browsercontrol
```

!!! note "Change at runtime"
    You can also resize at runtime with the [`set_viewport`](tools/devtools.md#set_viewport) tool.

### `BROWSER_TIMEOUT`

Navigation timeout in milliseconds. Default `30000` (30 seconds).

```bash
# Tighter timeout for fast pages
BROWSER_TIMEOUT=10000 browsercontrol

# Looser for slow connections
BROWSER_TIMEOUT=60000 browsercontrol
```

### `BROWSER_USER_DATA_DIR`

Where to store the browser profile (cookies, `localStorage`, history, extensions).

```bash
# Default
BROWSER_USER_DATA_DIR=~/.browsercontrol/user_data

# Shared profile (e.g., across multiple users)
BROWSER_USER_DATA_DIR=/var/lib/browsercontrol/profile browsercontrol
```

!!! info "Persistent sessions"
    BrowserControl reuses the profile across restarts. Sites can still expire your login session.

### `BROWSER_EXTENSION_PATH`

Set this to the directory of an unpacked Chromium extension.

```bash
BROWSER_EXTENSION_PATH=/path/to/unpacked/extension browsercontrol
```

### `BROWSER_EXECUTABLE_PATH`

Which Chrome or Chromium binary to drive. Left unset, BrowserControl tries
Playwright’s cached Chromium first, then Google Chrome. The Chrome fallback uses
a separate profile next to the configured profile, with `-chrome` appended to its
directory name. If neither browser starts, BrowserControl downloads Chromium.
When `BROWSER_EXTENSION_PATH` is set, automatic selection uses Playwright’s
Chromium.

Set it when `playwright install chromium` has no build for your platform and
refuses to install (newer Linux releases hit this), pointing it at a Chrome or
Chromium you already have:

```bash
BROWSER_EXECUTABLE_PATH=/usr/bin/google-chrome browsercontrol
```

When this is set, BrowserControl will **not** try to auto-install Chromium if the
launch fails — a binary you named is yours to fix, and installing over it would
hide the real error.

### `BROWSER_RECORDINGS_DIR`

Where to save Playwright traces. Defaults to a `recordings` directory beside
`BROWSER_USER_DATA_DIR` — so `~/.browsercontrol/recordings` unless you moved the
profile, in which case they follow it.

### `BROWSER_SNAPSHOTS_DIR`

Where to save PNG + HTML + URL snapshots. Defaults to a `snapshots` directory
beside `BROWSER_USER_DATA_DIR`, following the profile the same way.

### `BROWSER_DOWNLOADS_DIR`

Where downloaded files are saved. Defaults to a `downloads` directory beside
`BROWSER_USER_DATA_DIR`. Existing files are never overwritten.

### `BROWSER_GENERATED_TESTS_DIR`

Where [`export_test`](tools/recording.md#export_test) writes Playwright tests.
Defaults to a `generated_tests` directory beside `BROWSER_USER_DATA_DIR`.

### `BROWSER_CDP_URL`

Attach to an already running Chrome over the DevTools Protocol at startup, so the
agent uses that browser's logged-in sessions. The profile, extension, and
executable settings are ignored in this mode. See
[Sessions](tools/sessions.md#connect_to_chrome) for how to start Chrome.

```bash
BROWSER_CDP_URL=http://localhost:9222 browsercontrol
```

### `BROWSER_SETTLE_TIMEOUT`

After every action BrowserControl waits for DOMContentLoaded, in-flight
requests, and DOM mutations to stop, up to this many milliseconds. Lower it for
speed on static sites; raise it for slow single-page apps.

### `BROWSER_TRANSPORT`

`stdio` (default) for clients that launch the server themselves; `http` serves
Streamable HTTP at `http://BROWSER_HOST:BROWSER_PORT/mcp` so several clients
can share one browser; `sse` is the legacy HTTP transport. The same settings are
available as `--transport`, `--host`, and `--port` flags.

!!! warning "No authentication"
    Anyone who can reach the port controls the browser and its logged-in
    sessions. The default host is `127.0.0.1`; the server logs a warning if you
    bind anywhere else.

### `BROWSER_ISOLATE_CLIENTS`

With `true` (or `--isolate-clients`), every MCP client that connects gets its
own isolated browser session on its first tool call, so agents sharing an HTTP
server never see each other's cookies, tabs, or captured traffic.

### `LOG_LEVEL`

Logging verbosity for the MCP server itself. Default `INFO`.

| Level | What you get |
|---|---|
| `DEBUG` | Everything — tool calls, element map sizes, navigation events. |
| `INFO` | Lifecycle events, tool summaries. |
| `WARNING` | Recoverable issues. |
| `ERROR` | Failures. |

```bash
# Verbose for debugging
LOG_LEVEL=DEBUG browsercontrol
```

## See also

- **[Installation](getting-started/installation.md)** — how to install
- **[Connect your AI](getting-started/connect-your-ai.md)** — env var examples in MCP configs
- **[Troubleshooting](troubleshooting.md)** — common issues

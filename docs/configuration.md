# Configuration

All BrowserControl settings are environment variables. Sensible defaults out of the box.

## Quick reference

| Variable | Default | Description |
|---|---|---|
| [`BROWSER_HEADLESS`](#browser_headless) | `true` | Run without a visible window. Set `false` to watch the browser. |
| [`BROWSER_VIEWPORT_WIDTH`](#browser_viewport_width-browser_viewport_height) | `1280` | Viewport width in pixels. |
| [`BROWSER_VIEWPORT_HEIGHT`](#browser_viewport_width-browser_viewport_height) | `720` | Viewport height in pixels. |
| [`BROWSER_TIMEOUT`](#browser_timeout) | `30000` | Navigation timeout (ms). |
| [`BROWSER_USER_DATA_DIR`](#browser_user_data_dir) | `~/.browsercontrol/user_data` | Browser profile dir (cookies, history, extensions persist here). |
| [`BROWSER_EXTENSION_PATH`](#browser_extension_path) | — | Path to a `.crx`/unpacked extension to load at startup. |
| [`BROWSER_EXECUTABLE_PATH`](#browser_executable_path) | — | Chromium binary to drive, for platforms Playwright ships no build for. |
| [`BROWSER_RECORDINGS_DIR`](#browser_recordings_dir) | `~/.browsercontrol/recordings` | Where to save Playwright traces. |
| [`BROWSER_SNAPSHOTS_DIR`](#browser_snapshots_dir) | `~/.browsercontrol/snapshots` | Where to save PNG + HTML snapshots. |
| [`LOG_LEVEL`](#log_level) | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR`. |

## Setting environment variables

### In MCP client config

```json
{
  "mcpServers": {
    "browsercontrol": {
      "command": "browsercontrol",
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
    Because BrowserControl uses `launch_persistent_context`, the profile survives restarts. Log in once, and the session persists forever (until you clear it).

### `BROWSER_EXTENSION_PATH`

Path to a Chrome extension to load at startup. Can be a `.crx` file or an unpacked extension directory.

```bash
BROWSER_EXTENSION_PATH=/path/to/extension.crx browsercontrol
BROWSER_EXTENSION_PATH=/path/to/unpacked/extension browsercontrol
```

### `BROWSER_EXECUTABLE_PATH`

Which Chromium binary to drive. Left unset, Playwright uses the build it manages
itself — which is what you want almost always.

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

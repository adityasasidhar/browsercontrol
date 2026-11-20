---
title: Configuration
description: Every BrowserControl environment variable and command-line flag, with defaults and examples.
---

# Configuration

BrowserControl reads its settings from environment variables once, at startup. Change a value, then restart the server.

## At a glance

| Variable | Default | What it does |
| --- | --- | --- |
| [`BROWSER_HEADLESS`](#browser_headless) | `true` | `false` shows the browser window. |
| [`BROWSER_VIEWPORT_WIDTH`](#viewport) | `1280` | Viewport width in pixels. |
| [`BROWSER_VIEWPORT_HEIGHT`](#viewport) | `720` | Viewport height in pixels. |
| [`BROWSER_TIMEOUT`](#browser_timeout) | `30000` | Navigation timeout, in ms. |
| [`BROWSER_SETTLE_TIMEOUT`](#browser_settle_timeout) | `3000` | How long to wait for the page to settle after each action, in ms. |
| [`BROWSER_USER_DATA_DIR`](#browser_user_data_dir) | `~/.browsercontrol/user_data` | The persistent browser profile. |
| [`BROWSER_EXECUTABLE_PATH`](#browser_executable_path) | — | A specific Chrome or Chromium binary. |
| [`BROWSER_EXTENSION_PATH`](#browser_extension_path) | — | An unpacked extension to load. |
| [`BROWSER_CDP_URL`](#browser_cdp_url) | — | Attach to a running Chrome instead of launching one. |
| [`BROWSER_RECORDINGS_DIR`](#paths) | beside the profile | Traces and HAR files. |
| [`BROWSER_SNAPSHOTS_DIR`](#paths) | beside the profile | Snapshots. |
| [`BROWSER_DOWNLOADS_DIR`](#paths) | beside the profile | Downloads. |
| [`BROWSER_GENERATED_TESTS_DIR`](#paths) | beside the profile | Tests written by `export_test`. |
| [`BROWSER_TRANSPORT`](#transport) | `stdio` | `stdio`, `http`, or `sse`. |
| [`BROWSER_HOST`](#transport) | `127.0.0.1` | HTTP bind address. |
| [`BROWSER_PORT`](#transport) | `8000` | HTTP port. |
| [`BROWSER_ISOLATE_CLIENTS`](#browser_isolate_clients) | `false` | One isolated session per MCP client. |
| [`LOG_LEVEL`](#log_level) | `INFO` | `DEBUG`, `INFO`, `WARNING`, or `ERROR`. |

## Setting them

In an MCP client, add an `env` object to the server entry:

```json
{
  "mcpServers": {
    "browsercontrol": {
      "command": "uvx",
      "args": ["browsercontrol"],
      "env": {
        "BROWSER_HEADLESS": "false",
        "BROWSER_VIEWPORT_WIDTH": "1440",
        "BROWSER_VIEWPORT_HEIGHT": "900"
      }
    }
  }
}
```

In a shell:

::: code-group

```bash [bash / zsh]
BROWSER_HEADLESS=false browsercontrol
```

```fish [fish]
env BROWSER_HEADLESS=false browsercontrol
```

```powershell [PowerShell]
$env:BROWSER_HEADLESS = "false"; browsercontrol
```

:::

## Command-line flags

```text
browsercontrol [--transport {stdio,http,sse}] [--host HOST] [--port PORT] [--isolate-clients]
```

Flags override the matching environment variables. Run `browsercontrol --help` for the list.

## Browser

### `BROWSER_HEADLESS` {#browser_headless}

`true` by default: no window, which suits servers and CI. Set `false` to watch the agent work. Without a display (a server, CI), a visible browser needs a virtual one such as `xvfb-run browsercontrol`.

### `BROWSER_VIEWPORT_WIDTH` and `BROWSER_VIEWPORT_HEIGHT` {#viewport}

The starting viewport, `1280` × `720` by default. Agents can change it while running with [`set_viewport`](/reference/devtools#set_viewport) or [`emulate_device`](/reference/emulation#emulate_device).

### `BROWSER_TIMEOUT` {#browser_timeout}

How long a navigation may take before it fails, in milliseconds. Default `30000`.

### `BROWSER_SETTLE_TIMEOUT` {#browser_settle_timeout}

The budget, in milliseconds, for [settling](/concepts/settling) after each action: load, network quiet, DOM quiet. Default `3000`. Lower it on static sites for speed; raise it for slow single-page apps. Running out of budget never fails an action.

### `BROWSER_USER_DATA_DIR` {#browser_user_data_dir}

The persistent profile: cookies, `localStorage`, history, extensions. Default `~/.browsercontrol/user_data`. Only one running server can use a profile, so give each server its own.

### `BROWSER_EXECUTABLE_PATH` {#browser_executable_path}

A Chrome or Chromium binary to drive. Unset, BrowserControl tries Playwright's Chromium, then an installed Google Chrome (with a separate profile, the profile directory with `-chrome` appended), then downloads Chromium.

Set it when Playwright has no Chromium build for your platform:

```bash
BROWSER_EXECUTABLE_PATH=/usr/bin/google-chrome browsercontrol
```

With this set, BrowserControl won't download Chromium if the launch fails. The binary you named is the one to fix.

### `BROWSER_EXTENSION_PATH` {#browser_extension_path}

The directory of an unpacked Chromium extension to load. Automatic browser selection then uses Playwright's Chromium.

### `BROWSER_CDP_URL` {#browser_cdp_url}

Attach to a Chrome already running with remote debugging, instead of launching a browser, so the agent uses that Chrome's signed-in sites. The profile, executable, and extension settings are ignored in this mode. See [Use your own Chrome](/recipes/your-chrome).

```bash
BROWSER_CDP_URL=http://localhost:9222 browsercontrol
```

## Files {#paths}

| Variable | Default | Holds |
| --- | --- | --- |
| `BROWSER_RECORDINGS_DIR` | `~/.browsercontrol/recordings` | Playwright traces and HAR exports |
| `BROWSER_SNAPSHOTS_DIR` | `~/.browsercontrol/snapshots` | `take_snapshot` PNG and HTML |
| `BROWSER_DOWNLOADS_DIR` | `~/.browsercontrol/downloads` | Downloads (never overwritten) |
| `BROWSER_GENERATED_TESTS_DIR` | `~/.browsercontrol/generated_tests` | `export_test` output |

Each default sits beside the profile directory, so moving `BROWSER_USER_DATA_DIR` moves them too unless you set them yourself.

## Server

### `BROWSER_TRANSPORT`, `BROWSER_HOST`, `BROWSER_PORT` {#transport}

`stdio` (the default) is for clients that launch the server themselves. `http` serves Streamable HTTP at `http://BROWSER_HOST:BROWSER_PORT/mcp` so several clients can share one browser; `sse` is the older HTTP transport. The flags `--transport`, `--host`, and `--port` do the same. See [Share over HTTP](/guide/http).

::: danger No authentication
Anyone who can reach the port controls the browser and its signed-in sessions. The default host is `127.0.0.1`, and the server warns if you bind anywhere else.
:::

### `BROWSER_ISOLATE_CLIENTS` {#browser_isolate_clients}

`true` (or `--isolate-clients`) gives every MCP client its own isolated session on its first tool call, so agents sharing a server never see each other's cookies, tabs, or traffic.

### `LOG_LEVEL` {#log_level}

How much the server logs: `DEBUG`, `INFO` (default), `WARNING`, or `ERROR`. Logs go to stderr, which most clients show in their MCP log. `DEBUG` is the level to attach to a bug report.

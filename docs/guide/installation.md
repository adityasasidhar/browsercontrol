---
title: Installation
description: Requirements and every way to install BrowserControl, plus how it picks a browser on first launch.
---

# Installation

BrowserControl needs Python 3.11.5 or newer and runs on Linux, macOS, and Windows. Allow about 300 MB if it has to download Chromium.

## Choose how to run it

Most people don't install anything: their MCP client runs `uvx browsercontrol`, which fetches the package on first use. Install it yourself when you want a fixed version or a command on your `PATH`.

::: code-group

```bash [uvx]
# Nothing to install. Use this as your client's command:
uvx browsercontrol
```

```bash [uv]
uv tool install browsercontrol
# If uv warns that its tool directory is not on PATH:
uv tool update-shell
```

```bash [pip]
python -m pip install browsercontrol
```

```bash [pipx]
pipx install browsercontrol
```

```bash [source]
git clone https://github.com/adityasasidhar/browsercontrol
cd browsercontrol
uv sync
# Client command: uv --directory /absolute/path/to/browsercontrol run browsercontrol
```

:::

If you install into a virtual environment, give your MCP client the full path to that environment's `browsercontrol` executable.

Check the install:

```bash
browsercontrol --help
```

## How it picks a browser

On first launch BrowserControl looks for a browser in this order:

1. The binary in [`BROWSER_EXECUTABLE_PATH`](/reference/configuration#browser_executable_path), if you set one.
2. Playwright's cached Chromium.
3. An installed Google Chrome, run with its own separate profile so your everyday Chrome data is never touched.
4. If none of those start, it downloads Chromium.

With [`BROWSER_EXTENSION_PATH`](/reference/configuration#browser_extension_path) set, automatic selection uses Playwright's Chromium, since extensions need it.

To download Chromium ahead of time, run this in an environment that has Playwright (prefix with `uv run` inside a uv project):

```bash
python -m playwright install chromium
```

::: details Linux needs extra libraries?
Chromium depends on system libraries that minimal Linux images often lack. Install them with:

```bash
python -m playwright install chromium --with-deps
```

If Playwright has no Chromium build for your distribution, point `BROWSER_EXECUTABLE_PATH` at a Chrome or Chromium you already have. See [Troubleshooting](/help/troubleshooting#chromium-won-t-launch).
:::

BrowserControl is listed in the official [MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.adityasasidhar/browsercontrol) as `io.github.adityasasidhar/browsercontrol`.

## Next step

[Connect your MCP client →](/guide/clients)

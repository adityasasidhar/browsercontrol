# Install BrowserControl

Use Python 3.11 or newer on Linux, macOS, or Windows. Allow roughly 300 MB
if BrowserControl needs to download Chromium.

## Choose how to run the server

=== "uv"

    With [uv installed](https://docs.astral.sh/uv/getting-started/installation/),
    install BrowserControl as a standalone command:

    ```bash
    uv tool install browsercontrol
    ```

    If uv reports that its tools directory is missing from `PATH`, run
    `uv tool update-shell`, then open a new terminal.

=== "pip"

    ```bash
    python -m pip install browsercontrol
    ```

    If you install into a virtual environment, use the full path to its
    `browsercontrol` executable in your MCP client.

=== "pipx"

    ```bash
    pipx install browsercontrol
    ```

=== "From source"

    ```bash
    git clone https://github.com/adityasasidhar/browsercontrol
    cd browsercontrol
    uv sync
    ```

    Tell your client to run `uv --directory /path/to/browsercontrol run browsercontrol`.
    Replace the path with the absolute path to your checkout.

You can also [configure your client to run `uvx browsercontrol`](connect-your-ai.md#uvx-pipx-no-install-needed).
It downloads the package when needed.

## Browser selection at startup

BrowserControl first looks for Playwright’s cached Chromium, then checks for
Google Chrome. Chrome uses a separate profile to protect its data. If neither
browser starts, BrowserControl downloads Chromium. An explicit
[`BROWSER_EXECUTABLE_PATH`](../configuration.md#browser_executable_path) takes
precedence. With an extension configured, automatic selection uses Playwright’s
Chromium.

To preinstall Chromium or retry a download, run this in a Python environment with
Playwright installed. In a uv project, prefix the command with `uv run`.

```bash
python -m playwright install chromium
```

Linux may need additional system libraries. See [browser startup troubleshooting](../troubleshooting.md#chromium-executable-doesnt-exist).

[Connect your MCP client](connect-your-ai.md){ .md-button .md-button--primary }

# Installation

Installing BrowserControl also installs the Playwright Python package. BrowserControl selects the browser binary when the MCP server starts.

## Requirements

- **Python 3.11+**
- **Operating system:** Linux, macOS, or Windows
- **Disk space:** ~300 MB once Chromium is downloaded
- **Linux:** Chromium may require additional system libraries.

## Install with your tool of choice

=== "uv (recommended)"

    ```bash
    uv add browsercontrol
    ```

    If you don't have `uv` yet:

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "pip"

    ```bash
    pip install browsercontrol
    ```

=== "pipx (isolated CLI)"

    ```bash
    pipx install browsercontrol
    ```

=== "From source"

    ```bash
    git clone https://github.com/adityasasidhar/browsercontrol
    cd browsercontrol
    uv sync
    ```

!!! info "Browser selection at startup"
    BrowserControl tries Playwright's cached Chromium first, then Google Chrome if installed in a standard location. Chrome uses its own profile, a sibling of the configured one with a `-chrome` suffix, because sharing one profile between Chrome and Chromium builds can corrupt it. If neither starts (missing, or Chrome fails to launch), it downloads Chromium into Playwright's browser cache and retries. A configured `BROWSER_EXECUTABLE_PATH` takes precedence. When `BROWSER_EXTENSION_PATH` is set, automatic browser selection uses Playwright's Chromium for extension support.

    To preinstall Chromium or retry a failed download, run this in the environment where BrowserControl is installed. In a uv project, prefix the command with `uv run`.

    ```bash
    python -m playwright install chromium
    ```

    On Linux you may also want system deps:

    ```bash
    python -m playwright install chromium --with-deps
    ```

## Verify the install

```bash
# Show the CLI help
browsercontrol --help

# Run the server (will block waiting for an MCP client)
browsercontrol
```

If you see a `BrowserControl MCP server initialized with all tools` log line, you're ready to [connect your AI](connect-your-ai.md).

## Optional: install for a specific Python

=== "pyenv"

    ```bash
    pyenv install 3.12
    pyenv shell 3.12
    pip install browsercontrol
    ```

=== "conda"

    ```bash
    conda create -n browsercontrol python=3.12
    conda activate browsercontrol
    pip install browsercontrol
    ```

## Next

- **[Connect it to your AI](connect-your-ai.md)** — drop-in configs for every major client.
- **[Run your first session](first-session.md)** — a guided walkthrough.

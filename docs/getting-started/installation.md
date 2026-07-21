# Installation

BrowserControl is a single Python package with one optional browser binary download on first run.

## Requirements

- **Python 3.11+**
- **Operating system:** Linux, macOS, or Windows
- **Disk space:** ~300 MB once Chromium is downloaded
- **No other system dependencies** — Chromium bundles its own runtime

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

!!! info "Chromium auto-install"
    On first run, BrowserControl installs a private Chromium build into `~/.cache/ms-playwright/`. If the auto-install fails for any reason, run it manually:

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

# Development

How to set up BrowserControl for local development, run tests, lint, and contribute.

## Quick start

```bash
git clone https://github.com/adityasasidhar/browsercontrol
cd browsercontrol

# Install deps + Playwright + Chromium
uv sync
uv run playwright install chromium --with-deps

# Run the server in dev mode (FastMCP inspector UI)
uv run fastmcp dev browsercontrol/server.py

# Run tests
uv run pytest

# Lint, format, security checks
uv run ruff check .
uv run ruff format .
uv run pre-commit run --all-files
```

## Project layout

```
browsercontrol/
├── __init__.py              # Public exports (`mcp`)
├── __main__.py              # `python -m browsercontrol` entry point
├── server.py                # FastMCP server definition + tool registration
├── browser.py               # BrowserManager — Playwright lifecycle + SoM renderer
├── config.py                # Env-var configuration
└── tools/
    ├── navigation.py        # navigate_to, go_back, go_forward, refresh, scroll
    ├── interaction.py       # click, click_at, type_text, press_key, hover, scroll_to_element, wait
    ├── forms.py             # select_option, check_checkbox, upload_file
    ├── content.py           # get_page_content, get_text, get_page_info, run_javascript, screenshot
    ├── devtools.py          # console, network, errors, inspect, perf, cookies, viewport
    ├── recording.py         # start/stop_recording, take_snapshot, list_recordings
    └── tabs.py              # create_tab, switch_tab, close_tab, list_tabs

tests/                       # ~1,700 lines of pytest tests (mocked Playwright)
├── conftest.py              # Shared fixtures: mock_page, mock_context, mock_browser_manager…
└── test_*.py                # One file per module
```

## Running tests

```bash
# All tests
uv run pytest

# Single file
uv run pytest tests/test_interaction.py

# Single test
uv run pytest tests/test_interaction.py::test_click

# Verbose
uv run pytest -v

# With coverage
uv run pytest --cov=browsercontrol --cov-report=term-missing
```

The tests use mocked Playwright objects (see `tests/conftest.py`) so they run fast and don't need a real browser.

## Code style

- **Ruff** for linting and formatting (configured in `pyproject.toml`).
- **mypy --strict** for type checking.
- **Pre-commit** runs ruff, mypy, and other checks on every commit.

```bash
# Run everything
uv run pre-commit run --all-files

# Just ruff
uv run ruff check .
uv run ruff format .

# Just mypy
uv run mypy browsercontrol
```

CI runs the full suite on **Ubuntu, Windows, and macOS** with `ruff`, `mypy --strict`, `bandit`, and `pytest`.

## Adding a new tool

1. **Pick the right module.** Most tools belong in an existing category (`interaction.py`, `devtools.py`, etc.). If your tool is genuinely new, add a new file under `browsercontrol/tools/`.
2. **Use the `@mcp.tool()` decorator.** The signature is auto-exposed as the MCP tool signature.
3. **Return `(text, Image)`** if the tool changes the page (so the model gets a fresh screenshot). Return `str` for read-only tools.
4. **Use `browser.ensure_started()`** at the top of the tool body.
5. **Add a docstring** with `Args:` and `Returns:` — these become the tool's description.
6. **Add tests** in `tests/test_<module>.py`.
7. **Update the docs.** Add the new tool to the relevant `docs/tools/*.md` page.

Example skeleton:

```python
@mcp.tool()
async def my_new_tool(element_id: int) -> tuple[str, Image]:
    """
    One-line summary of what the tool does.

    Args:
        element_id: The number label shown on the element in the screenshot

    Returns:
        Description of the return value
    """
    try:
        await browser.ensure_started()
        elem_map = get_element_map()

        if element_id not in elem_map:
            image, summary = await _get_screenshot_with_summary()
            return f"Error: Element {element_id} not found.\n\n{summary}", image

        # ... your logic ...

        image, summary = await _get_screenshot_with_summary()
        return f"Did the thing to element {element_id}\n\n{summary}", image

    except Exception as e:
        logger.error(f"my_new_tool failed: {e}")
        try:
            image, summary = await _get_screenshot_with_summary()
            return f"Error: {e}\n\n{summary}", image
        except Exception:
            raise RuntimeError(f"my_new_tool failed: {e}")
```

## Building the docs

The docs site uses **MkDocs Material**, installed via the `docs` extra.

### One-time setup

Make sure your project's virtual environment has MkDocs Material installed:

```bash
uv sync --extra docs
```

`uv sync` (run as part of normal setup per [CONTRIBUTING.md](https://github.com/adityasasidhar/browsercontrol/blob/main/CONTRIBUTING.md)) already covers this — `--extra docs` is only required if you've previously synced without it.

### Preview locally

```bash
uv run mkdocs serve
```

Then open <http://localhost:8000>.

!!! warning "Why `uv run`?"
    Do **not** run a bare `mkdocs serve`. On many systems a stray `/usr/bin/mkdocs` (Python 3.x with no Material theme) takes precedence over the project venv and fails with `cannot find module 'material.extensions.emoji'`. `uv run` always resolves `mkdocs` from `.venv/bin/`.

### Build the static site (CI does this)

```bash
uv run mkdocs build --strict
```

The output goes to `site/` (gitignored).

## Good first contributions

Looking for something to work on? Start with one of these:

- [ ] Firefox / WebKit support
- [ ] DOM diffing (detect changes between snapshots)
- [ ] Accessibility audit tools
- [ ] Mobile emulation presets (iPhone, Pixel, iPad)
- [ ] Cookie import/export (Netscape format)
- [ ] `--record-video` MP4 output (in addition to traces)

## See also

- **[Architecture](concepts/architecture.md)** — how the components fit together
- **[Set of Marks](concepts/set-of-marks.md)** — the technique this is built on
- **[CONTRIBUTING.md](https://github.com/adityasasidhar/browsercontrol/blob/main/CONTRIBUTING.md)** — contribution workflow
- **[CODE_QUALITY.md](https://github.com/adityasasidhar/browsercontrol/blob/main/CODE_QUALITY.md)** — toolchain conventions

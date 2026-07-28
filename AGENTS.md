# Repository Guidelines

## Project Structure & Module Organization

- `browsercontrol/` contains the Python package. `server.py` composes the FastMCP server and registers tool groups; `browser.py` owns the Playwright browser lifecycle and Set-of-Marks state; `config.py` reads environment configuration.
- `browsercontrol/tools/` groups MCP tools by capability (`navigation.py`, `interaction.py`, `forms.py`, `content.py`, `devtools.py`, `recording.py`, and `tabs.py`).
- `tests/` contains pytest tests and shared mocked Playwright fixtures in `conftest.py`; keep module tests in matching `test_<module>.py` files.
- `docs/` is the MkDocs Material documentation site; images and other static assets live in `assets/` and `docs/assets/`.

## Build, Test, and Development Commands

Use Python 3.11+ and `uv` for all project commands:

```bash
uv sync
uv run playwright install chromium
uv run fastmcp dev browsercontrol/server.py
uv run pytest tests/test_navigation.py
uv run pytest
uv run mkdocs build --strict
```

The focused pytest command is useful while iterating; the full suite uses mocks and normally does not launch Chromium. Run the development server through FastMCP's inspector UI.

## Coding Style & Naming Conventions

Use four-space Python indentation, double quotes, and a 100-character Ruff target. Prefer explicit type annotations: `mypy` runs in strict mode. Name modules and functions in `snake_case`, classes in `PascalCase`, and tests `test_<behavior>`. Keep tool docstrings actionable because FastMCP exposes them to clients.

Before submitting code, run:

```bash
uv run pre-commit run --all-files
uv run ruff check .
uv run ruff format --check .
uv run mypy browsercontrol/
uv run bandit -c pyproject.toml -r . --exclude ./tests,./.venv
```

## Testing & Tool Changes

Cover both success and graceful-error paths. Tool tests should register against a throwaway `FastMCP` instance and patch the tool module's imported `browser`. New browser-changing tools should call `await browser.ensure_started()` and return a fresh annotated screenshot with an element summary. Element IDs are valid only for the latest screenshot.

Three things the tooling will not catch for you:

- **Register a tool, then update the server `instructions` string.** The prompt in `browsercontrol/server.py` is hand-maintained and is the only description MCP clients receive. A tool missing from it is invisible to agents even though tests and CI pass.
- **`_get_screenshot_with_summary()` is duplicated verbatim** in `tools/forms.py`, `tools/navigation.py`, `tools/content.py`, `tools/devtools.py`, and `tools/interaction.py` (`tools/tabs.py` imports the `content.py` copy). Changing the summary format means editing every copy, or tools will silently return differently-shaped summaries.
- **`config.py` calls `Config.from_env()` at import time.** Changing a `BROWSER_*` variable has no effect on a running server; restart it.

## Commits & Pull Requests

Follow Conventional Commits, such as `feat(forms): add date picker support`, `fix: retry localhost navigation`, or `docs: clarify setup`. Keep each commit focused. PRs should explain the user-visible change, link relevant issues, include tests and documentation updates when interfaces change, and attach screenshots for visual or docs-site changes. Do not commit credentials; use the documented environment variables for local configuration (they are read once at import, so a running server needs a restart to pick them up).

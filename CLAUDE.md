# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

BrowserControl is an MCP (Model Context Protocol) server that gives AI agents
vision-first browser automation via Playwright. Its defining idea is **Set of
Marks (SoM)**: every action returns an annotated screenshot where interactive
elements are overlaid with numbered red boxes, so the agent acts by referring to
an element's number (`click(7)`) instead of CSS selectors or XPath.

## Commands

This project uses `uv` for all dependency and task management.

```bash
uv sync                                    # Install deps (use --all-extras in CI to include dev group)
uv run playwright install chromium         # One-time: install the browser engine

uv run pytest                              # Run all tests
uv run pytest tests/test_navigation.py     # Run a single test file
uv run pytest tests/test_navigation.py::TestScroll::test_scroll_down_medium   # Single test
uv run pytest --cov=browsercontrol         # With coverage

uv run ruff check .                        # Lint
uv run ruff check . --fix                  # Lint + autofix
uv run ruff format .                       # Format (line length 100, double quotes)
uv run mypy browsercontrol/                # Type-check (strict mode)
uv run bandit -c pyproject.toml -r . --exclude ./tests,./.venv   # Security scan
uv run pre-commit run --all-files          # Run every hook (mirrors the CI lint job)

uv run fastmcp dev browsercontrol/server.py   # Run the server in dev mode with inspector
browsercontrol                                # Run the installed server (also: python -m browsercontrol)
```

CI (`.github/workflows/ci.yml`) gates on the lint job first, then runs tests on
Linux/Windows/macOS plus bandit and mypy. Run `ruff check`, `ruff format`, and
`pytest` locally before pushing.

## Architecture

The flow is: agent calls an MCP tool → tool drives the Playwright page → a fresh
annotated screenshot + element map is captured → both are returned to the agent.

**`browser.py` — the heart of the system.** Exposes a single module-global
`browser = BrowserManager()` instance and a module-global `element_map` dict.
Key behaviors to understand before touching anything:

- `screenshot_with_som()` is called at the end of nearly every tool. It takes a
  screenshot, runs `get_interactive_elements()` (injected JS that collects
  visible, on-screen interactive elements and their bounding boxes), draws the
  numbered boxes, and **overwrites the global `element_map`** with 1-indexed IDs.
- **Element IDs are ephemeral.** They are only valid against the most recent
  screenshot. Any navigation, click, scroll, or screenshot regenerates the map
  and renumbers everything. Tools look up the target via `get_element_map()` and
  return an error listing valid IDs when the ID is missing.
- The browser uses `launch_persistent_context` against a profile directory
  (`~/.browsercontrol/user_data` by default), so cookies, localStorage, and login
  state persist across server restarts. Launch args include localhost proxy
  bypass to avoid `ERR_CONNECTION_REFUSED`.
- DevTools data (console logs, network requests, page errors) is captured by
  event listeners attached in `_setup_page_listeners`, auto-wired to every new
  page/popup, and stored in capped in-memory ring buffers on the manager.

**`server.py` — composition root.** Creates the `FastMCP` instance, attaches a
`lifespan` context manager that starts/stops the browser, and calls each
`register_*_tools(mcp)`. The server-level `instructions` string is the prompt the
agent sees describing available tools — keep it in sync when adding tools.

**`tools/` — one module per category** (navigation, interaction, forms, content,
devtools, recording, tabs). Each exports a single `register_<category>_tools(mcp)`
function that defines inner `async` functions decorated with `@mcp.tool()`.
Conventions every tool follows:

- Signature returns `tuple[str, Image]`: a human-readable status string plus the
  annotated screenshot.
- Starts with `await browser.ensure_started()` (lazily boots the browser if the
  lifespan hasn't, e.g. in some test paths).
- Ends by building the result via a local `_get_screenshot_with_summary()`
  helper. **This helper is duplicated verbatim in several tool modules** — if you
  change the summary format, update every copy.

**`config.py`** — a `Config` dataclass loaded once at import via
`Config.from_env()` into a global `config`. All settings come from `BROWSER_*`
and `LOG_LEVEL` env vars (see README for the full table). Because it is read at
import time, env changes require a server restart.

## Testing conventions

Tests **do not launch a real browser** — everything is mocked. The pattern:

- `tests/conftest.py` provides `mock_browser_manager` (a fully stubbed
  `BrowserManager`), `mock_page`, `mock_context`, and `sample_element_map`.
- A test registers the tools onto a throwaway `FastMCP("test")`, then patches the
  module-level `browser` symbol **in that specific tool module** (e.g.
  `patch("browsercontrol.tools.navigation.browser", mock_browser_manager)`) —
  because each tool module does `from browsercontrol.browser import browser`, it
  holds its own reference that must be patched independently.
- The tool callable is reached by name and then called directly:
  `tool = await mcp_server.get_tool("navigate_to")` then `await tool.fn(...)`.
- `asyncio_mode = "auto"` is set, so `async def test_*` runs without an explicit
  marker (though existing tests also add `@pytest.mark.asyncio`).

When adding a tool, add a test covering both the happy path and graceful error
handling, following the existing per-module test files.

## Conventions

- Python 3.11+. Type hints are required and checked by mypy in **strict** mode
  (`disallow_untyped_defs`, etc.) — annotate fully.
- Commits follow Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`).
- Pre-commit hooks (ruff, prettier for md/yaml/json, bandit) run on commit;
  `git commit --no-verify` bypasses them but CI will still enforce them.

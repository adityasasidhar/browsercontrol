# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

BrowserControl is an MCP (Model Context Protocol) server that gives AI agents
vision-first browser automation via Playwright. Its defining idea is **Set of
Marks (SoM)**: every action returns an annotated screenshot where interactive
elements are overlaid with numbered red boxes, so the agent acts by referring to
an element's number (`click(7)`) instead of CSS selectors or XPath.

## Commands

This project uses `uv` for all dependency and task management. `make help` lists shortcuts
(`make check` = lint + mypy + pytest).

```bash
uv sync                                    # Install runtime + dev deps (add `--extra docs` for mkdocs)
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
uv run --extra docs mkdocs build --strict  # Build the docs site in docs/ (gated in docs.yml)

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
`browser = BrowserManager()` instance. Key behaviors to understand before
touching anything:

- `screenshot_with_som()` is called at the end of nearly every tool. It takes a
  screenshot, runs `get_interactive_elements()`, draws the numbered boxes, and
  **replaces the active tab's element map** with 1-indexed IDs. Maps are kept
  per tab (`_element_maps`), so IDs never resolve against another tab.
- **Element IDs are ephemeral.** They are only valid against the most recent
  screenshot. Any navigation, click, scroll, or screenshot regenerates the map
  and renumbers everything.
- **Tools act through `await browser.resolve_element(id)`**, which returns a
  Playwright `Locator` and raises `ElementNotFoundError` / `StaleElementError`
  (both `ElementError`). Tools catch `ElementError` and return
  `element_error_result(browser, e)` from `tools/_summary.py`. Never act at an
  element's stored coordinates (`elementFromPoint`, `mouse.click`): that hits
  shadow hosts, `<iframe>` elements, and overlays instead of the target.

**`elements.py` — detection and resolution.** `collect_elements()` runs injected
JS in **every frame** (`page.frames`, so cross-origin iframes too), recursing into
open shadow roots. It keeps visible, unobscured elements (hit-tested; matched by
selector or by a non-inherited `cursor: pointer`), flags disabled ones, and tags
each with `data-bc-id`. `locate()` finds the element again by that tag through a
frame-scoped locator and refuses it as stale if it is gone or moved. The moved
check compares frame-local boxes on purpose: Playwright's `bounding_box()` is off
by the iframe border for elements inside cross-origin frames.

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
agent sees describing available tools. It is hand-maintained; update it whenever
you add, rename, or remove a tool or change its parameters.
`tests/test_server.py` fails if the `- name(params)` lines drift from the
registered tools.

**`tools/` — one module per category** (navigation, interaction, forms, content,
devtools, recording, tabs). Each exports a single `register_<category>_tools(mcp)`
function that defines inner `async` functions decorated with `@mcp.tool()`.
Conventions every tool follows:

- Signature returns `tuple[str, Image]`: a human-readable status string plus the
  annotated screenshot.
- Starts with `await browser.ensure_started()` (lazily boots the browser if the
  lifespan hasn't, e.g. in some test paths).
- Ends by building the result via `get_screenshot_with_summary(browser)` from
  `tools/_summary.py`. It takes the manager as an argument on purpose: passing
  the module's own `browser` keeps the per-module test patching working.

**`config.py`** — a `Config` dataclass loaded once at import via
`Config.from_env()` into a global `config`. All settings come from `BROWSER_*`
and `LOG_LEVEL` env vars (see README for the full table). Because it is read at
import time, env changes require a server restart.

## Testing conventions

Almost all tests **do not launch a real browser** — everything is mocked. The
exception is `tests/test_som_real_browser.py` (marker `browser`), which drives a
real headless Chromium or installed Chrome against fixture pages served on two
local origins, and skips when no browser is available. Run it after any change to
`elements.py`: mocks cannot tell whether an ID reaches the right element. The
mocked pattern:

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
- Commits follow Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`) and are signed off
  (`git commit -s`, DCO enforced in CI; PR titles are checked too). PRs explain the
  user-visible change, link related issues, include tests and docs when interfaces change, and
  attach screenshots for visual or docs-site changes.
- Do not commit credentials; use the documented `BROWSER_*` environment variables for local
  configuration.
- Tools must build results via the shared `get_screenshot_with_summary` helper;
  `tests/test_element_summary.py` fails if a tool module defines its own copy.
- Keep tool docstrings actionable: FastMCP exposes them to clients.
- Pre-commit hooks (ruff lint + format, bandit, and the standard
  whitespace/YAML/TOML/JSON file checks) run on commit;
  `git commit --no-verify` bypasses them but CI will still enforce them.

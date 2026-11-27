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
uv sync                                    # Install runtime + dev deps
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
uv run python scripts/gen_tools_json.py    # Regenerate docs/public/tools.json after changing a tool
(cd docs && npm ci && npm run build)       # Build the VitePress docs site (gated in docs.yml)

uv run fastmcp dev inspector browsercontrol/server.py   # Run the server with the MCP Inspector
browsercontrol                                # Run the installed server (also: python -m browsercontrol)
browsercontrol --transport http --port 8000   # Streamable HTTP at /mcp (add --isolate-clients)
```

CI (`.github/workflows/ci.yml`) gates on the lint job first, then runs tests
(Python 3.11 and 3.14 on Linux/Windows/macOS, 3.12 and 3.13 on Linux) plus
bandit and mypy. Keep that matrix in step with `requires-python`. Run `ruff check`, `ruff format`, and
`pytest` locally before pushing.

## Architecture

The flow is: agent calls an MCP tool → tool drives the Playwright page → a fresh
annotated screenshot + element map is captured → both are returned to the agent.

**`browser.py` — the heart of the system.** Exposes a single module-global
`browser = BrowserManager()` instance. Key behaviors to understand before
touching anything:

- **Everything page-related goes through the current session.** The manager
  holds `Session` objects (`session.py`): `"default"` (the persistent profile, or
  the Chrome attached over CDP) plus isolated contexts from `create_session`.
  `browser.session` resolves the session the calling MCP client is bound to via
  the `current_client` contextvar, which `SessionBindingMiddleware`
  (`resources.py`) sets per tool call. The key comes from `_client_key`, never
  plain `ctx.session_id`: on the session-less MCP 2026-07-28 protocol (fastmcp
  4's default) `session_id` is new on every request. The key is the named
  `BROWSER_AUTH_TOKENS` token, else the legacy session id, else `"process"` on
  stdio/in-memory; session-less HTTP clients with no named token share `""`.
  `_context`, `_page`, `_console_logs`,
  `_network_requests`, `_page_errors`, and `_request_map` are properties onto
  that session (tests assign them directly). Code that runs outside a tool call
  (event listeners) must capture its `Session` explicitly, never read
  `browser.session`.
- Launch vs attach: `start()` uses `connect_over_cdp` when `BROWSER_CDP_URL` (or
  `connect_over_cdp()`) set a URL, else `launch_persistent_context`. In CDP mode
  the default context is the user's own browser: `stop()` only disconnects, and
  the agent gets a new tab instead of taking over an existing one.
- **Tools call `await browser.settle()` after acting**, not
  `wait_for_load_state`. It waits for DOMContentLoaded, then in-flight requests
  (`network_quiet` over the session's `request_map`), then DOM mutations, all
  bounded by `BROWSER_SETTLE_TIMEOUT`.

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
- Captured data lives on the `Session`, filled by `attach_page_listeners` in
  `session.py` (auto-wired to every new page/popup of that session's context):
  console, page errors, network (with headers, POST data, and the live
  `Response` kept under `_response` so bodies are read on demand), JS dialogs
  (answered per `session.dialog_policy`), and downloads (saved to
  `BROWSER_DOWNLOADS_DIR`). Dialogs and downloads push `session.notices`, which
  `get_screenshot_with_summary` drains into `Notice:` lines at the top of the
  next tool result. Keys starting with `_` are internal and stripped before
  serializing (resources, HAR).
- **Codegen action log.** `export_test` (`codegen.py`) renders
  `session.actions`. Element tools call `target = await
  browser.codegen_target(locator)` *before* acting (it verifies role/label/text/
  CSS candidates against the live page, which may navigate away afterwards) and
  `browser.log_action(kind, target, ...)` *after* success. `log_action` drops
  the text of password fields. New element actions should do the same, and
  `codegen._step` needs a renderer for any new action kind.
- Emulation (`emulation.py`) uses a per-page CDP session for user agent, touch,
  timezone, and throttling, but screen size must go through
  `page.set_viewport_size`: Playwright re-applies its own viewport on every
  screenshot, wiping a CDP device-metrics override. Settings are stored in
  `session.emulation` and re-applied to new tabs.

**`server.py` — composition root.** Creates the `FastMCP` instance, attaches a
`lifespan` context manager that starts/stops the browser, adds
`SessionBindingMiddleware`, calls each `register_*_tools(mcp)`, and registers the
`browser://` resources (`resources.py`; they read the caller's session and never
start the browser). `__main__.py` picks the transport (`--transport`/
`BROWSER_TRANSPORT`), wraps the HTTP/SSE app in bearer-token auth when
`BROWSER_AUTH_TOKEN` is set (`auth.py`), and warns when HTTP binds a non-loopback
host, saying whether the token is set. The server-level `instructions` string is the prompt the
agent sees describing available tools. It is hand-maintained; update it whenever
you add, rename, or remove a tool or change its parameters.
`tests/test_server.py` fails if the `- name(params)` lines drift from the
registered tools.

**`tools/` — one module per category** (navigation, search, interaction, batch,
waiting, forms, content, extract, devtools, network, emulate, recording, tabs,
sessions). Each exports a single `register_<category>_tools(mcp)`
function that defines inner `async` functions decorated with `@mcp.tool()`.
Conventions every tool follows:

- Signature returns `tuple[str, Image]`: a human-readable status string plus the
  annotated screenshot.
- Starts with `await browser.ensure_started()` (lazily boots the browser if the
  lifespan hasn't, e.g. in some test paths).
- Data-only tools (extraction, network details, listings) return `str` with no
  screenshot. `act` (`tools/batch.py`) has its own per-step executor rather than
  calling other tools; a new element action usually needs a step there too.
- Ends by building the result via `get_screenshot_with_summary(browser)` from
  `tools/_summary.py`. It takes the manager as an argument on purpose: passing
  the module's own `browser` keeps the per-module test patching working.

**`navigation_policy.py`** — the one place that decides whether a caller-supplied URL may be
opened (`BROWSER_ALLOWED_DOMAINS`, `BROWSER_ALLOW_UNSAFE_SCHEMES`). Every tool that navigates to a
caller-supplied URL (`navigate_to`, `act`'s navigate step, `create_tab`, `create_session`) calls
`check_navigation_allowed(url)` before touching the browser; a new such tool must too.

**`config.py`** — a `Config` dataclass loaded once at import via
`Config.from_env()` into a global `config`. All settings come from `BROWSER_*`
and `LOG_LEVEL` env vars (see README for the full table). Because it is read at
import time, env changes require a server restart.

## Testing conventions

Almost all tests **do not launch a real browser** — everything is mocked. The
exceptions (marker `browser`, skipped when no browser is available) drive a real
headless Chromium or installed Chrome against local fixture pages:
`tests/test_som_real_browser.py` (Set of Marks; run it after any change to
`elements.py`: mocks cannot tell whether an ID reaches the right element) and
`tests/test_features_real_browser.py` (find, act, dialogs, downloads, settling,
network, extraction, emulation, sessions, CDP attach, HTTP transport, and a
generated test replayed in a separate Playwright process). Run the second after
touching `session.py`, `emulation.py`, `codegen.py`, or the tools that use them:
two of its bugs (viewport reset on screenshot, throttling undoing offline) were
invisible to mocks. The mocked pattern:

- `tests/conftest.py` provides `mock_browser_manager` (a fully stubbed
  `BrowserManager`), `mock_page`, `mock_context`, and `sample_element_map`. The
  stub is a `MagicMock`, so any new **async** manager method a tool awaits (like
  `settle`, `codegen_target`) must be added there as an `AsyncMock`, or every
  tool test using it fails with "can't be used in 'await' expression".
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

- Python 3.11.5+. Type hints are required and checked by mypy in **strict** mode
  (`disallow_untyped_defs`, etc.) — annotate fully.
- Commits follow Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`) and are signed off
  (`git commit -s`, DCO enforced in CI; PR titles are checked too). PRs explain the
  user-visible change, link related issues, include tests and docs when interfaces change, and
  attach screenshots for visual or docs-site changes.
- Do not commit credentials; use the documented `BROWSER_*` environment variables for local
  configuration.
- The docs site is VitePress (`docs/`, theme in `docs/.vitepress/`). Adding or changing a
  tool means updating `docs/reference/<category>.md` (heading `` ## `name` {#name} `` plus every
  parameter) and running `scripts/gen_tools_json.py`; `tests/test_docs.py` fails otherwise.
- Tools must build results via the shared `get_screenshot_with_summary` helper;
  `tests/test_element_summary.py` fails if a tool module defines its own copy.
- Keep tool docstrings actionable: FastMCP exposes them to clients.
- Every file is capped at 800 lines (pre-commit `max-lines`). `browser.py` is close to
  it, so put new manager-adjacent logic in its own module (as `session.py`,
  `emulation.py`, and `codegen.py` do) rather than growing the manager.
- Pre-commit hooks run on commit: ruff lint + format, bandit, actionlint on the
  workflows, `uv-lock`, `max-lines`, the standard whitespace/YAML/TOML/JSON file
  checks, and **Tach** import boundaries (`tach.toml`): the core modules
  (`browser`, `codegen`, `config`, `elements`, `emulation`, `session`) must not
  import `tools` or `server`, and `tools` must not import `server`.
  `git commit --no-verify` bypasses them but CI will still enforce them.
- The version is set in `pyproject.toml`; `__version__` and the HAR creator read
  it from package metadata. A release must also bump `plugin.json`,
  `package.json`, and both files in `.claude-plugin/` (`tests/test_version.py`
  checks). The steps are in `docs/project/contributing.md#release`.

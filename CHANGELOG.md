# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- `BROWSER_AUTH_TOKENS`: named per-client bearer tokens (`name:token,name:token`). The name
  identifies the client, so `--isolate-clients` can keep HTTP clients apart on the current MCP
  protocol.

### Changed

- Requires fastmcp 4 (from 3). Clients that negotiate the session-less MCP 2026-07-28 protocol are
  now recognized across calls: over stdio by the process, over HTTP by their named token, and on
  the older session-based protocol by their session id as before. Previously `create_session`,
  `switch_session` and `--isolate-clients` lost track of such clients after every call.
- `--isolate-clients` on `http`/`sse` without `BROWSER_AUTH_TOKENS` now logs a warning: clients on
  the current protocol can't be told apart and share one session.
- Requires Python 3.11.5 or newer (was 3.11). Python 3.11.0 to 3.11.4 are no longer supported.
  This lets the lockfile use soupsieve 4.x for every supported Python, which fixes three open
  Dependabot advisories on soupsieve 2.10.

## [0.4.0] - 2026-11-27

### Added

- `BROWSER_AUTH_TOKEN`: optional bearer-token authentication for the `http` and `sse`
  transports. Requests without `Authorization: Bearer <token>` get `401`; the token is compared
  in constant time and is read from the environment only (no flag). The warning for binding to a
  non-loopback host now says whether the token is set.
- `BROWSER_ALLOWED_DOMAINS`: comma-separated domains (subdomains included) that `navigate_to`,
  `act`'s `navigate` step, `create_tab`, and `create_session` may open. Empty means no
  restriction. Blocked URLs return an error naming the URL and the setting.
- Isolated sessions can save and reuse logins: `save_auth_state(name)`, `list_auth_states()`, and an
  `auth_state` parameter on `create_session`. States live in `BROWSER_AUTH_DIR` with owner-only
  permissions, and names cannot escape that directory.
- `get_accessibility_tree`: the page (or one element) as an ARIA snapshot in text, with an optional
  depth limit, for reading text-heavy pages without a screenshot.
- `verify_text`, `verify_url`, `verify_value`: assertions that return PASS/FAIL and, on a pass, are
  recorded by `export_test` as `expect()` lines in Python and TypeScript. Password values are never
  recorded.
- Web storage tools `get_storage`, `set_storage`, `clear_storage` (localStorage and sessionStorage
  of the current origin) and `save_pdf` (print the page to the downloads directory). The server now
  has 79 tools.
- A live cursor is drawn for agent mouse actions.
- Codex plugin manifest now declares `composerIcon` (`assets/icon.svg`), as Codex plugin
  directories require.
- `SECURITY.md`, Dependabot configuration, and a Glama manifest (`glama.json`).
- `Dockerfile`: a container image that serves Streamable HTTP on port 8000 with headless Chromium
  (installs `libatomic1`, which Playwright's bundled Node needs on slim images), and the Glama
  score badge in the README.

### Changed

- **Breaking:** `javascript:`, `file:`, `data:`, and `chrome:` URLs (and similar internal
  schemes) are now blocked by the navigation tools. Set `BROWSER_ALLOW_UNSAFE_SCHEMES=true` to
  restore the old behavior.

### Fixed

- `verify_text` counted only the first match, so a hidden first match made it fail for text that
  is present and pass for text that is absent. It now counts visible matches, and the exported
  `to_have_count(0)` does too.

## [0.3.1] - 2026-11-21

### Added

- Listed in the official MCP Registry as `io.github.adityasasidhar/browsercontrol`
  (`server.json`); each tagged release now publishes it after PyPI.
- Codex, OpenCode, Hermes, and OpenClaw install options in the docs.

### Changed

- The browser now opens visibly by default (`BROWSER_HEADLESS` defaults to `false`).
  Set `BROWSER_HEADLESS=true` for servers and CI.
- Clearer PyPI summary, keywords, and Documentation/Changelog links.

### Fixed

- `browsercontrol.__version__` reported `0.1.4`; it and the HAR `creator` version now
  come from the installed package metadata.
- Docs: tool reference wording, mobile tables, keyboard access, and stale contributor,
  release, and version info.

## [0.3.0] - 2026-11-21

### Added

- Python 3.14 support on Linux, macOS, and Windows.
- Attach to the user's own Chrome over CDP (`connect_to_chrome`, `BROWSER_CDP_URL`); detaching never closes it.
- `find(query, role, nth)`: search the whole page, off-screen content, iframes, and shadow DOM included, scroll to a match, and return its element ID.
- `act(steps)`: run several steps in one call and return one screenshot.
- `export_test`: turn a recorded agent session into a pytest-playwright or `@playwright/test` file with verified role/label/text locators; typed passwords become environment variables.
- Structured extraction: `extract_table`, `extract_links`, and selector-schema `extract`.
- New actions: `double_click`, `right_click`, `drag`, key combinations in `press_key`, `wait_for` (text, selector, network idle), `handle_dialog`, and `list_downloads`.
- JS dialogs and downloads are handled automatically and reported as `Notice:` lines in the next response, instead of dialogs being dismissed silently.
- Smart settling after every action (load, network quiet, DOM quiet; `BROWSER_SETTLE_TIMEOUT`) replaces the fixed DOMContentLoaded wait.
- Network control: `mock_route`, `clear_mocks`, `wait_for_response`, `get_request_details` (headers and bodies), and `export_har`.
- Emulation: `list_devices`, `emulate_device`, `set_geolocation`, `set_timezone`, `set_color_scheme`, `throttle_network`, `reset_emulation`.
- Isolated sessions (`create_session`, `switch_session`, `list_sessions`, `close_session`), with captured data kept per session and each MCP client bound to its own session; `BROWSER_ISOLATE_CLIENTS` gives every client one automatically.
- MCP resources for console logs, network traffic, errors, tabs, downloads, sessions, and the action log (`browser://...`).
- Streamable HTTP transport: `browsercontrol --transport http` (also `BROWSER_TRANSPORT`, `BROWSER_HOST`, `BROWSER_PORT`).
- Claude Code plugin and marketplace (`.claude-plugin/`): installs the MCP server and the agent skill together.
- Codex and OpenCode plugin packaging.
- Documentation site rebuilt with VitePress; README rewritten.
- Issue and PR templates, DCO sign-off check, conventional-commit PR title check.
- `Makefile`, max-lines pre-commit check, refreshed pre-commit hooks.
- Reuse an installed Google Chrome when Playwright's Chromium is missing.
- Elements inside cross-origin iframes are now numbered and actionable.
- Framework click targets with no `onclick` attribute (detected by `cursor: pointer`) are numbered.
- Disabled controls are drawn grey and flagged `(disabled)` in the element list.
- Real-browser Set of Marks tests (`tests/test_som_real_browser.py`).

### Fixed

- Actions reach the numbered element itself instead of whatever sits at its centre
  point, so clicks and typing work inside shadow DOM and iframes.
- Stale element IDs (removed or moved since the screenshot) are refused with a fresh
  screenshot instead of acting on the wrong element.
- Element maps are kept per tab; IDs from one tab no longer resolve in another.
- Hidden, transparent, and covered elements are no longer numbered.
- `get_text` reads the live element (full text, or a field's current value) instead
  of the cached 50-character label.
- An element animating back and forth is no longer refused as stale when two
  samples happen to straddle the point where it reverses.

## [0.2.0] - 2026-07-28

### Added

- Configurable Chromium binary and output directories.
- Automated PyPI releases on version tags.
- Documentation site, Spanish README and agent skill.

### Fixed

- Form tool semantics, viewport validation and element labels.
- Upgraded Pillow to 12.3.0 for security advisories.

[Unreleased]: https://github.com/adityasasidhar/browsercontrol/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/adityasasidhar/browsercontrol/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/adityasasidhar/browsercontrol/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/adityasasidhar/browsercontrol/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/adityasasidhar/browsercontrol/compare/v0.1.4...v0.2.0

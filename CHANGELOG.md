# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

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

## [0.2.0]

### Added

- Configurable Chromium binary and output directories.
- Automated PyPI releases on version tags.
- Documentation site, Spanish README and agent skill.

### Fixed

- Form tool semantics, viewport validation and element labels.
- Upgraded Pillow to 12.3.0 for security advisories.

# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

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

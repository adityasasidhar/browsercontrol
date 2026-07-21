# Changelog

All notable changes to BrowserControl are documented here. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Public documentation site at `https://adityasasidhar.github.io/browsercontrol/`.

## [0.1.4] — 2026-02-28

### Fixed
- Resolve bugs, type errors, and tooling gaps across the codebase.

## [0.1.3] — 2026-02-15

### Changed
- Upgrade transitive dependencies to patch all open Dependabot vulnerabilities.

## [0.1.0] — 2025-06-27

### Added
- Initial release.
- ~25 MCP tools across navigation, interaction, tabs, forms, content, devtools, and recording.
- Set of Marks (SoM) renderer with shadow DOM + iframe support.
- Built-in devtools: console logs, network requests, JS errors, performance, cookies.
- Persistent session via `launch_persistent_context`.
- Multi-tab orchestration.
- Native file uploads via `set_input_files`.
- Smart localhost → 127.0.0.1 fallback.
- Recording via Playwright traces.

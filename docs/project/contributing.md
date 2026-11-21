---
title: Contributing
description: Set up BrowserControl for development, run the checks, add a tool, work on these docs, and cut a release.
---

# Contributing

Bug reports, fixes, docs, and new tools are all welcome. The [contribution guidelines](https://github.com/adityasasidhar/browsercontrol/blob/main/CONTRIBUTING.md) cover the workflow; this page is the practical setup.

## Set up

```bash
git clone https://github.com/adityasasidhar/browsercontrol
cd browsercontrol
uv sync                              # runtime and dev dependencies
uv run playwright install chromium   # the browser engine
uv run pre-commit install            # lint and format on commit
```

Run the server with the MCP inspector:

```bash
uv run fastmcp dev browsercontrol/server.py
```

## Checks

`make help` lists every shortcut. `make check` runs lint, type checks, and tests together.

| Check | Command |
| --- | --- |
| Tests | `uv run pytest` |
| One test | `uv run pytest tests/test_navigation.py::TestScroll::test_scroll_down_medium` |
| Lint and format | `uv run ruff check . && uv run ruff format .` |
| Types (strict) | `uv run mypy browsercontrol/` |
| Security | `uv run bandit -c pyproject.toml -r . --exclude ./tests,./.venv` |
| Every hook | `uv run pre-commit run --all-files` |

Most tests mock Playwright and run in seconds. Two files drive a real headless browser against local pages: `tests/test_som_real_browser.py` (run it after touching element detection) and `tests/test_features_real_browser.py` (sessions, emulation, codegen, and the tools that use them). They're skipped when no browser is available.

CI runs lint first, then tests on Python 3.11 and 3.14 on Linux, Windows, and macOS (and 3.12 and 3.13 on Linux), plus bandit and mypy.

Pre-commit also runs actionlint on the GitHub Actions workflows, `uv-lock` to keep `uv.lock` in sync, a max-lines check (800 per file), and [Tach](https://github.com/gauge-sh/tach) on imports: the browser core (`browser.py`, `elements.py`, `session.py`, …) must not import from `tools/` or `server.py`, and `tools/` must not import `server.py`. The server imports and registers everything (`tach.toml`).

## Commits and pull requests

- [Conventional Commits](https://www.conventionalcommits.org/) for commits and PR titles: `feat:`, `fix:`, `docs:`, `chore:`…
- Sign off every commit with `git commit -s` ([DCO](https://developercertificate.org/)); CI rejects commits without it.
- Explain the user-visible change, link related issues, and include tests, plus docs when an interface changes.

## Add a tool

1. Put it in the matching module under `browsercontrol/tools/` and decorate it with `@mcp.tool()`. Its docstring and parameter descriptions are what clients see, so make them actionable.
2. Start with `await browser.ensure_started()`. Resolve elements with `await browser.resolve_element(id)` and catch `ElementError` with `element_error_result`. Never act at stored coordinates.
3. Return `tuple[str, Image]` built with `get_screenshot_with_summary(browser)` if the tool changes the page, or `str` if it only reads.
4. For element actions, call `browser.codegen_target(locator)` before acting and `browser.log_action(...)` after, so [`export_test`](/reference/recording#export_test) can reproduce it. Add a step to `act` if it makes sense in a batch.
5. List it in the server `instructions` in `server.py` (`tests/test_server.py` checks they match).
6. Test the happy path and the error path, following the existing per-module test files.
7. Regenerate the tool catalog and document it (next section).

## Work on these docs

The site is [VitePress](https://vitepress.dev) with the [Catppuccin](https://github.com/catppuccin/vitepress) theme, in `docs/`.

```bash
cd docs
npm ci
npm run dev       # live preview at http://localhost:5173/browsercontrol/
npm run build     # production build in docs/.vitepress/dist
npm run check:links  # every internal link and #anchor in the build resolves
```

- **Tool catalog.** `docs/public/tools.json` is generated from the server and drives the [tool explorer](/reference/). After changing a tool, run `uv run python scripts/gen_tools_json.py`. A test fails while it's stale, and another checks that every tool and parameter appears in `docs/reference/`.
- **Pages.** Each page has a `description` in its frontmatter; it's used in search results, social previews, and `llms.txt`.
- **Components.** `<Mark n="7">Submit</Mark>` draws an inline numbered mark; `<CardGrid>` and `<Card>` make link cards; `<div class="steps">` numbers its `###` headings like marks.
- **Agents.** `llms.txt`, `llms-full.txt`, and a `.md` version of every page are generated at build time. Wrap text meant only for agents in `<llm-only>`.

## Release

Pushing a `v*` tag runs `.github/workflows/release.yml`: it re-runs the checks, builds, publishes to PyPI through Trusted Publishing, and opens a GitHub release.

The version lives in `pyproject.toml`, but the plugin manifests carry their own copy. A release bumps all of them in one commit:

| File | What to change |
| --- | --- |
| `pyproject.toml`, `uv.lock` | `uv version --bump minor` (or `patch` / `major`) updates both. |
| `plugin.json`, `package.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | Set `version` to the same value. |
| `server.json` | Set both `version` fields (the server and its PyPI package). The release job publishes it to the MCP Registry after PyPI. |
| `CHANGELOG.md` | Move the `[Unreleased]` entries under a new `## [X.Y.Z] - YYYY-MM-DD` heading, and add its compare link at the bottom. |

`tests/test_version.py` fails if any manifest disagrees with `pyproject.toml`. The package's `__version__` and the HAR `creator` version read the installed package metadata, so they need no edit.

Release through a pull request like any other change, then tag the merge commit:

```bash
git checkout -b release/vX.Y.Z
# bump the files above
git commit -s -am "chore: release X.Y.Z"
git push -u origin release/vX.Y.Z    # open a PR and merge it
git checkout main && git pull
git tag vX.Y.Z
git push origin vX.Y.Z
```

The tag must match `project.version` in `pyproject.toml`, and the workflow refuses a version that already exists on PyPI.

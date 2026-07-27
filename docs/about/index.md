# About BrowserControl

BrowserControl is an open-source MCP server that gives AI agents a real browser they can see, click, type, and debug — local, private, zero-cost.

## Mission

> Give AI agents a better way to use a browser — one they can actually see,
> running on your machine, free for anyone to use.

Agents are asked to work on the web every day, and most of the tooling still
hands them a DOM and hopes for the best. BrowserControl exists to close that
gap: show the agent the page, let it point at what it wants, and keep the whole
loop local, private, and free. Every design decision is measured against that —
does it make an agent more capable in a browser, and does it stay out of the
user's way?

## Origin

BrowserControl started as a single-engineer prototype to scratch one itch: **browsers shouldn't be hard to drive for AI agents**. Existing tools used fragile selectors, required cloud APIs, or cost money per action. None of that made sense for a tool that's running on the user's machine anyway.

The first version shipped ~25 tools organized into navigation, interaction, forms, content, devtools, recording, and tabs. Subsequent releases added Set of Marks (SoM), shadow DOM traversal, native file uploads, and built-in devtools.

## Project facts

| | |
|---|---|
| **License** | MIT |
| **Python** | 3.11+ |
| **Stack** | FastMCP, Playwright, Pillow |
| **CI** | GitHub Actions — Ubuntu, Windows, macOS |
| **First release** | June 2025 |
| **Current version** | 0.1.4 |
| **Repository** | [github.com/adityasasidhar/browsercontrol](https://github.com/adityasasidhar/browsercontrol) |
| **PyPI** | [pypi.org/project/browsercontrol](https://pypi.org/project/browsercontrol/) |

## Maintainers

- **Aditya Sasidhar** — original author and maintainer.

See the [CONTRIBUTING.md](https://github.com/adityasasidhar/browsercontrol/blob/main/CONTRIBUTING.md) for how to get involved.

## See also

- **[License](license.md)** — MIT license text
- **[Changelog](changelog.md)** — release notes

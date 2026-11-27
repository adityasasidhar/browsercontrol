---
title: About
description: Why BrowserControl exists, how it's built, and the project's license and links.
---

# About

<img src="/mascot.png" alt="The BrowserControl mascot: a smiling retro computer waving hello" width="160" height="160" class="no-zoom" style="float: right; margin: 0 0 16px 24px; border: 0;" />

Agents are asked to work on the web every day, and most browser tooling still hands them a DOM and hopes for the best. BrowserControl exists to close that gap: **show the agent the page, let it point at what it wants, and keep the whole loop local.**

Every design decision is measured against two questions. Does it make an agent more capable in a real browser? And does it stay out of the user's way?

## How it's built

| | |
| --- | --- |
| **Language** | Python 3.11.5+ |
| **Built on** | [FastMCP](https://gofastmcp.com), [Playwright](https://playwright.dev/python/), [Pillow](https://python-pillow.org) |
| **Browser** | Chromium, or your own Chrome over CDP |
| **Quality** | mypy strict, ruff, bandit; tests on Linux, Windows, and macOS |
| **License** | [MIT](https://github.com/adityasasidhar/browsercontrol/blob/main/LICENSE) |

## Links

- Source: [github.com/adityasasidhar/browsercontrol](https://github.com/adityasasidhar/browsercontrol)
- Package: [pypi.org/project/browsercontrol](https://pypi.org/project/browsercontrol/)
- Issues: [GitHub issues](https://github.com/adityasasidhar/browsercontrol/issues)
- Release notes: [Changelog](/project/changelog)

## Maintainer

BrowserControl was created and is maintained by [Aditya Sasidhar](https://github.com/adityasasidhar). Contributions are welcome; see [Contributing](/project/contributing).

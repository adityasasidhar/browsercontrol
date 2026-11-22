---
layout: page
title: BrowserControl
titleTemplate: Browser automation your agent can see
description: A local MCP server that gives AI agents a real Chromium browser, with numbered screenshots instead of selectors.
sidebar: false
aside: false
---

<HomePage />

<llm-only>

# BrowserControl

BrowserControl is a local MCP server that gives AI agents a real Chromium browser through Playwright. Every action returns an annotated screenshot: interactive elements are outlined with numbered boxes (Set of Marks), and the same numbers appear in a text list. The agent acts by number, for example `click(7)` or `type_text(3, "hello")`, instead of writing CSS selectors.

- Install for Claude Code: `/plugin marketplace add adityasasidhar/browsercontrol`, then `/plugin install browsercontrol@browsercontrol`.
- Any other MCP client: run `uvx browsercontrol` as a stdio server.
- 79 tools: navigation and `find`, interaction and `act` batching, waiting and dialogs, forms, content, extraction, tabs, sessions (including attaching to your own Chrome over CDP and saved logins), devtools and web storage, network mocking, emulation, recording with Playwright test export, and assertions that become `expect()` lines.

Start with the quickstart (/guide/quickstart.md), then Set of Marks (/concepts/set-of-marks.md). The tool reference starts at /reference.md, and /tools.json lists every tool with its parameters.

</llm-only>

# Getting started

Welcome to **BrowserControl** — the vision-first browser automation MCP server. This section walks you from a fresh install to a working agent in under five minutes.

## What you'll do

1. **[Install BrowserControl](installation.md)** — pip / uv / pipx in one command.
2. **[Connect it to your AI](connect-your-ai.md)** — Claude Desktop, Cursor, Cline, Continue, Zed, or programmatic Python.
3. **[Run your first session](first-session.md)** — navigate, click, type, and screenshot.
4. **[Add the agent skill](agent-skill.md)** _(optional)_ — a playbook that teaches your agent to drive the browser well.

## What you'll need

- **Python 3.11 or newer** on Linux, macOS, or Windows.
- **An MCP-compatible AI client** — Claude Desktop, Cursor, Cline, Continue, Gemini CLI, or any client that speaks MCP stdio.
- **No API key, no cloud account, no telemetry.** BrowserControl runs 100% on your machine.

!!! tip "Already have a Python project?"
    If you're using `uv`, BrowserControl drops in as a normal dependency. No browser binary to manage — Chromium auto-installs on first run.

## Quick taste

Once connected, ask your agent:

> _"Open Hacker News and tell me the top story."_

The agent will call the MCP tools:

```
→ navigate_to("https://news.ycombinator.com")
→ get_page_content()
→ "The top story is: ..."
```

That's the whole loop. No selectors, no XPath, no DOM debugging — just point at numbers.

## Where to next

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **[Install BrowserControl](installation.md)**

    ---

    Pick your installer and get Chromium auto-provisioned.

-   :material-link-variant:{ .lg .middle } **[Connect your AI](connect-your-ai.md)**

    ---

    Drop-in configs for every major MCP client.

-   :material-school:{ .lg .middle } **[Run your first session](first-session.md)**

    ---

    A guided walkthrough of the most common tools.

-   :material-book-open-variant:{ .lg .middle } **[Add the agent skill](agent-skill.md)**

    ---

    A drop-in playbook that makes agents markedly more reliable.

</div>

---
title: Quickstart
description: Install BrowserControl, connect it to your MCP client, and run a first browsing task in about two minutes.
---

# Quickstart

Install the server, connect your client, and ask your agent to use a browser.

<div class="steps">

### Install uv

The commands below launch BrowserControl with [uv](https://docs.astral.sh/uv/getting-started/installation/), which downloads it on first use. Check that uv is on your `PATH`:

```bash
uv --version
```

If you would rather install with pip, see [Installation](/guide/installation).

### Add BrowserControl to your client

<InstallBox />

For Claude Code, the plugin is the quickest route: it adds the MCP server and the [agent skill](/guide/agent-skill) together. Restart Claude Code or run `/reload-plugins` afterwards. For every other client, see [Connect a client](/guide/clients).

### Ask for something

Reload your client, then try:

> Open Hacker News with BrowserControl and tell me the top story.

The first launch can take a minute: BrowserControl reuses a Chromium or Chrome it finds, and otherwise downloads Chromium once.

</div>

## What just happened

1. The agent called `navigate_to("https://news.ycombinator.com")`.
2. BrowserControl loaded the page, waited for it to [settle](/concepts/settling), and returned a screenshot with every link and button numbered, plus the same numbers as text.
3. The agent read the top story from the screenshot or the text, and, if it needed more, called something like `click(12)` or `get_page_content()`.

The browser opens a visible window by default. To hide it, set `BROWSER_HEADLESS=true` in your client's MCP config. See [Configuration](/reference/configuration#browser_headless).

::: tip Not working?
If your client doesn't list BrowserControl's tools, check its MCP logs, then see [Troubleshooting](/help/troubleshooting#the-client-cant-find-browsercontrol).
:::

## Next steps

<CardGrid>
  <Card title="Your first session" link="/guide/first-session">Fill a demo form and learn to read the element map.</Card>
  <Card title="Set of Marks" link="/concepts/set-of-marks">Why the numbers work the way they do.</Card>
  <Card title="Recipes" link="/recipes/">Task-by-task walkthroughs: forms, debugging, testing.</Card>
</CardGrid>

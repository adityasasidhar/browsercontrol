# Getting started

BrowserControl runs as a local server. Your AI client starts it over MCP stdio
and calls its tools to control Chromium.

## Setup

1. [Install BrowserControl](installation.md). Choose a standalone install or let
   your client launch it with `uvx`.
2. [Connect an MCP client](connect-your-ai.md). Add the server to your client and
   confirm its tools are available.
3. [Run your first session](first-session.md). Open a demo form, fill a field,
   and verify the submission.

You need a client that supports MCP stdio. BrowserControl needs Python 3.11 or
newer and runs on Linux, macOS, and Windows. If you use `uv`, it can manage
Python for you.

## After setup

- [Add the agent skill](agent-skill.md) if your client supports skills.
- [Configure BrowserControl](../configuration.md) to show the browser window or
  choose where the profile and recordings are stored.
- [Troubleshoot startup](../troubleshooting.md) if the tools don’t appear.

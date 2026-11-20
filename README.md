<p align="center">
  <img src="https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/assets/logo-main.png" alt="" width="100">
</p>

# BrowserControl

BrowserControl gives your AI client a local Chromium browser over MCP. It
returns screenshots with numbered controls and a matching text list so the
agent can click, type, or read the page.

[Documentation](https://adityasasidhar.github.io/browsercontrol/) ·
[PyPI](https://pypi.org/project/browsercontrol/) ·
[Español](README.es-ES.md) ·
[MIT License](LICENSE)

## Quick start

### Claude Code plugin

With [uv](https://docs.astral.sh/uv/getting-started/installation/) on your
`PATH`, run these commands in Claude Code to install the MCP server and the
[agent skill](skills/browsercontrol/SKILL.md) together:

```text
/plugin marketplace add adityasasidhar/browsercontrol
/plugin install browsercontrol@browsercontrol
```

Restart Claude Code or run `/reload-plugins` to load the tools.

### Manual MCP setup

With [uv](https://docs.astral.sh/uv/getting-started/installation/) installed,
configure your client to launch `uvx browsercontrol`. For clients that use
`mcpServers` JSON, merge in this entry:

```json
{
  "mcpServers": {
    "browsercontrol": {
      "command": "uvx",
      "args": ["browsercontrol"]
    }
  }
}
```

For a manual setup in Claude Code, run:

```bash
claude mcp add --transport stdio browsercontrol -- uvx browsercontrol
```

Reload your client and try asking, “Open Hacker News with BrowserControl and
tell me the top story.” On first launch, BrowserControl reuses a compatible
local browser or downloads Chromium.

[Client setup for Cursor, VS Code, and more](https://adityasasidhar.github.io/browsercontrol/getting-started/connect-your-ai/) ·
[Install with pip or from source](https://adityasasidhar.github.io/browsercontrol/getting-started/installation/)

## How element numbers work

BrowserControl uses [Set of Marks](https://adityasasidhar.github.io/browsercontrol/concepts/set-of-marks/)
to label detected controls. For example, if a button is marked **5**, the agent
calls `click(5)`.

**Read the newest element map before each action that uses an ID.** Every
annotated screenshot generates a fresh map. If a control is off-screen, scroll
to it and read the returned map.

![Recorded BrowserControl session showing numbered elements as the agent navigates, searches, and fills a form](https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/assets/som-demo.gif)

## What you can do

| Task | Tools |
| --- | --- |
| [Navigate and interact](https://adityasasidhar.github.io/browsercontrol/tools/interaction/) | Open pages, scroll, click, type, and press keys. |
| [Fill forms](https://adityasasidhar.github.io/browsercontrol/tools/forms/) | Select options, check boxes, and upload local files. |
| [Read pages](https://adityasasidhar.github.io/browsercontrol/tools/content/) | Extract Markdown or text and take screenshots. |
| [Debug a web app](https://adityasasidhar.github.io/browsercontrol/guides/debug-web-app/) | Inspect console logs, failed requests, and page errors. |
| [Record a session](https://adityasasidhar.github.io/browsercontrol/guides/record-tests/) | Save Playwright traces and page snapshots. |

[Full tool reference](https://adityasasidhar.github.io/browsercontrol/tools/) ·
[Configuration](https://adityasasidhar.github.io/browsercontrol/configuration/) ·
[Agent skill](skills/browsercontrol/SKILL.md) ·
[Troubleshooting](https://adityasasidhar.github.io/browsercontrol/troubleshooting/)

## Development

```bash
uv sync
uv run playwright install chromium
uv run pytest
uv run --extra docs mkdocs serve
```

See the [development guide](https://adityasasidhar.github.io/browsercontrol/development/)
and [contribution guidelines](CONTRIBUTING.md).

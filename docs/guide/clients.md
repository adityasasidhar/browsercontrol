---
title: Connect a client
description: MCP configuration for Codex, Claude Code, Claude Desktop, Cursor, VS Code, Gemini CLI, Cline, Zed, Continue, OpenCode, Hermes, OpenClaw, and the Python SDK.
---

# Connect a client

Your MCP client launches BrowserControl as a local server over stdio. Plugin installs and the manual `uvx browsercontrol` examples need [uv](https://docs.astral.sh/uv/getting-started/installation/). If you [installed](/guide/installation) the `browsercontrol` command yourself, use it directly in your manual configuration.

## Codex

```bash
codex plugin marketplace add adityasasidhar/browsercontrol
codex plugin add browsercontrol@browsercontrol
```

The plugin installs the local MCP server and the [agent skill](/guide/agent-skill) together. Make sure `uv` is on the PATH that Codex uses, then start a new session and ask Codex to use BrowserControl.

The plugin keeps its browser profile and downloads in its Codex plugin data directory.

## Claude Code

::: code-group

```text [Plugin]
/plugin marketplace add adityasasidhar/browsercontrol
/plugin install browsercontrol@browsercontrol
```

```bash [Manual]
claude mcp add --transport stdio browsercontrol -- uvx browsercontrol
```

:::

The plugin installs the MCP server and the [agent skill](/guide/agent-skill) together; restart Claude Code or run `/reload-plugins` afterwards. The manual command adds only the server, for the current project. Run `/mcp` to check the connection.

## Clients with an `mcpServers` file

Most clients read a JSON file with an `mcpServers` object. Add this entry to it:

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

| Client | Where the file lives |
| --- | --- |
| Claude Desktop | **Settings → Developer → Edit Config** opens `claude_desktop_config.json`. |
| Cursor | `.cursor/mcp.json` in a project, or `~/.cursor/mcp.json` for all projects. [Docs](https://cursor.com/docs/mcp) |
| Gemini CLI | `.gemini/settings.json` in a project, or `~/.gemini/settings.json`. [Docs](https://geminicli.com/docs/tools/mcp-server/) |
| Cline | **MCP Servers → Configure → Configure MCP Servers**. [Docs](https://docs.cline.bot/mcp/mcp-overview) |
| VS Code (Copilot) | **Chat: Open Customizations → MCP Servers → Add Server**. In a portable config, add `"type": "stdio"` to the entry. [Docs](https://code.visualstudio.com/docs/agents/reference/mcp-configuration) |

## OpenCode

With OpenCode 2.3.2 or later, install the plugin globally:

```bash
opencode plugin add github:adityasasidhar/browsercontrol
opencode mcp list
```

The plugin loads the bundled MCP server and [agent skill](/guide/agent-skill). If you already configured a server named `browsercontrol`, the plugin uses that configuration. Open a session and mention `@browsercontrol` to load the skill.

For manual setup, add the server to your project's `opencode.json` or your OpenCode user configuration. Select the example for your major version.

::: code-group

```json [OpenCode 2]
{
  "mcp": {
    "servers": {
      "browsercontrol": {
        "type": "local",
        "command": ["uvx", "browsercontrol"]
      }
    }
  }
}
```

```json [OpenCode 1]
{
  "mcp": {
    "browsercontrol": {
      "type": "local",
      "command": ["uvx", "browsercontrol"],
      "enabled": true
    }
  }
}
```

:::

## Hermes

```bash
hermes mcp add browsercontrol --command uvx --args browsercontrol
```

This adds the server to your Hermes configuration. Start a new session so Hermes picks it up. It installs the server only, not the [agent skill](/guide/agent-skill).

## OpenClaw

```bash
openclaw mcp add browsercontrol --command uvx --arg browsercontrol
```

This registers the server with OpenClaw and probes it before saving. Restart the gateway or start a new session to load it. It installs the server only, not the [agent skill](/guide/agent-skill).

## Other formats

::: code-group

```json [Zed]
{
  "context_servers": {
    "browsercontrol": {
      "command": "uvx",
      "args": ["browsercontrol"]
    }
  }
}
```

```yaml [Continue]
mcpServers:
  - name: browsercontrol
    type: stdio
    command: uvx
    args:
      - browsercontrol
```

:::

Zed takes the entry in its settings JSON ([docs](https://zed.dev/docs/ai/mcp)), and Continue in its `config.yaml` ([docs](https://docs.continue.dev/customize/deep-dives/mcp)).

## From Python

The MCP Python SDK can launch BrowserControl and call its tools from a script:

```python
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    server = StdioServerParameters(command="uvx", args=["browsercontrol"])
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("navigate_to", {"url": "https://example.com"})
            print(result.content[0].text)


asyncio.run(main())
```

## Launch commands

| How you installed | Command | Arguments |
| --- | --- | --- |
| Nothing (uv) | `uvx` | `["browsercontrol"]` |
| Nothing (pipx) | `pipx` | `["run", "browsercontrol"]` |
| `uv tool`, `pip`, or `pipx install` | `browsercontrol` | none |
| Source checkout | `uv` | `["--directory", "/path/to/browsercontrol", "run", "browsercontrol"]` |

A desktop app may not see the same `PATH` as your terminal. If the client can't find the command, use its full path (`which uvx` prints it).

## Pass settings

Add an `env` object to the server entry to configure BrowserControl. For example, to run the browser headless:

```json
{
  "mcpServers": {
    "browsercontrol": {
      "command": "uvx",
      "args": ["browsercontrol"],
      "env": { "BROWSER_HEADLESS": "true" }
    }
  }
}
```

Every setting is listed in [Configuration](/reference/configuration).

## Check the connection

Reload your client's MCP servers or restart it, then look for `navigate_to` in its tool list. If the server doesn't start, read the client's MCP log and see [Troubleshooting](/help/troubleshooting).

To share one browser between several clients, run BrowserControl yourself over HTTP instead: see [Share over HTTP](/guide/http).

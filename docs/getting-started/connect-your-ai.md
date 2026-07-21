# Connect your AI

BrowserControl speaks MCP stdio, so it works with anything that speaks MCP. Pick your client, paste the config, restart, and you're done.

## Claude Desktop

Add to `claude_desktop_config.json`:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "browsercontrol": {
      "command": "browsercontrol"
    }
  }
}
```

Restart Claude Desktop. You should see a 🔨 hammer icon in the input box — click it to confirm the tools are loaded.

## Gemini CLI / Google AI Studio

Configure MCP servers in Gemini's settings, or via environment:

```bash
export MCP_SERVERS='{"browsercontrol": {"command": "browsercontrol"}}'
```

For Google AI Studio, configure in the MCP settings panel.

## Cline (VS Code)

1. Install [Cline](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev)
2. Open Cline settings → **MCP Servers** → Add:

```json
{
  "browsercontrol": {
    "command": "browsercontrol"
  }
}
```

## Continue.dev (VS Code / JetBrains)

Add to `~/.continue/config.json`:

```json
{
  "mcpServers": [
    { "name": "browsercontrol", "command": "browsercontrol" }
  ]
}
```

## Cursor IDE

Cursor Settings → **Features** → **Model Context Protocol** → Add:

```json
{ "browsercontrol": { "command": "browsercontrol" } }
```

## Zed Editor

Add to `~/.config/zed/settings.json`:

```json
{
  "context_servers": {
    "browsercontrol": {
      "command": { "path": "browsercontrol" }
    }
  }
}
```

## Python (programmatic)

Use the official MCP Python client to drive BrowserControl from a script:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    params = StdioServerParameters(command="browsercontrol", args=[])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            result = await session.call_tool(
                "navigate_to", {"url": "https://news.ycombinator.com"}
            )


asyncio.run(main())
```

## uvx / pipx (no install needed)

If you don't want to install BrowserControl globally, run it via `uvx` or `pipx`:

```json
{
  "mcpServers": {
    "browsercontrol": { "command": "uvx", "args": ["browsercontrol"] }
  }
}
```

```json
{
  "mcpServers": {
    "browsercontrol": { "command": "pipx", "args": ["run", "browsercontrol"] }
  }
}
```

## Advanced: environment variables

Pass environment variables to tune the browser:

```json
{
  "mcpServers": {
    "browsercontrol": {
      "command": "browsercontrol",
      "env": {
        "BROWSER_HEADLESS": "false",
        "BROWSER_VIEWPORT_WIDTH": "1920",
        "BROWSER_VIEWPORT_HEIGHT": "1080",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

See **[Configuration](../configuration.md)** for the full list of environment variables.

## Verifying the connection

Once you've added the config and restarted your client:

1. Look for a tools / MCP indicator in your client's UI.
2. Ask your agent: _"List the browser tools you have available."_
3. You should see ~30 tools organized into **Navigation**, **Interaction**, **Tabs**, **Forms**, **Content**, **DevTools**, and **Recording**.

If tools are missing, see the [Troubleshooting guide](../troubleshooting.md).

## Next

- **[Run your first session](first-session.md)** — a guided walkthrough.
- **[Browse the tools](../tools/index.md)** — every MCP tool documented.

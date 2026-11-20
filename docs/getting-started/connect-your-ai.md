# Connect an MCP client

Your client launches BrowserControl as a local MCP server over stdio. The
examples below use `uvx browsercontrol`, which requires
[uv](https://docs.astral.sh/uv/getting-started/installation/). If you
[installed BrowserControl](installation.md) separately, use `browsercontrol`
as the command and omit the arguments.

## Claude Code

=== "Plugin"

    With `uv` on your `PATH`, use the plugin to install the MCP server and the
    [agent skill](agent-skill.md) together. Run these commands in Claude Code:

    ```text
    /plugin marketplace add adityasasidhar/browsercontrol
    /plugin install browsercontrol@browsercontrol
    ```

    Restart Claude Code or run `/reload-plugins`, then use `/mcp` to check the
    connection.

=== "Manual"

    Run this from your project directory:

    ```bash
    claude mcp add --transport stdio browsercontrol -- uvx browsercontrol
    ```

    Run `/mcp` in Claude Code to check the connection. [Claude Code MCP docs](https://code.claude.com/docs/en/mcp)

## Clients that use `mcpServers`

Add the following entry to the indicated settings file. If it already has an
`mcpServers` object, add the `browsercontrol` entry inside it.

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

| Client | Where the settings live |
| --- | --- |
| Claude Desktop | Open **Settings → Developer → Edit Config** to find `claude_desktop_config.json`. |
| Cursor | Use `.cursor/mcp.json` in your project or `~/.cursor/mcp.json` for all projects. [Cursor docs](https://cursor.com/docs/mcp) |
| Gemini CLI | Use `.gemini/settings.json` in your project or `~/.gemini/settings.json` for all projects. [Gemini CLI docs](https://geminicli.com/docs/tools/mcp-server/) |
| Cline | Open **MCP Servers → Configure → Configure MCP Servers**. [Cline docs](https://docs.cline.bot/mcp/mcp-overview) |
| GitHub Copilot in VS Code | Open **Chat: Open Customizations → MCP Servers → Add Server** and select the destination. In a portable Copilot configuration, add `"type": "stdio"` to the server entry. [VS Code docs](https://code.visualstudio.com/docs/agents/reference/mcp-configuration) |

## Other client formats

=== "OpenCode"

    Add this to your project’s `opencode.json` or to
    `~/.config/opencode/opencode.json`. This example uses the OpenCode v2
    format. See the [OpenCode docs](https://opencode.ai/docs/mcp-servers) for
    version-specific formats. Confirm with `opencode mcp list`.

    ```json
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

=== "Zed"

    Add this to Zed’s settings JSON. [Zed MCP docs](https://zed.dev/docs/ai/mcp)

    ```json
    {
      "context_servers": {
        "browsercontrol": {
          "command": "uvx",
          "args": ["browsercontrol"]
        }
      }
    }
    ```

=== "Continue"

    Add the following to Continue’s `config.yaml`. [Continue MCP docs](https://docs.continue.dev/customize/deep-dives/mcp)

    ```yaml
    mcpServers:
      - name: browsercontrol
        type: stdio
        command: uvx
        args:
          - browsercontrol
    ```

## Python

The MCP Python client can launch BrowserControl from a script. This example
assumes `uvx` is available on `PATH`.

```python
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    server = StdioServerParameters(command="uvx", args=["browsercontrol"])
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "navigate_to", {"url": "https://example.com"}
            )
            print(result.isError)


asyncio.run(main())
```

## Launch options { #uvx-pipx-no-install-needed }

| Installation | Command | Arguments |
| --- | --- | --- |
| On demand with uv | `uvx` | `["browsercontrol"]` |
| On demand with pipx | `pipx` | `["run", "browsercontrol"]` |
| Standalone install | `browsercontrol` | None |
| Source checkout | `uv` | `["--directory", "/path/to/browsercontrol", "run", "browsercontrol"]` |

A desktop client may have a different `PATH` from your terminal. If it cannot
find the command, use the executable’s full path. See
[Configuration](../configuration.md) for environment variables such as
`BROWSER_HEADLESS=false`.

## Share one browser over HTTP

Clients that connect to a URL instead of launching a command can use
Streamable HTTP. Start the server yourself:

```bash
uvx browsercontrol --transport http --port 8000
```

and point the client at `http://127.0.0.1:8000/mcp`. Add `--isolate-clients`
to give each connected client its own browser session. There is no
authentication, so keep the default `127.0.0.1` host unless the network is
trusted. See [`BROWSER_TRANSPORT`](../configuration.md#browser_transport).

## Verify the connection

Reload the MCP servers or restart your client. Use its MCP tools list to check
for BrowserControl’s `navigate_to` tool. If the server fails to start, open the
client’s MCP logs and see [Troubleshooting](../troubleshooting.md).

[Run your first session](first-session.md){ .md-button .md-button--primary }

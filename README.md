<p align="center">
  <img alt="BrowserControl" src="https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/assets/logo-main.png" width="120"/>
</p>

<!-- mcp-name: io.github.adityasasidhar/browsercontrol -->

<h1 align="center">BrowserControl</h1>

<p align="center">
  <b>A real browser for your AI agent. It sees the page and clicks by number.</b>
</p>

<p align="center">
  <a href="https://pypi.org/project/browsercontrol/"><img src="https://img.shields.io/pypi/v/browsercontrol" alt="PyPI"></a>
  <a href="https://pypi.org/project/browsercontrol/"><img src="https://img.shields.io/pypi/pyversions/browsercontrol" alt="Python"></a>
  <a href="https://pepy.tech/projects/browsercontrol"><img src="https://static.pepy.tech/badge/browsercontrol" alt="Total downloads"></a>
  <a href="https://github.com/adityasasidhar/browsercontrol/blob/main/LICENSE"><img src="https://img.shields.io/github/license/adityasasidhar/browsercontrol" alt="MIT license"></a>
</p>

<p align="center">
  <a href="https://adityasasidhar.github.io/browsercontrol/"><b>Documentation</b></a> ·
  <a href="https://adityasasidhar.github.io/browsercontrol/guide/quickstart">Quickstart</a> ·
  <a href="https://adityasasidhar.github.io/browsercontrol/reference/">All 79 tools</a> ·
  <a href="https://adityasasidhar.github.io/browsercontrol/recipes/">Recipes</a> ·
  <a href="https://registry.modelcontextprotocol.io/v0/servers?search=io.github.adityasasidhar/browsercontrol">MCP Registry</a> ·
  <a href="https://github.com/adityasasidhar/browsercontrol/blob/main/README.es-ES.md">Español</a>
</p>

---

BrowserControl is an [MCP](https://modelcontextprotocol.io) server that lets Claude, Cursor, VS Code, or any other MCP client use a real Chromium browser on your machine.

After every action, the agent gets back a screenshot with a **numbered box on every button, link, and field**, plus the same list as text. To press the button marked 5, it calls `click(5)`. No CSS selectors, no guessing coordinates.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/assets/demo-dark.gif">
    <img alt="Animated demo: numbered boxes appear on a shop page, the agent types into box 5, clicks box 6, the numbers rebuild on the results page, and it clicks box 9 to add an item to the cart, while a transcript shows each tool call" src="https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/assets/demo-light.gif" width="720">
  </picture>
</p>

## Install

You need [uv](https://docs.astral.sh/uv/getting-started/installation/). Everything else, including the browser, is set up on first run.

**Codex** (installs the local MCP server and the BrowserControl skill):

```bash
codex plugin marketplace add adityasasidhar/browsercontrol
codex plugin add browsercontrol@browsercontrol
```

**Claude Code** (installs the server and a skill that teaches Claude to use it):

```text
/plugin marketplace add adityasasidhar/browsercontrol
/plugin install browsercontrol@browsercontrol
```

**OpenCode 2** (installs the local MCP server and the BrowserControl skill):

```bash
opencode plugin add github:adityasasidhar/browsercontrol
```

**VS Code or Cursor:** one click.

<a href="https://insiders.vscode.dev/redirect/mcp/install?name=browsercontrol&amp;config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22browsercontrol%22%5D%7D"><img src="https://img.shields.io/badge/VS_Code-Install-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white" alt="Install in VS Code"></a>
<a href="https://cursor.com/en/install-mcp?name=browsercontrol&amp;config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJicm93c2VyY29udHJvbCJdfQ%3D%3D"><img src="https://img.shields.io/badge/Cursor-Install-000000?style=flat-square&logo=cursor&logoColor=white" alt="Install in Cursor"></a>

**Anything else:** add this to your client's MCP config.

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

Restart your client and you're done. Setup for Claude Desktop, Gemini CLI, Zed, OpenCode, and others is in the [client guide](https://adityasasidhar.github.io/browsercontrol/guide/clients).

## Try it

Ask your agent something that needs a browser:

> Open Hacker News and tell me the top three stories.

> Go to my app on localhost:3000, sign up with a test account, and tell me if anything breaks.

> Find the cheapest flight from Berlin to Lisbon next Friday and show me the options.

## How it works

Each time the agent does something, BrowserControl waits for the page to settle, takes a screenshot, numbers everything you can interact with, and sends back both:

```text
Clicked element 5

Found 23 interactive elements:
  [1] a - Home
  [2] input[search] - Search products
  [3] button - Search
  [4] a - Sign in
  ...
```

The agent reads the picture to understand the page, then picks a number for its next action. Numbers are rebuilt after every step, so they always match what's on screen right now. If something has moved or gone, the tool says so instead of clicking the wrong thing.

This is called [Set of Marks](https://adityasasidhar.github.io/browsercontrol/concepts/set-of-marks). It works on any site, including ones with messy markup, iframes, and shadow DOM.

## What your agent can do

| | |
| --- | --- |
| **Browse** | Open pages, click, type, scroll, hover, drag, and press keys. `find("Checkout")` searches the whole page, not just what's visible. |
| **Batch** | `act([...])` runs several steps in one call and returns one screenshot, which saves time and tokens. |
| **Fill forms** | Pick from dropdowns, tick checkboxes, and upload files. |
| **Read and extract** | Get a page as Markdown, pull out tables and links, or extract fields into JSON. |
| **Use tabs and sessions** | Work across several tabs, or open isolated sessions side by side, each with its own cookies. |
| **Debug** | Read console logs, page errors, and network requests with their headers and bodies. Export a HAR file. |
| **Test edge cases** | Fake or block API responses, slow the network, go offline, and emulate phones, locations, timezones, and dark mode. |
| **Record** | Save Playwright traces, and turn what the agent did into a runnable Playwright test. |

See [all 79 tools](https://adityasasidhar.github.io/browsercontrol/reference/), with every parameter.

## Common setups

**Run it hidden.** The browser opens a visible window by default. To run it headless (servers, CI), set `BROWSER_HEADLESS`:

```json
"browsercontrol": {
  "command": "uvx",
  "args": ["browsercontrol"],
  "env": { "BROWSER_HEADLESS": "true" }
}
```

**Use your own Chrome.** Start Chrome with `--remote-debugging-port=9222`, then ask the agent to connect to it. It opens its own tab and leaves yours alone. [How to set it up](https://adityasasidhar.github.io/browsercontrol/recipes/your-chrome).

**Share one browser between clients.** Run it as an HTTP server, and point your clients at `http://127.0.0.1:8000/mcp`:

```bash
uvx browsercontrol --transport http
uvx browsercontrol --transport http --isolate-clients   # a separate session for each client
```

Every setting is listed in [Configuration](https://adityasasidhar.github.io/browsercontrol/reference/configuration).

## Good to know

- **It runs locally.** The browser runs on your machine. Nothing goes through a BrowserControl server.
- **Logins are kept.** The browser profile lives in `~/.browsercontrol/user_data`, so sites you sign in to stay signed in between runs.
- **It's built for vision models.** Every action returns an image. That gives the agent the full picture, but uses more tokens than text-only tools. See [how it compares](https://adityasasidhar.github.io/browsercontrol/concepts/comparison) to other approaches.
- **The HTTP mode has no authentication.** Keep it on `127.0.0.1` unless you put something in front of it.
- **Something not working?** Check [Troubleshooting](https://adityasasidhar.github.io/browsercontrol/help/troubleshooting), or [open an issue](https://github.com/adityasasidhar/browsercontrol/issues).

## For agents

The docs are built to be read by agents too: [`llms.txt`](https://adityasasidhar.github.io/browsercontrol/llms.txt) indexes every page, [`llms-full.txt`](https://adityasasidhar.github.io/browsercontrol/llms-full.txt) has all of it in one file, and [`tools.json`](https://adityasasidhar.github.io/browsercontrol/tools.json) lists every tool with its parameters. Any docs page is also available as Markdown by adding `.md` to its address.

## Contributing

Bug reports, fixes, and new tools are welcome.

```bash
git clone https://github.com/adityasasidhar/browsercontrol && cd browsercontrol
uv sync && uv run playwright install chromium
uv run pytest
```

The [contributing guide](https://adityasasidhar.github.io/browsercontrol/project/contributing) covers the checks, adding a tool, and working on the docs. Please also read [CONTRIBUTING.md](https://github.com/adityasasidhar/browsercontrol/blob/main/CONTRIBUTING.md).

## License

[MIT](https://github.com/adityasasidhar/browsercontrol/blob/main/LICENSE)

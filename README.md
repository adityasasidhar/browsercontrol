<p align="center">
  <img src="https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/assets/logo.png" alt="BrowserControl" width="140">
</p>

<h1 align="center">BrowserControl</h1>

<p align="center">
  <strong>Give your AI agent real browser superpowers.</strong><br>
  <sub>Vision-first browser automation for any MCP-compatible AI agent.</sub>
</p>

<p align="center">
  <a href="https://pypi.org/project/browsercontrol/"><img src="https://img.shields.io/pypi/v/browsercontrol?color=blue&label=PyPI" alt="PyPI"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.11+-3776ab.svg?logo=python&logoColor=white" alt="Python 3.11+"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT"></a>
  <a href="https://modelcontextprotocol.io/"><img src="https://img.shields.io/badge/MCP-compatible-7c3aed.svg" alt="MCP Compatible"></a>
  <a href="https://github.com/adityasasidhar/browsercontrol/stargazers"><img src="https://img.shields.io/github/stars/adityasasidhar/browsercontrol?style=social" alt="GitHub Stars"></a>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-the-secret-set-of-marks-som">How It Works</a> •
  <a href="#-available-tools">Tools</a> •
  <a href="#-configuration">Configuration</a> •
  <a href="#-examples">Examples</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

> **Ever wished Claude or Gemini could actually browse the web?** Not just fetch URLs, but truly **see**, **click**, **type**, and **interact** with any website like a human?

**BrowserControl** is an MCP server that gives your AI agent full browser access with a **vision-first approach**—no CSS selectors, no XPath, no guessing. Just point at numbers.

<br>

## ✨ What Makes This Different

<table>
<tr>
<td width="50%">

### ❌ Traditional Approach

```
"Find the button with class 'btn-primary'
that contains 'Submit' and is inside
form#contact-form..."
```

- Parse complex DOM structures
- Guess at CSS selectors
- No JavaScript support
- No login persistence
- No debugging tools

</td>
<td width="50%">

### ✅ BrowserControl

```
"click(7)"
```

- See the **rendered page** with numbered elements
- Just say **"click 5"** or **"type in 3"**
- Full **dynamic JavaScript** support
- **Persistent sessions** across restarts
- Complete **DevTools access**

</td>
</tr>
</table>

<br>

## 🎯 The Secret: Set of Marks (SoM)

Every screenshot comes annotated with **numbered red boxes** on interactive elements:

```
Found 15 interactive elements:
  [1] button - Sign In
  [2] input - Search...
  [3] a - Products
  [4] a - Pricing
  [5] button - Get Started
```

Your agent sees the numbers and simply calls `click(1)` to sign in. **No CSS selectors. No XPath. No guessing.**

<br>

## 🚀 Quick Start

### Installation

```bash
# Using pip
pip install browsercontrol

# Or with uv (recommended for faster installs)
uv add browsercontrol

# Chromium is auto-installed on first run—no extra steps needed!
```

### Run the Server

```bash
# Using the CLI
browsercontrol

# Or as a Python module
python -m browsercontrol

# Or with FastMCP
fastmcp run browsercontrol.server:mcp
```

### Connect to Your AI Agent

BrowserControl works with any MCP-compatible AI agent or IDE. Choose your platform:

<details>
<summary><b>Claude Desktop</b></summary>

Add to your Claude configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "browsercontrol": {
      "command": "browsercontrol"
    }
  }
}
```

Restart Claude Desktop, then ask:

> _"Go to GitHub and star the browsercontrol repo"_

</details>

<details>
<summary><b>� Gemini CLI / Google AI Studio</b></summary>

If using the Gemini CLI or Google AI Studio with MCP support:

```bash
# Set up MCP configuration
export MCP_SERVERS='{"browsercontrol": {"command": "browsercontrol"}}'

# Or add to your Gemini config file
```

For Google AI Studio, configure in the MCP settings panel.

</details>

<details>
<summary><b>🔧 Cline (VS Code Extension)</b></summary>

1. Install the [Cline extension](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev)
2. Open Cline settings (gear icon)
3. Navigate to "MCP Servers"
4. Add a new server:

```json
{
  "browsercontrol": {
    "command": "browsercontrol"
  }
}
```

</details>

<details>
<summary><b>🤖 Continue.dev (VS Code/JetBrains)</b></summary>

Add to your Continue configuration (`~/.continue/config.json`):

```json
{
  "mcpServers": [
    {
      "name": "browsercontrol",
      "command": "browsercontrol"
    }
  ]
}
```

</details>

<details>
<summary><b>🎯 Cursor IDE</b></summary>

1. Open Cursor Settings
2. Navigate to "Features" → "Model Context Protocol"
3. Add server configuration:

```json
{
  "browsercontrol": {
    "command": "browsercontrol"
  }
}
```

</details>

<details>
<summary><b>🔌 Zed Editor</b></summary>

Add to your Zed settings (`~/.config/zed/settings.json`):

```json
{
  "context_servers": {
    "browsercontrol": {
      "command": {
        "path": "browsercontrol"
      }
    }
  }
}
```

</details>

<details>
<summary><b>🐍 Custom Python Integration</b></summary>

Use the MCP Python SDK to integrate BrowserControl into your own agent:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Connect to BrowserControl
server_params = StdioServerParameters(
    command="browsercontrol",
    args=[],
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Initialize
        await session.initialize()

        # List available tools
        tools = await session.list_tools()

        # Call a tool
        result = await session.call_tool("navigate_to", {
            "url": "https://github.com"
        })
```

</details>

<details>
<summary><b>🚀 Using with uv or pipx</b></summary>

If you installed with `uv` or `pipx`, use the full path:

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

Or with pipx:

```json
{
  "mcpServers": {
    "browsercontrol": {
      "command": "pipx",
      "args": ["run", "browsercontrol"]
    }
  }
}
```

</details>

<details>
<summary><b>🔧 Advanced Configuration</b></summary>

You can pass environment variables to customize BrowserControl:

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

See [Configuration](#-configuration) for all available options.

</details>

<br>

## 🥊 Head-to-Head Comparison

| Feature                       | **BrowserControl** | Playwright MCP |    Stagehand     |   Browser-Use    |     AgentQL      |
| ----------------------------- | :----------------: | :------------: | :--------------: | :--------------: | :--------------: |
| **Vision-First (SoM)**        | ✅ Numbered boxes  |  ❌ Text tree  |   ⚠️ AI vision   |   ⚠️ AI vision   |   ❌ Selectors   |
| **Multi-Tab Support**         |  ✅ Full control   |  ⚠️ Implicit   |   ⚠️ Implicit    |     ⚠️ Basic     |     ❌ None      |
| **Cookie Management**         |  ✅ Direct tools   |   ⚠️ JS only   |    ⚠️ JS only    |     ⚠️ Basic     |     ❌ None      |
| **File Uploads**              |   ✅ Native tool   |   ⚠️ Manual    |      ❌ No       |      ❌ No       |      ❌ No       |
| **Developer Tools**           |     ✅ 8 tools     |    ❌ None     |     ❌ None      |     ❌ None      |     ❌ None      |
| **Session Recording**         |    ✅ Built-in     |   ⚠️ Manual    |     ❌ None      |     ❌ None      |     ❌ None      |
| **Persistent Sessions**       |    ✅ Automatic    |   ⚠️ Manual    |     ❌ None      |     ❌ None      |     ❌ None      |
| **Token Efficiency**          |    ✅ Tiny IDs     | ⚠️ Large tree  |  ❌ Full images  |  ❌ Full images  | ⚠️ Query results |
| **100% Local/Offline**        |       ✅ Yes       |     ✅ Yes     | ❌ Needs LLM API | ❌ Needs LLM API |  ❌ Cloud only   |
| **Monthly Cost (1k actions)** |       **$0**       |       $0       |     ~$30-50      |     ~$20-40      |      ~$50+       |

<br>

## 💪 Key Advantages

### 1. Multi-Tab Orchestration

Unlike other tools that get "lost" when a new window opens:

- `list_tabs()` — See every open page, title, and URL
- `switch_tab(index)` — Multitask between different sites
- `create_tab(url)` — Open references or parallel workflows

### 2. Session & Cookie Management

Stop fighting with login forms. Inject or inspect session state directly:

- `set_cookie()` — Log in instantly by injecting an auth token
- `get_cookies()` — Debug session issues or export state
- `clear_cookies()` — Fresh start without clearing the whole profile

### 3. Reliable File Uploads

Most AI agents fail when they hit a `<input type="file">`. BrowserControl uses native browser engine hooks:

- `upload_file(id, path)` — Just point at the button and the local file

### 4. Developer Tools Suite

Debug like a pro with tools no one else provides:

```python
get_console_logs()      # See browser errors
get_network_requests()  # Monitor API calls
get_page_errors()       # Catch JS exceptions
run_in_console(code)    # Debug in real-time
inspect_element(5)      # Get computed styles
get_page_performance()  # Core Web Vitals
```

### 5. Session Recording

```
start_recording()  →  Browse around  →  stop_recording()
                                              ↓
                               session_20260202.zip
                         (View with Playwright trace viewer)
```

### 6. Dynamic Viewport Control

Test responsive designs or emulate mobile screens on the fly:

- `set_viewport(width, height)` — Change resolution without restarting

### 7. True Persistence

| What Persists   | BrowserControl | Others |
| --------------- | :------------: | :----: |
| Cookies         |       ✅       |   ❌   |
| localStorage    |       ✅       |   ❌   |
| Session tokens  |       ✅       |   ❌   |
| Login state     |       ✅       |   ❌   |
| Browser history |       ✅       |   ❌   |

**Result**: Log in once, stay logged in across sessions.

<br>

## 🛠️ Available Tools

### Navigation

| Tool                        | Description               |
| --------------------------- | ------------------------- |
| `navigate_to(url)`          | Go to a URL               |
| `go_back()`                 | Navigate back             |
| `go_forward()`              | Navigate forward          |
| `refresh_page()`            | Reload the page           |
| `scroll(direction, amount)` | Scroll up/down/left/right |

### Interaction

| Tool                            | Description                           |
| ------------------------------- | ------------------------------------- |
| `click(element_id)`             | Click element by number               |
| `click_at(x, y)`                | Click at coordinates                  |
| `type_text(element_id, text)`   | Type into input field                 |
| `press_key(key)`                | Press keyboard key (Enter, Tab, etc.) |
| `hover(element_id)`             | Hover over element                    |
| `scroll_to_element(element_id)` | Scroll element into view              |
| `upload_file(element_id, path)` | Upload a file to an input             |
| `wait(seconds)`                 | Wait for page loading                 |

### Tab Management

| Tool                | Description                  |
| ------------------- | ---------------------------- |
| `create_tab(url)`   | Open a new browser tab       |
| `switch_tab(index)` | Switch to a tab by its index |
| `close_tab(index)`  | Close a specific tab         |
| `list_tabs()`       | List all open tabs and URLs  |

### Forms

| Tool                                 | Description            |
| ------------------------------------ | ---------------------- |
| `select_option(element_id, option)`  | Select dropdown option |
| `check_checkbox(element_id)`         | Toggle checkbox        |
| `upload_file(element_id, file_path)` | Upload file to input   |

### Content Extraction

| Tool                              | Description          |
| --------------------------------- | -------------------- |
| `get_page_content()`              | Get page as markdown |
| `get_text(element_id)`            | Get element text     |
| `get_page_info()`                 | Get URL and title    |
| `run_javascript(script)`          | Execute JavaScript   |
| `screenshot(annotate, full_page)` | Take screenshot      |

### Developer Tools

| Tool                           | Description               |
| ------------------------------ | ------------------------- |
| `get_console_logs()`           | Browser console output    |
| `get_network_requests()`       | API calls and responses   |
| `get_page_errors()`            | JavaScript errors         |
| `run_in_console(code)`         | Execute JS in console     |
| `inspect_element(id)`          | Element styles/properties |
| `get_cookies()`                | List browser cookies      |
| `set_cookie(name, value, ...)` | Set a cookie              |
| `delete_cookie(name)`          | Remove a cookie           |
| `clear_cookies()`              | Clear all cookies         |
| `set_viewport(width, height)`  | Change window size        |
| `get_page_performance()`       | Load times, Web Vitals    |

### Recording

| Tool                | Description             |
| ------------------- | ----------------------- |
| `start_recording()` | Begin session recording |
| `stop_recording()`  | Save recording          |
| `take_snapshot()`   | Save screenshot + HTML  |
| `list_recordings()` | View saved sessions     |

<br>

## ⚙️ Configuration

Configure via environment variables:

| Variable                  | Default                       | Description                |
| ------------------------- | ----------------------------- | -------------------------- |
| `BROWSER_HEADLESS`        | `true`                        | Run without visible window |
| `BROWSER_VIEWPORT_WIDTH`  | `1280`                        | Viewport width in pixels   |
| `BROWSER_VIEWPORT_HEIGHT` | `720`                         | Viewport height in pixels  |
| `BROWSER_TIMEOUT`         | `30000`                       | Navigation timeout (ms)    |
| `BROWSER_USER_DATA_DIR`   | `~/.browsercontrol/user_data` | Browser profile path       |
| `BROWSER_EXTENSION_PATH`  | —                             | Path to browser extension  |
| `LOG_LEVEL`               | `INFO`                        | Logging verbosity          |

**Examples:**

```bash
# Run with visible browser (for debugging)
BROWSER_HEADLESS=false browsercontrol

# Mobile viewport emulation
BROWSER_VIEWPORT_WIDTH=375 BROWSER_VIEWPORT_HEIGHT=812 browsercontrol

# Verbose logging
LOG_LEVEL=DEBUG browsercontrol
```

<br>

## 📖 Examples

### Web Research

```
You: "Go to Wikipedia and find out when Python was created"

Claude: *navigates to wikipedia.org*
        *types "Python programming language" in search*
        *clicks search result*
        *reads the page*

        "Python was created by Guido van Rossum and first released in 1991."
```

### Debug a Web App

```
You: "Go to my app at localhost:3000 and check for any errors"

Claude: *navigates to localhost:3000*
        *calls get_console_logs()*

        "I found 2 errors:
         [ERROR] Uncaught TypeError: Cannot read property 'map' of undefined
         [ERROR] Failed to load resource: 404 /api/users"

        *calls get_network_requests()*

        "The /api/users endpoint returned 404. Check your API route."
```

### Automated Testing with Recording

```
You: "Test the login flow on my site. Start recording."

Claude: *calls start_recording()*
        *navigates to site*
        *types email in element 3*
        *types password in element 4*
        *clicks Login button (element 5)*
        *verifies successful redirect*
        *calls stop_recording()*

        "Login test passed! Recording saved to session_20260202.zip"
```

### Form Automation

```
You: "Fill out the contact form on example.com"

Claude: *navigates to example.com/contact*
        *types name in element 2*
        *types email in element 3*
        *types message in element 4*
        *clicks Submit (element 5)*

        "Form submitted successfully!"
```

<br>

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│   AI Agent      │────▶│  BrowserControl  │────▶│   Browser   │
│ (Claude/Gemini) │◀────│   MCP Server     │◀────│ (Chromium)  │
└─────────────────┘     └──────────────────┘     └─────────────┘
        │                        │                      │
        │   "click(5)"           │   mouse.click()      │
        │◀───────────────────────│◀─────────────────────│
        │   [annotated           │   [screenshot +      │
        │    screenshot]         │    element map]      │
```

### How It Works

1. **AI sends command** — `click(5)`
2. **Server finds element** — Looks up element #5 from the last screenshot
3. **Browser acts** — Clicks at the element's coordinates
4. **Capture state** — Takes new screenshot, detects elements
5. **Annotate** — Draws numbered boxes on interactive elements
6. **Return to AI** — Sends annotated image + element list

<br>

## 📁 Project Structure

```
browsercontrol/
├── __init__.py          # Package exports
├── __main__.py          # CLI entry point
├── server.py            # MCP server setup
├── browser.py           # BrowserManager with SoM
├── config.py            # Environment configuration
└── tools/
    ├── navigation.py    # Navigation tools
    ├── interaction.py   # Click, type, hover tools
    ├── forms.py         # Form handling tools
    ├── content.py       # Content extraction tools
    ├── devtools.py      # Developer tools
    ├── recording.py     # Session recording tools
    └── tabs.py          # Tab management tools
```

<br>

## 🔧 Troubleshooting

<details>
<summary><b>"Missing X server" Error</b></summary>

Set `BROWSER_HEADLESS=true` or run with xvfb:

```bash
xvfb-run browsercontrol
```

</details>

<details>
<summary><b>Browser Not Starting</b></summary>

Chromium auto-installs on first run. If it fails, install manually:

```bash
python -m playwright install chromium
```

</details>

<details>
<summary><b>Session Not Persisting</b></summary>

Check that `BROWSER_USER_DATA_DIR` is writable:

```bash
ls -la ~/.browsercontrol/
```

</details>

<details>
<summary><b>Connection Refused</b></summary>

Ensure no other instance is running:

```bash
pkill -f browsercontrol
browsercontrol
```

</details>

<details>
<summary><b>View Session Recordings</b></summary>

Open recordings in the Playwright trace viewer:

```bash
npx playwright show-trace ~/.browsercontrol/recordings/session.zip
```

</details>

<br>

## 🤝 Contributing

Contributions are welcome! Check out our [Contributing Guide](CONTRIBUTING.md) for details.

**Ideas for contributions:**

- [ ] Firefox/WebKit support
- [ ] DOM diffing (detect changes)
- [ ] Accessibility audit tools
- [ ] Mobile emulation presets
- [ ] Cookie import/export files

```bash
# Clone and install
git clone https://github.com/adityasasidhar/browsercontrol
cd browsercontrol
uv sync

# Run tests
uv run pytest

# Run in development
uv run fastmcp dev browsercontrol/server.py
```

<br>

## 📄 License

[MIT License](LICENSE) — Use it however you want.

<br>

## 🙏 Acknowledgments

- Vision-first approach inspired by **Google's AntiGravity IDE**
- Built with [FastMCP](https://gofastmcp.com) and [Playwright](https://playwright.dev)
- Thanks to the MCP community for making AI-tool integration accessible

---

<p align="center">
  <strong>Built for AI agents that need to see the web.</strong>
</p>

<p align="center">
  <a href="https://github.com/adityasasidhar/browsercontrol">⭐ Star on GitHub</a> •
  <a href="https://github.com/adityasasidhar/browsercontrol/issues">🐛 Report Bug</a> •
  <a href="https://github.com/adityasasidhar/browsercontrol/issues">💡 Request Feature</a>
</p>

# BrowserControl

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

An MCP (Model Context Protocol) server that enables AI agents to browse the web with **Set of Marks (SoM)** - every screenshot shows numbered interactive elements, so AI can simply say "click element 5" instead of finding complex CSS selectors.

## Features

- 🎯 **Set of Marks (SoM)**: Screenshots with numbered bounding boxes on clickable elements
- 🖱️ **Simple Interaction**: `click(5)` instead of CSS selectors
- 📸 **Vision-First**: Every action returns an annotated screenshot
- 💾 **Persistent Sessions**: Cookies and localStorage survive restarts
- ⚙️ **Configurable**: Environment variables for all settings
- 🔒 **Headless by Default**: Works in server environments

## Installation

```bash
# Install with uv
uv add browsercontrol

# Or with pip
pip install browsercontrol

# Install Playwright browsers
playwright install chromium
```

## Quick Start

### Run the MCP Server

```bash
# Using the CLI
browsercontrol

# Or as a module
python -m browsercontrol

# Or with fastmcp
fastmcp run browsercontrol.server:mcp
```

### Configure Claude Desktop

Add to `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "browsercontrol": {
      "command": "browsercontrol"
    }
  }
}
```

Then ask Claude: *"Go to wikipedia.org and search for 'artificial intelligence'"*

## Available Tools

| Tool | Description |
|------|-------------|
| `navigate_to(url)` | Go to a URL |
| `go_back()` | Navigate back |
| `go_forward()` | Navigate forward |
| `refresh_page()` | Reload the page |
| `scroll(direction, amount)` | Scroll the page |
| `click(element_id)` | Click element by number |
| `click_at(x, y)` | Click at coordinates |
| `type_text(element_id, text)` | Type into input |
| `press_key(key)` | Press keyboard key |
| `hover(element_id)` | Hover over element |
| `scroll_to_element(element_id)` | Scroll to element |
| `wait(seconds)` | Wait for loading |
| `select_option(element_id, option)` | Select dropdown option |
| `check_checkbox(element_id)` | Toggle checkbox |
| `get_page_content()` | Get page as markdown |
| `get_text(element_id)` | Get element text |
| `get_page_info()` | Get URL and title |
| `run_javascript(script)` | Execute JS |
| `screenshot(annotate, full_page)` | Take screenshot |

## Configuration

Configure via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `BROWSER_HEADLESS` | `true` | Run without visible window |
| `BROWSER_VIEWPORT_WIDTH` | `1280` | Viewport width in pixels |
| `BROWSER_VIEWPORT_HEIGHT` | `720` | Viewport height in pixels |
| `BROWSER_TIMEOUT` | `30000` | Navigation timeout (ms) |
| `BROWSER_USER_DATA_DIR` | `~/.browsercontrol/user_data` | Browser profile path |
| `BROWSER_EXTENSION_PATH` | - | Path to browser extension |
| `LOG_LEVEL` | `INFO` | Logging level |

## How It Works

1. **Screenshot**: Captures the current page
2. **Detect Elements**: Finds all interactive elements (buttons, links, inputs)
3. **Annotate**: Draws numbered red boxes on each element
4. **Return**: Sends annotated image + element list to AI

The AI sees:
```
Found 15 interactive elements:
  [1] button - Sign In
  [2] input - Search...
  [3] a - Products
  [4] a - Pricing
  ...
```

Then it can simply call `click(1)` to click "Sign In"!

## Troubleshooting

### "Missing X server" Error
Set `BROWSER_HEADLESS=true` or run with `xvfb-run`.

### Browser Not Connecting
Make sure Playwright browsers are installed:
```bash
playwright install chromium
```

### Session Not Persisting
Check that `BROWSER_USER_DATA_DIR` is writable.

## Development

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

## License

MIT

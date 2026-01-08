# 🌐 BrowserControl

**Give your AI agent real browser superpowers.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Compatible-purple.svg)](https://modelcontextprotocol.io/)

Ever wished Claude, Gemini, or your custom AI agent could actually browse the web? Not just fetch URLs, but truly **see**, **click**, **type**, and **interact** with any website like a human?

**BrowserControl** is an MCP server that gives your AI agent full browser access with a vision-first approach inspired by Google's AntiGravity IDE.

---

## ✨ What Makes This Different

| Traditional Web Access | BrowserControl |
|------------------------|----------------|
| Fetch static HTML | See the **rendered page** |
| Parse complex DOM | Point at **numbered elements** |
| Guess at selectors | Just say **"click 5"** |
| No JavaScript support | Full **dynamic content** |
| No login persistence | **Persistent sessions** |

### The Secret: Set of Marks (SoM)

Every screenshot comes annotated with numbered boxes on interactive elements:

```
Found 15 interactive elements:
  [1] button - Sign In
  [2] input - Search...
  [3] a - Products
  [4] a - Pricing
```

Your agent sees the numbers and simply calls `click(1)` to sign in. No CSS selectors. No XPath. No guessing.

---

## 🚀 Quick Start

```bash
# Install
pip install browsercontrol
playwright install chromium

# Run
browsercontrol
```

### Connect to Claude Desktop

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

Then just ask:

> *"Go to GitHub and star the browsercontrol repo"*

Claude will navigate, find the star button, and click it—showing you screenshots along the way.

---

## 🛠️ Available Tools

| Tool | What it does |
|------|--------------|
| `navigate_to(url)` | Open any webpage |
| `click(element_id)` | Click element by its number |
| `type_text(element_id, text)` | Type into inputs |
| `scroll(direction, amount)` | Scroll the page |
| `press_key(key)` | Press Enter, Tab, Escape, etc. |
| `get_page_content()` | Extract page as markdown |
| `screenshot()` | Capture current state |
| `wait(seconds)` | Wait for loading |
| + 10 more... | Full browser control |

---

## ⚙️ Configuration

```bash
# Run with visible browser (debugging)
BROWSER_HEADLESS=false browsercontrol

# Custom viewport
BROWSER_VIEWPORT_WIDTH=1920 BROWSER_VIEWPORT_HEIGHT=1080 browsercontrol

# Verbose logging
LOG_LEVEL=DEBUG browsercontrol
```

| Variable | Default | Description |
|----------|---------|-------------|
| `BROWSER_HEADLESS` | `true` | Hide browser window |
| `BROWSER_VIEWPORT_WIDTH` | `1280` | Width in pixels |
| `BROWSER_VIEWPORT_HEIGHT` | `720` | Height in pixels |
| `BROWSER_TIMEOUT` | `30000` | Navigation timeout (ms) |
| `BROWSER_USER_DATA_DIR` | `~/.browsercontrol/user_data` | Persistent storage |

---

## 🔮 Use Cases

- **Automated Research**: Have your agent browse documentation, gather information
- **Form Filling**: Fill out applications, surveys, registrations
- **Testing**: Let AI test your web app like a real user
- **Social Media**: Post updates, check notifications (carefully!)
- **Shopping**: Compare prices, add to cart
- **Anything a human can do in a browser**

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│   AI Agent      │────▶│  BrowserControl  │────▶│   Browser   │
│ (Claude/Gemini) │◀────│   MCP Server     │◀────│ (Chromium)  │
└─────────────────┘     └──────────────────┘     └─────────────┘
        │                        │                      │
        │   "click(5)"          │   mouse.click()      │
        │◀──────────────────────│◀─────────────────────│
        │   [screenshot +       │   [annotated         │
        │    element list]      │    image]            │
```

---

## 📦 Installation Options

```bash
# With pip
pip install browsercontrol

# With uv (recommended)
uv add browsercontrol

# From source
git clone https://github.com/adityasasidhar/browsercontrol
cd browsercontrol
uv sync
```

Don't forget to install Playwright browsers:
```bash
playwright install chromium
```

---

## 🤝 Contributing

PRs welcome! Some ideas:
- [ ] Multi-tab support
- [ ] Video recording
- [ ] Mobile viewport presets
- [ ] Cookie import/export

---

## 📄 License

MIT - Use it however you want.

---

**Built with ❤️ for the AI agent community.**

*Inspired by the browser control capabilities in Google's AntiGravity IDE.*

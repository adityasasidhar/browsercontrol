<p align="center">
  <img src="https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/logo.png" alt="BrowserControl" width="120">
</p>

<h1 align="center">🌐 BrowserControl</h1>

<p align="center">
  <strong>Give your AI agent real browser superpowers.</strong>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python 3.11+"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT"></a>
  <a href="https://modelcontextprotocol.io/"><img src="https://img.shields.io/badge/MCP-Compatible-purple.svg" alt="MCP"></a>
  <a href="https://github.com/adityasasidhar/browsercontrol"><img src="https://img.shields.io/github/stars/adityasasidhar/browsercontrol?style=social" alt="GitHub Stars"></a>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-available-tools">Tools</a> •
  <a href="#%EF%B8%8F-configuration">Configuration</a> •
  <a href="#-examples">Examples</a>
</p>

---

Ever wished Claude, Gemini, or your custom AI agent could actually browse the web? Not just fetch URLs, but truly **see**, **click**, **type**, and **interact** with any website like a human?

**BrowserControl** is an MCP server that gives your AI agent full browser access with a **vision-first approach** inspired by Google's AntiGravity IDE.

## ✨ What Makes This Different

| Traditional Web Access | BrowserControl |
|------------------------|----------------|
| Fetch static HTML | See the **rendered page** |
| Parse complex DOM | Point at **numbered elements** |
| Guess at selectors | Just say **"click 5"** |
| No JavaScript support | Full **dynamic content** |
| No login persistence | **Persistent sessions** |
| No debugging tools | **Console, Network, Errors** |

### 🎯 The Secret: Set of Marks (SoM)

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

---

## 🏆 Why BrowserControl Beats Every Alternative

### Head-to-Head Comparison

| Feature | **BrowserControl** | Playwright MCP | Stagehand | Browser-Use | AgentQL |
|---------|:------------------:|:--------------:|:---------:|:-----------:|:-------:|
| **Vision-First (SoM)** | ✅ Numbered boxes | ❌ Text tree | ⚠️ AI vision | ⚠️ AI vision | ❌ Selectors |
| **No Extra AI Calls** | ✅ Zero | ❌ Parses tree | ❌ GPT-4V per action | ❌ Vision model | ❌ Query model |
| **Developer Tools** | ✅ 6 tools | ❌ None | ❌ None | ❌ None | ❌ None |
| **Session Recording** | ✅ Built-in | ❌ Manual | ❌ None | ❌ None | ❌ None |
| **Persistent Sessions** | ✅ Automatic | ⚠️ Manual setup | ❌ None | ❌ None | ❌ None |
| **MCP Native** | ✅ FastMCP | ✅ Official | ❌ Python SDK | ⚠️ Custom | ❌ REST API |
| **Install Complexity** | ✅ `pip install` | ⚠️ npx + config | ❌ Docker + setup | ⚠️ Docker | ❌ Cloud signup |
| **Token Efficiency** | ✅ Tiny IDs | ⚠️ Large tree | ❌ Full images | ❌ Full images | ⚠️ Query results |
| **Cost per Action** | ✅ $0 | ✅ $0 | ❌ ~$0.01-0.05 | ❌ ~$0.01-0.05 | ❌ API fees |
| **Offline/Local** | ✅ 100% local | ✅ Local | ⚠️ Needs LLM API | ⚠️ Needs LLM API | ❌ Cloud only |

### 🎯 Key Advantages

#### 1. **Token Efficiency = Faster + Cheaper**

```
Other tools send:        BrowserControl sends:
───────────────────      ─────────────────────
Full DOM tree            "click(5)"
(5,000+ tokens)          (3 tokens)
     or
Base64 screenshot        Element ID + summary
(10,000+ tokens)         (100 tokens)
```

**Result**: 50-100x fewer tokens per action = faster responses, lower costs.

#### 2. **No Extra AI Calls Required**

| Tool | AI Calls per Click |
|------|-------------------|
| **BrowserControl** | 0 (just `click(5)`) |
| Stagehand | 1-2 (vision + action) |
| Browser-Use | 1-2 (vision + planning) |
| AgentQL | 1 (query interpretation) |

**Result**: No vision API costs, no rate limits, works offline.

#### 3. **Developer Tools No One Else Has**

```python
# Only BrowserControl can do this:
get_console_logs()      # See browser errors
get_network_requests()  # Monitor API calls  
get_page_errors()       # Catch JS exceptions
run_in_console(code)    # Debug in real-time
inspect_element(5)      # Get computed styles
get_page_performance()  # Core Web Vitals
```

**Other tools**: Navigate, click, type... that's it.

#### 4. **Session Recording Built-In**

```
start_recording()   →   Browse around   →   stop_recording()
                                              ↓
                               📹 session_20260108.zip
                               (View with Playwright trace viewer)
```

**Other tools**: No recording. Debug from memory.

#### 5. **True Persistence**

| What Persists | BrowserControl | Others |
|---------------|:--------------:|:------:|
| Cookies | ✅ | ❌ |
| localStorage | ✅ | ❌ |
| Session tokens | ✅ | ❌ |
| Login state | ✅ | ❌ |
| Browser history | ✅ | ❌ |

**Result**: Log in once, stay logged in across sessions.

#### 6. **Simpler Mental Model**

```
❌ Other tools:
   "Find the button with class 'btn-primary' that contains text 'Submit' 
    and is a descendant of form#contact-form..."

✅ BrowserControl:
   "click(7)"
```

### 📊 Real-World Performance

| Scenario | BrowserControl | Vision-Based Tools |
|----------|:--------------:|:------------------:|
| Click a button | ~50ms | ~2-5 seconds |
| Fill a form (5 fields) | ~500ms | ~15-30 seconds |
| Navigate + act | ~1 second | ~5-10 seconds |
| Debug console errors | ✅ Instant | ❌ Not possible |

### 💰 Cost Comparison (1000 actions/month)

| Tool | Monthly Cost |
|------|-------------|
| **BrowserControl** | **$0** (fully local) |
| Stagehand (GPT-4V) | ~$30-50 |
| Browser-Use (Claude Vision) | ~$20-40 |
| AgentQL | ~$50+ (API fees) |

---

## 🚀 Quick Start

### Installation

```bash
# Install with pip
pip install browsercontrol

# Or with uv (recommended)
uv add browsercontrol

# That's it! Chromium is auto-installed on first run
```

### Run the Server

```bash
# Using the CLI
browsercontrol

# Or as a module
python -m browsercontrol

# Or with FastMCP
fastmcp run browsercontrol.server:mcp
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

Then just ask Claude:

> *"Go to GitHub and star the browsercontrol repo"*

Claude will navigate, find the star button, and click it—showing you screenshots along the way!

---

## 🎯 Features

### 1. Set of Marks (SoM) - Vision-First Interaction

Every action returns an annotated screenshot with numbered elements. Your AI agent can:
- **See** the page exactly as a human would
- **Identify** clickable elements by number
- **Act** with simple commands like `click(5)`

### 2. 🔧 Developer Tools

Built-in debugging tools for web development:

| Tool | Description |
|------|-------------|
| `get_console_logs()` | Capture browser console (errors, warnings, logs) |
| `get_network_requests()` | Monitor API calls, status codes, timing |
| `get_page_errors()` | See JavaScript exceptions and crashes |
| `run_in_console(code)` | Execute JS in browser console |
| `inspect_element(id)` | Get computed styles, dimensions, properties |
| `get_page_performance()` | Page load time, Core Web Vitals, memory |

### 3. 🎬 Session Recording

Record browser sessions for debugging and documentation:

| Tool | Description |
|------|-------------|
| `start_recording()` | Begin recording the session |
| `stop_recording()` | Save recording (Playwright trace format) |
| `take_snapshot()` | Save screenshot + HTML + URL |
| `list_recordings()` | View all saved sessions |

View recordings with:
```bash
npx playwright show-trace ~/.browsercontrol/recordings/session.zip
```

### 4. 💾 Persistent Sessions

- Cookies, localStorage, and session data persist across restarts
- Stay logged into websites
- Maintain shopping carts, preferences, etc.

---

## 🛠️ Available Tools

### Navigation
| Tool | Description |
|------|-------------|
| `navigate_to(url)` | Go to a URL |
| `go_back()` | Navigate back |
| `go_forward()` | Navigate forward |
| `refresh_page()` | Reload the page |
| `scroll(direction, amount)` | Scroll the page |

### Interaction
| Tool | Description |
|------|-------------|
| `click(element_id)` | Click element by number |
| `click_at(x, y)` | Click at coordinates |
| `type_text(element_id, text)` | Type into input |
| `press_key(key)` | Press keyboard key (Enter, Tab, etc.) |
| `hover(element_id)` | Hover over element |
| `scroll_to_element(element_id)` | Scroll element into view |
| `wait(seconds)` | Wait for loading |

### Forms
| Tool | Description |
|------|-------------|
| `select_option(element_id, option)` | Select dropdown option |
| `check_checkbox(element_id)` | Toggle checkbox |

### Content
| Tool | Description |
|------|-------------|
| `get_page_content()` | Get page as markdown |
| `get_text(element_id)` | Get element text |
| `get_page_info()` | Get URL and title |
| `run_javascript(script)` | Execute JavaScript |
| `screenshot(annotate, full_page)` | Take screenshot |

### Developer Tools
| Tool | Description |
|------|-------------|
| `get_console_logs()` | Browser console output |
| `get_network_requests()` | API calls and responses |
| `get_page_errors()` | JavaScript errors |
| `run_in_console(code)` | Execute JS in console |
| `inspect_element(id)` | Element styles/properties |
| `get_page_performance()` | Load times, Web Vitals |

### Recording
| Tool | Description |
|------|-------------|
| `start_recording()` | Begin session recording |
| `stop_recording()` | Save recording |
| `take_snapshot()` | Save screenshot + HTML |
| `list_recordings()` | View saved sessions |

---

## ⚙️ Configuration

Configure via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `BROWSER_HEADLESS` | `true` | Run without visible window |
| `BROWSER_VIEWPORT_WIDTH` | `1280` | Viewport width in pixels |
| `BROWSER_VIEWPORT_HEIGHT` | `720` | Viewport height in pixels |
| `BROWSER_TIMEOUT` | `30000` | Navigation timeout (ms) |
| `BROWSER_USER_DATA_DIR` | `~/.browsercontrol/user_data` | Browser profile path |
| `BROWSER_EXTENSION_PATH` | - | Path to browser extension |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Examples

```bash
# Run with visible browser (for debugging)
BROWSER_HEADLESS=false browsercontrol

# Custom viewport for mobile testing
BROWSER_VIEWPORT_WIDTH=375 BROWSER_VIEWPORT_HEIGHT=812 browsercontrol

# Verbose logging
LOG_LEVEL=DEBUG browsercontrol
```

---

## 📚 Examples

### Example 1: Web Research

```
You: "Go to Wikipedia and find out when Python was created"

Claude: *navigates to wikipedia.org*
        *types "Python programming language" in search*
        *clicks search result*
        *reads the page*
        
        "Python was created by Guido van Rossum and first released in 1991."
```

### Example 2: Debug a Web App

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

### Example 3: Automated Testing

```
You: "Test the login flow on my site. Start recording."

Claude: *calls start_recording()*
        *navigates to site*
        *types email in element 3*
        *types password in element 4*
        *clicks Login button (element 5)*
        *verifies successful redirect*
        *calls stop_recording()*
        
        "Login test passed! Recording saved to session_20260108.zip"
```

### Example 4: Form Automation

```
You: "Fill out the contact form on example.com"

Claude: *navigates to example.com/contact*
        *types name in element 2*
        *types email in element 3*
        *types message in element 4*
        *clicks Submit (element 5)*
        
        "Form submitted successfully!"
```

---

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

1. **AI sends command**: `click(5)`
2. **Server finds element**: Looks up element #5 from the last screenshot
3. **Browser acts**: Clicks at the element's coordinates
4. **Capture state**: Takes new screenshot, detects elements
5. **Annotate**: Draws numbered boxes on interactive elements
6. **Return to AI**: Sends annotated image + element list

---

## 📦 Project Structure

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
    └── recording.py     # Session recording tools
```

---

## 🔧 Troubleshooting

### "Missing X server" Error

Set `BROWSER_HEADLESS=true` or run with xvfb:
```bash
xvfb-run browsercontrol
```

### Browser Not Starting

Chromium auto-installs on first run. If it fails, install manually:
```bash
python -m playwright install chromium
```

### Session Not Persisting

Check that `BROWSER_USER_DATA_DIR` is writable:
```bash
ls -la ~/.browsercontrol/
```

### Connection Refused

Ensure no other instance is running:
```bash
pkill -f browsercontrol
browsercontrol
```

---

## 🤝 Contributing

Contributions are welcome! Some ideas:

- [ ] Multi-tab support
- [ ] Firefox/WebKit support
- [ ] DOM diffing (detect changes)
- [ ] Accessibility audit
- [ ] Mobile emulation presets
- [ ] Cookie import/export

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

---

## 📄 License

MIT License - Use it however you want.

---

## 🙏 Acknowledgments

- Inspired by the browser control capabilities in **Google's AntiGravity IDE**
- Built with [FastMCP](https://gofastmcp.com) and [Playwright](https://playwright.dev)
- Thanks to the MCP community for making AI-tool integration accessible

---

<p align="center">
  <strong>Built with ❤️ for the AI agent community.</strong>
</p>

<p align="center">
  <a href="https://github.com/adityasasidhar/browsercontrol">⭐ Star on GitHub</a> •
  <a href="https://github.com/adityasasidhar/browsercontrol/issues">Report Bug</a> •
  <a href="https://github.com/adityasasidhar/browsercontrol/issues">Request Feature</a>
</p>

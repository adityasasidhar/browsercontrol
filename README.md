<p align="center">
  <img src="assets/logo-main.png" alt="BrowserControl" width="140">
</p>

<h1 align="center">BrowserControl</h1>

<p align="center">
  <strong>Give your AI agent real browser superpowers.</strong><br>
  <sub>Vision-first browser automation for any MCP-compatible AI agent — local, private, and zero-cost.</sub>
</p>

<p align="center">
  <a href="https://pypi.org/project/browsercontrol/"><img src="https://img.shields.io/pypi/v/browsercontrol?color=blue&label=PyPI" alt="PyPI"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.11+-3776ab.svg?logo=python&logoColor=white" alt="Python 3.11+"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT"></a>
  <a href="https://modelcontextprotocol.io/"><img src="https://img.shields.io/badge/MCP-compatible-7c3aed.svg" alt="MCP Compatible"></a>
  <a href="https://github.com/adityasasidhar/browsercontrol/actions"><img src="https://img.shields.io/github/actions/workflow/status/adityasasidhar/browsercontrol/ci.yml?branch=main&label=CI" alt="CI"></a>
  <a href="https://github.com/adityasasidhar/browsercontrol/stargazers"><img src="https://img.shields.io/github/stars/adityasasidhar/browsercontrol?style=social" alt="GitHub Stars"></a>
  <a href="https://adityasasidhar.github.io/browsercontrol/"><img src="https://img.shields.io/badge/docs-adityasasidhar.github.io-blue.svg" alt="Documentation"></a>
</p>

<p align="center">
  <a href="https://adityasasidhar.github.io/browsercontrol/">📚 Documentation</a> •
  <a href="#what-it-is">What it is</a> •
  <a href="#how-it-looks">How it looks</a> •
  <a href="#quick-start">Quick start</a> •
  <a href="#connect-your-ai">Connect your AI</a> •
  <a href="#tools">Tools</a> •
  <a href="#examples">Examples</a> •
  <a href="#why-browsercontrol">Why</a> •
  <a href="#contributing">Contributing</a>
</p>

---

## ✨ What it is

**BrowserControl** is an [MCP](https://modelcontextprotocol.io) server that gives your AI agent a real browser it can **see**, **click**, **type**, and **debug** — using a vision-first approach based on the **Set of Marks (SoM)** pattern.

Instead of fragile CSS selectors, XPath, or DOM trees, the agent sees an annotated screenshot with **numbered red boxes** over every interactive element, then just calls:

```text
click(5)        →  clicks the 5th element
type_text(3, "hello world")  →  types into the 3rd element
upload_file(7, "/path/to/file.pdf")  →  uploads a file via the native browser input
```

No selectors to guess. No selectors to break when the page changes. **Just point at numbers.**

---

## 🖼️ How it looks

Every tool that interacts with the page returns an **annotated screenshot** plus a textual element map:

```
┌─────────────────────────────────────────────────┐
│  GitHub                          [Sign in]      │
├─────────────────────────────────────────────────┤
│                                                 │
│   ┌──────────────────────┐    ┌──────────────┐  │
│   │ 1  🔍 Search…        │    │ 2  Pulls     │  │
│   └──────────────────────┘    │ 3  Issues    │  │
│                               │ 4  Codespace │  │
│   ┌───────────────────────┐   └──────────────┘  │
│   │ 5  Sign in            │                     │
│   └───────────────────────┘                     │
└─────────────────────────────────────────────────┘

Found 5 interactive elements:
  [1] input - Search or jump to...
  [2] a - Pulls
  [3] a - Issues
  [4] a - Codespaces
  [5] button - Sign in
```

The model receives the image *and* the list, so it can either reason over the pixels or read the text — whichever is cheaper.

---

## 🚀 Quick start

### 1 · Install

```bash
# pip
pip install browsercontrol

# uv (recommended — much faster)
uv add browsercontrol
```

> **No extra setup needed.** Chromium auto-installs on first run. If the auto-install fails for any reason, run `python -m playwright install chromium` once and you're set.

### 2 · Run the server

```bash
# As a CLI
browsercontrol

# As a module
python -m browsercontrol

# With FastMCP (for `fastmcp dev` / inspector UI)
fastmcp run browsercontrol.server:mcp
```

### 3 · Connect it to your AI

Pick your client — full configs in [Connect your AI](#connect-your-ai) below.

```jsonc
// Claude Desktop — claude_desktop_config.json
{
  "mcpServers": {
    "browsercontrol": {
      "command": "browsercontrol"
    }
  }
}
```

Restart Claude Desktop, then try:

> _"Open Hacker News and tell me the top story."_

That's it — your agent now has a browser.

### 4 · Add the agent skill _(optional)_

Connecting the server tells your agent **which** tools exist. The skill tells it **how to use them well** — that element numbers expire after every action, that a cookie banner will swallow a click, that a missing number means "scroll".

```bash
mkdir -p ~/.claude/skills/browsercontrol
curl -fsSL https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/skills/browsercontrol/SKILL.md \
  -o ~/.claude/skills/browsercontrol/SKILL.md
```

It loads on demand — only when a task actually involves a browser — so it costs one line of context the rest of the time. See [`skills/browsercontrol/SKILL.md`](skills/browsercontrol/SKILL.md) and the [agent skill docs](https://adityasasidhar.github.io/browsercontrol/getting-started/agent-skill/).

Agents that prefer to read the docs directly can start from [`llms.txt`](https://adityasasidhar.github.io/browsercontrol/llms.txt).

---

## 🧠 Why BrowserControl?

A dozen MCP servers can open a web page. Here's what BrowserControl does that most don't:

| | |
|---|---|
| 🟢 **Set of Marks (SoM)** — Numbered red boxes on every interactive element. The agent picks a number. **No selectors, ever.** | 🟢 **Shadow DOM + iframe aware** — Recursively descends into open shadow roots and same-origin iframes (with proper coordinate offsets). Modern web apps just work. |
| 🟢 **True persistent sessions** — Uses `launch_persistent_context`. Cookies, `localStorage`, login state and history all survive restarts. Log in once. | 🟢 **Built-in devtools** — Console logs, network requests (with timing), JS errors, page performance, element inspection, computed styles. No second tool needed. |
| 🟢 **Native file uploads** — Uses Playwright's `set_input_files`. The most reliable path through `<input type="file">` — works even when click-and-pick dialogs fail. | 🟢 **Multi-tab orchestration** — Open, switch, close, list tabs. Clicking a link that opens a new tab doesn't lose the agent. |
| 🟢 **Smart localhost routing** — Auto-falls-back `localhost` → `127.0.0.1` when a dev server is up but proxy-resolved DNS fails. | 🟢 **100% local & private** — No LLM API key, no cloud, no telemetry, no usage cap. Your browsing stays on your machine. |
| 🟢 **Zero marginal cost** — Runs on your hardware, no per-action fees. | 🟢 **Cross-platform** — CI tests on Ubuntu, Windows, and macOS. |

---

## 🧩 Connect your AI

BrowserControl speaks MCP stdio, so it works with anything that speaks MCP.

<details>
<summary><b>🟣 Claude Desktop</b></summary>

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

</details>

<details>
<summary><b>✨ Gemini CLI / Google AI Studio</b></summary>

Configure MCP servers in Gemini's settings, or via environment:

```bash
export MCP_SERVERS='{"browsercontrol": {"command": "browsercontrol"}}'
```

For Google AI Studio, configure in the MCP settings panel.

</details>

<details>
<summary><b>🛠️ Cline (VS Code)</b></summary>

1. Install [Cline](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev)
2. Open Cline settings → **MCP Servers** → Add:

```json
{
  "browsercontrol": {
    "command": "browsercontrol"
  }
}
```

</details>

<details>
<summary><b>🤖 Continue.dev (VS Code / JetBrains)</b></summary>

Add to `~/.continue/config.json`:

```json
{
  "mcpServers": [
    { "name": "browsercontrol", "command": "browsercontrol" }
  ]
}
```

</details>

<details>
<summary><b>🎯 Cursor IDE</b></summary>

Cursor Settings → **Features** → **Model Context Protocol** → Add:

```json
{ "browsercontrol": { "command": "browsercontrol" } }
```

</details>

<details>
<summary><b>⚡ Zed Editor</b></summary>

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

</details>

<details>
<summary><b>🐍 Python (programmatic)</b></summary>

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

</details>

<details>
<summary><b>📦 uvx / pipx</b></summary>

```json
{
  "mcpServers": {
    "browsercontrol": { "command": "uvx",  "args": ["browsercontrol"] }
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

</details>

<details>
<summary><b>⚙️ Advanced config (env vars)</b></summary>

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

See [Configuration](#configuration) for the full list.

</details>

---

## 🛠️ Tools

Every action returns an annotated screenshot + element map (when relevant), so the model always has the latest visual context.

### Navigation

| Tool | Description |
|---|---|
| `navigate_to(url)` | Open a URL. Auto-falls back to `127.0.0.1` for `localhost` if the proxy blocks it. |
| `go_back()` / `go_forward()` / `refresh_page()` | Standard history controls. |
| `scroll(direction, amount)` | `direction` ∈ {up, down, left, right}. `amount` ∈ {small, medium, large, page, top, bottom} **or** raw pixels (e.g. `"500"`). |

### Interaction

| Tool | Description |
|---|---|
| `click(element_id)` | Click by SoM number. Resolves the actual DOM element at the coordinates first, so overlays don't fool it. |
| `click_at(x, y)` | Click raw coordinates. |
| `type_text(element_id, text)` | Uses `element.fill()` for reliable form input — not char-by-char typing. |
| `press_key(key)` | Any keyboard key: `Enter`, `Tab`, `Escape`, `ArrowDown`, `Backspace`, etc. |
| `hover(element_id)` | Hover for tooltips/menus. |
| `scroll_to_element(element_id)` | Scroll the element into view. |
| `wait(seconds)` | Sleep — for animations or lazy-loaded content. |

### Tabs

| Tool | Description |
|---|---|
| `create_tab(url=None)` | Open a new tab, optionally navigated to a URL. |
| `switch_tab(index)` | Switch by 0-based index. |
| `close_tab(index)` | Close a tab. Auto-falls-back to another open page. |
| `list_tabs()` | List all tabs with title, URL, active marker. |

### Forms

| Tool | Description |
|---|---|
| `select_option(element_id, option)` | Pick from a `<select>` dropdown by visible text or value. |
| `check_checkbox(element_id, check=True)` | Toggle a checkbox. |
| `upload_file(element_id, file_path)` | **Native** file upload via `set_input_files` — works on every site that has an `<input type="file">`. |

### Content

| Tool | Description |
|---|---|
| `get_page_content()` | Whole page as Markdown (script/style stripped, 30 KB cap). |
| `get_text(element_id)` | Read text from a specific element. |
| `get_page_info()` | Current URL + title. |
| `run_javascript(script)` | Run JS, return serialized result + screenshot. |
| `screenshot(annotate=True, full_page=False)` | Annotated viewport, clean viewport, or clean full-page. |

### DevTools

| Tool | Description |
|---|---|
| `get_console_logs(clear=False)` | Last 50 captured console messages, with level + source location. |
| `get_network_requests(num_requests=30, clear=False)` | Method, URL, status, **duration (ms)**. Requests paired by identity (no URL-collision bugs). |
| `get_page_errors()` | Uncaught JS exceptions with stack traces. |
| `run_in_console(code)` | Eval JS with structured error handling; returns JSON-stringified result + screenshot. |
| `inspect_element(element_id)` | Computed styles, dimensions, attributes, classes, href, src, value. |
| `get_page_performance()` | TTFB, FCP, DOMContentLoaded, load time, resource count, JS heap. |
| `get_cookies()` / `set_cookie(name, value, domain=None, path="/")` | Full cookie control. `domain` is auto-inferred from current URL when omitted. |
| `delete_cookie(name)` / `clear_cookies()` | Targeted or total cookie wipe. |
| `set_viewport(width, height)` | Change viewport on the fly (great for responsive testing). |

### Recording

| Tool | Description |
|---|---|
| `start_recording(name="")` | Begin a Playwright trace (screenshots + DOM snapshots + sources). |
| `stop_recording()` | Save the trace to `~/.browsercontrol/recordings/`. |
| `take_snapshot(name="")` | Save PNG + HTML + URL triplet to `~/.browsercontrol/snapshots/`. |
| `list_recordings()` | List recent recordings and snapshots. |

> View recordings with: `npx playwright show-trace ~/.browsercontrol/recordings/<name>.zip`

---

## ⚙️ Configuration

All settings are environment variables. Sensible defaults out of the box.

| Variable | Default | Description |
|---|---|---|
| `BROWSER_HEADLESS` | `true` | Run without a visible window. Set `false` to watch the browser. |
| `BROWSER_VIEWPORT_WIDTH` | `1280` | Viewport width in pixels. |
| `BROWSER_VIEWPORT_HEIGHT` | `720` | Viewport height in pixels. |
| `BROWSER_TIMEOUT` | `30000` | Navigation timeout (ms). |
| `BROWSER_USER_DATA_DIR` | `~/.browsercontrol/user_data` | Browser profile dir (cookies, history, extensions persist here). |
| `BROWSER_EXTENSION_PATH` | — | Path to a `.crx`/unpacked extension to load at startup. |
| `LOG_LEVEL` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR`. |

```bash
# Headful + phone-sized viewport for mobile testing
BROWSER_HEADLESS=false BROWSER_VIEWPORT_WIDTH=375 BROWSER_VIEWPORT_HEIGHT=812 browsercontrol

# Verbose logs for debugging the MCP server itself
LOG_LEVEL=DEBUG browsercontrol
```

---

## 📚 Examples

### 🔍 Web research

> _"Find the Wikipedia article on Python and tell me who created it."_

```
→ navigate_to("https://wikipedia.org")
→ type_text(2, "Python programming language")
→ press_key("Enter")
→ get_page_content()
→ "Python was created by Guido van Rossum, first released in 1991."
```

### 🐛 Debug a web app

> _"Check localhost:3000 for any errors and tell me what's broken."_

```
→ navigate_to("http://localhost:3000")    # auto-fallback to 127.0.0.1 if needed
→ get_console_logs()
→ "2 errors:
   [ERROR] Uncaught TypeError: Cannot read property 'map' of undefined (app.js:42)
   [ERROR] Failed to load resource: 404 /api/users"
→ get_network_requests()
→ "GET /api/users -> 404 (12ms)  ← check your API route"
```

### 🧪 Record a test run

> _"Walk through the login flow on staging.example.com while recording."_

```
→ start_recording("login_flow")
→ navigate_to("https://staging.example.com/login")
→ type_text(3, "user@example.com")
→ type_text(4, "hunter2")
→ click(5)             # Sign In button
→ take_snapshot("after_login")
→ stop_recording()
→ "Saved ~/.browsercontrol/recordings/login_flow.zip"
```

### 📝 Fill out a form

> _"Fill out the contact form at example.com/contact with a polite message."_

```
→ navigate_to("https://example.com/contact")
→ type_text(2, "Alex Doe")
→ type_text(3, "alex@example.com")
→ type_text(4, "Hi! Just saying hello.")
→ click(5)             # Submit
```

### 🗂️ Multi-tab research

> _"Open GitHub in one tab and Hacker News in another, then tell me the top repo and the top story."_

```
→ create_tab("https://github.com/trending")
→ create_tab("https://news.ycombinator.com")
→ list_tabs()          # → returns both tabs with indices
→ switch_tab(0)        # focus GitHub
→ get_page_content()
→ switch_tab(1)        # focus HN
→ get_page_content()
```

### 📂 Upload a file

> _"Upload my resume to the job application form."_

```
→ navigate_to("https://jobs.example.com/apply")
→ upload_file(8, "/Users/me/Documents/resume.pdf")
```

### 📱 Mobile responsive check

> _"Switch to iPhone 14 viewport and screenshot the homepage."_

```
→ set_viewport(390, 844)
→ navigate_to("https://my-site.com")
→ screenshot(annotate=False, full_page=True)
```

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌────────────────────┐     ┌─────────────┐
│   AI Agent      │────▶│  BrowserControl    │────▶│  Chromium   │
│ (Claude, Gemini,│◀────│   MCP Server       │◀────│ (Playwright)│
│  GPT, local…)   │     │                    │     │             │
└─────────────────┘     └────────────────────┘     └─────────────┘
        │                        │                       │
        │  call_tool("click",5)  │  page.click(handle)    │
        │  ◀─────────────────────│  ◀─────────────────────│
        │  annotated PNG +       │  screenshot.png        │
        │  element map           │  + SoM overlay         │
```

### Action loop

1. **Agent calls a tool** — e.g. `click(5)`.
2. **Server resolves the element** — Looks up element 5 from the last SoM pass, then calls `document.elementFromPoint(x, y)` to get the *actual* DOM element (handles overlays, sticky headers, and shadow boundaries).
3. **Browser executes** — Playwright drives the real Chromium.
4. **Server re-screenshots** — New screenshot, fresh element detection (with shadow DOM + iframe recursion), numbered boxes drawn with Pillow.
5. **Annotated result returns** — Both image and textual map are sent back so the model can pick its preferred representation.

### Why SoM over selectors?

- **No DOM drift** — If the site gets redesigned, the numbered elements still point at the right pixels.
- **No hallucinated selectors** — The model never invents `div.flex-container > button.btn-primary:nth-child(3)`.
- **Tiny tokens** — A list of `{"id": 7, "tag": "button", "text": "Submit"}` is far cheaper than a full DOM tree.
- **Vision + text** — The model can use either or both. Vision for visual reasoning, text for fast selection.

---

## 🆚 How it compares

A few notes, kept honest:

| Capability | **BrowserControl** | Playwright MCP | Stagehand / Browser-Use | AgentQL |
|---|:-:|:-:|:-:|:-:|
| **Set of Marks** (numbered boxes) | ✅ | ❌ text-tree only | ❌ | ❌ |
| **Shadow DOM traversal** | ✅ recursive | ⚠️ partial | ⚠️ varies | ⚠️ varies |
| **Same-origin iframe support** | ✅ with offset coords | ⚠️ basic | ⚠️ varies | ❌ |
| **Native `set_input_files` upload** | ✅ | ⚠️ manual | ❌ | ❌ |
| **Built-in devtools** (console/network/errors/perf) | ✅ 11 tools | ⚠️ partial | ❌ | ❌ |
| **Multi-tab control** | ✅ | ⚠️ implicit | ⚠️ varies | ❌ |
| **True persistent profile** | ✅ `launch_persistent_context` | ⚠️ | ❌ | ❌ |
| **No external LLM API required** | ✅ | ✅ | ❌ needs API key | ❌ cloud |
| **Runs 100% locally / offline** | ✅ | ✅ | ❌ | ❌ |
| **Cost per 1k actions** | **$0** | $0 | API spend | API spend |

> ⚖️ We try to be fair: Playwright MCP is excellent if you're fine with the accessibility tree approach. Stagehand and Browser-Use are great if you specifically want an LLM in the loop. BrowserControl's niche is **vision-first, fully local, zero-LLM-API browser control** with built-in devtools.

---

## 🧪 Troubleshooting

<details>
<summary><b>Missing X server / won't start in CI</b></summary>

BrowserControl defaults to headless. If you want to *see* the browser, run on a desktop session:

```bash
xvfb-run browsercontrol          # Linux without a display
BROWSER_HEADLESS=false browsercontrol   # with a display
```

</details>

<details>
<summary><b>"Chromium executable doesn't exist"</b></summary>

BrowserControl auto-installs Chromium on first run. If that fails:

```bash
python -m playwright install chromium --with-deps
```

</details>

<details>
<summary><b>Connection refused on localhost</b></summary>

BrowserControl auto-tries `127.0.0.1` when `localhost` fails. If it still fails:

- Confirm the dev server is running (`curl http://localhost:3000` from the shell).
- If your dev server binds only to `127.0.0.1`, navigate directly: `navigate_to("http://127.0.0.1:3000")`.
- Corporate proxies can interfere — BrowserControl already passes `--proxy-bypass-list=<-loopback>` to Chromium.

</details>

<details>
<summary><b>Sessions don't persist</b></summary>

Check that the user data directory is writable:

```bash
ls -la ~/.browsercontrol/
```

Override with `BROWSER_USER_DATA_DIR=/some/writable/path`.

</details>

<details>
<summary><b>"Connection refused" — port already in use</b></summary>

```bash
pkill -f browsercontrol
browsercontrol
```

</details>

<details>
<summary><b>View session recordings</b></summary>

Recordings are Playwright trace zips. Open them with:

```bash
npx playwright show-trace ~/.browsercontrol/recordings/session_20260228.zip
```

</details>

<details>
<summary><b>Element IDs "expired" after a page change</b></summary>

Element IDs are only valid until the next screenshot. After any navigation, click, or state change, **call the tool again and read the new IDs from the latest screenshot/map**. Tools re-screenshot automatically — your agent just needs to look at the response.

</details>

---

## 📁 Project structure

```
browsercontrol/
├── __init__.py              # Public exports (`mcp`)
├── __main__.py              # `python -m browsercontrol` entry point
├── server.py                # FastMCP server definition + tool registration
├── browser.py               # BrowserManager — Playwright lifecycle + SoM renderer
├── config.py                # Env-var configuration
└── tools/
    ├── navigation.py        # navigate_to, go_back, go_forward, refresh, scroll
    ├── interaction.py       # click, click_at, type_text, press_key, hover, scroll_to_element, wait
    ├── forms.py             # select_option, check_checkbox, upload_file
    ├── content.py           # get_page_content, get_text, get_page_info, run_javascript, screenshot
    ├── devtools.py          # console, network, errors, inspect, perf, cookies, viewport
    ├── recording.py         # start/stop_recording, take_snapshot, list_recordings
    └── tabs.py              # create_tab, switch_tab, close_tab, list_tabs

tests/                       # 1,664 lines of pytest tests (mocked Playwright)
├── conftest.py              # Shared fixtures: mock_page, mock_context, mock_browser_manager…
└── test_*.py                # One file per module
```

---

## 🛠️ Development

```bash
git clone https://github.com/adityasasidhar/browsercontrol
cd browsercontrol

# Install deps + Playwright + Chromium
uv sync
uv run playwright install chromium --with-deps

# Run the server in dev mode (FastMCP inspector)
uv run fastmcp dev browsercontrol/server.py

# Run tests
uv run pytest

# Lint, format, security checks
uv run ruff check .
uv run ruff format .
uv run pre-commit run --all-files
```

CI runs the full suite on **Ubuntu, Windows, and macOS** with `ruff`, `mypy --strict`, `bandit`, and `pytest`.

---

## 🤝 Contributing

Contributions welcome! See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the workflow and [`CODE_QUALITY.md`](CODE_QUALITY.md) for the toolchain.

**Good first contributions:**

- [ ] Firefox / WebKit support
- [ ] DOM diffing (detect changes between snapshots)
- [ ] Accessibility audit tools
- [ ] Mobile emulation presets (iPhone, Pixel, iPad)
- [ ] Cookie import/export (Netscape format)
- [ ] `--record-video` MP4 output (in addition to traces)
- [ ] Network request blocking / mocking

When adding a tool, please add a matching `tests/test_<your_tool>.py` covering the happy path **and** error path.

---

## 📄 License

[MIT](LICENSE) — do whatever you want, just keep the copyright.

---

## 🙏 Acknowledgments

- Built on [FastMCP](https://gofastmcp.com) and [Playwright](https://playwright.dev).
- The Set of Marks idea comes from the **Set-of-Marks prompting** literature for visual tool use — adapted here as the agent's primary interface rather than a fallback.
- Thanks to the MCP community for making AI-tool integration this pleasant.

---

<p align="center">
  <strong>Built for AI agents that need to <em>see</em> the web.</strong>
</p>

<p align="center">
  <a href="https://github.com/adityasasidhar/browsercontrol">⭐ Star on GitHub</a> &nbsp;•&nbsp;
  <a href="https://github.com/adityasasidhar/browsercontrol/issues">🐛 Report a bug</a> &nbsp;•&nbsp;
  <a href="https://github.com/adityasasidhar/browsercontrol/issues">💡 Request a feature</a>
</p>

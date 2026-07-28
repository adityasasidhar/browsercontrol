<p align="center">
  <img src="https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/assets/logo-main.png" alt="" width="130">
</p>

<h1 align="center">BrowserControl</h1>

<p align="center"><b>An MCP server that gives your agent a browser it can see.</b></p>

<p align="center">
  <a href="https://pypi.org/project/browsercontrol/"><img src="https://img.shields.io/pypi/v/browsercontrol?color=1f6feb&label=pypi" alt="PyPI"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.11+-3776ab.svg" alt="Python 3.11+"></a>
  <a href="https://github.com/adityasasidhar/browsercontrol/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/adityasasidhar/browsercontrol/ci.yml?branch=main&label=ci" alt="CI"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-3fb950.svg" alt="MIT"></a>
  <a href="https://adityasasidhar.github.io/browsercontrol/"><img src="https://img.shields.io/badge/docs-live-8957e5.svg" alt="Documentation"></a>
</p>

<p align="center">
  <a href="https://insiders.vscode.dev/redirect/mcp/install?name=browsercontrol&amp;config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22browsercontrol%22%5D%7D"><img src="https://img.shields.io/badge/VS_Code-Install_Server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white" alt="Install in VS Code"></a>
  <a href="https://insiders.vscode.dev/redirect/mcp/install?name=browsercontrol&amp;config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22browsercontrol%22%5D%7D&amp;quality=insiders"><img src="https://img.shields.io/badge/VS_Code_Insiders-Install_Server-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white" alt="Install in VS Code Insiders"></a>
  <a href="https://cursor.com/en/install-mcp?name=browsercontrol&amp;config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJicm93c2VyY29udHJvbCJdfQ%3D%3D"><img src="https://img.shields.io/badge/Cursor-Install_Server-000000?style=flat-square&logo=cursor&logoColor=white" alt="Install in Cursor"></a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/assets/som-demo.gif" alt="A real BrowserControl session: a documentation page is marked with 20 numbered red boxes, the agent types into the search field by number, the results open and everything is renumbered, then it clicks a result and the next page is marked from scratch again." width="900">
</p>

<p align="center"><sub>A real session — BrowserControl driving its own documentation. Navigate, type, click; and after every one of them the page is re-marked and the numbers change. That's why the agent re-reads them each time.</sub></p>

## The idea

Most browser tools hand a model a DOM tree and hope it writes a working selector.
BrowserControl hands it a **picture**.

Every action returns a fresh screenshot with numbered red boxes drawn over the
interactive elements, plus the same list as text. The agent acts by number:

```text
click(5)
type_text(3, "hello world")
upload_file(7, "/path/to/resume.pdf")
```

No selectors to guess, none to break on the next redesign. This is the
[Set of Marks](https://adityasasidhar.github.io/browsercontrol/concepts/set-of-marks/)
pattern, used as the primary interface rather than a fallback.

## Quick start

```bash
uv add browsercontrol      # or: pip install browsercontrol
```

Chromium installs itself on first run. If that fails, run
`python -m playwright install chromium` once.

Point your client at the `browsercontrol` command:

```json
{
  "mcpServers": {
    "browsercontrol": {
      "command": "browsercontrol"
    }
  }
}
```

<details>
<summary>Where that file lives, per client</summary>

| Client | Location |
|---|---|
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) · `~/.config/Claude/claude_desktop_config.json` (Linux) · `%APPDATA%\Claude\claude_desktop_config.json` (Windows) |
| **Claude Code** | `claude mcp add browsercontrol -- browsercontrol` |
| **Cursor** | Settings → Model Context Protocol |
| **Cline** | Settings → MCP Servers |
| **Continue.dev** | `~/.continue/config.json`, under `mcpServers` |
| **Zed** | `~/.config/zed/settings.json`, under `context_servers` as `{"command": {"path": "browsercontrol"}}` |

No install at all, if you prefer: `"command": "uvx", "args": ["browsercontrol"]`.

</details>

Restart the client and ask it for something:

> *"Open Hacker News and tell me the top story."*

Full walkthrough: [Getting started](https://adityasasidhar.github.io/browsercontrol/getting-started/).

## The one rule

**Element numbers expire after every action.** The map is rebuilt from scratch on
every click, type, scroll, navigation, and screenshot — element `7` before a
click is rarely element `7` after it.

So an agent should never plan two clicks from one screenshot. It acts, reads the
new screenshot, finds the target again, then acts again. Almost every failure
worth debugging traces back to this.

Two corollaries:

- **Only what's in the viewport gets marked.** No number usually means "below the
  fold" — scroll, then look again.
- **Cross-origin iframes are never marked.** Open shadow roots and same-origin
  frames are traversed and numbered; third-party payment fields and embedded
  widgets can't be. That's a boundary of the browser, not a bug.

## Tools

39 tools across seven categories. Everything that touches the page returns an
annotated screenshot plus the element map.

| Category | | Tools |
|---|:-:|---|
| [**Navigation**](https://adityasasidhar.github.io/browsercontrol/tools/navigation/) | 5 | `navigate_to` `go_back` `go_forward` `refresh_page` `scroll` |
| [**Interaction**](https://adityasasidhar.github.io/browsercontrol/tools/interaction/) | 7 | `click` `click_at` `type_text` `press_key` `hover` `scroll_to_element` `wait` |
| [**Forms**](https://adityasasidhar.github.io/browsercontrol/tools/forms/) | 3 | `select_option` `check_checkbox` `upload_file` |
| [**Content**](https://adityasasidhar.github.io/browsercontrol/tools/content/) | 5 | `get_page_content` `get_text` `get_page_info` `run_javascript` `screenshot` |
| [**Tabs**](https://adityasasidhar.github.io/browsercontrol/tools/tabs/) | 4 | `create_tab` `switch_tab` `close_tab` `list_tabs` |
| [**DevTools**](https://adityasasidhar.github.io/browsercontrol/tools/devtools/) | 11 | `get_console_logs` `get_network_requests` `get_page_errors` `run_in_console` `inspect_element` `get_page_performance` `get_cookies` `set_cookie` `delete_cookie` `clear_cookies` `set_viewport` |
| [**Recording**](https://adityasasidhar.github.io/browsercontrol/tools/recording/) | 4 | `start_recording` `stop_recording` `take_snapshot` `list_recordings` |

A few behaviours that aren't obvious from the names:

- `type_text` uses Playwright's `fill()` — it **replaces** the field, it doesn't append.
- `click` resolves the topmost element at the mark's centre, so a cookie banner
  overlapping your target will eat the click. Dismiss overlays first.
- `upload_file` goes through `set_input_files`, which works on sites where
  driving the file picker doesn't.
- `screenshot(annotate=True, full_page=True)` returns a *clean* image —
  full-page captures can't be marked.
- `get_page_content` returns Markdown, capped at 30 KB.
- Recordings are Playwright traces. Open one with
  `npx playwright show-trace ~/.browsercontrol/recordings/<name>.zip`.

## Teach your agent to use it well

Connecting the server tells an agent *which* tools exist. The bundled
[agent skill](skills/browsercontrol/SKILL.md) tells it *how to use them well* —
that numbers expire, that a banner will swallow a click, that a missing number
means scroll.

```bash
mkdir -p ~/.claude/skills/browsercontrol
curl -fsSL https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/skills/browsercontrol/SKILL.md \
  -o ~/.claude/skills/browsercontrol/SKILL.md
```

It loads only when a task actually involves a browser, so it costs one line of
context the rest of the time. Agents that would rather read the docs directly can
start at [`llms.txt`](https://adityasasidhar.github.io/browsercontrol/llms.txt).

## Configuration

Environment variables, read once at startup.

| Variable | Default | |
|---|---|---|
| `BROWSER_HEADLESS` | `true` | `false` to watch the browser work |
| `BROWSER_VIEWPORT_WIDTH` | `1280` | |
| `BROWSER_VIEWPORT_HEIGHT` | `720` | |
| `BROWSER_TIMEOUT` | `30000` | Navigation timeout, ms |
| `BROWSER_USER_DATA_DIR` | `~/.browsercontrol/user_data` | Profile directory |
| `BROWSER_EXTENSION_PATH` | — | Unpacked extension to load at launch |
| `BROWSER_EXECUTABLE_PATH` | — | Chromium binary to drive, when Playwright ships no build for your platform |
| `BROWSER_RECORDINGS_DIR` | next to the profile | Where traces are saved |
| `BROWSER_SNAPSHOTS_DIR` | next to the profile | Where snapshots are saved |
| `LOG_LEVEL` | `INFO` | |

```bash
BROWSER_HEADLESS=false BROWSER_VIEWPORT_WIDTH=390 BROWSER_VIEWPORT_HEIGHT=844 browsercontrol
```

## Why this one

The session is a real Chromium profile (`launch_persistent_context`), so cookies,
`localStorage` and logins survive restarts — log in once and your agent stays
logged in. DevTools are first-class: console, network timing, uncaught
exceptions, performance and computed styles are tools, not an afterthought. And
it runs entirely on your machine — no LLM API key, no cloud round-trip, no
per-action cost, nothing leaving the box.

Honest positioning: if you're happy driving the accessibility tree, Playwright
MCP is excellent. If you want an LLM planning the interactions for you, look at
Stagehand or Browser-Use. BrowserControl's niche is **vision-first, fully local
browser control with devtools built in**. Longer comparison
[in the docs](https://adityasasidhar.github.io/browsercontrol/concepts/comparison/).

## Development

```bash
git clone https://github.com/adityasasidhar/browsercontrol
cd browsercontrol
uv sync
uv run playwright install chromium --with-deps

uv run pytest                                  # tests (Playwright is mocked — no real browser)
uv run ruff check . && uv run ruff format .    # lint + format
uv run fastmcp dev browsercontrol/server.py    # dev server with the MCP inspector
```

```
browsercontrol/
├── server.py     # FastMCP instance, lifespan, tool registration
├── browser.py    # BrowserManager: Playwright lifecycle, element detection, SoM rendering
├── config.py     # env-var config
└── tools/        # one module per category, each exporting register_*_tools(mcp)
```

CI runs the suite on Ubuntu, Windows and macOS with `ruff`, `mypy --strict`,
`bandit` and `pytest`.

## Contributing

Issues and PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). New tools should
come with a test for the happy path *and* the error path; the existing
`tests/test_*.py` files show the pattern.

On the list, if you're looking for somewhere to start: Firefox and WebKit
support, mobile device presets, network mocking, DOM diffing between snapshots,
and accessibility auditing.

## License

[MIT](LICENSE). Built on [FastMCP](https://gofastmcp.com) and
[Playwright](https://playwright.dev).

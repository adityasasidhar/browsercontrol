# Architecture

BrowserControl has three runtime components: the **AI agent** (your model + MCP client), the **MCP server** (this package), and **Chromium** (the real browser, driven via Playwright).

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

## The action loop

1. **Agent calls a tool** — e.g. `click(5)`.
2. **Server resolves the element** — Looks up element 5 from the last SoM pass, then calls `document.elementFromPoint(x, y)` to get the *actual* DOM element (handles overlays, sticky headers, and shadow boundaries).
3. **Browser executes** — Playwright drives the real Chromium.
4. **Server re-screenshots** — New screenshot, fresh element detection (with shadow DOM + iframe recursion), numbered boxes drawn with Pillow.
5. **Annotated result returns** — Both image and textual map are sent back so the model can pick its preferred representation.

The agent never sees a raw DOM tree. It sees a screenshot and a list of numbered elements.

## Components

### MCP server (`browsercontrol.server`)

- Built on [FastMCP](https://github.com/jlowin/fastmcp).
- Registers ~30 tools organized into seven categories.
- Manages browser lifecycle via the `lifespan` async context manager.
- Reads config from environment variables.

### Browser manager (`browsercontrol.browser`)

- Owns the Playwright `Browser`, `BrowserContext`, and `Page` instances.
- Runs `launch_persistent_context` so cookies, `localStorage`, and login state survive restarts.
- Implements the SoM renderer (detect → annotate → return).
- Provides `screenshot_with_som()` and `get_element_map()` helpers.

### Tools (`browsercontrol.tools.*`)

Each module registers a related group of tools:

| Module | Tools |
|---|---|
| `navigation.py` | `navigate_to`, `go_back`, `go_forward`, `refresh_page`, `scroll` |
| `interaction.py` | `click`, `click_at`, `type_text`, `press_key`, `hover`, `scroll_to_element`, `wait` |
| `forms.py` | `select_option`, `check_checkbox`, `upload_file` |
| `content.py` | `get_page_content`, `get_text`, `get_page_info`, `run_javascript`, `screenshot` |
| `devtools.py` | `get_console_logs`, `get_network_requests`, `get_page_errors`, `run_in_console`, `inspect_element`, `get_page_performance`, `get_cookies`, `set_cookie`, `delete_cookie`, `clear_cookies`, `set_viewport` |
| `recording.py` | `start_recording`, `stop_recording`, `take_snapshot`, `list_recordings` |
| `tabs.py` | `create_tab`, `switch_tab`, `close_tab`, `list_tabs` |

### Persistence

BrowserControl uses `launch_persistent_context`, not `launch`. This means:

- Cookies persist across runs (login once).
- `localStorage` and `sessionStorage` persist.
- The browser profile directory (`~/.browsercontrol/user_data/` by default) holds extensions, history, and other profile state.
- Override the location with `BROWSER_USER_DATA_DIR`.

## Why SoM over selectors?

See [Set of Marks](set-of-marks.md) for the full reasoning. In short:

- **No DOM drift** — If the site gets redesigned, the numbered elements still point at the right pixels.
- **No hallucinated selectors** — The model never invents `div.flex-container > button.btn-primary:nth-child(3)`.
- **Tiny tokens** — A list of `{"id": 7, "tag": "button", "text": "Submit"}` is far cheaper than a full DOM tree.
- **Vision + text** — The model can use either or both. Vision for visual reasoning, text for fast selection.

## The smart localhost fallback

`navigate_to("http://localhost:3000")` tries to resolve `localhost`. If DNS resolution fails (a common case on machines with misconfigured proxies), it automatically retries with `127.0.0.1`. This works around a long-standing pain point in browser automation.

Internally, Chromium is launched with `--proxy-bypass-list=<-loopback>` so the proxy can't intercept localhost traffic.

## Shadow DOM and iframes

Modern web apps love shadow DOM and iframes. Both are first-class in BrowserControl:

- **Shadow DOM** — The SoM renderer recursively descends into open shadow roots. Each shadow root gets its own element map with offset coordinates.
- **Same-origin iframes** — Recursively scanned, with coordinate offsets so clicks land in the right place.

This is one of the things BrowserControl does that most alternatives don't.

## See also

- **[Set of Marks](set-of-marks.md)** — the visual prompting technique
- **[How it compares](comparison.md)** — BrowserControl vs. alternatives
- **[Tool reference](../tools/index.md)** — every MCP tool

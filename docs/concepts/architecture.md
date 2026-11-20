# Architecture

BrowserControl has three runtime components: the **AI agent** (your model + MCP client), the **MCP server** (this package), and **Chromium** (the real browser, driven via Playwright).

```
┌─────────────────┐     ┌────────────────────┐     ┌─────────────┐
│   AI Agent      │────▶│  BrowserControl    │────▶│  Chromium   │
│ (Claude, Gemini,│◀────│   MCP Server       │◀────│ (Playwright)│
│  GPT, local…)   │     │                    │     │             │
└─────────────────┘     └────────────────────┘     └─────────────┘
        │                        │                       │
        │  call_tool("click",5)  │  locator.click()       │
        │  ◀─────────────────────│  ◀─────────────────────│
        │  annotated PNG +       │  screenshot.png        │
        │  element map           │  + SoM overlay         │
```

## The action loop

1. **Agent calls a tool** — e.g. `click(5)`.
2. **Server resolves the element** — Looks up element 5 in the active tab's map from the last SoM pass and finds it again by its `data-bc-id` tag, in its own frame and through shadow DOM. If it was removed or moved since, the tool returns a "stale" error and a fresh screenshot instead of acting.
3. **Browser executes** — Playwright drives the real Chromium.
4. **Page settles** — The server waits for DOMContentLoaded, then for in-flight requests, then for the DOM to stop changing, bounded by [`BROWSER_SETTLE_TIMEOUT`](../configuration.md#browser_settle_timeout). No fixed sleeps.
5. **Server re-screenshots** — New screenshot, fresh element detection in every frame (shadow DOM included), numbered boxes drawn with Pillow.
6. **Annotated result returns** — Both image and textual map are sent back so the model can pick its preferred representation. Dialogs and downloads that happened along the way are reported as `Notice:` lines at the top.

The agent never sees a raw DOM tree. It sees a screenshot and a list of numbered elements.

## Components

### MCP server (`browsercontrol.server`)

- Built on [FastMCP](https://github.com/jlowin/fastmcp).
- Registers 69 tools in fourteen modules, eight `browser://` MCP resources, and middleware that runs each call in the calling client's browser session.
- Manages browser lifecycle via the `lifespan` async context manager.
- Serves over stdio by default, or Streamable HTTP with `--transport http`.
- Reads config from environment variables.

### Browser manager (`browsercontrol.browser`)

- Starts the browser in one of two ways: `launch_persistent_context` against its own profile, or `connect_over_cdp` to attach to [your running Chrome](../guides/use-your-chrome.md).
- Holds one or more sessions and resolves which one the calling client is bound to.
- Waits for the page to settle after each action.
- Draws the SoM overlay and keeps one element map per tab.
- Provides `screenshot_with_som()`, `get_element_map()` and `resolve_element(id)`.

### Sessions (`browsercontrol.session`)

- A `Session` is one browser context: the default (persistent profile or attached Chrome) or an isolated one from `create_session`.
- Each session keeps its own tabs, console logs, network traffic, page errors, dialog policy, downloads, emulation settings, and action log.
- Event listeners are wired to every new page and popup in the session.

### Emulation and codegen

- `browsercontrol.emulation` applies device, geolocation, timezone, color scheme, and network throttling per page, and re-applies them to new tabs.
- `browsercontrol.codegen` turns a session's action log into a pytest-playwright or `@playwright/test` file for `export_test`.

### Element detection (`browsercontrol.elements`)

- Collects and tags elements in every frame (`collect_elements`), and resolves an ID back to a live, verified locator (`locate`).

### Tools (`browsercontrol.tools.*`)

Each module registers a related group of tools:

| Module | Tools |
|---|---|
| `navigation.py` | `navigate_to`, `go_back`, `go_forward`, `refresh_page`, `scroll` |
| `search.py` | `find` |
| `interaction.py` | `click`, `click_at`, `type_text`, `press_key`, `hover`, `double_click`, `right_click`, `drag`, `scroll_to_element`, `wait` |
| `batch.py` | `act` |
| `waiting.py` | `wait_for`, `handle_dialog`, `list_downloads` |
| `forms.py` | `select_option`, `check_checkbox`, `upload_file` |
| `content.py` | `get_page_content`, `get_text`, `get_page_info`, `run_javascript`, `screenshot` |
| `extract.py` | `extract_table`, `extract_links`, `extract` |
| `devtools.py` | `get_console_logs`, `get_network_requests`, `get_page_errors`, `run_in_console`, `inspect_element`, `get_page_performance`, `get_cookies`, `set_cookie`, `delete_cookie`, `clear_cookies`, `set_viewport` |
| `network.py` | `mock_route`, `clear_mocks`, `get_request_details`, `wait_for_response`, `export_har` |
| `emulate.py` | `list_devices`, `emulate_device`, `set_geolocation`, `set_timezone`, `set_color_scheme`, `throttle_network`, `reset_emulation` |
| `recording.py` | `start_recording`, `stop_recording`, `take_snapshot`, `list_recordings`, `export_test` |
| `tabs.py` | `create_tab`, `switch_tab`, `close_tab`, `list_tabs` |
| `sessions.py` | `create_session`, `switch_session`, `list_sessions`, `close_session`, `connect_to_chrome`, `disconnect_chrome` |

### Persistence

In its default mode BrowserControl uses `launch_persistent_context`, not `launch`. This means:

- Cookies persist across runs (login once).
- `localStorage` and `sessionStorage` persist.
- The browser profile directory (`~/.browsercontrol/user_data/` by default) holds extensions, history, and other profile state.
- Override the location with `BROWSER_USER_DATA_DIR`.

When attached to your own Chrome over CDP, the profile is Chrome's, and stopping the server only disconnects. Isolated sessions are in-memory and discarded when closed.

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

- **Shadow DOM** — Detection descends into open shadow roots, and resolution goes through Playwright locators, which pierce them.
- **Iframes, cross-origin included** — Detection runs in every frame Playwright exposes, and each frame's boxes are offset by where its content sits on screen (border and padding included). Actions run in the element's own frame.

This is one of the things BrowserControl does that most alternatives don't.

## See also

- **[Set of Marks](set-of-marks.md)** — the visual prompting technique
- **[How it compares](comparison.md)** — BrowserControl vs. alternatives
- **[Tool reference](../tools/index.md)** — every MCP tool

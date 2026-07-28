# Tools reference

BrowserControl exposes **39 MCP tools** organized into seven categories. Every tool that touches the page returns an **annotated screenshot** plus a textual element map, so the model always has the latest visual context.

!!! info "Element IDs are fresh on every response"
    The `[1]`, `[2]`, … numbers you see in a tool's response are only valid until the next screenshot. After any navigation, click, or state change, **read the new IDs from the latest screenshot/map**. The tools re-screenshot automatically — your agent just needs to look at the response.

## Categories

<div class="grid cards" markdown>

-   :material-compass:{ .lg .middle } **[Navigation](navigation.md)**

    ---

    Navigate the browser: open URLs, history, scroll.

-   :material-cursor-default-click:{ .lg .middle } **[Interaction](interaction.md)**

    ---

    Click, type, hover, press keys, wait.

-   :material-tab:{ .lg .middle } **[Tabs](tabs.md)**

    ---

    Open, switch, close, and list browser tabs.

-   :material-form-select:{ .lg .middle } **[Forms](forms.md)**

    ---

    Dropdowns, checkboxes, file uploads.

-   :material-text-box-search:{ .lg .middle } **[Content](content.md)**

    ---

    Read the page: text, markdown, JS evaluation, screenshots.

-   :material-tools:{ .lg .middle } **[DevTools](devtools.md)**

    ---

    Console, network, errors, performance, cookies, viewport.

-   :material-record-rec:{ .lg .middle } **[Recording](recording.md)**

    ---

    Capture Playwright traces and DOM snapshots for debugging.

</div>

## Quick index

### Navigation

| Tool | Description |
|---|---|
| [`navigate_to(url)`](navigation.md#navigate_to) | Open a URL. Auto-falls back to `127.0.0.1` for `localhost` if the proxy blocks it. |
| [`go_back()`](navigation.md#go_back) | Browser history back. |
| [`go_forward()`](navigation.md#go_forward) | Browser history forward. |
| [`refresh_page()`](navigation.md#refresh_page) | Reload the current page. |
| [`scroll(direction, amount)`](navigation.md#scroll) | Scroll the viewport. |

### Interaction

| Tool | Description |
|---|---|
| [`click(element_id)`](interaction.md#click) | Click by SoM number. Resolves the actual DOM element first, so overlays don't fool it. |
| [`click_at(x, y)`](interaction.md#click_at) | Click raw coordinates. |
| [`type_text(element_id, text)`](interaction.md#type_text) | Atomic `element.fill()` — reliable for forms. |
| [`press_key(key)`](interaction.md#press_key) | Any keyboard key: `Enter`, `Tab`, `Escape`, arrows, etc. |
| [`hover(element_id)`](interaction.md#hover) | Hover for tooltips/menus. |
| [`scroll_to_element(element_id)`](interaction.md#scroll_to_element) | Scroll the element into view. |
| [`wait(seconds)`](interaction.md#wait) | Sleep — for animations or lazy-loaded content. |

### Tabs

| Tool | Description |
|---|---|
| [`create_tab(url=None)`](tabs.md#create_tab) | Open a new tab. |
| [`switch_tab(index)`](tabs.md#switch_tab) | Switch by 0-based index. |
| [`close_tab(index)`](tabs.md#close_tab) | Close a tab. |
| [`list_tabs()`](tabs.md#list_tabs) | List all tabs with title, URL, active marker. |

### Forms

| Tool | Description |
|---|---|
| [`select_option(element_id, option)`](forms.md#select_option) | Pick from a `<select>` dropdown. |
| [`check_checkbox(element_id, check=True)`](forms.md#check_checkbox) | Toggle a checkbox. |
| [`upload_file(element_id, file_path)`](forms.md#upload_file) | Native file upload via `set_input_files`. |

### Content

| Tool | Description |
|---|---|
| [`get_page_content()`](content.md#get_page_content) | Whole page as Markdown (script/style stripped). |
| [`get_text(element_id)`](content.md#get_text) | Read text from a specific element. |
| [`get_page_info()`](content.md#get_page_info) | Current URL + title. |
| [`run_javascript(script)`](content.md#run_javascript) | Run JS, return serialized result + screenshot. |
| [`screenshot(annotate, full_page)`](content.md#screenshot) | Annotated viewport, clean viewport, or clean full-page. |

### DevTools

| Tool | Description |
|---|---|
| [`get_console_logs(clear=False)`](devtools.md#get_console_logs) | Last 50 captured console messages. |
| [`get_network_requests(num_requests, clear=False)`](devtools.md#get_network_requests) | Method, URL, status, **duration (ms)**. |
| [`get_page_errors()`](devtools.md#get_page_errors) | Uncaught JS exceptions with stack traces. |
| [`run_in_console(code)`](devtools.md#run_in_console) | Eval JS with structured error handling. |
| [`inspect_element(element_id)`](devtools.md#inspect_element) | Computed styles, dimensions, attributes. |
| [`get_page_performance()`](devtools.md#get_page_performance) | TTFB, FCP, DOMContentLoaded, load time. |
| [`get_cookies()`](devtools.md#get_cookies) | All cookies in the current context. |
| [`set_cookie(name, value, domain, path)`](devtools.md#set_cookie) | Set a cookie (domain auto-inferred). |
| [`delete_cookie(name)`](devtools.md#delete_cookie) | Delete cookies by name. |
| [`clear_cookies()`](devtools.md#clear_cookies) | Wipe all cookies. |
| [`set_viewport(width, height)`](devtools.md#set_viewport) | Resize the viewport on the fly. |

### Recording

| Tool | Description |
|---|---|
| [`start_recording(name="")`](recording.md#start_recording) | Begin a Playwright trace. |
| [`stop_recording()`](recording.md#stop_recording) | Save the trace. |
| [`take_snapshot(name="")`](recording.md#take_snapshot) | Save PNG + HTML + URL triplet. |
| [`list_recordings()`](recording.md#list_recordings) | List recent recordings and snapshots. |

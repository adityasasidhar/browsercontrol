# Tool reference

Use this index to find the arguments, return values, and examples for any of
BrowserControl’s 69 MCP tools. Most tools return an annotated screenshot with
their result. See [Set of Marks](../concepts/set-of-marks.md) for how to read it.

!!! tip "Use IDs from the latest annotated screenshot"
    If a tool returns a new annotated screenshot, look up the next target in
    its element map before passing an ID to another tool.

## Navigation

| Tool | Description |
|---|---|
| [`navigate_to(url)`](navigation.md#navigate_to) | Open a URL. Auto-falls back to `127.0.0.1` for `localhost` if the proxy blocks it. |
| [`go_back()`](navigation.md#go_back) | Browser history back. |
| [`go_forward()`](navigation.md#go_forward) | Browser history forward. |
| [`refresh_page()`](navigation.md#refresh_page) | Reload the current page. |
| [`scroll(direction, amount)`](navigation.md#scroll) | Scroll the viewport. |
| [`find(query, role, nth)`](navigation.md#find) | Search the whole page (off-screen too), scroll to a match, return its ID. |

## Interaction

| Tool | Description |
|---|---|
| [`click(element_id)`](interaction.md#click) | Click the element identified by its current screenshot number. |
| [`click_at(x, y)`](interaction.md#click_at) | Click raw coordinates. |
| [`type_text(element_id, text)`](interaction.md#type_text) | Replace the text in an editable field. |
| [`press_key(key)`](interaction.md#press_key) | Any keyboard key: `Enter`, `Tab`, `Escape`, arrows, etc. |
| [`hover(element_id)`](interaction.md#hover) | Hover for tooltips/menus. |
| [`scroll_to_element(element_id)`](interaction.md#scroll_to_element) | Scroll the element into view. |
| [`wait(seconds)`](interaction.md#wait) | Wait for animations or lazy-loaded content. |
| [`double_click(element_id)`](interaction.md#double_click) | Double-click. |
| [`right_click(element_id)`](interaction.md#right_click) | Open the context menu. |
| [`drag(source_id, target_id)`](interaction.md#drag) | Drag and drop. |
| [`act(steps, stop_on_error)`](interaction.md#act) | Several steps, one call, one screenshot. |

## Waiting, dialogs, and downloads

| Tool | Description |
|---|---|
| [`wait_for(text, selector, state, network_idle, timeout_seconds)`](waiting.md#wait_for) | Wait for a condition instead of sleeping. |
| [`handle_dialog(accept, prompt_text)`](waiting.md#handle_dialog) | Answer the next alert, confirm, or prompt. |
| [`list_downloads()`](waiting.md#list_downloads) | Files the page downloaded. |

## Tabs

| Tool | Description |
|---|---|
| [`create_tab(url=None)`](tabs.md#create_tab) | Open a new tab. |
| [`switch_tab(index)`](tabs.md#switch_tab) | Switch by 0-based index. |
| [`close_tab(index)`](tabs.md#close_tab) | Close a tab. |
| [`list_tabs()`](tabs.md#list_tabs) | List all tabs with title, URL, active marker. |

## Sessions

| Tool | Description |
|---|---|
| [`connect_to_chrome(cdp_url)`](sessions.md#connect_to_chrome) | Use your own signed-in Chrome. |
| [`disconnect_chrome()`](sessions.md#disconnect_chrome) | Go back to the managed browser. |
| [`create_session(name, device, url)`](sessions.md#create_session) | Open an isolated session with its own cookies and tabs. |
| [`switch_session(name)`](sessions.md#switch_session) | Change session. |
| [`list_sessions()`](sessions.md#list_sessions) | Sessions and their tabs. |
| [`close_session(name)`](sessions.md#close_session) | Discard an isolated session. |

## Forms

| Tool | Description |
|---|---|
| [`select_option(element_id, option)`](forms.md#select_option) | Pick from a `<select>` dropdown. |
| [`check_checkbox(element_id, check=True)`](forms.md#check_checkbox) | Toggle a checkbox. |
| [`upload_file(element_id, file_path)`](forms.md#upload_file) | Native file upload via `set_input_files`. |

## Content

| Tool | Description |
|---|---|
| [`get_page_content()`](content.md#get_page_content) | Read page content as Markdown. |
| [`get_text(element_id)`](content.md#get_text) | Read text from a specific element. |
| [`get_page_info()`](content.md#get_page_info) | Current URL + title. |
| [`run_javascript(script)`](content.md#run_javascript) | Run JS, return serialized result + screenshot. |
| [`screenshot(annotate, full_page)`](content.md#screenshot) | Annotated viewport, clean viewport, or clean full-page. |

## Extraction

| Tool | Description |
|---|---|
| [`extract_table(element_id, index, output_format)`](extraction.md#extract_table) | A table as JSON, Markdown, or CSV. |
| [`extract_links(contains, limit)`](extraction.md#extract_links) | All links with absolute URLs. |
| [`extract(schema)`](extraction.md#extract) | JSON from a selector schema. |

## DevTools

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
| [`get_request_details(request_id, include_body)`](devtools.md#get_request_details) | Headers, POST data, and body of one request. |

## Network control

| Tool | Description |
|---|---|
| [`mock_route(url_pattern, status, body, content_type, headers, abort)`](network.md#mock_route) | Stub or block matching requests. |
| [`clear_mocks(url_pattern)`](network.md#clear_mocks) | Remove mocks. |
| [`wait_for_response(url_pattern, status, timeout_seconds)`](network.md#wait_for_response) | Wait for an API call to come back. |
| [`export_har(name, include_bodies)`](network.md#export_har) | Save traffic as a HAR file. |

## Emulation

| Tool | Description |
|---|---|
| [`list_devices(contains)`](emulation.md#list_devices) | Device names. |
| [`emulate_device(name)`](emulation.md#emulate_device) | Screen size, user agent, and touch. |
| [`set_geolocation(latitude, longitude, accuracy)`](emulation.md#set_geolocation) | Fake location. |
| [`set_timezone(timezone_id)`](emulation.md#set_timezone) | Fake timezone. |
| [`set_color_scheme(scheme)`](emulation.md#set_color_scheme) | Dark or light mode. |
| [`throttle_network(profile)`](emulation.md#throttle_network) | Slow 3G, 4G, or offline. |
| [`reset_emulation()`](emulation.md#reset_emulation) | Undo all emulation. |

## Recording

| Tool | Description |
|---|---|
| [`start_recording(name="")`](recording.md#start_recording) | Begin a Playwright trace. |
| [`stop_recording()`](recording.md#stop_recording) | Save the trace. |
| [`take_snapshot(name="")`](recording.md#take_snapshot) | Save PNG + HTML + URL triplet. |
| [`list_recordings()`](recording.md#list_recordings) | List recent recordings and snapshots. |
| [`export_test(name, language, clear)`](recording.md#export_test) | Turn the session into a replayable Playwright test. |

## MCP resources

Read captured data without a tool call or a screenshot. Each resource reads the
calling client's session and never starts the browser.

| URI | Contents |
|---|---|
| `browser://console` | Console messages |
| `browser://network` | Last 100 requests with headers and status |
| `browser://network/{request_id}` | One request |
| `browser://errors` | Uncaught page errors |
| `browser://tabs` | Open tabs |
| `browser://downloads` | Downloaded files |
| `browser://actions` | The action log `export_test` uses |
| `browser://sessions` | Sessions |

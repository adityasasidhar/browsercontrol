---
title: Tool reference
description: Search and filter all 79 BrowserControl MCP tools, with signatures, parameters, and links to each category's reference.
---

# Tool reference

BrowserControl exposes 69 MCP tools. Search them below, filter by category, and open any tool for its signature and parameters. Tools marked **screenshot** return a fresh annotated screenshot with their result; tools marked **text** return text only. Either kind can change browser state: `clear_cookies`, for example, returns text.

<ToolExplorer />

## By category

<CardGrid>
  <Card title="Navigation" link="/reference/navigation">Open URLs, history, scrolling, and <code>find</code>.</Card>
  <Card title="Interaction" link="/reference/interaction">Click, type, keys, hover, drag, and <code>act</code>.</Card>
  <Card title="Waiting & dialogs" link="/reference/waiting">Wait for conditions; dialogs and downloads.</Card>
  <Card title="Assertions" link="/reference/assertions">Verify text, URLs, and field values; recorded into <code>export_test</code>.</Card>
  <Card title="Forms" link="/reference/forms">Dropdowns, checkboxes, and file uploads.</Card>
  <Card title="Content" link="/reference/content">Markdown, element text, JavaScript, screenshots.</Card>
  <Card title="Extraction" link="/reference/extraction">Tables, links, and schema fields as JSON.</Card>
  <Card title="Tabs" link="/reference/tabs">Open, switch, list, and close tabs.</Card>
  <Card title="Sessions" link="/reference/sessions">Your own Chrome and isolated sessions.</Card>
  <Card title="DevTools" link="/reference/devtools">Console, errors, requests, cookies, inspection.</Card>
  <Card title="Network" link="/reference/network">Mocks, response waits, request details, HAR.</Card>
  <Card title="Emulation" link="/reference/emulation">Devices, color scheme, timezone, location, throttling.</Card>
  <Card title="Recording" link="/reference/recording">Traces, snapshots, and test export.</Card>
</CardGrid>

## Also in the reference

- [MCP resources](/reference/resources): captured data readable without a tool call.
- [Configuration](/reference/configuration): environment variables and command-line flags.
- [`tools.json`](/tools.json){target="_blank"}: this catalog as JSON, generated from the server.

<llm-only>

## Every tool

| Tool | Category | Summary |
| --- | --- | --- |
| `navigate_to(url)` | Navigation | Open a URL in the current tab. |
| `find(query, role, nth)` | Navigation | Search the whole page and scroll to a match; returns its element ID. |
| `scroll(direction, amount)` | Navigation | Scroll the page. |
| `go_back()`, `go_forward()`, `refresh_page()` | Navigation | History and reload. |
| `click(element_id)` | Interaction | Click a numbered element. |
| `type_text(element_id, text)` | Interaction | Replace a field's text. |
| `press_key(key)` | Interaction | Press a key or combination such as `Control+A`. |
| `act(steps, stop_on_error)` | Interaction | Run up to 25 steps in one call. |
| `hover`, `double_click`, `right_click`, `scroll_to_element` (element_id) | Interaction | Pointer actions on a numbered element. |
| `drag(source_id, target_id)` | Interaction | Drag one element onto another. |
| `click_at(x, y)` | Interaction | Click at coordinates, for spots with no number. |
| `wait(seconds)` | Interaction | Fixed sleep; prefer `wait_for`. |
| `wait_for(text, selector, state, network_idle, timeout_seconds)` | Waiting | Wait for a condition. |
| `handle_dialog(accept, prompt_text)` | Waiting | Choose the answer to the next JS dialog. |
| `list_downloads()` | Waiting | Files downloaded in this session. |
| `select_option(element_id, option)` | Forms | Pick from a native select. |
| `check_checkbox(element_id, check)` | Forms | Set a checkbox or radio. |
| `upload_file(element_id, file_path)` | Forms | Set a file on a file input. |
| `get_page_content()` | Content | The page as Markdown. |
| `get_text(element_id)` | Content | One element's full text. |
| `get_page_info()` | Content | URL and title. |
| `screenshot(annotate, full_page)` | Content | Annotated or clean screenshot. |
| `run_javascript(script)` | Content | Evaluate JavaScript. |
| `extract_table(element_id, index, output_format)` | Extraction | A table as JSON, Markdown, or CSV. |
| `extract_links(contains, limit)` | Extraction | All links as JSON. |
| `extract(schema)` | Extraction | Fields from a selector schema. |
| `create_tab(url)`, `list_tabs()`, `switch_tab(index)`, `close_tab(index)` | Tabs | Tab management. |
| `connect_to_chrome(cdp_url)`, `disconnect_chrome()` | Sessions | Attach to and detach from your own Chrome. |
| `create_session(name, device, url)`, `switch_session(name)`, `list_sessions()`, `close_session(name)` | Sessions | Isolated sessions. |
| `get_console_logs(clear)`, `get_page_errors()`, `get_network_requests(num_requests, clear)` | DevTools | Captured logs, errors, traffic. |
| `inspect_element(element_id)`, `run_in_console(code)`, `get_page_performance()` | DevTools | Inspection and performance. |
| `get_cookies()`, `set_cookie(name, value, domain, path)`, `delete_cookie(name)`, `clear_cookies()` | DevTools | Cookies. |
| `set_viewport(width, height)` | DevTools | Resize the viewport. |
| `mock_route(url_pattern, status, body, content_type, headers, abort)`, `clear_mocks(url_pattern)` | Network | Mock or block requests. |
| `wait_for_response(url_pattern, status, timeout_seconds)` | Network | Wait for a matching response. |
| `get_request_details(request_id, include_body)`, `export_har(name, include_bodies)` | Network | Request details and HAR export. |
| `list_devices(contains)`, `emulate_device(name)` | Emulation | Devices. |
| `set_color_scheme(scheme)`, `set_timezone(timezone_id)`, `set_geolocation(latitude, longitude, accuracy)` | Emulation | Environment. |
| `throttle_network(profile)`, `reset_emulation()` | Emulation | Network speed and reset. |
| `start_recording(name)`, `stop_recording()`, `take_snapshot(name)`, `list_recordings()` | Recording | Traces and snapshots. |
| `export_test(name, language, clear)` | Recording | The session as a Playwright test. |

</llm-only>

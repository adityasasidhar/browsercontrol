---
title: Debug a web app
description: Find out why a page is broken with BrowserControl's console, page error, network, and inspection tools.
---

# Debug a web app

> The Users page on localhost:3000 is blank. Find out why.

```text
→ navigate_to("http://localhost:3000/users")
→ get_page_errors()
→ get_console_logs()
→ get_network_requests()
→ get_request_details(14)
```

BrowserControl records console messages, uncaught errors, and network traffic for every tab from the moment it opens. Debugging is a matter of reading the right one first.

<div class="steps">

### Open the page

```text
→ navigate_to("http://localhost:3000/users")
```

If `localhost` refuses the connection, BrowserControl retries with `127.0.0.1` on its own.

### Start with uncaught errors

```text
→ get_page_errors()
Page Errors:
 TypeError: Cannot read properties of undefined (reading 'map')
   at UserList (http://localhost:3000/src/UserList.tsx:14:22)
```

An uncaught exception is usually the whole story.

### Then the console

```text
→ get_console_logs()
Console Logs:
[ERROR] Failed to load resource: the server responded with a status of 500 (Internal Server Error) (http://localhost:3000/api/users)
[WARNING] Each child in a list should have a unique "key" prop.
```

The last 50 messages, with their level and source.

### Then the network

```text
→ get_network_requests()
Network Requests:
#12 GET http://localhost:3000/users -> 200 (31ms)
#14 GET http://localhost:3000/api/users -> 500 (88ms)
```

The 30 most recent requests by default (`num_requests` to change it), each with an `#id`, status, and timing. Pass the id to see everything about one request:

```text
→ get_request_details(14)
```

Request and response headers, POST data, and the response body (text up to 10,000 characters, binary as base64). Bodies are read on demand, so ask before navigating away.

</div>

## Reproduce an interaction

To see what one action causes, clear the buffers first so only new entries show:

```text
→ get_console_logs(clear=True)
→ get_network_requests(clear=True)
→ click(7)                        # the button that misbehaves
→ get_page_errors()
→ get_console_logs()
→ get_network_requests()
```

If the click fires a request you care about, `wait_for_response("/api/save")` right after it waits for that response and shows its status and body.

## Look closer

| Question | Tool |
| --- | --- |
| Why is this element invisible or misplaced? | `inspect_element(id)`: tag, attributes, size, position, and computed styles |
| What's in this variable? | `run_in_console("window.__APP_STATE__")` |
| Is the page slow? | `get_page_performance()`: time to first byte, first contentful paint, load timings, resource count, JS heap |
| What cookies does it have? | `get_cookies()` |
| Can I share this with someone? | `export_har("users-500")` saves the traffic; `take_snapshot("users-500")` saves a screenshot and the HTML |

Captured data is also available without a tool call, as [MCP resources](/reference/resources) like `browser://errors` and `browser://network`.

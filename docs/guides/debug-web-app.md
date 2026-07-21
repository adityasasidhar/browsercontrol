# Debug a web app

BrowserControl ships with the devtools most agents need, so debugging is a 30-second job: navigate, pull logs, pull network, pull errors.

## What the agent does

> _"Check localhost:3000 for any errors and tell me what's broken."_

```text
→ navigate_to("http://localhost:3000")        # auto-fallback to 127.0.0.1 if needed
→ get_console_logs()
→ "2 errors:
   [ERROR] Uncaught TypeError: Cannot read property 'map' of undefined (app.js:42)
   [ERROR] Failed to load resource: 404 /api/users"
→ get_network_requests()
→ "GET /api/users -> 404 (12ms)  ← check your API route"
→ get_page_errors()
```

## Step by step

### 1. Open the app

```text
navigate_to("http://localhost:3000")
```

If the proxy blocks `localhost`, BrowserControl auto-retries with `127.0.0.1`.

### 2. Read console output

```text
get_console_logs(clear=False)
```

Returns the last 50 captured console messages with level, text, and source location. Pass `clear=True` after you've read them so you don't get noise from the next page load.

### 3. Read network requests

```text
get_network_requests(num_requests=50)
```

Method, URL, status, and **duration in ms** for the most recent N requests. Requests are paired by identity — no deduplication bugs that lose timing data.

### 4. Read JS errors

```text
get_page_errors()
```

Returns uncaught exceptions with the first line of the stack trace.

### 5. (Optional) Performance

```text
get_page_performance()
```

TTFB, First Contentful Paint, DOMContentLoaded, load time, resource count, JS heap size.

## A complete debugging session

```text
→ navigate_to("http://localhost:3000")
→ get_console_logs()
→ get_page_errors()
→ get_network_requests(num_requests=20)

# Reproduce the failing interaction
→ click(7)                          # click the broken button
→ wait(1.0)                         # let async requests settle
→ get_console_logs()
→ get_network_requests(num_requests=10)
→ get_page_errors()

# Inspect a specific element
→ inspect_element(7)
```

The post-reproduction logs will show the new errors triggered by the click, not just the ones that fired on initial page load.

## Tips

!!! tip "Clear between phases"
    Pass `clear=True` to `get_console_logs` and `get_network_requests` to clear the captured set. Otherwise you'll see every message since session start.

!!! tip "Inspect computed styles"
    `inspect_element(id)` returns computed styles, bounding box, classes, attributes, and text. Great for "why is this button invisible?" or "why does my click miss?".

!!! tip "Persist a failing page"
    When something goes wrong, save the state with `take_snapshot("repro_$(date)")`. You get the URL, full HTML, and a screenshot — everything you need to file a bug or send a teammate.

## See also

- **[DevTools reference](../tools/devtools.md)** — every dev tool documented
- **[Recording guide](record-tests.md)** — capture a full Playwright trace for replay

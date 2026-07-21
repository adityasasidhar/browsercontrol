# DevTools

Built-in developer tools — console logs, network requests, JS errors, performance, cookies, and viewport control. No second tool needed.

---

## `get_console_logs`

Get browser console logs (errors, warnings, info, log).

```python
get_console_logs(clear: bool = False) -> str
```

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `clear` | `bool` | `False` | If `True`, clears the captured logs after returning them. |

**Returns**

```text
Console Logs:
[ERROR] Uncaught TypeError: Cannot read property 'map' of undefined (app.js:42)
[WARNING] React: Each child in a list should have a unique "key" prop. (bundle.js:1042)
[INFO] WebSocket connected to ws://localhost:3001 (socket.js:18)
```

**Behavior**

- Returns the last 50 captured messages.
- Includes level, text, and source location.
- Logs are accumulated across the session unless `clear=True`.

---

## `get_network_requests`

Get captured network requests (API calls, images, scripts, etc.).

```python
get_network_requests(num_requests: int | None = None, clear: bool = False) -> str
```

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `num_requests` | `int \| None` | `None` (→ 30) | How many of the most recent requests to return. |
| `clear` | `bool` | `False` | If `True`, clears the captured requests after returning them. |

**Returns**

```text
Network Requests:
GET https://api.example.com/users -> 200 (142ms)
POST https://api.example.com/login -> 200 (89ms)
GET https://api.example.com/avatar/me.jpg -> 404 (12ms)
```

**Why this is good**

Requests are paired by request identity, not URL string. You won't see "phantom 404s" caused by deduplication bugs that lose the timing data.

---

## `get_page_errors`

Get uncaught JavaScript errors with stack traces.

```python
get_page_errors() -> str
```

**Returns**

```text
Page Errors:
 Uncaught TypeError: Cannot read property 'map' of undefined
   at renderList (app.js:42:15)
   at HTMLButtonElement.onClick (app.js:88:5)
```

---

## `run_in_console`

Eval JavaScript with structured error handling. Returns the result plus a fresh annotated screenshot.

```python
run_in_console(code: str) -> tuple[str, Image]
```

**Parameters**

| Name | Type | Description |
|---|---|---|
| `code` | `str` | JavaScript code to eval in the page context. |

**Returns**

```text
Console Result:
{"id": 7, "tag": "button", "text": "Sign in"}

Found 5 interactive elements:
  [1] input - Search…
  ...
```

**When to use**

- Inspect a variable without typing a full `run_javascript` extraction.
- Trigger a UI change and then immediately see the new state in the screenshot.
- Test if a piece of code throws.

---

## `inspect_element`

Inspect an element to get its computed styles, dimensions, attributes, and properties.

```python
inspect_element(element_id: int) -> str
```

**Parameters**

| Name | Type | Description |
|---|---|---|
| `element_id` | `int` | The number label of the element to inspect. |

**Returns**

```text
Element 5 Inspection:
  Tag: <button>
  ID: #submit
  Classes: .btn.btn-primary
  Text: Sign in
  Size: 96x40px
  Position: (832, 412)
  Styles:
    color: rgb(255, 255, 255)
    background: rgb(13, 110, 253)
    font: 16px Inter, sans-serif
```

**Why this is good**

- Computed styles — what the browser actually rendered, not what's in the stylesheet.
- Bounding box — useful for figuring out why a click landed in the wrong place.
- Attributes — first 10 attributes shown.

---

## `get_page_performance`

Get page performance metrics: TTFB, First Contentful Paint, load time, resource count, JS heap.

```python
get_page_performance() -> str
```

**Returns**

```text
Page Performance:
  Time to First Byte: 87ms
  First Contentful Paint: 412ms
  DOM Content Loaded: 678ms
  Load Complete: 1230ms
  Resources Loaded: 47
  JS Heap: 28MB / 128MB
```

---

## `get_cookies`

Get all cookies in the current browser context.

```python
get_cookies() -> str
```

**Returns**

```text
Cookies:
  session=eyJhbGciOiJIUzI1N... (domain=.example.com)
  csrf_token=abc123def456... (domain=example.com)
```

---

## `set_cookie`

Set a cookie.

```python
set_cookie(name: str, value: str, domain: str | None = None, path: str = "/") -> str
```

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | — | Cookie name. |
| `value` | `str` | — | Cookie value. |
| `domain` | `str \| None` | `None` | Cookie domain. **Auto-inferred from the current page URL when omitted.** |
| `path` | `str` | `"/"` | Cookie path. |

**Examples**

```text
→ set_cookie("session", "abc123")                        # domain inferred from current page
→ set_cookie("auth", "xyz789", domain=".example.com")    # explicit domain
```

---

## `delete_cookie`

Delete cookies by name across all domains in the current context.

```python
delete_cookie(name: str) -> str
```

---

## `clear_cookies`

Wipe all cookies in the current context.

```python
clear_cookies() -> str
```

---

## `set_viewport`

Resize the browser viewport on the fly. Great for responsive testing.

```python
set_viewport(width: int, height: int) -> tuple[str, Image]
```

**Parameters**

| Name | Type | Description |
|---|---|---|
| `width` | `int` | Width in pixels. |
| `height` | `int` | Height in pixels. |

**Examples**

```text
→ set_viewport(1920, 1080)        # desktop full-HD
→ set_viewport(390, 844)          # iPhone 14
→ set_viewport(768, 1024)         # iPad portrait
```

**Common device presets**

| Device | Width × Height |
|---|---|
| iPhone SE | 375 × 667 |
| iPhone 14 | 390 × 844 |
| iPhone 14 Pro Max | 430 × 932 |
| Pixel 7 | 412 × 915 |
| iPad | 768 × 1024 |
| iPad Pro | 1024 × 1366 |
| Desktop HD | 1920 × 1080 |

!!! info "About:blank first"
    If you get an error, navigate to `about:blank` first, then resize, then navigate to your target.

---

## See also

- **[Debug a web app guide](../guides/debug-web-app.md)** — console + network + errors in action
- **[Mobile responsive guide](../guides/mobile-responsive.md)** — using `set_viewport`

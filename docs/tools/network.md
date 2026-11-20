# Network control

Builds on the captured traffic from [DevTools](devtools.md#get_network_requests):
stub or block requests, wait for a specific response, read full headers and
bodies, and export everything as a HAR file.

URL patterns everywhere accept a plain **substring** (`/api/users`), a **glob**
(`**/api/*`), or a **regex** prefixed with `re:` (`re:/users/\d+$`).

---

## `mock_route`

```python
mock_route(url_pattern: str, status: int = 200, body: str = "",
           content_type: str = "application/json",
           headers: dict | None = None, abort: bool = False) -> str
```

Answers matching requests from every tab with a canned response, or fails them
(`abort=True`, e.g. to block trackers or simulate an outage). A second mock with
the same pattern replaces the first.

```text
→ mock_route("/api/cart", status=500, body='{"error": "boom"}')   # test the error state
→ mock_route("**/analytics/**", abort=True)                       # block a tracker
```

## `clear_mocks`

```python
clear_mocks(url_pattern: str | None = None) -> str
```

Removes one mock, or all of them.

---

## `wait_for_response`

```python
wait_for_response(url_pattern: str, status: int | None = None,
                  timeout_seconds: float = 10.0) -> tuple[str, Image]
```

Waits for a response whose URL matches. Responses that arrived during the
previous tool call count, so call it right after the click that fires the
request. Returns the `#id`, status, timing, and a body preview.

```text
→ click(12)
→ wait_for_response("/api/save", status=200)
Response received: #57 POST https://app.test/api/save -> 200 (84ms)
Body: {"ok": true}
```

## `get_request_details`

```python
get_request_details(request_id: int, include_body: bool = True) -> str
```

Request headers, POST data, response headers, and the response body (text
clipped to 10 000 characters, binary as base64) for a `#id` from
`get_network_requests` or `wait_for_response`. Bodies are read on demand and may
be unavailable once the page has navigated away.

## `export_har`

```python
export_har(name: str = "", include_bodies: bool = False) -> str
```

Writes the captured requests (the last 100) to `<BROWSER_RECORDINGS_DIR>/<name>.har`.
Open it in Chrome DevTools (Network → Import HAR) or any HAR viewer.

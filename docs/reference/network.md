---
title: Network
description: Mock or block requests, wait for a specific response, read full request details, and export HAR.
---

# Network

Control and inspect traffic. URL patterns accept a **substring** (`/api/users`), a **glob** (`**/api/*`), or a **regex** prefixed with `re:` (`re:/users/\d+$`).

| Tool | Does | Returns |
| --- | --- | --- |
| [`mock_route`](#mock_route) | Answer matching requests with a canned response, or block them, in every tab. | text |
| [`clear_mocks`](#clear_mocks) | Remove request mocks so requests reach the network again. | text |
| [`wait_for_response`](#wait_for_response) | Wait for a network response whose URL matches, e.g. the API call a click triggered. | text + screenshot |
| [`get_request_details`](#get_request_details) | Show one captured request in full: headers, POST data, response headers and body. | text |
| [`export_har`](#export_har) | Save the captured network traffic (last 100 requests) as a HAR file. | text |

## `mock_route` {#mock_route}

Answer matching requests with a canned response, or block them, in every tab.

```python
mock_route(url_pattern: str, status: int = 200, body: str = '', content_type: str = 'application/json', headers: dict[str, str] | None = None, abort: bool = False)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `url_pattern` | `str` | required | Substring of the URL, a glob like `**/api/users*`, or `re:<regex>` |
| `status` | `int` | `200` | HTTP status to return (default 200) |
| `body` | `str` | `""` | Response body (e.g. a JSON string) |
| `content_type` | `str` | `"application/json"` | Content-Type of the body (default application/json) |
| `headers` | `dict[str, str] \| None` | `None` | Extra response headers |
| `abort` | `bool` | `False` | Fail matching requests with a network error instead of responding |

Answers matching requests in every tab with a canned response, or fails them with `abort=True`. A second mock with the same pattern replaces the first. Mocks stay until [`clear_mocks`](#clear_mocks).

```text
→ mock_route("/api/cart", status=500, body='{"error": "boom"}')   # an error state
→ mock_route("/api/items", body='{"items": []}')                  # an empty list
→ mock_route("**/analytics/**", abort=True)                       # block a tracker
```

## `clear_mocks` {#clear_mocks}

Remove request mocks so requests reach the network again.

```python
clear_mocks(url_pattern: str | None = None)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `url_pattern` | `str \| None` | `None` | The pattern given to mock_route; omit to remove every mock |

Removes one mock by its pattern, or all of them with no argument.

## `wait_for_response` {#wait_for_response}

Wait for a network response whose URL matches, e.g. the API call a click triggered.

```python
wait_for_response(url_pattern: str, status: int | None = None, timeout_seconds: float = 10.0)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `url_pattern` | `str` | required | Substring of the URL, a glob like `**/api/save*`, or `re:<regex>` |
| `status` | `int \| None` | `None` | Only accept this HTTP status |
| `timeout_seconds` | `float` | `10.0` | Give up after this long (default 10) |

Waits for a response whose URL matches and returns its `#id`, status, timing, and a body preview. Responses that arrived during the previous tool call count, so call it right after the action that sends the request.

```text
→ click(12)
→ wait_for_response("/api/save", status=200)
Response received: #57 POST https://app.test/api/save -> 200 (84ms)
Body: {"ok": true}
```

## `get_request_details` {#get_request_details}

Show one captured request in full: headers, POST data, response headers and body.

```python
get_request_details(request_id: int, include_body: bool = True)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `request_id` | `int` | required | The #id shown by get_network_requests or wait_for_response |
| `include_body` | `bool` | `True` | Include the response body (text, truncated; binary as base64) |

Request headers, POST data, response headers, and the response body (text up to 10,000 characters, binary as base64) for an `#id` from `get_network_requests` or `wait_for_response`. Bodies are read on demand and may be gone once the page has navigated away.

## `export_har` {#export_har}

Save the captured network traffic (last 100 requests) as a HAR file.

```python
export_har(name: str = '', include_bodies: bool = False)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `name` | `str` | `""` | File name without extension (default: timestamp) |
| `include_bodies` | `bool` | `False` | Also save response bodies (up to 1MB each) |

Writes the captured requests (the last 100) to `<recordings dir>/<name>.har`. Open it in Chrome DevTools (Network → Import HAR) or any HAR viewer. `include_bodies=True` adds response bodies.

## See also

- [Test edge states](/recipes/edge-states)
- [Debug a web app](/recipes/debug)

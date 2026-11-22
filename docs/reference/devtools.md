---
title: DevTools
description: Console logs, page errors, network requests, element inspection, performance, cookies, and viewport size.
---

# DevTools

What the browser's developer tools would show you. Logs and requests are captured per session from the moment a tab opens.

| Tool | Does | Returns |
| --- | --- | --- |
| [`get_console_logs`](#get_console_logs) | Get browser console logs (errors, warnings, info, log messages). | text |
| [`get_page_errors`](#get_page_errors) | Get JavaScript errors that occurred on the page. | text |
| [`get_network_requests`](#get_network_requests) | Get captured network requests (API calls, resources, etc.). | text |
| [`inspect_element`](#inspect_element) | Inspect an element to get its computed styles, dimensions, and properties. | text |
| [`run_in_console`](#run_in_console) | Execute JavaScript code in the browser console and return the result. Useful for debugging, inspecting variables, or manipulating the page. | text + screenshot |
| [`get_page_performance`](#get_page_performance) | Get page performance metrics (load time, Core Web Vitals). | text |
| [`get_cookies`](#get_cookies) | Get all cookies for the current context. | text |
| [`set_cookie`](#set_cookie) | Set a cookie. | text |
| [`delete_cookie`](#delete_cookie) | Delete a cookie by name. Note: This deletes all cookies with this name across all domains in context. | text |
| [`clear_cookies`](#clear_cookies) | Clear all cookies. | text |
| [`get_storage`](#get_storage) | Read localStorage or sessionStorage for the current page's origin. | text |
| [`set_storage`](#set_storage) | Set a localStorage or sessionStorage item for the current page's origin. | text |
| [`clear_storage`](#clear_storage) | Remove one key from, or clear all of, localStorage or sessionStorage for the current origin. | text |
| [`set_viewport`](#set_viewport) | Set the browser viewport size. | text + screenshot |

## `get_console_logs` {#get_console_logs}

Get browser console logs (errors, warnings, info, log messages).

```python
get_console_logs(clear: bool = False)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `clear` | `bool` | `False` | If True, clear the captured logs after returning them |

The last 50 console messages with their level and source. `clear=True` empties the buffer after reading, so the next call shows only new messages.

```text
Console Logs:
[ERROR] Uncaught TypeError: items is undefined (http://localhost:3000/app.js:42:15)
[WARNING] Each child in a list should have a unique "key" prop.
```

## `get_page_errors` {#get_page_errors}

Get JavaScript errors that occurred on the page.

```python
get_page_errors()
```

Returns text only.

Uncaught exceptions with the first line of their stack.

```text
Page Errors:
 TypeError: Cannot read properties of undefined (reading 'map')
   at UserList (http://localhost:3000/src/UserList.tsx:14:22)
```

## `get_network_requests` {#get_network_requests}

Get captured network requests (API calls, resources, etc.).

```python
get_network_requests(num_requests: int | None = None, clear: bool = False)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `num_requests` | `int \| None` | `None` | Number of recent requests to return. Defaults to 30. |
| `clear` | `bool` | `False` | If True, clear the captured requests after returning them |

The most recent requests (30 by default), each with an `#id` to pass to [`get_request_details`](/reference/network#get_request_details). `clear=True` empties the buffer.

```text
Network Requests:
#12 GET https://api.example.com/users -> 200 (142ms)
#13 POST https://api.example.com/login -> 401 (89ms)
```

## `inspect_element` {#inspect_element}

Inspect an element to get its computed styles, dimensions, and properties.

```python
inspect_element(element_id: int)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `element_id` | `int` | required | The number label of the element to inspect |

Tag, id, classes, text, size, position, attributes, and key computed styles: what the browser actually rendered. Useful for "why is this invisible?" or "why did my click miss?".

## `run_in_console` {#run_in_console}

Execute JavaScript code in the browser console and return the result. Useful for debugging, inspecting variables, or manipulating the page.

```python
run_in_console(code: str)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `code` | `str` | required | JavaScript code to execute in the console |

Evaluates JavaScript like the DevTools console, with structured error handling, and returns the result with a fresh screenshot.

## `get_page_performance` {#get_page_performance}

Get page performance metrics (load time, Core Web Vitals).

```python
get_page_performance()
```

Returns text only.

Time to first byte, first contentful paint, DOMContentLoaded and load timings, resource count, and JS heap size.

## `get_cookies` {#get_cookies}

Get all cookies for the current context.

```python
get_cookies()
```

Returns text only.

All cookies in the current session, with their domains.

## `set_cookie` {#set_cookie}

Set a cookie.

```python
set_cookie(name: str, value: str, domain: str | None = None, path: str = '/')
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `name` | `str` | required | Cookie name |
| `value` | `str` | required | Cookie value |
| `domain` | `str \| None` | `None` | Cookie domain (optional, defaults to current page domain) |
| `path` | `str` | `"/"` | Cookie path (default: "/") |

Sets a cookie. Without `domain`, it uses the current page's domain.

## `delete_cookie` {#delete_cookie}

Delete a cookie by name. Note: This deletes all cookies with this name across all domains in context.

```python
delete_cookie(name: str)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `name` | `str` | required | — |

Deletes every cookie with this name, across all domains in the session.

## `clear_cookies` {#clear_cookies}

Clear all cookies.

```python
clear_cookies()
```

Returns text only.

Deletes every cookie in the session.

## `get_storage` {#get_storage}

Read localStorage or sessionStorage for the current page's origin.

```python
get_storage(kind: str = 'local', key: str | None = None)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `kind` | `str` | `"local"` | "local" for localStorage (default) or "session" for sessionStorage |
| `key` | `str \| None` | `None` | A single key to read. Omit to list every key with a value preview. |

Without `key`, lists every key with its value cut to 100 characters, prefixed by the origin and a count. With `key`, returns the full value or says the key is missing. Pages without storage access, such as `about:blank`, return a clear error.

## `set_storage` {#set_storage}

Set a localStorage or sessionStorage item for the current page's origin.

```python
set_storage(key: str, value: str, kind: str = 'local')
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `key` | `str` | required | Storage key |
| `value` | `str` | required | String value to store |
| `kind` | `str` | `"local"` | "local" for localStorage (default) or "session" for sessionStorage |

The page's own scripts see the change immediately; reload if the app only reads storage on load.

## `clear_storage` {#clear_storage}

Remove one key from, or clear all of, localStorage or sessionStorage for the current origin.

```python
clear_storage(kind: str = 'local', key: str | None = None)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `kind` | `str` | `"local"` | "local" for localStorage (default) or "session" for sessionStorage |
| `key` | `str \| None` | `None` | The key to remove. Omit to clear every key. |

Only touches the current origin's storage. Use `clear_cookies` for cookies.

## `set_viewport` {#set_viewport}

Set the browser viewport size.

```python
set_viewport(width: int, height: int)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `width` | `int` | required | Width in pixels |
| `height` | `int` | required | Height in pixels |

Resizes the viewport immediately. For a phone with its user agent and touch input, use [`emulate_device`](/reference/emulation#emulate_device).

## See also

- [Debug a web app](/recipes/debug)
- [Network](/reference/network)

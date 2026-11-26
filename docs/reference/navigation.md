---
title: Navigation
description: Open URLs, move through history, scroll, and find anything on the page.
---

# Navigation

Open pages, move through history, scroll, and search the whole page for the element you want.

| Tool | Does | Returns |
| --- | --- | --- |
| [`navigate_to`](#navigate_to) | Navigate to a URL. Returns an annotated screenshot with numbered interactive elements. | text + screenshot |
| [`find`](#find) | Search the whole page, including content scrolled out of view, and scroll to a match. | text + screenshot |
| [`scroll`](#scroll) | Scroll the page. | text + screenshot |
| [`go_back`](#go_back) | Navigate back to the previous page. | text + screenshot |
| [`go_forward`](#go_forward) | Navigate forward to the next page. | text + screenshot |
| [`refresh_page`](#refresh_page) | Refresh the current page. | text + screenshot |

## `navigate_to` {#navigate_to}

Navigate to a URL. Returns an annotated screenshot with numbered interactive elements.

```python
navigate_to(url: str)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `url` | `str` | required | The URL to navigate to |

Opens the URL in the current tab and waits for it to settle. `http`, `https`, and `about:blank` URLs work. `javascript:`, `file:`, `data:`, and `chrome:` URLs are blocked unless [`BROWSER_ALLOW_UNSAFE_SCHEMES`](/reference/configuration#navigation-policy) is `true`, and when [`BROWSER_ALLOWED_DOMAINS`](/reference/configuration#navigation-policy) is set, so is any host outside it. A blocked URL returns an error that names the URL and the setting. If a `localhost` URL refuses the connection, it retries with `127.0.0.1`. Navigation times out after [`BROWSER_TIMEOUT`](/reference/configuration#browser_timeout) (30 s).

```text
→ navigate_to("https://news.ycombinator.com")
→ navigate_to("http://localhost:3000")
```

## `find` {#find}

Search the whole page, including content scrolled out of view, and scroll to a match.

```python
find(query: str, role: str | None = None, nth: int = 1)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `query` | `str` | required | Text to look for (case-insensitive substring) |
| `role` | `str \| None` | `None` | Optional ARIA role to restrict matches to |
| `nth` | `int` | `1` | Which match to scroll to, 1-based (default 1) |

Searches every frame and open shadow root, including content scrolled out of view, scrolls to a match, and lists every match with the number it has in the new screenshot. A match inside a button maps to the button.

```text
→ find("Delete account")
Found 2 match(es) for 'Delete account'; scrolled to match 1.
  1. button 'Delete account' -> element [14]  <- scrolled here
  2. h2 'Delete account' -> off-screen; find('Delete account', nth=2) scrolls to it
```

`find("", role="button")` lists every button on the page.

## `scroll` {#scroll}

Scroll the page.

```python
scroll(direction: str = 'down', amount: str = 'medium')
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `direction` | `str` | `"down"` | "up", "down", "left", or "right" |
| `amount` | `str` | `"medium"` | "small" (100px), "medium" (400px), "large" (800px),     "page" (full viewport), "top", "bottom", or pixels like "500" |

| `amount` | Distance |
| --- | --- |
| `small` | 100 px |
| `medium` | 400 px |
| `large` | 800 px |
| `page` | 720 px |
| `top`, `bottom` | Jump to the top or bottom |
| `"500"` | Exactly that many pixels |

```text
→ scroll()                    # 400 px down
→ scroll("up", "small")
→ scroll("down", "bottom")
```

## `go_back` {#go_back}

Navigate back to the previous page.

```python
go_back()
```

Returns text and a fresh annotated screenshot.

Moves back one entry in the tab's history.

## `go_forward` {#go_forward}

Navigate forward to the next page.

```python
go_forward()
```

Returns text and a fresh annotated screenshot.

Moves forward one entry in the tab's history.

## `refresh_page` {#refresh_page}

Refresh the current page.

```python
refresh_page()
```

Returns text and a fresh annotated screenshot.

Reloads the current page and waits for it to settle.

## See also

- [Research a question](/recipes/research)
- [Set of Marks](/concepts/set-of-marks)

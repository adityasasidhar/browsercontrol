# Navigation

Tools for moving the browser around: opening URLs, going back/forward, refreshing, and scrolling.

!!! info "Response shape"
    All navigation tools that change the page state return `(text_summary, annotated_screenshot, element_map)`.

---

## `navigate_to`

Open a URL in the current tab.

```python
navigate_to(url: str) -> tuple[str, Image]
```

**Parameters**

| Name | Type | Description |
|---|---|---|
| `url` | `str` | The URL to open. `http://`, `https://`, `file://`, and `about:blank` all work. |

**Behavior**

- If `url` is `localhost` and DNS resolution fails, **automatically retries with `127.0.0.1`** to bypass proxy blockers.
- Waits up to `BROWSER_TIMEOUT` ms (default 30s) for `domcontentloaded`.
- Returns the post-navigation annotated screenshot and a fresh element map.

**Example**

```text
→ navigate_to("https://news.ycombinator.com")
→ navigate_to("http://localhost:3000")     # auto-fallback to 127.0.0.1
```

---

## `go_back`

Navigate back in browser history.

```python
go_back() -> tuple[str, Image]
```

**Example**

```text
→ go_back()
```

!!! note "No history yet?"
    Returns the current page unchanged if there is no previous entry in history.

---

## `go_forward`

Navigate forward in browser history.

```python
go_forward() -> tuple[str, Image]
```

---

## `refresh_page`

Reload the current page.

```python
refresh_page() -> tuple[str, Image]
```

**Example**

```text
→ refresh_page()
```

---

## `scroll`

Scroll the viewport in a direction by a named amount or raw pixel count.

```python
scroll(direction: str = "down", amount: str = "medium") -> tuple[str, Image]
```

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `direction` | `str` | `"down"` | One of: `up`, `down`, `left`, `right`. |
| `amount` | `str` | `"medium"` | Named (`small`, `medium`, `large`, `page`, `top`, `bottom`) **or** raw pixels as a string (e.g. `"500"`). |

**Named amounts**

| Name | Pixels |
|---|---|
| `small` | 200 |
| `medium` | 500 |
| `large` | 1000 |
| `page` | one full viewport |
| `top` | scroll to top |
| `bottom` | scroll to bottom |

**Examples**

```text
→ scroll("down")                          # 500px down
→ scroll("up", "small")                   # 200px up
→ scroll("down", "500")                   # exactly 500px
→ scroll("down", "page")                  # one viewport
→ scroll("down", "bottom")                # jump to bottom
```

---

## `find`

Search the whole page, including content scrolled out of view, and scroll to a match.

```python
find(query: str, role: str | None = None, nth: int = 1) -> tuple[str, Image]
```

| Name | Type | Default | Description |
|---|---|---|---|
| `query` | `str` | | Case-insensitive text to look for. Matches visible text and `aria-label`, `placeholder`, `title`, `alt`, and field values. |
| `role` | `str \| None` | `None` | Only elements with this ARIA role (`button`, `link`, `textbox`, `heading`, …). `query` then filters by name and may be empty. |
| `nth` | `int` | `1` | Which match to scroll to. |

Searches every frame and open shadow root. The response lists every match with
the element ID it maps to in the new screenshot (a match inside a button maps to
the button), or tells you which `nth` scrolls to an off-screen one.

```text
→ find("Delete account")
Found 2 match(es) for 'Delete account'; scrolled to match 1.
  1. button 'Delete account' -> element [14]  <- scrolled here
  2. h2 'Delete account' -> off-screen; find('Delete account', nth=2) scrolls to it
```

---

## See also

- **[Interaction tools](interaction.md)** — click, type, hover
- **[Tabs tools](tabs.md)** — multi-page navigation
- **[Web research guide](../guides/web-research.md)** — a worked example

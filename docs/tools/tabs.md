# Tabs

Multi-tab orchestration. BrowserControl lets the agent open, switch, close, and list tabs without losing context.

!!! info "Tab indices are 0-based"
    Tab 0 is the first tab. Use `list_tabs()` to see current indices — they can shift if you close a tab.

---

## `create_tab`

Open a new tab, optionally navigated to a URL.

```python
create_tab(url: str | None = None) -> tuple[str, Image]
```

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `url` | `str \| None` | `None` | Optional URL to open. If omitted, opens `about:blank`. |

**Behavior**

- Creates a new browser tab.
- Focuses the new tab.
- Returns an annotated screenshot and element map for the new tab's page (if any).

**Examples**

```text
→ create_tab()                                    # new empty tab
→ create_tab("https://news.ycombinator.com")      # new tab navigated to HN
```

---

## `switch_tab`

Switch to a tab by its 0-based index.

```python
switch_tab(index: int) -> tuple[str, Image]
```

**Parameters**

| Name | Type | Description |
|---|---|---|
| `index` | `int` | The tab's 0-based position in the tab bar. |

**Behavior**

- Makes the tab at `index` the active tab.
- Returns an annotated screenshot and element map for the newly active tab.

**Example**

```text
→ list_tabs()       # see current indices
→ switch_tab(1)     # focus the second tab
```

!!! warning "Indices shift"
    If you `close_tab(0)`, what was index 1 becomes index 0. Always re-list after a close.

---

## `close_tab`

Close a tab by its 0-based index.

```python
close_tab(index: int) -> tuple[str, Image]
```

**Parameters**

| Name | Type | Description |
|---|---|---|
| `index` | `int` | The tab's 0-based position. |

**Behavior**

- Closes the tab at `index`.
- **Auto-falls-back to another open tab** if you close the active one — you won't lose the browser session.
- Returns an annotated screenshot of whichever tab becomes active.

---

## `list_tabs`

List all open tabs with their title, URL, and active marker.

```python
list_tabs() -> str
```

**Returns**

```text
Open Tabs:
  [0] GitHub - https://github.com (active)
  [1] Hacker News - https://news.ycombinator.com
  [2] about:blank
```

!!! info "Plain text return"
    `list_tabs` returns a plain string — no screenshot. It's cheap to call.

---

## See also

- **[Multi-tab research guide](../guides/multi-tab.md)** — a worked example
- **[Navigation tools](navigation.md)** — `navigate_to` works on the active tab

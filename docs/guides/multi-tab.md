# Multi-tab research

When the question needs more than one source, BrowserControl's tab tools let the agent open multiple pages, switch between them, and read from each.

## What the agent does

> _"Open GitHub in one tab and Hacker News in another, then tell me the top repo and the top story."_

```text
→ create_tab("https://github.com/trending")
→ create_tab("https://news.ycombinator.com")
→ list_tabs()                    # → see both tabs with their indices
→ switch_tab(0)                  # focus GitHub
→ get_page_content()
→ switch_tab(1)                  # focus HN
→ get_page_content()
```

## Step by step

### 1. Open the tabs

```text
create_tab("https://github.com/trending")
create_tab("https://news.ycombinator.com")
```

Each `create_tab` returns an annotated screenshot of the newly active tab, so you can keep going from there.

### 2. Confirm what's open

```text
list_tabs()
```

Returns:

```text
Open Tabs:
  [0] GitHub Trending · Build software better, together - https://github.com/trending (active)
  [1] Hacker News - https://news.ycombinator.com
```

Note: `list_tabs` returns plain text — no screenshot, so it's cheap.

### 3. Switch and read each tab

```text
switch_tab(0)              # focus GitHub Trending
get_page_content()

switch_tab(1)              # focus HN
get_page_content()
```

The agent now has content from both sources and can synthesize the answer.

## Workflows that benefit from multi-tab

### Compare products

> _"Compare the pricing pages of Linear and Height."_

```text
create_tab("https://linear.app/pricing")
create_tab("https://height.app/pricing")
list_tabs()
switch_tab(0); get_page_content()
switch_tab(1); get_page_content()
```

### Search then drill in

> _"Search for X, then click the first result and tell me more."_

```text
create_tab("https://duckduckgo.com/?q=fastmcp+python")
# ... parse results, find the link to click ...
click(8)             # first organic result, opens in the SAME tab
get_page_content()
```

### Persist context across tabs

Cookies and `localStorage` are shared across all tabs in the same browser context. Log in once in one tab, and every other tab is logged in too.

## Tips

!!! warning "Indices shift after `close_tab`"
    Closing tab `[0]` makes what was `[1]` become `[0]`. Always re-list before switching after a close.

!!! tip "Use `take_snapshot` to checkpoint"
    Save the state of each tab with `take_snapshot("after_search")`. Useful when you want to come back to a specific state later.

!!! info "Shared session"
    Tabs share cookies, `localStorage`, and `sessionStorage` — they all live in the same browser context. This is usually what you want.

## See also

- **[Tabs tools reference](../tools/tabs.md)** — `create_tab`, `switch_tab`, `close_tab`, `list_tabs`
- **[Web research guide](web-research.md)** — single-tab research pattern

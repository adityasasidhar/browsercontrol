# Your first session

A guided tour of the BrowserControl action loop. By the end you'll know how to navigate, see, click, type, and debug — and you'll understand the **Set of Marks** response pattern that makes all of this work.

## The core idea

Every action in BrowserControl returns the same shape:

1. **An annotated screenshot** — your current viewport with numbered red boxes over every interactive element.
2. **A textual element map** — the same elements as a list of `[id] tag - text`.

The agent picks a number; BrowserControl does the rest.

## Step 1 — Navigate

Ask your agent:

> _"Open the Playwright homepage and tell me what's there."_

The agent will call `navigate_to("https://playwright.dev")`. You'll get back something like:

```text
Navigated to https://playwright.dev

Found 8 interactive elements:
  [1] a - Get started
  [2] a - Docs
  [3] a - API
  [4] a - GitHub
  [5] button - Search (Ctrl+K)
  [6] input - Search…
  [7] a - Node.js
  [8] a - Python
```

…and an annotated screenshot showing the same numbers as red boxes on the page.

## Step 2 — Click

> _"Click Get started."_

The agent calls `click(1)`:

```text
Clicked element 1 (a: Get started)

Found 12 interactive elements:
  [1] a - Installation
  [2] a - Writing tests
  [3] a - Running tests
  ...
```

Notice how the element IDs are **fresh after every action** — they reflect the current page state, not the state at navigation.

## Step 3 — Type

> _"Search for 'browser automation'."_

```text
→ click(6)              # the search input
→ type_text(6, "browser automation")
→ press_key("Enter")
→ get_page_content()
```

`type_text` uses `element.fill()` under the hood — it's atomic and reliable, not char-by-char typing. Works with `<input>`, `<textarea>`, and content-editable elements.

## Step 4 — Debug

> _"Are there any JavaScript errors on this page?"_

```text
→ get_page_errors()
→ get_console_logs()
→ get_network_requests()
```

DevTools come built-in — no second tool needed.

## Step 5 — Screenshot & save

> _"Save a full-page screenshot and a snapshot of the DOM."_

```text
→ screenshot(annotate=False, full_page=True)
→ take_snapshot("after_search")
```

Snapshots save a `(URL, HTML, PNG)` triple to `~/.browsercontrol/snapshots/` — handy for debugging later or sharing with a teammate.

## What you should take away

!!! tip "The action loop"
    1. **Call a tool.** The tool returns an annotated screenshot + element map.
    2. **Read the element map.** Pick a number (or use `get_text` / `get_page_content` to read more).
    3. **Call the next tool.** Element IDs are fresh on every response.

    The whole interface is **read screenshot → pick number → call next tool**. That's it.

## Try these next

- **[Browse the tools](../tools/index.md)** — see everything available.
- **[Web research guide](../guides/web-research.md)** — a full worked example.
- **[Debug a web app](../guides/debug-web-app.md)** — console + network + errors in 30 seconds.

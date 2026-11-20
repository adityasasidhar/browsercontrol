---
title: How it works
description: The act, settle, look loop every BrowserControl tool runs, what a tool response contains, and how the pieces fit together.
---

# How it works

Three things are involved: your **agent** (a model plus an MCP client), the **BrowserControl server**, and a real **Chromium** that the server drives through [Playwright](https://playwright.dev/python/). The agent never touches the page directly. It calls tools, and every tool that changes the page answers with a fresh picture of it.

```text
  Agent + MCP client            BrowserControl              Chromium
 ───────────────────         ───────────────────        ────────────────
  click(7)          ───────▶  find element 7     ─────▶  real click
                              wait for the page to settle
  screenshot + map  ◀───────  number the controls ◀────  screenshot
```

## The loop

Every page-changing tool runs the same cycle.

<div class="steps">

### Act

The agent names an element by its number, for example `click(7)`. BrowserControl looks up element 7 in the current tab's map and finds that exact element again through a tag it placed on it, inside the right frame and through shadow DOM. If the element was removed, hidden, or moved since the screenshot, the tool doesn't act. It returns a [stale ID](/concepts/set-of-marks#stale-ids) error and a fresh screenshot instead.

### Settle

The page is given time to finish reacting: the DOMContentLoaded event, then in-flight network requests, then DOM changes, all within a budget of 3 seconds by default. See [Settling](/concepts/settling).

### Look

BrowserControl takes a screenshot, finds the interactive elements in every frame, numbers them, draws the boxes, and returns the image together with a text list of the same numbers. The previous map is replaced.

</div>

## What a response looks like

A tool like `click` returns a status line, any notices, the element list, and the annotated image:

```text
Clicked element 7 (button: Add to cart)

Notice: Downloaded invoice.pdf to /home/me/.browsercontrol/downloads/invoice.pdf

Found 23 interactive elements:
  [1] a - acme.shop
  [2] a - Shop
  [3] input[search] - Search keyboards
  [4] button[submit] - Search
  [5] input[checkbox] - In stock only
  [6] button (disabled) - Checkout
  ...
```

- **Status line.** What the tool did, or `Error: …` and why.
- **Notices.** Things that happened during the action that the screenshot can't show, such as a [JS dialog](/reference/waiting#handle_dialog) that was answered or a file that was downloaded.
- **Element list.** One line per element: number, tag, input type, `(disabled)` when relevant, and up to 40 characters of its text. It lists the first 30 elements; higher numbers still work.
- **Image.** The screenshot with the same numbers drawn on it.

Tools that only read (like `get_console_logs`, `list_tabs`, or the extraction tools) return text without a screenshot. The [tool explorer](/reference/) marks which is which.

## The pieces

| Part | What it does |
| --- | --- |
| **Server** | A [FastMCP](https://gofastmcp.com) app with 69 tools, 8 `browser://` [resources](/reference/resources), and middleware that binds each call to the calling client's session. It serves stdio by default, or [Streamable HTTP](/guide/http). |
| **Browser manager** | Starts the browser: a persistent profile, or [your own Chrome](/recipes/your-chrome) over CDP. Settles the page after each action and keeps one element map per tab. |
| **Element detection** | Runs in every frame (cross-origin included), descends into open shadow roots, keeps elements that are visible and not covered, and tags each with a numbered attribute so it can be found again. |
| **Sessions** | Each [session](/concepts/sessions) is one browser context with its own tabs, captured console and network data, mocks, emulation, dialog policy, and action log. |
| **Codegen** | Records each action with a locator a person would write, for [`export_test`](/reference/recording#export_test). |

## Why a screenshot plus a list

- **Nothing to invent.** The model picks a number it can see. It never writes `div.flex > button:nth-child(3)` and hopes.
- **Both views at once.** The image shows layout, color, and state; the list names icon-only buttons and input types the image can't.
- **Small.** A list of numbered elements costs far fewer tokens than a DOM or accessibility tree.
- **Honest about change.** Numbers are rebuilt every time, and an out-of-date number is refused rather than silently applied to whatever moved into its place.

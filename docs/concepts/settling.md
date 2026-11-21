---
title: Settling
description: How BrowserControl waits for a page to finish reacting after each action, and when to wait longer with wait_for or wait_for_response.
---

# Settling

After every action, BrowserControl waits for the page to finish reacting before it takes the screenshot. A single-page app that fetches data and then renders is captured complete, not half drawn, and the agent rarely needs to sleep.

## The three stages

<div class="steps">

### Load

Wait for the `DOMContentLoaded` event, which matters after a navigation.

### Network quiet

Wait until no request has been in flight for 200 ms. Streams (WebSocket, EventSource, media) and requests open for more than 10 seconds, such as long polling, are ignored so they can't hold every action hostage.

### DOM quiet

Wait until the page has gone 200 ms without a DOM change, for at most one second.

</div>

All three share one budget, [`BROWSER_SETTLE_TIMEOUT`](/reference/configuration#browser_settle_timeout), 3 seconds by default. When the budget runs out, BrowserControl takes the screenshot anyway. Settling never fails an action.

Tune the budget for your sites: lower it on static pages for speed, raise it for slow apps.

## When to wait longer

Some things take longer than any sensible budget: a report that renders after ten seconds, a payment that confirms asynchronously. Wait for the condition itself rather than for time.

| You're waiting for | Use |
| --- | --- |
| Text to appear | `wait_for(text="Order confirmed")` |
| An element to appear or go away | `wait_for(selector=".spinner", state="hidden")` |
| All network activity to stop | `wait_for(network_idle=True)` (500 ms with nothing in flight) |
| A specific API call | `wait_for_response("/api/orders")`, called right after the action that sends it |
| Nothing in particular | `wait(seconds)`, as a last resort |

`wait_for` and `wait_for_response` time out after 10 seconds by default (`timeout_seconds`). A timeout isn't an error: the response says what timed out and still includes the screenshot.

```text
→ click(12)                                   # "Place order"
→ wait_for_response("/api/orders", status=201)
Response received: #57 POST https://shop.test/api/orders -> 201 (842ms)
Body: {"id": "ord_123", "status": "confirmed"}
```

`wait_for_response` also counts responses that arrived during the previous tool call, so calling it right after the click never misses a fast response.

## Things that happen while settling

A JS `alert`, `confirm`, or `prompt` can't be allowed to block the page, so BrowserControl answers it straight away. Alerts are acknowledged, confirms and prompts are dismissed, and `beforeunload` is accepted. Files the page downloads are saved. Both show up as `Notice:` lines at the top of the next response:

```text
Notice: A JS dialog appeared: confirm('Delete this item?'), dismissed. Call handle_dialog() before the action to choose the answer.
```

To answer differently, call [`handle_dialog(accept=True)`](/reference/waiting#handle_dialog) and repeat the action.

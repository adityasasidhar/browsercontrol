---
title: Test edge states
description: Check how a page handles server errors, empty data, slow or offline networks, and other hard-to-reach states with request mocks and throttling.
---

# Test edge states

The bugs that hurt are in states a real backend rarely produces on demand: a 500 from the API, an empty list, a slow network. Mock the request or throttle the network, and let the agent check what the page does.

> On localhost:3000/cart, make the cart API fail and check that the page shows a useful error.

```text
→ mock_route("/api/cart", status=500, body='{"error": "internal"}')
→ navigate_to("http://localhost:3000/cart")
→ get_console_logs()
→ clear_mocks()
```

<div class="steps">

### Mock before you load

```text
→ mock_route("/api/cart", status=500, body='{"error": "internal"}')
```

From now on, every tab in the session answers matching requests with this response. A second mock with the same pattern replaces the first.

Patterns can be a **substring** (`/api/cart`), a **glob** (`**/api/*`), or a **regex** prefixed with `re:` (`re:/users/\d+$`).

### Load the page and check it

```text
→ navigate_to("http://localhost:3000/cart")
```

The screenshot shows what a user would see. `get_console_logs()` and `get_page_errors()` show what they wouldn't.

### Clean up

```text
→ clear_mocks()
```

Mocks stay until you clear them. `clear_mocks("/api/cart")` removes just one.

</div>

## Common mocks

| State | Mock |
| --- | --- |
| Server error | `mock_route("/api/cart", status=500, body='{"error": "internal"}')` |
| Empty list | `mock_route("/api/cart", body='{"items": []}')` |
| Signed out | `mock_route("/api/me", status=401)` |
| Outage | `mock_route("/api/", abort=True)` |
| A tracker you don't want | `mock_route("**/analytics/**", abort=True)` |
| Custom headers | `mock_route("/api/cart", body="{}", headers={"Retry-After": "30"}, status=429)` |

## Slow and offline

```text
→ throttle_network("slow-3g")
→ refresh_page()
```

Check spinners, skeletons, and timeouts. Profiles are `slow-3g`, `fast-3g`, and `4g` (Chrome DevTools' presets), `offline`, and `none` to restore the network.

## Requests the page sends later

When a request fires on a click, wait for it right after the click:

```text
→ click(8)                           # "Apply coupon"
→ wait_for_response("/api/coupon")
Response received: #31 POST http://localhost:3000/api/coupon -> 500 (12ms)
Body: {"error": "internal"}
```

Pass the `#id` to `get_request_details` for the full headers and body.

::: tip Turn it into a test
Mocks are part of the action log, so [`export_test`](/recipes/record-tests#export-a-playwright-test) reproduces them in the generated Playwright test.
:::

For devices, dark mode, timezones, and locations, see [Mobile & dark mode](/recipes/responsive).

# Test error and edge states

Most bugs hide in states that are hard to reach on a real backend: a 500 from
the API, an empty list, a slow network, a user in another timezone. Mock the
request or emulate the condition, and let the agent check what the page does.

## What the agent does

> _"On localhost:3000/cart, make the cart API fail and check that the page shows a useful error."_

```text
→ mock_route("/api/cart", status=500, body='{"error": "internal"}')
→ navigate_to("http://localhost:3000/cart")
→ get_page_content()
→ get_console_logs()
→ clear_mocks()
```

## Step by step

### 1. Mock the request before loading the page

```text
mock_route("/api/cart", status=500, body='{"error": "internal"}')
```

Every tab in the session answers matching requests with this response until you
clear it. Patterns can be a substring (`/api/cart`), a glob (`**/api/*`), or a
regex (`re:/users/\d+$`).

Common mocks:

| State | Mock |
|---|---|
| Server error | `mock_route("/api/cart", status=500, body='{"error": "internal"}')` |
| Empty list | `mock_route("/api/cart", body='{"items": []}')` |
| Signed out | `mock_route("/api/me", status=401)` |
| Outage | `mock_route("/api/", abort=True)` |
| Blocked tracker | `mock_route("**/analytics/**", abort=True)` |

### 2. Load the page and check it

```text
navigate_to("http://localhost:3000/cart")
```

The screenshot shows what a user would see. Then check what users wouldn't:

```text
get_console_logs()     # errors the app logged
get_page_errors()      # uncaught exceptions
```

### 3. Trigger requests from the page

If the request fires on a click rather than on load, wait for it right after
the click:

```text
click(8)                                   # "Apply coupon"
wait_for_response("/api/coupon")
```

`wait_for_response` returns the request's `#id`, status, and body preview. Pass
the `#id` to `get_request_details` for full headers and body.

### 4. Slow things down

```text
throttle_network("slow-3g")
refresh_page()
```

Use this to check loading spinners, skeletons, and timeouts. Profiles are
`slow-3g`, `fast-3g`, `4g`, `offline`, and `none`.

### 5. Change who the user is

```text
emulate_device("iPhone 13")
set_timezone("Asia/Tokyo")
set_geolocation(35.68, 139.69)
set_color_scheme("dark")
```

These apply to every tab in the session, including tabs opened later.

### 6. Clean up

```text
clear_mocks()
reset_emulation()
```

## Tips

!!! tip "Turn the check into a test"
    Mocks are recorded in the action log, so
    [`export_test`](record-tests.md#6-export-a-playwright-test) reproduces them
    in the generated Playwright test.

!!! tip "Share the evidence"
    `export_har("cart-500")` saves the captured traffic as a HAR file you can
    attach to a bug report.

## See also

- **[Network control reference](../tools/network.md)**: `mock_route`, `wait_for_response`, `export_har`
- **[Emulation reference](../tools/emulation.md)**: devices, location, timezone, throttling
- **[Debug a web app](debug-web-app.md)**: console, network, and errors on a real backend

---
title: Mobile & dark mode
description: Check a page on phones and tablets, in dark mode, and in other timezones and locations with BrowserControl's emulation tools.
---

# Mobile & dark mode

> Check the home page on an iPhone in dark mode and tell me if anything overflows.

```text
→ emulate_device("iPhone 13")
→ set_color_scheme("dark")
→ navigate_to("https://my-site.test")
→ screenshot(annotate=False, full_page=True)
→ reset_emulation()
```

## Pick how faithful you need to be

| Need | Use | What you get |
| --- | --- | --- |
| A quick size check | `set_viewport(390, 844)` | The viewport only |
| A phone, quickly | `emulate_device("iPhone 13")` | Screen size, user agent, and touch input, then a reload |
| A phone, exactly | `create_session("phone", device="iPhone 13")` | A new context created as that device, pixel ratio and mobile layout viewport included |

Device pixel ratio and the mobile layout viewport can only be set when a browser context is created, which is why the exact option opens a new [session](/concepts/sessions). `list_devices("iphone")` shows the available names (about 140 phones, tablets, and desktops).

## Other conditions

| Condition | Tool |
| --- | --- |
| Dark or light mode | `set_color_scheme("dark")`, `"light"`, or `"no-preference"` |
| Another timezone | `set_timezone("Asia/Tokyo")`; `""` resets |
| Another location | `set_geolocation(35.68, 139.69)`, which also grants the permission |
| A slow or offline network | `throttle_network("slow-3g")`; see [Test edge states](/recipes/edge-states) |

Emulation applies to every tab in the session, including tabs opened later, and stays until `reset_emulation()`.

## Capture the result

- `screenshot(annotate=False)` gives a clean image for a bug report.
- `screenshot(annotate=False, full_page=True)` captures the whole scrollable page. Full-page screenshots are never annotated, so use them to review layout, not to find numbers.

## Compare several sizes

```text
→ set_viewport(1440, 900);  screenshot(annotate=False, full_page=True)
→ set_viewport(768, 1024);  screenshot(annotate=False, full_page=True)
→ set_viewport(390, 844);   screenshot(annotate=False, full_page=True)
```

Each screenshot comes back inline, so the agent can compare them directly.

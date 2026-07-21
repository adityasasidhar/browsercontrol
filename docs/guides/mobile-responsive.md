# Mobile responsive check

Resize the viewport to phone or tablet dimensions and screenshot the page. Useful for QA and visual regression checks.

## What the agent does

> _"Switch to iPhone 14 viewport and screenshot the homepage."_

```text
→ set_viewport(390, 844)
→ navigate_to("https://my-site.com")
→ screenshot(annotate=False, full_page=True)
```

## Step by step

### 1. Resize the viewport

```text
set_viewport(390, 844)         # iPhone 14
```

The viewport resizes on the fly. The current page will reflow (or not, if it doesn't have responsive CSS — that's the bug you're looking for).

### 2. Navigate (or navigate first, then resize)

You can do either order:

```text
# Resize first, then navigate
set_viewport(390, 844)
navigate_to("https://my-site.com")

# Or navigate first, then resize
navigate_to("https://my-site.com")
set_viewport(390, 844)
```

Both work. Resize-first is faster if you're doing many devices in a row.

### 3. Screenshot

```text
screenshot(annotate=False, full_page=True)
```

`annotate=False` keeps the screenshot clean (no red boxes) — better for sharing with teammates or attaching to bug reports.

`full_page=True` captures the entire scrollable page, not just the viewport. Useful for seeing the whole responsive layout in one image.

## Common device presets

| Device | Width × Height | Viewport |
|---|---|---|
| iPhone SE | 375 × 667 | `set_viewport(375, 667)` |
| iPhone 14 | 390 × 844 | `set_viewport(390, 844)` |
| iPhone 14 Pro Max | 430 × 932 | `set_viewport(430, 932)` |
| Pixel 7 | 412 × 915 | `set_viewport(412, 915)` |
| iPad | 768 × 1024 | `set_viewport(768, 1024)` |
| iPad Pro | 1024 × 1366 | `set_viewport(1024, 1366)` |
| Desktop HD | 1920 × 1080 | `set_viewport(1920, 1080)` |

## Comparing multiple devices

For "check that this page works on every common viewport", loop through them:

```text
→ set_viewport(1920, 1080); navigate_to("https://my-site.com")
→ screenshot(annotate=False, full_page=True)        # save as desktop_*.png

→ set_viewport(768, 1024); navigate_to("https://my-site.com")
→ screenshot(annotate=False, full_page=True)        # save as tablet_*.png

→ set_viewport(390, 844); navigate_to("https://my-site.com")
→ screenshot(annotate=False, full_page=True)        # save as mobile_*.png
```

Each `screenshot` returns the image inline — the agent can compare them, or your MCP client can save them to disk.

## Tips

!!! tip "Navigate to `about:blank` first if you get errors"
    A few sites don't like being resized mid-load. If `set_viewport` fails, navigate to `about:blank` first, resize, then navigate to your target.

!!! tip "User agent is real Chromium"
    BrowserControl doesn't fake the user agent. The browser identifies as the default Chromium UA at the chosen viewport size. If you need to fake a mobile UA (some sites check), use `run_javascript` to override `navigator.userAgent`.

!!! tip "Persistent context"
    Cookies, `localStorage`, and session state persist across resizes. Resize, screenshot, resize, screenshot — same browser session.

## See also

- **[DevTools reference](../tools/devtools.md#set_viewport)** — `set_viewport` signature
- **[Content tools reference](../tools/content.md#screenshot)** — `screenshot` parameters

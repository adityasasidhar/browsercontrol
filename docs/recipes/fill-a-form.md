---
title: Fill a form
description: Fill text fields, dropdowns, checkboxes, and custom widgets with BrowserControl, then submit and verify the result.
---

# Fill a form

> Sign up on the demo shop with the name Ada Lovelace and ada@example.com, pick "United Kingdom", accept the terms, and submit.

```text
→ navigate_to("https://shop.test/signup")
→ act([{"action": "type", "element_id": 3, "text": "Ada Lovelace"},
       {"action": "type", "element_id": 4, "text": "ada@example.com"},
       {"action": "select", "element_id": 5, "option": "United Kingdom"},
       {"action": "check", "element_id": 6}])
→ click(7)
→ wait_for(text="Welcome")
```

## Pick the right tool for each control

| Control | Tool | Notes |
| --- | --- | --- |
| Text, email, search, textarea, rich text | `type_text(id, text)` | **Replaces** the current value. To append, read it with `get_text(id)` first. |
| Native `<select>` | `select_option(id, option)` | Matches the visible label or the value; lists the options if nothing matches. |
| Checkbox or radio | `check_checkbox(id, check=True)` | **Sets** the state; calling it twice is safe. Works on styled inputs too. |
| File input | `upload_file(id, path)` | See [Upload a file](/recipes/upload-a-file). |
| Custom dropdown (React Select, Headless UI…) | `click` to open, then `click` the option | The options get numbers once the list is open. Or type and press `ArrowDown`, `Enter`. |
| Date pickers and sliders | `type_text` if it's an input, otherwise click or drag | Many date inputs accept typed text such as `2026-12-24`. |

`type_text` refuses checkboxes, buttons, dropdowns, and file inputs, and names the right tool instead.

## Fill several fields at once

When all the fields are on screen, [`act`](/reference/interaction#act) fills them in one call and returns one screenshot. Every ID in the batch refers to the screenshot from **before** the call, so read them all first. `act` stops at the first failed step unless you pass `stop_on_error=False`. Up to 25 steps.

Fields below the fold need a separate pass: `scroll` or `find` them, then read the new numbers.

## Submit and verify

Find Submit in the **latest** map and click it. Don't trust that the form went through until you see the result:

- `wait_for(text="Welcome")` waits for the confirmation instead of a fixed sleep.
- Look for validation messages in the screenshot, or read them with `get_page_content()`.
- A disabled Submit (`(disabled)` in the list) usually means a required field is still empty.

::: warning Passwords and personal data
Typed text shows up in tool results and in your client's transcript. Use test accounts, and don't paste real credentials into a prompt. If you [export a test](/recipes/record-tests), typed passwords become environment variables rather than literals.
:::

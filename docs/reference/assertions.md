---
title: Assertions
description: Verify text, the URL, and field values, and record passing checks as expect() lines in export_test.
---

# Assertions

These tools check the page and answer `PASS:` or `FAIL:` without a screenshot. A mismatch is not an error. Each passing check is recorded in the session's action log, so [`export_test`](/reference/recording#export_test) turns it into an `expect()` assertion in the generated Playwright test.

| Tool | Does | Returns |
| --- | --- | --- |
| [`verify_text`](#verify_text) | Check that text is (or is not) on the page, or inside one element. | text |
| [`verify_url`](#verify_url) | Check that the current URL matches a pattern. | text |
| [`verify_value`](#verify_value) | Check that an input, textarea, or select has exactly the expected value. | text |

## `verify_text` {#verify_text}

Check that text is (or is not) on the page, or inside one element.

```python
verify_text(text: str, element_id: int | None = None, present: bool = True)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `text` | `str` | required | The text to look for |
| `element_id` | `int \| None` | `None` | Only look inside this element's text (from the latest screenshot) |
| `present` | `bool` | `True` | False to check that the text is NOT there |

Without `element_id`, the check passes when an element with that text is visible. With one, it passes when the element's text contains it. `present=False` inverts either check.

```text
→ verify_text(text="Order confirmed")
PASS: 'Order confirmed' is visible on the page
```

In the exported test this becomes `expect(page.get_by_text("Order confirmed").first).to_be_visible()`, or `to_contain_text` / `not_to_contain_text` on the element's locator.

## `verify_url` {#verify_url}

Check that the current URL matches a pattern.

```python
verify_url(pattern: str)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `pattern` | `str` | required | A plain substring, a glob with `*` or `?`, or `re:<regex>` |

Prefix `re:` for a regular expression, `*` or `?` for a glob, anything else is a substring. The exported test uses `expect(page).to_have_url(...)`.

## `verify_value` {#verify_value}

Check that an input, textarea, or select has exactly the expected value.

```python
verify_value(element_id: int, expected: str)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `element_id` | `int` | required | The field's number from the latest screenshot |
| `expected` | `str` | required | The value the field should hold |

The exported test uses `expect(locator).to_have_value(...)`. Values of password fields are never recorded, so their check becomes a comment.

## See also

- [Recording](/reference/recording): `export_test` turns the action log into a test.

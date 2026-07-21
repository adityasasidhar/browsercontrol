# Content

Read what's on the page. Markdown extraction, element text, JS evaluation, and screenshots.

---

## `get_page_content`

Get the whole page as Markdown (scripts, styles, and noise stripped).

```python
get_page_content() -> tuple[str, Image]
```

**Returns**

```text
# Python programming language

Python is a high-level, general-purpose programming language. Its design
philosophy emphasizes code readability with the use of significant
indentation...

Found 12 interactive elements:
  [1] a - Contents
  [2] a - History
  ...
```

**Behavior**

- HTML → Markdown conversion via `markdownify`.
- 30 KB cap (the result is truncated with a note if the page is longer).
- Returns both the content and a screenshot so you can still see what's interactive.

!!! tip "When to use"
    Best for: reading articles, documentation, search results, blog posts.
    Not great for: heavy SPAs with mostly JavaScript-rendered text — for those, use `run_javascript` to extract what you need.

---

## `get_text`

Read text from a specific element by its **Set of Marks** number.

```python
get_text(element_id: int) -> str
```

**Parameters**

| Name | Type | Description |
|---|---|---|
| `element_id` | `int` | The number label of the element to read. |

**Returns**

```text
Python is a high-level, general-purpose programming language...
```

**When to use**

- You want just one paragraph's text without the full page dump.
- You're extracting structured data from a list or table.

---

## `get_page_info`

Get the current URL and page title.

```python
get_page_info() -> str
```

**Returns**

```text
Current page info:
  URL: https://en.wikipedia.org/wiki/Python_(programming_language)
  Title: Python (programming language) - Wikipedia
```

---

## `run_javascript`

Run JavaScript code in the page context and return the serialized result.

```python
run_javascript(script: str) -> tuple[str, Image]
```

**Parameters**

| Name | Type | Description |
|---|---|---|
| `script` | `str` | A JavaScript expression or statement. |

**Behavior**

- The script is evaluated in the page's main world.
- Return values are JSON-stringified.
- Errors are caught and returned as `"Error: <message>"`.
- A fresh annotated screenshot is returned.

**Examples**

```text
→ run_javascript("document.title")
→ run_javascript("Array.from(document.querySelectorAll('a')).map(a => a.href).slice(0, 10)")
→ run_javascript("document.querySelectorAll('img').length")
```

!!! info "Inside the page"
    `run_javascript` runs in the **page's** context — so `document`, `window`, and the page's globals are all available. Use it for scraping, DOM inspection, or kicking off a state change.

---

## `screenshot`

Take a screenshot of the current viewport or the full page.

```python
screenshot(annotate: bool = True, full_page: bool = False) -> tuple[str, Image]
```

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `annotate` | `bool` | `True` | If `True`, draws numbered red boxes over interactive elements. If `False`, returns a clean screenshot. |
| `full_page` | `bool` | `False` | If `True`, captures the entire scrollable page. If `False`, captures only the viewport. |

**Examples**

```text
→ screenshot()                              # annotated viewport
→ screenshot(annotate=False)                # clean viewport
→ screenshot(full_page=True)                # annotated full page
→ screenshot(annotate=False, full_page=True) # clean full page (great for sharing)
```

!!! tip "Clean screenshots for humans"
    When sharing a screenshot with a teammate or attaching to a bug report, use `annotate=False`. The red boxes are for the model, not for humans.

---

## See also

- **[DevTools](devtools.md)** — console, network, errors
- **[Recording](recording.md)** — capture a full session, not just one screenshot

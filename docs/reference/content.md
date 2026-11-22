---
title: Content
description: Read the page as Markdown, read one element, run JavaScript, and take screenshots.
---

# Content

Read what's on the page, and take screenshots on demand.

| Tool | Does | Returns |
| --- | --- | --- |
| [`get_page_content`](#get_page_content) | Get the page content as markdown text. | text + screenshot |
| [`get_text`](#get_text) | Get the full, current text of an element by its ID. | text |
| [`get_accessibility_tree`](#get_accessibility_tree) | Get the accessibility tree (ARIA snapshot) of the page or one element as text. | text |
| [`get_page_info`](#get_page_info) | Get current page URL and title. | text |
| [`screenshot`](#screenshot) | Take a screenshot of the page. | text + screenshot |
| [`run_javascript`](#run_javascript) | Execute JavaScript and return the result. | text + screenshot |
| [`save_pdf`](#save_pdf) | Save the current page as a PDF in the downloads directory (needs headless Chromium). | text |

## `get_page_content` {#get_page_content}

Get the page content as markdown text.

```python
get_page_content()
```

Returns text and a fresh annotated screenshot.

Returns the page as Markdown, with scripts and styles stripped, cut off at 30,000 characters, plus the annotated screenshot. For one element, use `get_text`; for structured data, the [extraction tools](/reference/extraction).

## `get_text` {#get_text}

Get the full, current text of an element by its ID.

```python
get_text(element_id: int)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `element_id` | `int` | required | The number label of the element |

Reads the live element, so it returns the whole text rather than the 40-character label from the element list (up to 10,000 characters). Form fields return their current value.

## `get_accessibility_tree` {#get_accessibility_tree}

Get the accessibility tree (ARIA snapshot) of the page or one element as text.

```python
get_accessibility_tree(element_id: int | None = None, depth: int | None = None)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `element_id` | `int \| None` | `None` | Number label of an element to snapshot; omit for the whole page |
| `depth` | `int \| None` | `None` | Maximum nesting depth to include; omit for the full tree |

Returns Playwright's YAML-like ARIA snapshot: roles, accessible names, and text, nested as the page is (up to 20,000 characters; pass `depth` or `element_id` to narrow a larger tree). It is much cheaper than a screenshot, so use it to read text-heavy pages or to find headings, landmarks, and form controls before acting. Element IDs still come from the annotated screenshot.

## `get_page_info` {#get_page_info}

Get current page URL and title.

```python
get_page_info()
```

Returns text only.

```text
→ get_page_info()
Current page info:
  URL: https://en.wikipedia.org/wiki/Python_(programming_language)
  Title: Python (programming language) - Wikipedia
```

## `screenshot` {#screenshot}

Take a screenshot of the page.

```python
screenshot(annotate: bool = True, full_page: bool = False)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `annotate` | `bool` | `True` | If True, overlay numbered element markers (default). If False, clean screenshot. |
| `full_page` | `bool` | `False` | If True, capture the full scrollable page. |

| Call | Result |
| --- | --- |
| `screenshot()` | Annotated viewport, with a new element map |
| `screenshot(annotate=False)` | Clean viewport, for sharing |
| `screenshot(annotate=False, full_page=True)` | Clean image of the whole scrollable page |

Full-page screenshots are never annotated, even with `annotate=True`. Use them to review layout, not to find numbers.

## `run_javascript` {#run_javascript}

Execute JavaScript and return the result.

```python
run_javascript(script: str)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `script` | `str` | required | JavaScript code to execute |

Evaluates JavaScript in the page and returns the result as JSON, with a fresh screenshot. Errors come back as `Error: …`. Use it to read state; for acting on the page, numbered tools are safer.

```text
→ run_javascript("document.title")
→ run_javascript("[...document.querySelectorAll('img')].length")
```

## `save_pdf` {#save_pdf}

Save the current page as a PDF in the downloads directory (needs headless Chromium).

```python
save_pdf(file_name: str | None = None, landscape: bool = False, print_background: bool = True)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `file_name` | `str \| None` | `None` | File name for the PDF (directories are stripped). Defaults to the page title. |
| `landscape` | `bool` | `False` | Print in landscape orientation. |
| `print_background` | `bool` | `True` | Include background colors and images. |

Saves into `BROWSER_DOWNLOADS_DIR`, adds `.pdf` if missing, and never overwrites an existing file (it appends ` (1)`, ` (2)`, ...). Returns the saved path and size. Chromium only prints PDFs headless, so with a visible browser it fails and asks you to restart with `BROWSER_HEADLESS=true`.

## See also

- [Extraction](/reference/extraction)
- [Research a question](/recipes/research)

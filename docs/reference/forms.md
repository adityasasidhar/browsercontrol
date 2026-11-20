---
title: Forms
description: Native dropdowns, checkboxes and radios, and file uploads.
---

# Forms

Controls that need more than a click or typed text. For text fields, use [`type_text`](/reference/interaction#type_text).

| Tool | Does | Returns |
| --- | --- | --- |
| [`select_option`](#select_option) | Select an option from a dropdown by element ID. | text + screenshot |
| [`check_checkbox`](#check_checkbox) | Check or uncheck a checkbox (or select a radio button) by element ID. | text + screenshot |
| [`upload_file`](#upload_file) | Upload a file to a file input element. | text + screenshot |

## `select_option` {#select_option}

Select an option from a dropdown by element ID.

```python
select_option(element_id: int, option: str)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `element_id` | `int` | required | The number label of the select element |
| `option` | `str` | required | The value or visible text of the option to select |

For native `<select>` elements. `option` matches the visible label or the value. If nothing matches, the error lists the available options. For a custom dropdown, `click` it open and `click` the option.

```text
→ select_option(7, "United Kingdom")
→ select_option(7, "uk")
```

## `check_checkbox` {#check_checkbox}

Check or uncheck a checkbox (or select a radio button) by element ID.

```python
check_checkbox(element_id: int, check: bool = True)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `element_id` | `int` | required | The number label of the checkbox |
| `check` | `bool` | `True` | True to check, False to uncheck |

**Sets** the state rather than toggling, so calling it twice is safe. Also selects radio buttons. Works on inputs hidden under a styled replacement, but refuses one covered by a dialog or banner.

```text
→ check_checkbox(8)
→ check_checkbox(8, check=False)
```

## `upload_file` {#upload_file}

Upload a file to a file input element.

```python
upload_file(element_id: int, file_path: str)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `element_id` | `int` | required | The number label of the file input |
| `file_path` | `str` | required | The absolute path to the file to upload |

Sets the file on an `<input type="file">` directly, with no native file picker involved. Use an absolute path on the machine running BrowserControl; one file per call.

```text
→ upload_file(8, "/home/me/Documents/resume.pdf")
Uploaded 'resume.pdf' to element 8
```

See [Upload a file](/recipes/upload-a-file).

## See also

- [Fill a form](/recipes/fill-a-form)
- [Upload a file](/recipes/upload-a-file)

# Forms

Tools for `<select>` dropdowns, checkboxes, and file uploads. All return annotated screenshots so the next action has fresh element IDs.

---

## `select_option`

Pick an option from a `<select>` dropdown by visible text or value.

```python
select_option(element_id: int, option: str) -> tuple[str, Image]
```

**Parameters**

| Name | Type | Description |
|---|---|---|
| `element_id` | `int` | The number label of the `<select>` element. |
| `option` | `str` | The option to select — by visible text (`"United States"`) or value attribute (`"us"`). |

**Behavior**

- Works with single-select and multi-select dropdowns.
- Native HTML `<select>` only — not custom JS-rendered comboboxes. For those, click to open then click the option.

**Example**

```text
→ select_option(7, "United States")        # pick by visible text
→ select_option(7, "us")                   # pick by value attribute
```

---

## `check_checkbox`

Toggle a checkbox by its **Set of Marks** number.

```python
check_checkbox(element_id: int, check: bool = True) -> tuple[str, Image]
```

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `element_id` | `int` | — | The number label of the checkbox element. |
| `check` | `bool` | `True` | Set to `True` to check, `False` to uncheck. Idempotent — already-checked checkboxes stay checked if you pass `True`. |

**Examples**

```text
→ check_checkbox(8)              # ensure checkbox 8 is checked
→ check_checkbox(8, check=False) # uncheck checkbox 8
```

---

## `upload_file`

Upload a file via the native browser file input.

```python
upload_file(element_id: int, file_path: str) -> tuple[str, Image]
```

**Parameters**

| Name | Type | Description |
|---|---|---|
| `element_id` | `int` | The number label of the `<input type="file">` element. |
| `file_path` | `str` | Absolute path to the file on the local filesystem. |

**Why this matters**

Uses Playwright's `set_input_files` under the hood. This is **the most reliable path through file uploads** — works even when click-and-pick dialogs fail (which is most of the time, because MCP servers can't show native OS dialogs).

**Examples**

```text
→ upload_file(8, "/Users/me/Documents/resume.pdf")
→ upload_file(8, "/tmp/screenshot.png")
```

!!! warning "Use absolute paths"
    Relative paths are resolved against the MCP server's working directory, which may not be what you expect.

!!! tip "Multiple files"
    If the input has `multiple`, pass a comma-separated string of paths.

---

## See also

- **[Interaction tools](interaction.md)** — `type_text`, `click`
- **[Upload a file guide](../guides/upload-files.md)** — worked example

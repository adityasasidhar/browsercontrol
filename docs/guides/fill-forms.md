# Fill a form

The most common interaction: open a page, type into a few fields, submit. BrowserControl's atomic `type_text` makes this rock-solid — no char-by-char timing issues.

## What the agent does

> _"Fill out the contact form at example.com/contact with a polite message."_

```text
→ navigate_to("https://example.com/contact")
→ type_text(2, "Alex Doe")
→ type_text(3, "alex@example.com")
→ type_text(4, "Hi! Just saying hello.")
→ click(5)             # Submit
→ wait(2.0)
→ screenshot(annotate=False)
```

## Step by step

### 1. Navigate to the form

```text
navigate_to("https://example.com/contact")
```

The element map will identify the form fields by their visible labels (the model reads them from the element map text).

### 2. Fill each field

```text
type_text(2, "Alex Doe")              # name field
type_text(3, "alex@example.com")     # email field
type_text(4, "Hi! Just saying hello.") # message textarea
```

`type_text` calls `element.fill()` under the hood. It's atomic, handles clearing the field first, and works with `<input>`, `<textarea>`, and `contenteditable` elements.

### 3. Submit

```text
click(5)               # the Submit button
```

Or, if the button is focused after the last field, you can press Enter:

```text
press_key("Enter")
```

### 4. Wait and verify

```text
wait(2.0)              # let the form submit and the next page render
screenshot(annotate=False)
```

A clean screenshot (no red boxes) is great for sharing back with the user as proof of completion.

## Forms with selects, checkboxes, and uploads

### Dropdowns

```text
select_option(7, "United States")     # pick by visible text
select_option(7, "us")                # pick by value attribute
```

### Checkboxes

```text
check_checkbox(8)                     # ensure checked
check_checkbox(8, check=False)        # uncheck
```

### File uploads

See the [upload files guide](upload-files.md).

## Tips

!!! tip "Re-screenshot between fields"
    You don't need to — every `type_text` already returns a fresh screenshot. But if the form has dynamic validation that adds new fields (e.g. a billing address section that appears when you check "billing same as shipping"), call a fresh screenshot tool first.

!!! tip "Persistent sessions help"
    Forms that require login will already be logged in across runs — BrowserControl uses `launch_persistent_context`. See [Configuration](../configuration.md#browser_user_data_dir).

!!! tip "Tab + arrow keys for comboboxes"
    Custom JS comboboxes (not native `<select>`) need to be opened with `click`, then have options picked with `click` or `press_key("ArrowDown")` + `press_key("Enter")`.

## See also

- **[Interaction tools](../tools/interaction.md)** — `type_text`, `click`, `press_key`
- **[Forms tools](../tools/forms.md)** — `select_option`, `check_checkbox`, `upload_file`

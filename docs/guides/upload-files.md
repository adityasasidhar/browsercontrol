# Upload a file

BrowserControl's `upload_file` is the most reliable way to get a file through a browser form. It uses Playwright's `set_input_files` under the hood — works even when click-and-pick dialogs fail (which is most of the time, because MCP servers can't show native OS file pickers).

## What the agent does

> _"Upload my resume to the job application form."_

```text
→ navigate_to("https://jobs.example.com/apply")
→ upload_file(8, "/Users/me/Documents/resume.pdf")
```

## Step by step

### 1. Navigate to the upload form

```text
navigate_to("https://jobs.example.com/apply")
```

The element map will identify the file input (typically labeled "Resume", "Upload", or "Choose file"). File inputs have `tag=input` and an attribute list that includes `type=file`.

### 2. Upload

```text
upload_file(8, "/Users/me/Documents/resume.pdf")
```

That's it. Playwright writes the file to the input. The form sees the selection just as if you'd used the OS picker.

### 3. Submit

```text
click(9)             # Submit application button
wait(2.0)            # let the upload finish
```

## Why this works when other approaches don't

Most browser automation libraries try to handle file uploads one of two ways:

- **Click the file input** → triggers the OS file picker dialog → no way to drive the dialog programmatically from MCP.
- **Manually copy the file to the page** → doesn't work for `<input type="file">` because the browser enforces the security boundary.

Playwright's `set_input_files` is the official escape hatch: it sets the files on the input element directly, which is what would happen if the user picked the file via the picker. It works on every site that has a real `<input type="file">`.

## Multiple files

If the input supports `multiple` (i.e. has the `multiple` attribute), pass a comma-separated string of paths:

```text
upload_file(8, "/Users/me/photo1.jpg, /Users/me/photo2.jpg, /Users/me/photo3.jpg")
```

## Hidden file inputs

Some sites hide the file input and surface a styled button. The file input is still in the DOM (otherwise the form wouldn't work). Use `inspect_element` to find it, or look for an `<input type="file">` in the element map:

```text
→ get_page_content()                  # look for <input type="file">
→ inspect_element(8)                  # confirm it's the right input
→ upload_file(8, "/path/to/file.pdf")
```

## Tips

!!! warning "Use absolute paths"
    Relative paths resolve against the MCP server's working directory, which may not be what you expect. Always pass an absolute path.

!!! tip "Confirm with a screenshot"
    After uploading, screenshot the page to confirm the file is shown next to the input (e.g. `"resume.pdf"` next to the upload field). Most sites update the UI on selection.

!!! tip "Check the input accepts your file type"
    Some inputs have `accept=".pdf,.doc,.docx"`. If your file isn't accepted, the upload will silently fail. Use `inspect_element` to check the `accept` attribute.

## See also

- **[Forms tools reference](../tools/forms.md#upload_file)** — `upload_file` signature
- **[Fill a form guide](fill-forms.md)** — full form workflow

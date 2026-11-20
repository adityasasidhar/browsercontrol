---
title: Upload a file
description: Attach a local file to a web form with upload_file, which sets it on the file input directly instead of opening a native file picker.
---

# Upload a file

> Upload my résumé at /home/me/Documents/resume.pdf to the job application and submit it.

```text
→ navigate_to("https://jobs.example.com/apply")
→ upload_file(8, "/home/me/Documents/resume.pdf")
→ click(9)
→ wait_for(text="Application received")
```

## Why it works without a file picker

Clicking a file input opens the operating system's file dialog, which no browser automation can drive. `upload_file` skips the dialog: it sets the file on the `<input type="file">` directly, exactly as if the user had picked it. The page sees an ordinary selection.

<div class="steps">

### Find the file input

File inputs show up in the element list as `input[file]`. Many sites hide the real input behind a styled "Choose file" button; BrowserControl still numbers the hidden input, so look for `input[file]` rather than the button.

### Upload

```text
→ upload_file(8, "/home/me/Documents/resume.pdf")
Uploaded 'resume.pdf' to element 8
```

Use an **absolute path** on the machine where BrowserControl runs. A relative path is resolved against the server's working directory, which is rarely what you expect. If the file doesn't exist, the tool says `File not found`.

### Confirm and submit

Most sites show the chosen file name next to the input; check the screenshot, then submit as usual.

</div>

## When it doesn't take

| Symptom | Cause | Fix |
| --- | --- | --- |
| The page ignores the file | The input's `accept` attribute rejects the type | `inspect_element(id)` shows `accept`; use a matching file. |
| No `input[file]` in the list | A drop zone that only accepts drag and drop | Look for a hidden input with `find("", role="button")` or `run_javascript("document.querySelectorAll('input[type=file]').length")`. |
| Upload starts but never finishes | The upload request is slow | `wait_for_response("/upload")` right after the action. |

`upload_file` sends one file per call.

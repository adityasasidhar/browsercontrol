---
title: Recording
description: Playwright traces, snapshots, and exporting a session as a Playwright test.
---

# Recording

Keep a record of what happened. Traces go to `~/.browsercontrol/recordings`, snapshots to `~/.browsercontrol/snapshots`, and tests to `~/.browsercontrol/generated_tests`; see [Configuration](/reference/configuration#paths) to move them.

| Tool | Does | Returns |
| --- | --- | --- |
| [`start_recording`](#start_recording) | Start recording the browser session as a Playwright trace. The trace will be saved when stop_recording is called. Also restarts the action log, so export_test() afterwards covers exactly this recording. | text |
| [`stop_recording`](#stop_recording) | Stop recording and save the session trace. | text |
| [`export_test`](#export_test) | Turn the actions taken so far into a replayable Playwright test file. | text |
| [`take_snapshot`](#take_snapshot) | Take a named snapshot (screenshot + HTML) for later reference. | text |
| [`list_recordings`](#list_recordings) | List all saved recordings and snapshots. | text |

## `start_recording` {#start_recording}

Start recording the browser session as a Playwright trace. The trace will be saved when stop_recording is called. Also restarts the action log, so export_test() afterwards covers exactly this recording.

```python
start_recording(name: str = '')
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `name` | `str` | `""` | Optional name for the recording (default: timestamp) |

Starts a Playwright trace and restarts the action log, so `export_test` afterwards covers exactly this recording. Without a name, a timestamp is used.

```text
→ start_recording("checkout")
Recording started: checkout.zip
Call stop_recording() when done.
```

## `stop_recording` {#stop_recording}

Stop recording and save the session trace.

```python
stop_recording()
```

Returns text only.

Saves the trace and returns its path and the command to open it.

```text
Recording saved: /home/me/.browsercontrol/recordings/checkout.zip
View with: npx playwright show-trace /home/me/.browsercontrol/recordings/checkout.zip
```

## `export_test` {#export_test}

Turn the actions taken so far into a replayable Playwright test file.

```python
export_test(name: str = '', language: str = 'python', clear: bool = False)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `name` | `str` | `""` | Test name and file name (default: timestamp) |
| `language` | `str` | `"python"` | "python" (pytest-playwright) or "typescript" (@playwright/test) |
| `clear` | `bool` | `False` | Empty the action log afterwards, to start the next test fresh |

Writes the actions so far (since the session started, or since `start_recording`) as a test file, and returns its path, the command to run it, and the code. `language` is `python` (pytest-playwright, `test_<name>.py`) or `typescript` (`@playwright/test`, `<name>.spec.ts`). `clear=True` empties the action log afterwards.

```python
def test_checkout(page: Page) -> None:
    page.goto("https://shop.test/")
    page.get_by_role("textbox", name="Email", exact=True).fill("ada@example.com")
    page.get_by_label("Password", exact=True).fill(os.environ["BC_SECRET_1"])
    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Pay", exact=True).click()
    expect(page.get_by_text("Order confirmed").first).to_be_visible()
```

Elements are located by test id, role and name, label, placeholder, or text, falling back to a CSS path, each checked against the live page. Covers navigation, clicks, typing, keys, selects, checkboxes, uploads, drags, scrolls, waits for text, dialog answers, and request mocks. Typed passwords become `BC_SECRET_n` environment variables. Review the file before committing.

## `take_snapshot` {#take_snapshot}

Take a named snapshot (screenshot + HTML) for later reference.

```python
take_snapshot(name: str = '')
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `name` | `str` | `""` | Optional name for the snapshot (default: timestamp) |

Saves a PNG screenshot and the page's HTML (with BrowserControl's markers removed) under the given name. Without a name, a timestamp is used.

## `list_recordings` {#list_recordings}

List all saved recordings and snapshots.

```python
list_recordings()
```

Returns text only.

Lists recent traces and snapshots with their paths.

## See also

- [Record & export tests](/recipes/record-tests)

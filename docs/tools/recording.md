# Recording

Capture Playwright traces (video + DOM snapshots + sources) and save snapshots of interesting page states. Recordings save to `~/.browsercontrol/recordings/`; snapshots save to `~/.browsercontrol/snapshots/`.

---

## `start_recording`

Begin a Playwright trace.

```python
start_recording(name: str = "") -> str
```

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | `""` | Optional base name for the trace file. If empty, a timestamp is used. |

**Behavior**

- Starts capturing screenshots, DOM snapshots, and JS sources for every action.
- Records are saved when `stop_recording` is called.

**Returns**

```text
Recording started: login_flow
```

!!! warning "One at a time"
    Calling `start_recording` while another recording is active is a no-op (returns the existing recording's status).

---

## `stop_recording`

Stop the current recording and save it to disk.

```python
stop_recording() -> str
```

**Returns**

```text
Recording saved: ~/.browsercontrol/recordings/login_flow_20260228.zip
```

**View the recording**

The saved file is a [Playwright trace zip](https://playwright.dev/python/docs/trace-viewer). Open it with:

```bash
npx playwright show-trace ~/.browsercontrol/recordings/login_flow_20260228.zip
```

Or use the browser-based viewer at <https://trace.playwright.dev>.

---

## `take_snapshot`

Save a PNG + HTML + URL triplet for the current page state.

```python
take_snapshot(name: str = "") -> str
```

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | `""` | Optional base name. If empty, a timestamp is used. |

**Returns**

```text
Snapshot saved: ~/.browsercontrol/snapshots/after_login_20260228.png
  HTML: ~/.browsercontrol/snapshots/after_login_20260228.html
  URL: ~/.browsercontrol/snapshots/after_login_20260228.url
```

**Why this is good**

- HTML is the **complete** DOM at the moment of capture — easier to inspect than a screenshot for "what was on the page when X happened?".
- The `.url` file is a plain-text one-liner with the URL the snapshot was taken at.

---

## `list_recordings`

List recent recordings and snapshots.

```python
list_recordings() -> str
```

**Returns**

```text
Recordings:
  2026-02-28 10:14 ~/.browsercontrol/recordings/login_flow.zip (3.2 MB)
  2026-02-28 09:55 ~/.browsercontrol/recordings/checkout.zip (5.7 MB)

Snapshots:
  2026-02-28 10:18 ~/.browsercontrol/snapshots/after_login.png
  2026-02-28 10:18 ~/.browsercontrol/snapshots/after_login.html
```

---

## `export_test`

Turn what the agent did into a replayable Playwright test.

```python
export_test(name: str = "", language: str = "python", clear: bool = False) -> str
```

| Name | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | timestamp | Test and file name. |
| `language` | `str` | `"python"` | `python` (pytest-playwright) or `typescript` (`@playwright/test`). |
| `clear` | `bool` | `False` | Empty the action log afterwards. |

Every action is logged with locators a person would write (test id, role and
name, label, placeholder, text, falling back to a CSS path), each checked against
the live page to match exactly that one element before the action ran. Frames,
dialog answers, and request mocks are reproduced. Typed passwords are never
stored; the test reads them from `BC_SECRET_n` environment variables.
`start_recording()` restarts the log, so a trace and a test can describe the same run.

```python
def test_checkout(page: Page) -> None:
    page.goto("https://shop.test/")
    page.get_by_role("textbox", name="Email", exact=True).fill("ada@example.com")
    page.get_by_label("Password", exact=True).fill(os.environ["BC_SECRET_1"])
    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Pay", exact=True).click()
    expect(page.get_by_text("Order confirmed").first).to_be_visible()
```

Files land in `BROWSER_GENERATED_TESTS_DIR` (`~/.browsercontrol/generated_tests`).
Review them before committing: an agent's exploration often includes steps a
test does not need.

---

## Custom paths

Override the storage directories via env vars:

| Variable | Default |
|---|---|
| `BROWSER_RECORDINGS_DIR` | `~/.browsercontrol/recordings` |
| `BROWSER_SNAPSHOTS_DIR` | `~/.browsercontrol/snapshots` |

See **[Configuration](../configuration.md)** for the full list.

---

## See also

- **[Record a test run guide](../guides/record-tests.md)** — full worked example

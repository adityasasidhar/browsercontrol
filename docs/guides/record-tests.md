# Record a test run

Capture a Playwright trace as the agent walks through a flow, then turn the same run into a Playwright test you can keep. The trace replays in the official trace viewer for bug reports and PR review. The test runs in CI.

## What the agent does

> _"Walk through the login flow on staging.example.com while recording."_

```text
→ start_recording("login_flow")
→ navigate_to("https://staging.example.com/login")
→ type_text(3, "user@example.com")
→ type_text(4, "hunter2")
→ click(5)             # Sign In button
→ wait_for(text="Dashboard")
→ take_snapshot("after_login")
→ stop_recording()
→ "Saved ~/.browsercontrol/recordings/login_flow_20260228.zip"
→ export_test("login_flow")
```

## Step by step

### 1. Start recording

```text
start_recording("login_flow")
```

A Playwright trace begins capturing screenshots, DOM snapshots, and JS sources for every subsequent action.

### 2. Walk through the flow

Just call the tools normally — every action is automatically captured.

```text
navigate_to("https://staging.example.com/login")
type_text(3, "user@example.com")
type_text(4, "hunter2")
click(5)
```

### 3. Wait for the result

Every action already waits for the page to settle. When the redirect takes
longer, wait for something the next page shows instead of sleeping:

```text
wait_for(text="Dashboard")
```

### 4. Snapshot the interesting state (optional)

```text
take_snapshot("after_login")
```

Saves a PNG + HTML + URL triplet to `~/.browsercontrol/snapshots/`. Use this alongside the trace — the HTML alone is often enough to diagnose a problem.

### 5. Stop recording

```text
stop_recording()
```

Returns the saved path. The trace file is a standard Playwright trace zip.

### 6. Export a Playwright test

```text
export_test("login_flow")                          # pytest-playwright
export_test("login_flow", language="typescript")   # @playwright/test
```

`start_recording()` restarts the action log, so the test covers the same run as
the trace. Each step uses the locator a person would write (role and name,
label, text), checked against the live page before the action ran:

```python
def test_login_flow(page: Page) -> None:
    page.goto("https://staging.example.com/login")
    page.get_by_label("Email", exact=True).fill("user@example.com")
    page.get_by_label("Password", exact=True).fill(os.environ["BC_SECRET_1"])
    page.get_by_role("button", name="Sign in", exact=True).click()
```

Typed passwords are never written to the file. Set `BC_SECRET_1` (and so on)
when you run the test. Files land in `~/.browsercontrol/generated_tests/`.
Review them before committing: the agent's exploration often includes steps
the test doesn't need.

## Viewing the recording

The trace file is a [Playwright trace zip](https://playwright.dev/python/docs/trace-viewer). Open it with:

```bash
npx playwright show-trace ~/.browsercontrol/recordings/login_flow_20260228.zip
```

Or use the browser-based viewer: <https://trace.playwright.dev>.

The trace viewer shows:

- **A timeline** of every action with screenshots before and after.
- **The DOM snapshot** at each step.
- **Network requests** with timing.
- **Console output** for every step.
- **The source code** of any JS that ran.

## Tips

!!! tip "Use a descriptive name"
    The recording name becomes the filename. Use names that tell you (and your teammates) what the trace shows: `checkout_flow`, `login_with_oauth`, `mobile_signup`.

!!! tip "One recording per flow"
    Stop and start a new recording for each distinct scenario. Long traces are hard to navigate.

!!! tip "Custom storage paths"
    Override `BROWSER_RECORDINGS_DIR` and `BROWSER_SNAPSHOTS_DIR` to point at a shared location. See **[Configuration](../configuration.md)**.

!!! tip "Snapshots are cheap"
    Take a snapshot before and after critical actions. The HTML alone is often enough to debug "what was the page state when this broke?".

## See also

- **[Recording tools reference](../tools/recording.md)** — every recording tool
- **[Troubleshooting](../troubleshooting.md#view-session-recordings)** — viewing recordings

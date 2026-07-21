# Record a test run

Capture a Playwright trace as the agent walks through a flow. The saved trace can be replayed in the official trace viewer — perfect for bug reports and PR review.

## What the agent does

> _"Walk through the login flow on staging.example.com while recording."_

```text
→ start_recording("login_flow")
→ navigate_to("https://staging.example.com/login")
→ type_text(3, "user@example.com")
→ type_text(4, "hunter2")
→ click(5)             # Sign In button
→ wait(2.0)
→ take_snapshot("after_login")
→ stop_recording()
→ "Saved ~/.browsercontrol/recordings/login_flow_20260228.zip"
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

### 3. Wait for any async behavior

```text
wait(2.0)                       # let the login API respond and the redirect complete
```

Without the wait, the trace might end before the post-login page finishes loading.

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

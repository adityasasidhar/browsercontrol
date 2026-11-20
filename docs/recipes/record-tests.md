---
title: Record & export tests
description: Capture a Playwright trace of an agent's session for bug reports, and turn the same run into a Playwright test you can keep and run in CI.
---

# Record & export tests

Two outputs, from the same run:

- A **trace**: a replayable recording with a timeline, screenshots, DOM snapshots, and network, for bug reports and review.
- A **test**: a pytest-playwright or `@playwright/test` file that repeats what the agent did, for CI.

> Walk through the login flow on staging while recording, then export it as a test.

```text
→ start_recording("login_flow")
→ navigate_to("https://staging.example.com/login")
→ type_text(3, "user@example.com")
→ type_text(4, "correct-horse-battery")
→ click(5)
→ wait_for(text="Dashboard")
→ stop_recording()
→ export_test("login_flow")
```

<div class="steps">

### Start recording

```text
→ start_recording("login_flow")
Recording started: login_flow.zip
Call stop_recording() when done.
```

It also restarts the action log, so the test you export afterwards covers exactly this run.

### Walk through the flow

Call tools as usual. Every action goes into the trace and the action log. Wait for results with `wait_for` rather than fixed sleeps, so the trace and the test wait for the same thing.

### Stop and view the trace

```text
→ stop_recording()
Recording saved: /home/me/.browsercontrol/recordings/login_flow.zip
View with: npx playwright show-trace /home/me/.browsercontrol/recordings/login_flow.zip
```

Open it with that command, or drop the file on [trace.playwright.dev](https://trace.playwright.dev).

### Export a Playwright test {#export-a-playwright-test}

```text
→ export_test("login_flow")                          # pytest-playwright
→ export_test("login_flow", language="typescript")   # @playwright/test
```

```python
def test_login_flow(page: Page) -> None:
    page.goto("https://staging.example.com/login")
    page.get_by_label("Email", exact=True).fill("user@example.com")
    page.get_by_label("Password", exact=True).fill(os.environ["BC_SECRET_1"])
    page.get_by_role("button", name="Sign in", exact=True).click()
    expect(page.get_by_text("Dashboard").first).to_be_visible()
```

The response includes the file path (`test_login_flow.py` or `login_flow.spec.ts` in `~/.browsercontrol/generated_tests`) and the command to run it.

</div>

## How the test is written

- **Locators a person would write.** Each step uses a test id, role and name, label, placeholder, or text, falling back to a CSS path. Every locator was checked against the live page, before the action ran, to match exactly that one element. Element numbers never appear.
- **What's covered:** navigation, clicks, typing, keys, selects, checkboxes, uploads, drags, scrolls, waits for text, dialog answers, and request mocks.
- **No secrets.** Text typed into password fields is never stored; the test reads it from `BC_SECRET_1`, `BC_SECRET_2`, and so on. Set those when you run it.
- **Review before committing.** An agent's exploration often includes steps a test doesn't need. Trim them, and add assertions for what matters.

`export_test(clear=True)` empties the action log afterwards, ready for the next flow.

## Snapshots

For a single moment rather than a whole flow, `take_snapshot("checkout-error")` saves a PNG and the page's HTML to `~/.browsercontrol/snapshots`. `list_recordings()` lists recent traces and snapshots.

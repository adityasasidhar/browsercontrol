# Use your own Chrome

Let the agent work in the Chrome you already use, with the sites you are signed
in to, instead of logging in again inside BrowserControl's own browser.

## What the agent does

> _"Connect to my Chrome and check whether my last order on shop.example.com has shipped."_

```text
→ connect_to_chrome("http://localhost:9222")
→ navigate_to("https://shop.example.com/orders")
→ find("Order #", role="link")
→ click(14)
→ get_page_content()
→ disconnect_chrome()
```

## Step by step

### 1. Start Chrome with remote debugging

Quit Chrome, then start it with a debugging port and a profile directory for the
agent:

=== "Linux"

    ```bash
    google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-agent"
    ```

=== "macOS"

    ```bash
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
      --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-agent"
    ```

=== "Windows"

    ```powershell
    & "C:\Program Files\Google\Chrome\Application\chrome.exe" `
      --remote-debugging-port=9222 --user-data-dir="$env:USERPROFILE\.chrome-agent"
    ```

!!! warning "Chrome 136 and later need a separate profile"
    Chrome ignores `--remote-debugging-port` on its default profile. The first
    time you use `--user-data-dir`, sign in to the sites the agent needs. That
    profile remembers them from then on.

### 2. Attach

Ask the agent to connect, or attach at startup so every session begins in your
Chrome:

=== "From the agent"

    ```text
    connect_to_chrome("http://localhost:9222")
    ```

=== "At startup"

    ```bash
    BROWSER_CDP_URL=http://localhost:9222 browsercontrol
    ```

    In an MCP client config, set `BROWSER_CDP_URL` in the server's `env` block.

The agent opens a tab of its own instead of taking over the one you are looking
at. `list_tabs` and `switch_tab` reach your other tabs if you ask it to.

### 3. Work as usual

Every tool works the same way: annotated screenshots, `find`, `act`, extraction,
network capture, and recording.

### 4. Detach

```text
disconnect_chrome()
```

This only disconnects. Your Chrome and its tabs keep running, and BrowserControl
goes back to its own browser. Stopping the server has the same effect.

## Tips

!!! danger "The debugging port is full control"
    Anything that can reach port 9222 can read and drive that browser, signed-in
    sessions included. Keep it on `localhost` and close Chrome when you are done.

!!! tip "Keep work and agent browsing apart"
    Use a dedicated `--user-data-dir` signed in only to the sites the agent
    needs, rather than the profile holding your email and banking.

!!! tip "Need a signed-out view too?"
    `create_session("guest")` opens an isolated session alongside your Chrome
    for comparing logged-in and logged-out pages. See [Sessions](../tools/sessions.md).

## See also

- **[Sessions reference](../tools/sessions.md)**: `connect_to_chrome`, `create_session`, and the rest
- **[Configuration](../configuration.md#browser_cdp_url)**: `BROWSER_CDP_URL`

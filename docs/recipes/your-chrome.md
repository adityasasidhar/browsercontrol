---
title: Use your own Chrome
description: Attach BrowserControl to a Chrome you started with remote debugging, so the agent works in sites you're already signed in to.
---

# Use your own Chrome

Let the agent work in your own Chrome, with the sites you're already signed in to, instead of logging in again inside BrowserControl's browser.

> Connect to my Chrome and check whether my last order on shop.example.com has shipped.

```text
→ connect_to_chrome("http://localhost:9222")
→ navigate_to("https://shop.example.com/orders")
→ find("Order #", role="link")
→ click(14)
→ get_page_content()
→ disconnect_chrome()
```

<div class="steps">

### Start Chrome with remote debugging

Quit Chrome, then start it with a debugging port and a profile directory for agent work:

::: code-group

```bash [Linux]
google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-agent"
```

```bash [macOS]
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-agent"
```

```powershell [Windows]
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --remote-debugging-port=9222 --user-data-dir="$env:USERPROFILE\.chrome-agent"
```

:::

::: warning Chrome 136 and later need a separate profile
Chrome ignores `--remote-debugging-port` on its default profile. The first time you use the `--user-data-dir` above, sign in to the sites the agent needs. That profile remembers them from then on.
:::

### Attach

Ask the agent to connect, or attach at startup so every session begins in your Chrome:

::: code-group

```text [From the agent]
connect_to_chrome("http://localhost:9222")
```

```json [At startup]
{
  "mcpServers": {
    "browsercontrol": {
      "command": "uvx",
      "args": ["browsercontrol"],
      "env": { "BROWSER_CDP_URL": "http://localhost:9222" }
    }
  }
}
```

:::

The agent opens a tab of its own rather than taking over the one you're looking at. `list_tabs()` and `switch_tab()` reach your other tabs if you ask it to.

### Work as usual

Every tool works the same: numbered screenshots, `find`, `act`, extraction, network capture, recording. [Isolated sessions](/concepts/sessions#isolated-sessions) created while attached open as incognito-like contexts in your Chrome.

### Detach

```text
→ disconnect_chrome()
```

This only detaches. Your Chrome and its tabs keep running, and BrowserControl goes back to its own browser. Stopping the server has the same effect.

</div>

::: danger The debugging port is full control
Anything that can reach port 9222 can read and drive that browser, signed-in sessions included. Keep it on `localhost`, use a profile signed in only to what the agent needs, and close Chrome when you're done.
:::

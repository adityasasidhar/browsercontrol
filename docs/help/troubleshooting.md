---
title: Troubleshooting
description: Fixes for BrowserControl problems with connecting, launching Chromium, element numbers, uploads, localhost, profiles, and recordings.
---

# Troubleshooting

| Symptom | Go to |
| --- | --- |
| The client doesn't list BrowserControl's tools | [The client can't find BrowserControl](#the-client-cant-find-browsercontrol) |
| Chromium fails to start | [Chromium won't launch](#chromium-won-t-launch) |
| "Element 7 is stale" or "not found" | [Element numbers stop working](#element-numbers-stop-working) |
| A visible button has no number | [Something on screen has no number](#something-on-screen-has-no-number) |
| The click lands but nothing happens | [A click does nothing](#a-click-does-nothing) |
| A file won't upload | [Uploads](#uploads) |
| `localhost` refuses to connect | [Localhost](#localhost) |
| Logins don't stick | [Profiles](#profiles) |

## Connecting

### The client can't find BrowserControl {#the-client-cant-find-browsercontrol}

1. **Open the client's MCP log.** It shows the command it ran and why it failed.
2. **Check the command exists.** Desktop apps often have a shorter `PATH` than your terminal. Run `which uvx` (or `which browsercontrol`) and put that full path in the config.
3. **Check the JSON.** A trailing comma or a missing brace makes most clients skip the whole file.
4. **Reload.** Most clients read MCP config only at startup.

### The profile is already in use

Only one BrowserControl can use a browser profile at a time. If two clients each launch their own server, the second fails. Either give each its own [`BROWSER_USER_DATA_DIR`](/reference/configuration#browser_user_data_dir), or run one server [over HTTP](/guide/http) and point both clients at it.

## Launching

### Chromium won't launch {#chromium-won-t-launch}

BrowserControl downloads Chromium if it can't find a browser. If that fails, install it yourself:

```bash
python -m playwright install chromium
```

On Linux, add the system libraries Chromium needs:

```bash
python -m playwright install chromium --with-deps
```

If Playwright has no build for your distribution, point BrowserControl at a browser you have:

```bash
BROWSER_EXECUTABLE_PATH=/usr/bin/google-chrome browsercontrol
```

### It won't start on a server or in CI

BrowserControl opens a visible window by default, which needs a display. On a server or in CI, set `BROWSER_HEADLESS=true`, or run it under a virtual display: `xvfb-run browsercontrol`.

### Install fails on old Python

BrowserControl needs Python 3.11 or newer. `python --version` shows yours; `uv python install 3.12` installs a newer one, and `uvx` picks a suitable Python on its own.

## Elements

### Element numbers stop working

Numbers belong to the screenshot they came from. After any action, read the number from the **latest** response.

- `Element 7 is stale (it moved)` (or *no longer on the page*, *no longer visible*, *its content changed*): the page changed after the screenshot. Nothing was clicked. Use the fresh screenshot that came with the error.
- `Element 42 not found. Valid IDs: [...]`: that number isn't in the current map at all.

Inside [`act`](/reference/interaction#act), every number refers to the map from before the call, so a step after a navigation fails as stale. Put navigation last.

### Something on screen has no number

Something covers it: a cookie banner, a modal, a sticky header, a chat widget. Close the overlay, then look again. If it's simply off-screen, `find("its text")` scrolls to it.

### A click does nothing

- The element may be **disabled**: the list shows `(disabled)`, and the tool says so. Something else (a required field) usually comes first.
- The page may still be busy. Check the result with `wait_for(text=…)` rather than assuming.
- It may be a custom control that reacts to something else. `inspect_element(id)` shows what it is; `get_console_logs()` shows errors it raised.

### `select_option` fails on a dropdown

`select_option` works on native `<select>` only. For a custom dropdown, `click` it open, then `click` the option in the fresh screenshot, or press `ArrowDown` and `Enter`.

### Typed text replaced what was there

That's intended: `type_text` replaces the field's value. To append, read it with `get_text(id)` and type the combined text.

## Uploads {#uploads}

- **Use an absolute path.** Relative paths resolve against the server's working directory.
- **Check the file type.** `inspect_element(id)` shows the input's `accept` attribute; a file that doesn't match may be ignored.
- **Find the real input.** It's listed as `input[file]`, even when the site hides it behind a styled button.

## Localhost {#localhost}

BrowserControl retries `localhost` as `127.0.0.1` when the connection is refused, and Chromium bypasses proxies for loopback addresses. If it still fails:

- Check the dev server is up: `curl http://localhost:3000`.
- If it listens only on IPv6 or another interface, use that address.
- Behind a corporate proxy, set `NO_PROXY=localhost,127.0.0.1`.

## Profiles {#profiles}

Logins live in the profile directory. If they don't survive restarts:

- Check it's writable: `ls -la ~/.browsercontrol/`.
- Check you aren't in an [isolated session](/concepts/sessions#isolated-sessions); those are in memory.
- Some sites expire sessions on their own schedule.

## Recordings

- Traces are in `~/.browsercontrol/recordings` unless [`BROWSER_RECORDINGS_DIR`](/reference/configuration#paths) moves them. `list_recordings()` lists them.
- Open one with `npx playwright show-trace <file>.zip`, or drop it on [trace.playwright.dev](https://trace.playwright.dev).

## Still stuck?

Search the [issues](https://github.com/adityasasidhar/browsercontrol/issues), or open a new one with your OS, Python version, client, and the server's output at `LOG_LEVEL=DEBUG`.

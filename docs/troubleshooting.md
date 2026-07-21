# Troubleshooting

Solutions to common issues, in roughly the order you'll hit them.

## Installation

### "Chromium executable doesn't exist"

BrowserControl auto-installs Chromium on first run. If that fails:

```bash
python -m playwright install chromium
```

On Linux you may also need system dependencies:

```bash
python -m playwright install chromium --with-deps
```

### `uv sync` fails

Make sure you're on the latest `uv`:

```bash
uv self update
```

If the lockfile is out of date:

```bash
uv lock --upgrade
uv sync
```

### `pip install` fails on Python < 3.11

BrowserControl requires Python 3.11+. Check your version:

```bash
python --version
```

Use `pyenv`, `conda`, or `uv python install` to install a newer version.

## Running

### Missing X server / won't start in CI

BrowserControl defaults to headless, so it works on servers with no display. If you set `BROWSER_HEADLESS=false`, you need a display:

```bash
# Linux without a display
xvfb-run browsercontrol

# With a display
BROWSER_HEADLESS=false browsercontrol
```

### "Connection refused" on localhost

BrowserControl auto-tries `127.0.0.1` when `localhost` fails. If it still fails:

- Confirm the dev server is running: `curl http://localhost:3000` from the shell.
- If your dev server binds only to `127.0.0.1`, navigate directly: `navigate_to("http://127.0.0.1:3000")`.
- Corporate proxies can interfere — BrowserControl already passes `--proxy-bypass-list=<-loopback>` to Chromium. If you're behind a proxy, you may need to set `HTTPS_PROXY` or `NO_PROXY` env vars.

### Sessions don't persist

Check that the user data directory is writable:

```bash
ls -la ~/.browsercontrol/
```

Override with `BROWSER_USER_DATA_DIR=/some/writable/path`. See [Configuration](configuration.md#browser_user_data_dir).

### "Connection refused" — port already in use

```bash
pkill -f browsercontrol
browsercontrol
```

## Using

### Element IDs "expired" after a page change

Element IDs are only valid until the next screenshot. After any navigation, click, or state change, **call the tool again and read the new IDs from the latest screenshot/map**. Tools re-screenshot automatically — your agent just needs to look at the response.

!!! tip "The pattern"
    ```text
    → click(5)
    → get_text(7)        # this ID 7 is from the response to click(5), not the call before
    ```

### File upload fails silently

Most likely cause: the file path is relative. BrowserControl resolves file paths against the MCP server's working directory, which may not be what you expect.

**Fix:** use an absolute path:

```text
→ upload_file(8, "/Users/me/Documents/resume.pdf")    # ✓ absolute
→ upload_file(8, "resume.pdf")                       # ✗ relative
```

### File upload rejected by the input

The input may have an `accept` attribute that filters file types. Check it:

```text
→ inspect_element(8)        # look for accept=".pdf,.doc,.docx"
```

Make sure your file matches the allowed types.

### Custom comboboxes don't work with `select_option`

`select_option` only works with native `<select>` elements. For custom JS comboboxes (think downshift, react-select, headless UI), use `click` to open then `click` or keyboard navigation to pick:

```text
→ click(7)                  # opens the combobox
→ press_key("ArrowDown")    # or click(8) on the desired option
→ press_key("Enter")
```

### Element not found / wrong element clicked

If `click(id)` says the element isn't there, or clicks the wrong thing:

1. **Re-screenshot** — `screenshot(annotate=True)` to get fresh IDs.
2. **Inspect** — `inspect_element(id)` to see what's actually at those coordinates.
3. **Try `click_at`** — if you have specific coordinates from vision reasoning.

The element lookup uses `document.elementFromPoint(x, y)`, which can return a different element than what you expect if there are overlays or sticky headers.

### No console logs after a `clear=True`

If you pass `clear=True` to `get_console_logs(clear=True)`, the buffer is wiped after the call. Subsequent calls will be empty until new logs are captured. Just don't pass `clear=True` if you want to keep reading.

## Recording

### "Recording not found" when trying to view

Check the path:

```bash
ls -la ~/.browsercontrol/recordings/
```

Override the location with `BROWSER_RECORDINGS_DIR`. See [Configuration](configuration.md#browser_recordings_dir).

### View session recordings

Recordings are Playwright trace zips. Open them with:

```bash
npx playwright show-trace ~/.browsercontrol/recordings/<name>.zip
```

Or use the browser-based viewer at <https://trace.playwright.dev>.

## Getting help

- **Search existing issues:** [github.com/adityasasidhar/browsercontrol/issues](https://github.com/adityasasidhar/browsercontrol/issues)
- **File a bug:** Open an issue with the output of `browsercontrol` at `LOG_LEVEL=DEBUG` plus your OS and Python version.
- **Discussions:** For questions and ideas, use [GitHub Discussions](https://github.com/adityasasidhar/browsercontrol/discussions).

## See also

- **[Configuration](configuration.md)** — every env var
- **[Architecture](concepts/architecture.md)** — how the pieces fit together

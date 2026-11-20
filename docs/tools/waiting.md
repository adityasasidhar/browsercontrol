# Waiting, dialogs & downloads

Wait for a real condition instead of sleeping, decide how JavaScript dialogs are
answered, and find files the page downloaded.

!!! info "Every action already settles"
    After each action BrowserControl waits for DOMContentLoaded, then for
    in-flight requests to finish, then for the DOM to stop changing (bounded by
    `BROWSER_SETTLE_TIMEOUT`, 3 s by default). Content a single-page app renders
    after its data arrives is usually in the screenshot without any wait.
    Reach for `wait_for` when something takes longer than that.

---

## `wait_for`

Wait until text or a selector appears (or disappears), and/or the network goes idle.

```python
wait_for(
    text: str | None = None,
    selector: str | None = None,
    state: str = "visible",
    network_idle: bool = False,
    timeout_seconds: float = 10.0,
) -> tuple[str, Image]
```

| Name | Type | Default | Description |
|---|---|---|---|
| `text` | `str \| None` | `None` | Wait for an element containing this text. |
| `selector` | `str \| None` | `None` | Wait for an element matching this CSS selector. |
| `state` | `str` | `"visible"` | `visible`, `hidden`, `attached`, or `detached`. |
| `network_idle` | `bool` | `False` | Also wait until no request has been in flight for 500 ms. |
| `timeout_seconds` | `float` | `10.0` | Give up after this long. |

A timeout is not an error: the response says what timed out and still carries
the screenshot. With no condition it just settles the page.

```text
→ wait_for(text="Order confirmed")
→ wait_for(selector=".spinner", state="hidden", timeout_seconds=30)
→ wait_for(network_idle=True)
```

---

## `handle_dialog`

Choose how the **next** `alert`, `confirm`, `prompt`, or `beforeunload` dialog is answered.

```python
handle_dialog(accept: bool = True, prompt_text: str | None = None) -> str
```

Dialogs are never left blocking the page. Without a choice, alerts are
acknowledged, confirms and prompts are dismissed, and `beforeunload` is accepted.
Either way the next tool response starts with a notice:

```text
Notice: A JS dialog appeared: confirm('Delete this item?'), dismissed. Call handle_dialog() before the action to choose the answer.
```

So the usual sequence is: see the notice, call `handle_dialog(accept=True)`, then repeat the action.

---

## `list_downloads`

```python
list_downloads() -> str
```

Downloads are saved automatically to `BROWSER_DOWNLOADS_DIR`
(`~/.browsercontrol/downloads` by default) under the server's suggested file
name, never overwriting an existing file. Each one is also reported as a
`Notice:` in the next response.

---

## See also

- **[Interaction tools](interaction.md)**
- **[Network control](network.md)**: `wait_for_response` for a specific API call

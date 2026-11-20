---
title: Waiting & dialogs
description: Wait for a condition instead of sleeping, choose how JS dialogs are answered, and list downloads.
---

# Waiting & dialogs

Every action already [settles](/concepts/settling) before it returns. These tools cover what takes longer, and the dialogs and downloads that happen along the way.

| Tool | Does | Returns |
| --- | --- | --- |
| [`wait_for`](#wait_for) | Wait until a condition holds instead of sleeping a fixed time. | text + screenshot |
| [`handle_dialog`](#handle_dialog) | Choose how to answer the next JS dialog (alert, confirm, prompt, beforeunload). | text |
| [`list_downloads`](#list_downloads) | List files downloaded in this session, with where they were saved. | text |

## `wait_for` {#wait_for}

Wait until a condition holds instead of sleeping a fixed time.

```python
wait_for(text: str | None = None, selector: str | None = None, state: str = 'visible', network_idle: bool = False, timeout_seconds: float = 10.0)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `text` | `str \| None` | `None` | Wait for an element containing this text |
| `selector` | `str \| None` | `None` | Wait for an element matching this CSS selector |
| `state` | `str` | `"visible"` | "visible" (default), "hidden", "attached", or "detached" |
| `network_idle` | `bool` | `False` | Also wait until no request has been in flight for 500ms |
| `timeout_seconds` | `float` | `10.0` | Give up after this long (default 10) |

Waits for text or a CSS selector to reach a state, for the network to go idle (500 ms with nothing in flight), or any combination. With no condition, it just settles the page. A timeout is not an error: the response says what timed out and still has the screenshot.

```text
→ wait_for(text="Order confirmed")
→ wait_for(selector=".spinner", state="hidden", timeout_seconds=30)
→ wait_for(network_idle=True)
```

`state` is `visible`, `hidden`, `attached`, or `detached`.

## `handle_dialog` {#handle_dialog}

Choose how to answer the next JS dialog (alert, confirm, prompt, beforeunload).

```python
handle_dialog(accept: bool = True, prompt_text: str | None = None)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `accept` | `bool` | `True` | True to press OK, False to press Cancel |
| `prompt_text` | `str \| None` | `None` | Text to enter into a prompt() dialog (only used when accepting) |

Dialogs are never left blocking the page. Without a choice, alerts are acknowledged, confirms and prompts are dismissed, and `beforeunload` is accepted. Either way, the next response starts with a notice:

```text
Notice: A JS dialog appeared: confirm('Delete this item?'), dismissed. Call handle_dialog() before the action to choose the answer.
```

To answer differently, call `handle_dialog(accept=True)` (with `prompt_text` for a prompt) and repeat the action.

## `list_downloads` {#list_downloads}

List files downloaded in this session, with where they were saved.

```python
list_downloads()
```

Returns text only.

Downloads are saved automatically to [`BROWSER_DOWNLOADS_DIR`](/reference/configuration#paths) under the name the server suggests, never overwriting an existing file. Each is also reported as a `Notice:` in the next response.

## See also

- [Settling](/concepts/settling)
- [wait_for_response](/reference/network#wait_for_response)

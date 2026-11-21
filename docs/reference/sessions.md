---
title: Sessions
description: Attach to your own Chrome over CDP, and create, switch, list, and close isolated sessions.
---

# Sessions

Choose which browser and which context the agent works in. See [Sessions & profiles](/concepts/sessions) for the model.

| Tool | Does | Returns |
| --- | --- | --- |
| [`connect_to_chrome`](#connect_to_chrome) | Attach to your own running Chrome so the agent uses its logged-in sessions. | text + screenshot |
| [`disconnect_chrome`](#disconnect_chrome) | Detach from an attached Chrome (leaving it open) and go back to the managed browser. | text + screenshot |
| [`create_session`](#create_session) | Open an isolated browser session (its own cookies, storage, tabs) and switch to it. | text + screenshot |
| [`switch_session`](#switch_session) | Switch to another session. "default" is the persistent, logged-in profile. | text + screenshot |
| [`list_sessions`](#list_sessions) | List browser sessions, their tabs, and which one you are using. | text |
| [`close_session`](#close_session) | Close an isolated session and discard its cookies and tabs. | text |

## `connect_to_chrome` {#connect_to_chrome}

Attach to your own running Chrome so the agent uses its logged-in sessions.

```python
connect_to_chrome(cdp_url: str = 'http://localhost:9222')
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `cdp_url` | `str` | `"http://localhost:9222"` | Chrome's remote debugging endpoint (default `http://localhost:9222`) |

Attaches over the Chrome DevTools Protocol to a Chrome started with `--remote-debugging-port`. The agent works in a new tab of that Chrome; `list_tabs` and `switch_tab` reach the others. Disconnecting never closes your Chrome. To attach at startup, set [`BROWSER_CDP_URL`](/reference/configuration#browser_cdp_url).

::: warning
Chrome 136 and later ignore `--remote-debugging-port` on the default profile, so start Chrome with a separate `--user-data-dir`. See [Use your own Chrome](/recipes/your-chrome).
:::

## `disconnect_chrome` {#disconnect_chrome}

Detach from an attached Chrome (leaving it open) and go back to the managed browser.

```python
disconnect_chrome()
```

Returns text and a fresh annotated screenshot.

Detaches, leaving your Chrome open, and returns to the browser BrowserControl manages.

## `create_session` {#create_session}

Open an isolated browser session (its own cookies, storage, tabs) and switch to it.

```python
create_session(name: str, device: str | None = None, url: str | None = None)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `name` | `str` | required | A name for the session, used by switch_session and close_session |
| `device` | `str \| None` | `None` | Optional device to emulate for the whole session (see list_devices) |
| `url` | `str \| None` | `None` | Optional URL to open in the session |

Opens a fresh context with no shared cookies, storage, or tabs, and switches to it. With `device`, the whole context is created as that device, pixel ratio and mobile viewport included. With `url`, it opens that page. Sessions live in memory and are lost when closed.

## `switch_session` {#switch_session}

Switch to another session. "default" is the persistent, logged-in profile.

```python
switch_session(name: str)
```

Returns text and a fresh annotated screenshot.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `name` | `str` | required | The session name (see list_sessions) |

Makes another session current. `"default"` is the persistent profile, or your Chrome when attached. With several clients on one server, each client keeps its own choice.

## `list_sessions` {#list_sessions}

List browser sessions, their tabs, and which one you are using.

```python
list_sessions()
```

Returns text only.

Lists sessions, their tabs, and which one is current.

## `close_session` {#close_session}

Close an isolated session and discard its cookies and tabs.

```python
close_session(name: str)
```

Returns text only.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `name` | `str` | required | The session to close (the default session cannot be closed) |

Closes an isolated session and discards its cookies and tabs. The default session can't be closed.

## See also

- [Use your own Chrome](/recipes/your-chrome)
- [Share over HTTP](/guide/http)

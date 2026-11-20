# Sessions

Three ways to give the agent a browser:

| | Cookies & logins | Use it for |
|---|---|---|
| **Default session** | Persistent profile in `BROWSER_USER_DATA_DIR` | Day-to-day work; log in once and stay logged in. |
| **Your own Chrome** (`connect_to_chrome`) | Whatever you are signed in to | Acting on sites you already use, without logging in again. |
| **Isolated session** (`create_session`) | Fresh and in-memory | A second user, signed-out flows, or keeping several agents apart. |

---

## `connect_to_chrome`

```python
connect_to_chrome(cdp_url: str = "http://localhost:9222") -> tuple[str, Image]
```

Attaches over the Chrome DevTools Protocol. Start Chrome with remote debugging first:

```bash
google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-agent"
```

!!! warning "Chrome 136 and later"
    Chrome ignores `--remote-debugging-port` on its default profile, so use a
    dedicated `--user-data-dir` and sign in to your sites there once. Anything
    that can reach the debugging port controls that browser, so keep it on
    `localhost`.

The agent opens a tab of its own instead of taking over the one you are looking
at; `list_tabs`/`switch_tab` reach the others. Stopping the server or calling
`disconnect_chrome()` only detaches; your Chrome keeps running. To attach at
startup instead, set `BROWSER_CDP_URL=http://localhost:9222`.

## `disconnect_chrome`

```python
disconnect_chrome() -> tuple[str, Image]
```

Detaches and goes back to the managed browser.

---

## `create_session`

```python
create_session(name: str, device: str | None = None, url: str | None = None) -> tuple[str, Image]
```

Opens an isolated context (no shared cookies, storage, or tabs) and switches to
it. With `device`, the whole context is created as that device, pixel ratio and
mobile viewport included. Captured logs, network traffic, mocks, emulation, and
the action log are all kept per session.

## `switch_session`

```python
switch_session(name: str) -> tuple[str, Image]
```

`"default"` is the persistent profile (or the attached Chrome).

## `list_sessions`

```python
list_sessions() -> str
```

## `close_session`

```python
close_session(name: str) -> str
```

The default session cannot be closed.

---

## One session per agent

When several MCP clients share one server (over [Streamable HTTP](../configuration.md#browser_transport)),
each client is bound to its own session choice: one agent calling
`switch_session` does not move another. Set `BROWSER_ISOLATE_CLIENTS=true` (or
pass `--isolate-clients`) to give every new client its own isolated session
automatically.

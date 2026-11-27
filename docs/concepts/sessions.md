---
title: Sessions & profiles
description: The persistent default profile, attaching to your own Chrome, isolated sessions, and how several MCP clients share one server.
---

# Sessions & profiles

A **session** is one browser context: its own cookies, storage, and tabs. BrowserControl always has a default session, and you can open more.

| | Cookies and logins | Use it for |
| --- | --- | --- |
| **Default session** | A persistent profile on disk | Everyday work: log in once, stay logged in. |
| **Your own Chrome** | Whatever you're signed in to | Sites you already use, without logging in again. |
| **Isolated session** | Fresh, in memory, gone when closed | A second user, signed-out flows, or keeping agents apart. |

## The default session

BrowserControl launches Chromium with a persistent profile in `~/.browsercontrol/user_data` ([`BROWSER_USER_DATA_DIR`](/reference/configuration#browser_user_data_dir)). Cookies, `localStorage`, and history survive restarts, so an agent that signed in yesterday is still signed in today. Sites can still expire a login on their own schedule.

Only one process can use a profile at a time. To run two BrowserControl servers side by side, give each its own `BROWSER_USER_DATA_DIR`.

## Your own Chrome

Instead of launching its own browser, BrowserControl can attach to a Chrome you started with remote debugging, using the Chrome DevTools Protocol (CDP):

```text
connect_to_chrome("http://localhost:9222")
```

The agent opens a tab of its own rather than taking over yours. Disconnecting, or stopping the server, only detaches, and your Chrome keeps running. To attach at startup, set [`BROWSER_CDP_URL`](/reference/configuration#browser_cdp_url). The full walkthrough is in [Use your own Chrome](/recipes/your-chrome).

## Isolated sessions

```text
create_session("buyer", device="iPhone 13", url="https://shop.test")
```

This opens a fresh context with no shared cookies, storage, or tabs, and switches to it. With `device`, the whole context is created as that device, pixel ratio and mobile layout included, which is more faithful than emulating a device in an existing session. Isolated sessions live in memory and disappear when closed.

Move between sessions with `switch_session(name)` (`"default"` is the persistent one), list them with `list_sessions()`, and discard one with `close_session(name)`. The default session can't be closed.

## What each session keeps

Everything BrowserControl captures or changes belongs to the session it happened in:

- tabs, and the element map of each tab
- console messages, page errors, and network requests
- request mocks and emulation settings
- the dialog policy and downloads
- the action log that [`export_test`](/reference/recording#export_test) turns into a test

Switching sessions switches all of it.

## Several clients, one server

When several MCP clients share a server over [HTTP](/guide/http), each client keeps its own current session. One agent calling `switch_session` doesn't move another.

To isolate clients completely, start the server with `--isolate-clients` (or `BROWSER_ISOLATE_CLIENTS=true`). Each client then gets its own isolated session on its first tool call.

### How the server tells clients apart {#client-identity}

The current MCP protocol (2026-07-28) has no sessions: each request stands alone, so the server needs something else to recognize a client from one call to the next. In order, it uses:

1. **A named token.** Over HTTP, a client that authenticates with its own token from [`BROWSER_AUTH_TOKENS`](/reference/configuration#browser_auth_tokens) is identified by that token's name, on any protocol version.
2. **The MCP session.** A client on the older session-based protocol is identified by its session id, as before.
3. **The process.** Over stdio, one server process serves one client, so that client is always the same.

A client on the current protocol that connects over HTTP without a named token can't be recognized. All such clients share one current session, and `--isolate-clients` can't keep them apart; the server warns at startup if `--isolate-clients` is on without `BROWSER_AUTH_TOKENS`. Give each client [its own token](/guide/http#per-client-tokens) to isolate them.

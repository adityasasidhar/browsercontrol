---
title: Share over HTTP
description: Run BrowserControl as a Streamable HTTP server so several MCP clients can share one browser, with optional per-client isolation.
---

# Share over HTTP

By default each MCP client launches its own BrowserControl over stdio. To let several clients or agents share one browser, start the server yourself and serve it over Streamable HTTP.

## Start the server

```bash
uvx browsercontrol --transport http
```

It listens on `http://127.0.0.1:8000/mcp`. Change the address with `--host` and `--port`, or with `BROWSER_HOST` and `BROWSER_PORT`. `--transport sse` serves the older SSE transport for clients that still need it.

## Point clients at it

::: code-group

```bash [Claude Code]
claude mcp add --transport http browsercontrol http://127.0.0.1:8000/mcp
```

```json [mcpServers]
{
  "mcpServers": {
    "browsercontrol": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

:::

Clients differ in how they name URL-based servers (`url`, `serverUrl`, or a `type: "http"` field). Check your client's MCP docs if the entry above isn't recognized.

## Shared or isolated

Every connected client drives the same browser, but each keeps its own choice of [session](/concepts/sessions). One agent calling `switch_session` doesn't move another.

To keep clients fully apart, give each its own isolated session automatically:

```bash
uvx browsercontrol --transport http --isolate-clients
```

With `--isolate-clients` (or `BROWSER_ISOLATE_CLIENTS=true`), each client gets a fresh in-memory session on its first tool call: separate cookies, tabs, captured traffic, mocks, and action log. Use it when agents work in parallel and must not see each other's logins.

## Security

::: danger Authentication is off unless you set a token
Anyone who can reach the port controls the browser, including every site it is signed in to. Keep the default `127.0.0.1` host, or set `BROWSER_AUTH_TOKEN` as below. BrowserControl logs a warning if you bind to any other address, and says in it whether the token is set.
:::

### Authenticate clients {#authenticate-clients}

Set `BROWSER_AUTH_TOKEN` and the server rejects every request that lacks `Authorization: Bearer <token>` with `401 Unauthorized`, comparing the token in constant time:

```bash
export BROWSER_AUTH_TOKEN="$(openssl rand -hex 32)"
uvx browsercontrol --transport http --host 0.0.0.0
```

Then give each client the header:

```bash
claude mcp add --transport http browsercontrol http://HOST:8000/mcp \
  --header "Authorization: Bearer $BROWSER_AUTH_TOKEN"
```

```json
{
  "mcpServers": {
    "browsercontrol": {
      "url": "http://HOST:8000/mcp",
      "headers": { "Authorization": "Bearer <token>" }
    }
  }
}
```

The token is read from the environment only. There is deliberately no `--auth-token` flag, because command-line arguments show up in process lists. It also applies to `--transport sse`.

::: warning Plain HTTP is not encrypted
A bearer token sent over plain HTTP can be read by anyone on the network path. Off loopback, terminate TLS in front of BrowserControl (a reverse proxy) or use an SSH tunnel (`ssh -L 8000:127.0.0.1:8000 host`).
:::

### Limit where the agent can browse

Shared servers should also restrict navigation with [`BROWSER_ALLOWED_DOMAINS`](/reference/configuration#navigation-policy).

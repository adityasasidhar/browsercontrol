"""MCP resources exposing captured browser data, and per-client session binding.

Resources let a client read logs and traffic without spending a tool call (and
without a screenshot). They read the caller's session and never start the
browser themselves.
"""

import json
import logging
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from mcp_types.version import MODERN_PROTOCOL_VERSIONS

from browsercontrol.auth import CLIENT_STATE_KEY
from browsercontrol.browser import browser, current_client

logger = logging.getLogger(__name__)


def _public(entry: dict[str, Any]) -> dict[str, Any]:
    """Drop internal fields (live Playwright objects) before serializing."""
    return {k: v for k, v in entry.items() if not k.startswith("_")}


def _dump(data: Any) -> str:
    return json.dumps(data, indent=2, default=str)


def register_resources(mcp: FastMCP) -> None:
    """Register browser data resources with the MCP server."""

    @mcp.resource(
        "browser://console", mime_type="application/json", description="Captured console messages"
    )
    def console_logs() -> str:
        return _dump(browser.get_console_logs())

    @mcp.resource(
        "browser://network",
        mime_type="application/json",
        description="The last 100 network requests with headers and status",
    )
    def network_requests() -> str:
        return _dump([_public(e) for e in browser.get_network_requests()])

    @mcp.resource(
        "browser://network/{request_id}",
        mime_type="application/json",
        description="One captured network request by its #id",
    )
    def network_request(request_id: str) -> str:
        entry = browser.session.find_request(int(request_id))
        if entry is None:
            raise ValueError(f"No captured request #{request_id}")
        return _dump(_public(entry))

    @mcp.resource(
        "browser://errors", mime_type="application/json", description="Uncaught page errors"
    )
    def page_errors() -> str:
        return _dump(browser.get_page_errors())

    @mcp.resource("browser://tabs", mime_type="application/json", description="Open tabs")
    async def tabs() -> str:
        return _dump(await browser.list_tabs())

    @mcp.resource(
        "browser://downloads", mime_type="application/json", description="Downloaded files"
    )
    def downloads() -> str:
        return _dump(browser.session.downloads)

    @mcp.resource(
        "browser://actions",
        mime_type="application/json",
        description="The action log that export_test turns into a test",
    )
    def actions() -> str:
        return _dump(browser.get_action_log())

    @mcp.resource("browser://sessions", mime_type="application/json", description="Sessions")
    def sessions() -> str:
        return _dump(browser.list_sessions() if browser.is_started else [])


# The key for the one client of a stdio or in-memory server on the session-less protocol.
PROCESS_CLIENT = "process"


def _token_client() -> str | None:
    """The name of the BROWSER_AUTH_TOKENS client that sent this HTTP request, if any."""
    try:
        state = get_http_request().scope.get("state") or {}
    except RuntimeError:  # not an HTTP request (stdio, in-memory)
        return None
    name = state.get(CLIENT_STATE_KEY)
    return str(name) if name else None


def _client_key(context: MiddlewareContext[Any]) -> str:
    """A key that stays the same across one MCP client's calls; "" when nothing identifies it.

    In order: the client's named bearer token (BROWSER_AUTH_TOKENS); the session id on a
    handshake-era (legacy) connection, which lasts the whole MCP session; one fixed key on a
    session-less stdio or in-memory connection, which serves a single client. A session-less
    HTTP request without a named token carries nothing stable, since ``session_id`` is new
    on every request there, so those clients all share "".
    """
    try:
        ctx = context.fastmcp_context
        if ctx is None:
            return ""
        name = _token_client()
        if name:
            return f"token:{name}"
        request_context = ctx.request_context
        if (
            request_context is not None
            and request_context.protocol_version not in MODERN_PROTOCOL_VERSIONS
        ):
            return str(ctx.session_id)
        if ctx.transport in ("sse", "streamable-http"):
            return ""
        return PROCESS_CLIENT
    except Exception:
        logger.debug("Could not identify the MCP client", exc_info=True)
        return ""


class SessionBindingMiddleware(Middleware):
    """Run each tool call and resource read in the calling client's browser session."""

    async def on_call_tool(
        self, context: MiddlewareContext[Any], call_next: CallNext[Any, Any]
    ) -> Any:
        client = _client_key(context)
        token = current_client.set(client)
        try:
            await browser.ensure_client_session(client)
            browser.mark_call_started()
            return await call_next(context)
        finally:
            current_client.reset(token)

    async def on_read_resource(
        self, context: MiddlewareContext[Any], call_next: CallNext[Any, Any]
    ) -> Any:
        token = current_client.set(_client_key(context))
        try:
            return await call_next(context)
        finally:
            current_client.reset(token)

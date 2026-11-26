"""Bearer-token authentication for the network transports (http and sse).

Enabled by ``BROWSER_AUTH_TOKEN``. The token is read from the environment only, never a
command-line flag, so it does not show up in process lists.
"""

import hmac
import logging

from starlette.middleware import Middleware
from starlette.types import ASGIApp, Receive, Scope, Send

from browsercontrol.config import config

logger = logging.getLogger(__name__)

_UNAUTHORIZED = b'{"error": "unauthorized", "detail": "Missing or invalid bearer token."}'


def token_matches(header: str | None, token: str) -> bool:
    """True when ``header`` is ``Authorization: Bearer <token>``, compared in constant time."""
    if not header:
        return False
    scheme, _, presented = header.partition(" ")
    if scheme.lower() != "bearer":
        return False
    # Compare bytes: compare_digest rejects non-ASCII str, and HTTP headers can carry any byte.
    return hmac.compare_digest(presented.strip().encode(), token.encode())


class BearerAuthMiddleware:
    """ASGI middleware that rejects requests without the right bearer token."""

    def __init__(self, app: ASGIApp, token: str) -> None:
        self.app = app
        self.token = token

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            await self.app(scope, receive, send)
            return
        headers = dict(scope.get("headers") or [])
        header = headers.get(b"authorization", b"").decode("latin-1")
        if scope["type"] == "http" and token_matches(header, self.token):
            await self.app(scope, receive, send)
            return
        logger.warning("Rejected a request without a valid bearer token")
        if scope["type"] == "http":
            await send(
                {
                    "type": "http.response.start",
                    "status": 401,
                    "headers": [
                        (b"content-type", b"application/json"),
                        (b"content-length", str(len(_UNAUTHORIZED)).encode()),
                        (b"www-authenticate", b'Bearer realm="browsercontrol"'),
                    ],
                }
            )
            await send({"type": "http.response.body", "body": _UNAUTHORIZED})
        elif scope["type"] == "websocket":
            await send({"type": "websocket.close", "code": 1008})


def auth_middleware() -> list[Middleware]:
    """The middleware list for ``mcp.run``: bearer auth when a token is configured."""
    if not config.auth_token:
        return []
    return [Middleware(BearerAuthMiddleware, token=config.auth_token)]

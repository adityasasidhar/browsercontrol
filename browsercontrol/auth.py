"""Bearer-token authentication for the network transports (http and sse).

Enabled by ``BROWSER_AUTH_TOKEN`` (one shared token) and/or ``BROWSER_AUTH_TOKENS`` (one named
token per client). Tokens are read from the environment only, never a command-line flag, so they
do not show up in process lists. A named token also identifies its client: the middleware puts the
name in the request scope, where ``SessionBindingMiddleware`` reads it as the client key.
"""

import hmac
import logging
from collections.abc import Mapping

from starlette.middleware import Middleware
from starlette.types import ASGIApp, Receive, Scope, Send

from browsercontrol.config import config

logger = logging.getLogger(__name__)

# Request-scope state key holding the name of the client whose named token matched.
CLIENT_STATE_KEY = "browsercontrol_client"

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
    """ASGI middleware that rejects requests without a configured bearer token.

    ``token`` is the shared token (no client name); ``tokens`` maps client names to their own
    tokens. Every token is compared, with no early exit, so timing does not reveal which matched.
    """

    def __init__(
        self, app: ASGIApp, token: str | None = None, tokens: Mapping[str, str] | None = None
    ) -> None:
        self.app = app
        self.token = token
        self.tokens = dict(tokens or {})

    def _match(self, header: str) -> tuple[bool, str | None]:
        """(authenticated, client name). A named token wins over an identical shared one."""
        name: str | None = None
        ok = bool(self.token) and token_matches(header, self.token or "")
        for candidate, token in self.tokens.items():
            if token_matches(header, token):
                ok, name = True, candidate
        return ok, name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            await self.app(scope, receive, send)
            return
        headers = dict(scope.get("headers") or [])
        header = headers.get(b"authorization", b"").decode("latin-1")
        ok, name = self._match(header) if scope["type"] == "http" else (False, None)
        if ok:
            # Always overwrite, so nothing upstream can pre-set a client name.
            scope.setdefault("state", {})[CLIENT_STATE_KEY] = name
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
    """The middleware list for ``mcp.run``: bearer auth when any token is configured."""
    if not config.auth_token and not config.auth_tokens:
        return []
    return [Middleware(BearerAuthMiddleware, token=config.auth_token, tokens=config.auth_tokens)]

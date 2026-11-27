"""
Entry point for running BrowserControl as a module.

Usage:
    browsercontrol                                   # stdio (default)
    browsercontrol --transport http --port 8000      # Streamable HTTP at /mcp
    python -m browsercontrol --transport http
"""

import argparse
import ipaddress
import logging

from browsercontrol.auth import auth_middleware
from browsercontrol.config import config

TRANSPORTS = ("stdio", "http", "sse")

logger = logging.getLogger("browsercontrol")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="browsercontrol", description="BrowserControl MCP server")
    parser.add_argument(
        "--transport",
        choices=TRANSPORTS,
        default=config.transport if config.transport in TRANSPORTS else "stdio",
        help="stdio (default), http (Streamable HTTP), or sse (legacy)",
    )
    parser.add_argument("--host", default=config.host, help="HTTP bind address (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=config.port, help="HTTP port (default 8000)")
    parser.add_argument(
        "--isolate-clients",
        action="store_true",
        default=config.isolate_clients,
        help="give every MCP client its own isolated browser session",
    )
    return parser.parse_args(argv)


def _is_loopback(host: str) -> bool:
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _auth_enabled() -> bool:
    return bool(config.auth_token or config.auth_tokens)


def non_loopback_warning(host: str) -> str:
    """The warning for serving beyond loopback; says whether a token protects the port."""
    if _auth_enabled():
        return (
            f"Serving on {host}, which is reachable from other machines. Requests need a "
            "bearer token from BROWSER_AUTH_TOKEN or BROWSER_AUTH_TOKENS, but the connection "
            "is plain HTTP, so the token can be read on the network; use a TLS proxy or bind "
            "to 127.0.0.1 unless the network is trusted."
        )
    return (
        f"Serving on {host}, which is reachable from other machines, and "
        "BROWSER_AUTH_TOKEN is not set, so BrowserControl has no authentication: anyone who "
        "can reach the port controls the browser. Set BROWSER_AUTH_TOKEN, or bind to "
        "127.0.0.1 unless the network is trusted."
    )


ISOLATION_WARNING = (
    "--isolate-clients is on but BROWSER_AUTH_TOKENS is not set. Clients on the current MCP "
    "protocol (2026-07-28) send nothing that identifies them between calls, so they all "
    "share one browser session; only clients on the older session-based protocol get their "
    "own. Give each client its own named token in BROWSER_AUTH_TOKENS to isolate them."
)


def main(argv: list[str] | None = None) -> None:
    """Run the MCP server."""
    args = parse_args(argv)
    config.isolate_clients = args.isolate_clients

    from browsercontrol.server import mcp

    if args.transport == "stdio":
        mcp.run()
        return
    if not _is_loopback(args.host):
        logger.warning(non_loopback_warning(args.host))
    if _auth_enabled():
        sources = ["BROWSER_AUTH_TOKEN"] if config.auth_token else []
        if config.auth_tokens:
            sources.append(f"{len(config.auth_tokens)} named client tokens in BROWSER_AUTH_TOKENS")
        logger.info("Bearer token authentication is enabled (%s).", " and ".join(sources))
    if config.isolate_clients and not config.auth_tokens:
        logger.warning(ISOLATION_WARNING)
    mcp.run(
        transport=args.transport,
        host=args.host,
        port=args.port,
        middleware=auth_middleware(),
    )


if __name__ == "__main__":
    main()

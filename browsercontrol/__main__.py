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


def main(argv: list[str] | None = None) -> None:
    """Run the MCP server."""
    args = parse_args(argv)
    config.isolate_clients = args.isolate_clients

    from browsercontrol.server import mcp

    if args.transport == "stdio":
        mcp.run()
        return
    if not _is_loopback(args.host):
        # There is no authentication: anyone who can reach the port controls the
        # browser, including its logged-in sessions.
        logger.warning(
            f"Serving on {args.host}, which is reachable from other machines. "
            "BrowserControl has no authentication; bind to 127.0.0.1 unless the "
            "network is trusted."
        )
    mcp.run(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()

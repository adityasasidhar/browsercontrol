"""
Entry point for running BrowserControl as a module.

Usage:
    python -m browsercontrol
    # or
    browsercontrol
"""

from browsercontrol.server import mcp


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()

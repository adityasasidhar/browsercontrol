"""
BrowserControl - Browser automation MCP server with Set of Marks.
"""

from importlib.metadata import version

from browsercontrol.server import mcp

__version__ = version("browsercontrol")
__all__ = ["mcp"]

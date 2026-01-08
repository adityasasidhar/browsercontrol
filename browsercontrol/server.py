"""
Browser Control MCP Server

Main server module that sets up the MCP server with all tools.
"""

import logging
from contextlib import asynccontextmanager

from fastmcp import FastMCP

from browsercontrol.browser import browser
from browsercontrol.config import config
from browsercontrol.tools import (
    register_navigation_tools,
    register_interaction_tools,
    register_form_tools,
    register_content_tools,
    register_devtools,
    register_recording_tools,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastMCP):
    """Manage browser lifecycle with the MCP server."""
    logger.info("Starting Browser Control MCP server")
    try:
        await browser.start()
        yield
    except Exception as e:
        logger.error(f"Failed to start browser: {e}")
        raise
    finally:
        logger.info("Shutting down Browser Control MCP server")
        await browser.stop()


# Create the MCP server
mcp = FastMCP(
    "BrowserControl",
    instructions="""Full-featured browser automation for AI agents.

Features:
- Set of Marks (SoM): Screenshots show numbered interactive elements.
- Developer Tools: Console logs, network requests, errors, and performance metrics.
- Session Recording: Capture video traces and snapshots for debugging.
- Persistent Session: Cookies and login state are saved automatically.
- Smart Navigation: Auto-handles localhost/127.0.0.1 and bypasses proxies.

Core Actions:
- navigate_to(url)
- click(element_id)
- type_text(element_id, text)
- scroll(direction, amount)

Developer Tools:
- get_console_logs()
- get_network_requests()
- get_page_errors()
- inspect_element(id)

Session Recording:
- start_recording()
- stop_recording()
- take_snapshot()
- list_recordings()""",
    lifespan=lifespan,
)

# Register all tools
register_navigation_tools(mcp)
register_interaction_tools(mcp)
register_form_tools(mcp)
register_content_tools(mcp)
register_devtools(mcp)
register_recording_tools(mcp)

logger.info("Browser Control MCP server initialized with all tools")



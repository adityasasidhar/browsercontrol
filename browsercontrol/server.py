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
    instructions="""Browser automation with Set of Marks (SoM), Developer Tools, and Session Recording.

Every screenshot shows numbered interactive elements. Use element IDs to interact:
- click(5) - Click element 5
- type_text(3, "hello") - Type into element 3

Developer Tools:
- get_console_logs() - Browser console output
- get_network_requests() - Monitor API calls
- get_page_errors() - JavaScript errors
- run_in_console(code) - Execute JS
- inspect_element(id) - Get styles/properties
- get_page_performance() - Load times, Web Vitals

Session Recording:
- start_recording() - Begin recording session
- stop_recording() - Save recording
- take_snapshot() - Save screenshot + HTML
- list_recordings() - View saved sessions""",
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



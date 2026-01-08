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
    instructions="""Browser automation with Set of Marks (SoM).

Every screenshot shows numbered interactive elements. Use element IDs to interact:
- click(5) - Click element 5
- type_text(3, "hello") - Type into element 3
- scroll("down", "large") - Scroll the page

Available tools: navigate_to, go_back, go_forward, refresh_page, scroll,
click, click_at, type_text, press_key, hover, scroll_to_element, wait,
select_option, check_checkbox, get_page_content, get_text, get_page_info,
run_javascript, screenshot""",
    lifespan=lifespan,
)

# Register all tools
register_navigation_tools(mcp)
register_interaction_tools(mcp)
register_form_tools(mcp)
register_content_tools(mcp)

logger.info("Browser Control MCP server initialized with all tools")

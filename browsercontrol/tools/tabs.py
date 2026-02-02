import logging

from fastmcp import FastMCP
from fastmcp.utilities.types import Image

from browsercontrol.browser import browser
from browsercontrol.tools.content import _get_screenshot_with_summary

logger = logging.getLogger(__name__)


def register_tab_tools(mcp: FastMCP) -> None:
    """Register tab management tools with the MCP server."""

    @mcp.tool()
    async def create_tab(url: str | None = None) -> tuple[str, Image]:
        """
        Create a new tab and switch to it.

        Args:
            url: Optional URL to open in the new tab.
        """
        try:
            await browser.ensure_started()
            await browser.create_tab(url)

            image, summary = await _get_screenshot_with_summary()
            msg = "Created new tab" + (f" and navigated to {url}" if url else "")
            return f"{msg}\n\n{summary}", image

        except Exception as e:
            logger.error(f"Create tab failed: {e}")
            raise RuntimeError(f"Create tab failed: {e}")

    @mcp.tool()
    async def switch_tab(index: int) -> tuple[str, Image]:
        """
        Switch to a specific tab by its index.

        Args:
            index: The 0-based index of the tab to switch to.
        """
        try:
            await browser.ensure_started()
            await browser.switch_to_tab(index)

            image, summary = await _get_screenshot_with_summary()
            return f"Switched to tab {index}\n\n{summary}", image

        except Exception as e:
            logger.error(f"Switch tab failed: {e}")
            raise RuntimeError(f"Switch tab failed: {e}")

    @mcp.tool()
    async def close_tab(index: int) -> tuple[str, Image]:
        """
        Close a specific tab by its index.

        Args:
            index: The 0-based index of the tab to close.
        """
        try:
            await browser.ensure_started()
            await browser.close_tab(index)

            image, summary = await _get_screenshot_with_summary()
            return f"Closed tab {index}\n\n{summary}", image

        except Exception as e:
            logger.error(f"Close tab failed: {e}")
            raise RuntimeError(f"Close tab failed: {e}")

    @mcp.tool()
    async def list_tabs() -> str:
        """List all open tabs with their indices, titles, and URLs."""
        try:
            await browser.ensure_started()
            tabs = await browser.list_tabs()

            lines = ["Open Tabs:"]
            for tab in tabs:
                active_marker = "*" if tab["active"] else " "
                lines.append(f"{active_marker} [{tab['index']}] {tab['title']} - {tab['url']}")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"List tabs failed: {e}")
            raise RuntimeError(f"List tabs failed: {e}")

    logger.debug("Registered tab tools")

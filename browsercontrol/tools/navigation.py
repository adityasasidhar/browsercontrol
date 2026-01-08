"""Navigation tools for browser control."""

import logging
from fastmcp import FastMCP
from fastmcp.utilities.types import Image

from browsercontrol.browser import browser
from browsercontrol.config import config

logger = logging.getLogger(__name__)


async def _get_screenshot_with_summary() -> tuple[Image, str]:
    """Helper to get annotated screenshot with element summary."""
    screenshot_bytes, elem_map = await browser.screenshot_with_som()
    image = Image(data=screenshot_bytes, format="png")
    
    summary_lines = [f"Found {len(elem_map)} interactive elements:"]
    for eid, elem in list(elem_map.items())[:30]:
        desc = elem["text"][:40] if elem["text"] else elem["tag"]
        summary_lines.append(f"  [{eid}] {elem['tag']} - {desc}")
    
    if len(elem_map) > 30:
        summary_lines.append(f"  ... and {len(elem_map) - 30} more")
    
    return image, "\n".join(summary_lines)


def register_navigation_tools(mcp: FastMCP) -> None:
    """Register navigation tools with the MCP server."""
    
    @mcp.tool()
    async def navigate_to(url: str) -> tuple[str, Image]:
        """
        Navigate to a URL. Returns an annotated screenshot with numbered interactive elements.
        
        Args:
            url: The URL to navigate to
            
        Returns:
            Element summary and annotated screenshot
        """
        try:
            await browser.ensure_started()
            logger.info(f"Navigating to: {url}")
            
            try:
                await browser.page.goto(url, wait_until="domcontentloaded", timeout=config.timeout_ms)
            except Exception as e:
                # Handle localhost vs 127.0.0.1 resolution issues
                if "ERR_CONNECTION_REFUSED" in str(e) and "localhost" in url:
                    fallback_url = url.replace("localhost", "127.0.0.1")
                    logger.info(f"Navigation to localhost failed, retrying with: {fallback_url}")
                    await browser.page.goto(fallback_url, wait_until="domcontentloaded", timeout=config.timeout_ms)
                    url = fallback_url  # Update for success message
                else:
                    raise e

            await browser.page.wait_for_timeout(500)
            image, summary = await _get_screenshot_with_summary()
            return f"Navigated to {url}\n\n{summary}", image
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            try:
                image, summary = await _get_screenshot_with_summary()
                return f"Error navigating to {url}: {e}\n\n{summary}", image
            except Exception:
                raise RuntimeError(f"Navigation failed: {e}")
    
    @mcp.tool()
    async def go_back() -> tuple[str, Image]:
        """Navigate back to the previous page."""
        try:
            await browser.ensure_started()
            await browser.page.go_back(timeout=config.timeout_ms)
            await browser.page.wait_for_timeout(500)
            image, summary = await _get_screenshot_with_summary()
            return f"Navigated back\n\n{summary}", image
        except Exception as e:
            logger.error(f"Go back failed: {e}")
            image, summary = await _get_screenshot_with_summary()
            return f"Error going back: {e}\n\n{summary}", image
    
    @mcp.tool()
    async def go_forward() -> tuple[str, Image]:
        """Navigate forward to the next page."""
        try:
            await browser.ensure_started()
            await browser.page.go_forward(timeout=config.timeout_ms)
            await browser.page.wait_for_timeout(500)
            image, summary = await _get_screenshot_with_summary()
            return f"Navigated forward\n\n{summary}", image
        except Exception as e:
            logger.error(f"Go forward failed: {e}")
            image, summary = await _get_screenshot_with_summary()
            return f"Error going forward: {e}\n\n{summary}", image
    
    @mcp.tool()
    async def refresh_page() -> tuple[str, Image]:
        """Refresh the current page."""
        try:
            await browser.ensure_started()
            await browser.page.reload(timeout=config.timeout_ms)
            await browser.page.wait_for_timeout(500)
            image, summary = await _get_screenshot_with_summary()
            return f"Page refreshed\n\n{summary}", image
        except Exception as e:
            logger.error(f"Refresh failed: {e}")
            image, summary = await _get_screenshot_with_summary()
            return f"Error refreshing: {e}\n\n{summary}", image
    
    @mcp.tool()
    async def scroll(
        direction: str = "down",
        amount: str = "medium"
    ) -> tuple[str, Image]:
        """
        Scroll the page.
        
        Args:
            direction: "up", "down", "left", or "right"
            amount: "small" (100px), "medium" (400px), "large" (800px), 
                    "page" (full viewport), "top", "bottom", or pixels like "500"
        """
        try:
            await browser.ensure_started()
            
            amount_map = {"small": 100, "medium": 400, "large": 800, "page": 720}
            
            if amount == "top":
                await browser.page.evaluate("window.scrollTo(0, 0)")
                image, summary = await _get_screenshot_with_summary()
                return f"Scrolled to top\n\n{summary}", image
            
            if amount == "bottom":
                await browser.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                image, summary = await _get_screenshot_with_summary()
                return f"Scrolled to bottom\n\n{summary}", image
            
            pixels = amount_map.get(amount)
            if pixels is None:
                try:
                    pixels = int(amount)
                except ValueError:
                    pixels = 400
            
            if direction == "up":
                await browser.page.evaluate(f"window.scrollBy(0, -{pixels})")
            elif direction == "down":
                await browser.page.evaluate(f"window.scrollBy(0, {pixels})")
            elif direction == "left":
                await browser.page.evaluate(f"window.scrollBy(-{pixels}, 0)")
            elif direction == "right":
                await browser.page.evaluate(f"window.scrollBy({pixels}, 0)")
            
            image, summary = await _get_screenshot_with_summary()
            return f"Scrolled {direction} by {pixels}px\n\n{summary}", image
            
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            raise RuntimeError(f"Scroll failed: {e}")
    
    logger.debug("Registered navigation tools")

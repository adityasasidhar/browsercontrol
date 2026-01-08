"""Content extraction tools for browser control."""

import logging
from fastmcp import FastMCP
from fastmcp.utilities.types import Image

from browsercontrol.browser import browser, get_element_map

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


def register_content_tools(mcp: FastMCP) -> None:
    """Register content extraction tools with the MCP server."""
    
    @mcp.tool()
    async def get_page_content() -> tuple[str, Image]:
        """Get the page content as markdown text."""
        try:
            await browser.ensure_started()
            from markdownify import markdownify
            
            html = await browser.page.content()
            markdown = markdownify(html, heading_style="ATX", strip=["script", "style"])
            
            if len(markdown) > 30000:
                markdown = markdown[:30000] + "\n\n... [content truncated]"
            
            image, summary = await _get_screenshot_with_summary()
            return f"{markdown}\n\n---\n{summary}", image
            
        except Exception as e:
            logger.error(f"Get page content failed: {e}")
            raise RuntimeError(f"Get page content failed: {e}")
    
    @mcp.tool()
    async def get_text(element_id: int) -> tuple[str, Image]:
        """
        Get the text content of an element by its ID.
        
        Args:
            element_id: The number label of the element
        """
        try:
            await browser.ensure_started()
            elem_map = get_element_map()
            
            if element_id not in elem_map:
                image, summary = await _get_screenshot_with_summary()
                return f"Error: Element {element_id} not found.\n\n{summary}", image
            
            elem = elem_map[element_id]
            text = elem.get("text", "")
            
            image, summary = await _get_screenshot_with_summary()
            return f"Element {element_id} text: {text}\n\n{summary}", image
            
        except Exception as e:
            logger.error(f"Get text failed: {e}")
            raise RuntimeError(f"Get text failed: {e}")
    
    @mcp.tool()
    async def get_page_info() -> tuple[str, Image]:
        """Get current page URL and title."""
        try:
            await browser.ensure_started()
            url = browser.page.url
            title = await browser.page.title()
            
            image, summary = await _get_screenshot_with_summary()
            return f"Title: {title}\nURL: {url}\n\n{summary}", image
            
        except Exception as e:
            logger.error(f"Get page info failed: {e}")
            raise RuntimeError(f"Get page info failed: {e}")
    
    @mcp.tool()
    async def run_javascript(script: str) -> tuple[str, Image]:
        """
        Execute JavaScript and return the result.
        
        Args:
            script: JavaScript code to execute
        """
        try:
            await browser.ensure_started()
            logger.info(f"Executing JavaScript: {script[:50]}...")
            result = await browser.page.evaluate(script)
            image, summary = await _get_screenshot_with_summary()
            return f"Result: {result}\n\n{summary}", image
            
        except Exception as e:
            logger.error(f"Run JavaScript failed: {e}")
            raise RuntimeError(f"Run JavaScript failed: {e}")
    
    @mcp.tool()
    async def screenshot(annotate: bool = True, full_page: bool = False) -> tuple[str, Image]:
        """
        Take a screenshot of the page.
        
        Args:
            annotate: If True, overlay numbered element markers (default). If False, clean screenshot.
            full_page: If True, capture the full scrollable page.
        """
        try:
            await browser.ensure_started()
            
            if annotate and not full_page:
                image, summary = await _get_screenshot_with_summary()
                return f"Screenshot captured (annotated)\n\n{summary}", image
            else:
                screenshot_bytes = await browser.page.screenshot(type="png", full_page=full_page)
                image = Image(data=screenshot_bytes, format="png")
                return "Screenshot captured (clean)", image
                
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            raise RuntimeError(f"Screenshot failed: {e}")
    
    logger.debug("Registered content tools")

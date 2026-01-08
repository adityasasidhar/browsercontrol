"""Interaction tools for browser control."""

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


def register_interaction_tools(mcp: FastMCP) -> None:
    """Register interaction tools with the MCP server."""
    
    @mcp.tool()
    async def click(element_id: int) -> tuple[str, Image]:
        """
        Click on an element by its ID number shown in the screenshot.
        
        Args:
            element_id: The number label shown on the element in the screenshot
        """
        try:
            await browser.ensure_started()
            elem_map = get_element_map()
            
            if element_id not in elem_map:
                image, summary = await _get_screenshot_with_summary()
                return f"Error: Element {element_id} not found. Valid IDs: {list(elem_map.keys())[:20]}\n\n{summary}", image
            
            elem = elem_map[element_id]
            logger.info(f"Clicking element {element_id}: {elem['tag']} - {elem.get('text', '')[:30]}")
            await browser.page.mouse.click(elem["centerX"], elem["centerY"])
            await browser.page.wait_for_timeout(500)
            
            image, summary = await _get_screenshot_with_summary()
            return f"Clicked element {element_id} ({elem['tag']}: {elem['text'][:30] if elem['text'] else 'no text'})\n\n{summary}", image
            
        except Exception as e:
            logger.error(f"Click failed: {e}")
            try:
                image, summary = await _get_screenshot_with_summary()
                return f"Error clicking element {element_id}: {e}\n\n{summary}", image
            except Exception:
                raise RuntimeError(f"Click failed: {e}")
    
    @mcp.tool()
    async def click_at(x: int, y: int) -> tuple[str, Image]:
        """
        Click at specific x,y coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        try:
            await browser.ensure_started()
            logger.info(f"Clicking at ({x}, {y})")
            await browser.page.mouse.click(x, y)
            await browser.page.wait_for_timeout(500)
            image, summary = await _get_screenshot_with_summary()
            return f"Clicked at ({x}, {y})\n\n{summary}", image
        except Exception as e:
            logger.error(f"Click at coordinates failed: {e}")
            raise RuntimeError(f"Click at ({x}, {y}) failed: {e}")
    
    @mcp.tool()
    async def type_text(element_id: int, text: str) -> tuple[str, Image]:
        """
        Type text into an input element by its ID number.
        
        Args:
            element_id: The number label shown on the element
            text: Text to type
        """
        try:
            await browser.ensure_started()
            elem_map = get_element_map()
            
            if element_id not in elem_map:
                image, summary = await _get_screenshot_with_summary()
                return f"Error: Element {element_id} not found.\n\n{summary}", image
            
            elem = elem_map[element_id]
            logger.info(f"Typing into element {element_id}")
            await browser.page.mouse.click(elem["centerX"], elem["centerY"])
            await browser.page.keyboard.press("Control+a")
            await browser.page.keyboard.type(text)
            
            image, summary = await _get_screenshot_with_summary()
            return f"Typed '{text}' into element {element_id}\n\n{summary}", image
            
        except Exception as e:
            logger.error(f"Type text failed: {e}")
            raise RuntimeError(f"Type text failed: {e}")
    
    @mcp.tool()
    async def press_key(key: str) -> tuple[str, Image]:
        """
        Press a keyboard key.
        
        Args:
            key: Key to press (e.g., "Enter", "Tab", "Escape", "ArrowDown", "Backspace")
        """
        try:
            await browser.ensure_started()
            logger.info(f"Pressing key: {key}")
            await browser.page.keyboard.press(key)
            await browser.page.wait_for_timeout(300)
            image, summary = await _get_screenshot_with_summary()
            return f"Pressed key '{key}'\n\n{summary}", image
        except Exception as e:
            logger.error(f"Press key failed: {e}")
            raise RuntimeError(f"Press key '{key}' failed: {e}")
    
    @mcp.tool()
    async def hover(element_id: int) -> tuple[str, Image]:
        """
        Hover over an element by its ID number.
        
        Args:
            element_id: The number label shown on the element
        """
        try:
            await browser.ensure_started()
            elem_map = get_element_map()
            
            if element_id not in elem_map:
                image, summary = await _get_screenshot_with_summary()
                return f"Error: Element {element_id} not found.\n\n{summary}", image
            
            elem = elem_map[element_id]
            logger.info(f"Hovering over element {element_id}")
            await browser.page.mouse.move(elem["centerX"], elem["centerY"])
            await browser.page.wait_for_timeout(300)
            
            image, summary = await _get_screenshot_with_summary()
            return f"Hovering over element {element_id}\n\n{summary}", image
            
        except Exception as e:
            logger.error(f"Hover failed: {e}")
            raise RuntimeError(f"Hover failed: {e}")
    
    @mcp.tool()
    async def scroll_to_element(element_id: int) -> tuple[str, Image]:
        """
        Scroll to bring an element into view.
        
        Args:
            element_id: The number label shown on the element
        """
        try:
            await browser.ensure_started()
            elem_map = get_element_map()
            
            if element_id not in elem_map:
                image, summary = await _get_screenshot_with_summary()
                return f"Error: Element {element_id} not found.\n\n{summary}", image
            
            elem = elem_map[element_id]
            await browser.page.evaluate(f"window.scrollTo(0, {elem['y'] - 100})")
            await browser.page.wait_for_timeout(300)
            
            image, summary = await _get_screenshot_with_summary()
            return f"Scrolled to element {element_id}\n\n{summary}", image
            
        except Exception as e:
            logger.error(f"Scroll to element failed: {e}")
            raise RuntimeError(f"Scroll to element failed: {e}")
    
    @mcp.tool()
    async def wait(seconds: float = 1.0) -> tuple[str, Image]:
        """
        Wait for a specified time (useful for pages with animations or loading).
        
        Args:
            seconds: Time to wait in seconds (default: 1.0)
        """
        try:
            await browser.ensure_started()
            await browser.page.wait_for_timeout(int(seconds * 1000))
            image, summary = await _get_screenshot_with_summary()
            return f"Waited {seconds}s\n\n{summary}", image
        except Exception as e:
            logger.error(f"Wait failed: {e}")
            raise RuntimeError(f"Wait failed: {e}")
    
    logger.debug("Registered interaction tools")

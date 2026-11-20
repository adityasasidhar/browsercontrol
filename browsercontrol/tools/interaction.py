import contextlib
import logging

from fastmcp import FastMCP
from fastmcp.utilities.types import Image
from playwright.async_api import Error as PlaywrightError

from browsercontrol.browser import browser
from browsercontrol.elements import ACTION_TIMEOUT_MS, ElementError
from browsercontrol.tools._summary import element_error_result, get_screenshot_with_summary

logger = logging.getLogger(__name__)


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
            try:
                locator = await browser.resolve_element(element_id)
            except ElementError as e:
                return await element_error_result(browser, e)

            elem = browser.get_element_map()[element_id]
            text = (elem.get("text") or "no text")[:30]
            logger.info(f"Clicking element {element_id}: {elem['tag']} - {text}")
            await locator.click(timeout=ACTION_TIMEOUT_MS)
            with contextlib.suppress(Exception):
                await browser.page.wait_for_load_state("domcontentloaded", timeout=3000)

            image, summary = await get_screenshot_with_summary(browser)
            return (
                f"Clicked element {element_id} ({elem['tag']}: {text})\n\n{summary}",
                image,
            )

        except Exception as e:
            logger.error(f"Click failed: {e}")
            try:
                image, summary = await get_screenshot_with_summary(browser)
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
            with contextlib.suppress(Exception):
                await browser.page.wait_for_load_state("domcontentloaded", timeout=3000)
            image, summary = await get_screenshot_with_summary(browser)
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
            try:
                locator = await browser.resolve_element(element_id)
            except ElementError as e:
                return await element_error_result(browser, e)

            logger.info(f"Typing into element {element_id}")
            try:
                await locator.fill(text, timeout=ACTION_TIMEOUT_MS)
            except PlaywrightError:
                # Not fillable (e.g. a custom widget): focus it by clicking, then type.
                await locator.click(timeout=ACTION_TIMEOUT_MS)
                await browser.page.keyboard.type(text)

            image, summary = await get_screenshot_with_summary(browser)
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
            with contextlib.suppress(Exception):
                await browser.page.wait_for_load_state("domcontentloaded", timeout=3000)
            image, summary = await get_screenshot_with_summary(browser)
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
            try:
                locator = await browser.resolve_element(element_id)
            except ElementError as e:
                return await element_error_result(browser, e)

            logger.info(f"Hovering over element {element_id}")
            await locator.hover(timeout=ACTION_TIMEOUT_MS)
            await browser.page.wait_for_timeout(300)

            image, summary = await get_screenshot_with_summary(browser)
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
            try:
                locator = await browser.resolve_element(element_id)
            except ElementError as e:
                return await element_error_result(browser, e)

            await locator.evaluate("el => el.scrollIntoView({block: 'center', inline: 'nearest'})")
            await browser.page.wait_for_timeout(300)

            image, summary = await get_screenshot_with_summary(browser)
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
            image, summary = await get_screenshot_with_summary(browser)
            return f"Waited {seconds}s\n\n{summary}", image
        except Exception as e:
            logger.error(f"Wait failed: {e}")
            raise RuntimeError(f"Wait failed: {e}")

    logger.debug("Registered interaction tools")

import logging

from fastmcp import FastMCP
from fastmcp.utilities.types import Image

from browsercontrol.browser import browser
from browsercontrol.elements import ElementError, strip_marks
from browsercontrol.pointer import HIDE_POINTER_STYLE
from browsercontrol.tools._summary import get_screenshot_with_summary

logger = logging.getLogger(__name__)

MAX_TEXT_CHARS = 10_000

# Form fields report their value; everything else its rendered text.
READ_TEXT_JS = """
(el) => {
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(el.tagName)) return String(el.value ?? '');
    return (el.innerText || el.textContent || '').trim();
}
"""


def register_content_tools(mcp: FastMCP) -> None:
    """Register content extraction tools with the MCP server."""

    @mcp.tool()
    async def get_page_content() -> tuple[str, Image]:
        """Get the page content as markdown text."""
        try:
            await browser.ensure_started()
            from markdownify import markdownify

            html = strip_marks(await browser.page.content())
            markdown = markdownify(html, heading_style="ATX", strip=["script", "style"])

            if len(markdown) > 30000:
                markdown = markdown[:30000] + "\n\n... [content truncated]"

            image, summary = await get_screenshot_with_summary(browser)
            return f"{markdown}\n\n---\n{summary}", image

        except Exception as e:
            logger.error(f"Get page content failed: {e}")
            raise RuntimeError(f"Get page content failed: {e}")

    @mcp.tool()
    async def get_text(element_id: int) -> str:
        """
        Get the full, current text of an element by its ID.

        Reads the live page, so it returns the whole text (not the truncated
        label from the summary). Form fields return their current value.

        Args:
            element_id: The number label of the element
        """
        try:
            await browser.ensure_started()
            try:
                locator = await browser.resolve_element(element_id)
            except ElementError as e:
                return f"Error: {e}"

            text = await locator.evaluate(READ_TEXT_JS)
            if len(text) > MAX_TEXT_CHARS:
                text = text[:MAX_TEXT_CHARS] + "\n... [text truncated]"
            return f"Element {element_id} text: {text}"

        except Exception as e:
            logger.error(f"Get text failed: {e}")
            raise RuntimeError(f"Get text failed: {e}")

    @mcp.tool()
    async def get_page_info() -> str:
        """Get current page URL and title."""
        try:
            await browser.ensure_started()
            url = browser.page.url
            title = await browser.page.title()

            return f"Title: {title}\nURL: {url}"

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
            image, summary = await get_screenshot_with_summary(browser)
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

            if annotate and full_page:
                # Annotation not supported for full page, fallback to clean
                screenshot_bytes = await browser.page.screenshot(
                    type="png", full_page=True, style=HIDE_POINTER_STYLE
                )
                image = Image(data=screenshot_bytes, format="png")
                return (
                    "Screenshot captured (clean) - Note: Annotation disabled for full-page screenshot.",
                    image,
                )

            elif annotate:
                image, summary = await get_screenshot_with_summary(browser)
                return f"Screenshot captured (annotated)\n\n{summary}", image
            else:
                screenshot_bytes = await browser.page.screenshot(
                    type="png", full_page=full_page, style=HIDE_POINTER_STYLE
                )
                image = Image(data=screenshot_bytes, format="png")
                return "Screenshot captured (clean)", image

        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            raise RuntimeError(f"Screenshot failed: {e}")

    logger.debug("Registered content tools")

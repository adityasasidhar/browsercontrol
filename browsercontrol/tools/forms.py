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
        desc = elem.get("text", "")[:40] if elem.get("text") else elem.get("tag", "unknown")
        summary_lines.append(f"  [{eid}] {elem.get('tag', 'unknown')} - {desc}")

    if len(elem_map) > 30:
        summary_lines.append(f"  ... and {len(elem_map) - 30} more")

    return image, "\n".join(summary_lines)


def register_form_tools(mcp: FastMCP) -> None:
    """Register form tools with the MCP server."""

    @mcp.tool()
    async def select_option(element_id: int, option: str) -> tuple[str, Image]:
        """
        Select an option from a dropdown by element ID.

        Args:
            element_id: The number label of the select element
            option: The value or visible text of the option to select
        """
        try:
            await browser.ensure_started()
            elem_map = get_element_map()

            if element_id not in elem_map:
                image, summary = await _get_screenshot_with_summary()
                return f"Error: Element {element_id} not found.\n\n{summary}", image

            elem = elem_map[element_id]
            logger.info(f"Selecting option '{option}' from element {element_id}")

            handle = await browser.page.evaluate_handle(
                f"document.elementFromPoint({elem['centerX']}, {elem['centerY']})"
            )
            element = handle.as_element()
            if element:
                await element.scroll_into_view_if_needed()
                await element.click()
            else:
                await browser.page.mouse.click(elem["centerX"], elem["centerY"])  # fallback
            await browser.page.wait_for_timeout(200)

            try:
                await browser.page.get_by_text(option).click(timeout=3000)
            except Exception:
                await browser.page.keyboard.type(option)
                await browser.page.keyboard.press("Enter")

            image, summary = await _get_screenshot_with_summary()
            return f"Selected '{option}' from element {element_id}\n\n{summary}", image

        except Exception as e:
            logger.error(f"Select option failed: {e}")
            raise RuntimeError(f"Select option failed: {e}")

    @mcp.tool()
    async def check_checkbox(element_id: int, check: bool = True) -> tuple[str, Image]:
        """
        Check or uncheck a checkbox by element ID.

        Args:
            element_id: The number label of the checkbox
            check: True to check, False to uncheck
        """
        try:
            await browser.ensure_started()
            elem_map = get_element_map()

            if element_id not in elem_map:
                image, summary = await _get_screenshot_with_summary()
                return f"Error: Element {element_id} not found.\n\n{summary}", image

            elem = elem_map[element_id]
            logger.info(f"{'Checking' if check else 'Unchecking'} element {element_id}")
            handle = await browser.page.evaluate_handle(
                f"document.elementFromPoint({elem['centerX']}, {elem['centerY']})"
            )
            element = handle.as_element()
            if element:
                await element.scroll_into_view_if_needed()
                await element.click()
            else:
                await browser.page.mouse.click(elem["centerX"], elem["centerY"])  # fallback

            image, summary = await _get_screenshot_with_summary()
            action = "Checked" if check else "Toggled"
            return f"{action} element {element_id}\n\n{summary}", image

        except Exception as e:
            logger.error(f"Check checkbox failed: {e}")
            raise RuntimeError(f"Check checkbox failed: {e}")

    @mcp.tool()
    async def upload_file(element_id: int, file_path: str) -> tuple[str, Image]:
        """
        Upload a file to a file input element.

        Args:
            element_id: The number label of the file input
            file_path: The absolute path to the file to upload
        """
        try:
            import pathlib

            path = pathlib.Path(file_path)
            if not path.exists():
                raise ValueError(f"File not found: {file_path}")

            await browser.ensure_started()
            elem_map = get_element_map()

            if element_id not in elem_map:
                image, summary = await _get_screenshot_with_summary()
                return f"Error: Element {element_id} not found.\n\n{summary}", image

            elem = elem_map[element_id]
            logger.info(f"Uploading file '{file_path}' to element {element_id}")

            # Get element handle via coordinates
            handle = await browser.page.evaluate_handle(
                f"document.elementFromPoint({elem['centerX']}, {elem['centerY']})"
            )

            # Ensure it's an element handle
            elem_handle = handle.as_element()
            if elem_handle is None:
                raise RuntimeError(f"Could not find DOM element at ID {element_id}")

            await elem_handle.set_input_files(str(path))

            image, summary = await _get_screenshot_with_summary()
            return f"Uploaded '{path.name}' to element {element_id}\n\n{summary}", image

        except Exception as e:
            logger.error(f"Upload file failed: {e}")
            raise RuntimeError(f"Upload file failed: {e}")

    logger.debug("Registered form tools")

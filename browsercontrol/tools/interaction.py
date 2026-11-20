import json
import logging

from fastmcp import FastMCP
from fastmcp.utilities.types import Image

from browsercontrol.browser import browser
from browsercontrol.elements import ACTION_TIMEOUT_MS, ElementError
from browsercontrol.tools._summary import (
    disabled_result,
    element_error_result,
    get_screenshot_with_summary,
)

logger = logging.getLogger(__name__)

NON_TEXT_INPUT_TYPES = (
    "checkbox",
    "radio",
    "button",
    "submit",
    "reset",
    "file",
    "image",
    "range",
    "color",
    "hidden",
)

# How type_text should enter text: "fill" for native fields and contenteditable,
# "custom" for widgets that only declare a text role, "none" for everything else.
EDIT_KIND_JS = (
    """
el => {
    const NON_TEXT = """
    + json.dumps(NON_TEXT_INPUT_TYPES)
    + """;
    const tag = el.tagName;
    if (tag === 'TEXTAREA' || el.isContentEditable) return 'fill';
    if (tag === 'INPUT') {
        return NON_TEXT.includes((el.type || 'text').toLowerCase()) ? 'none' : 'fill';
    }
    const role = (el.getAttribute('role') || '').toLowerCase();
    return ['textbox', 'searchbox', 'combobox'].includes(role) ? 'custom' : 'none';
}
"""
)

# True when keyboard focus (in the element's own document, through shadow roots)
# sits in something that accepts typed text.
FOCUS_IS_EDITABLE_JS = """
el => {
    let a = el.ownerDocument.activeElement;
    while (a && a.shadowRoot && a.shadowRoot.activeElement) a = a.shadowRoot.activeElement;
    return !!a && (a.isContentEditable || a.tagName === 'TEXTAREA' || a.tagName === 'INPUT');
}
"""


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

            if await locator.is_disabled():
                return await disabled_result(browser, element_id, "clicked")

            elem = browser.get_element_map()[element_id]
            text = (elem.get("text") or "no text")[:30]
            logger.info(f"Clicking element {element_id}: {elem['tag']} - {text}")
            target = await browser.codegen_target(locator)
            await locator.click(timeout=ACTION_TIMEOUT_MS)
            browser.log_action("click", target)
            await browser.settle()

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
            await browser.settle()
            image, summary = await get_screenshot_with_summary(browser)
            return f"Clicked at ({x}, {y})\n\n{summary}", image
        except Exception as e:
            logger.error(f"Click at coordinates failed: {e}")
            raise RuntimeError(f"Click at ({x}, {y}) failed: {e}")

    @mcp.tool()
    async def type_text(element_id: int, text: str) -> tuple[str, Image]:
        """
        Type text into a text field by its ID number, replacing what it holds.

        Works on text inputs, textareas, contenteditable regions, and widgets with
        role=textbox/searchbox/combobox. Checkboxes, buttons, dropdowns and file
        inputs are refused; use check_checkbox, click, select_option or upload_file.

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

            if await locator.is_disabled():
                return await disabled_result(browser, element_id, "typed into")

            logger.info(f"Typing into element {element_id}")
            target = await browser.codegen_target(locator)
            kind = await locator.evaluate(EDIT_KIND_JS)
            if kind == "fill":
                await locator.fill(text, timeout=ACTION_TIMEOUT_MS)
            elif kind == "custom":
                # A widget that only declares a text role: focus it by clicking,
                # then replace whatever it holds, as fill() would.
                await locator.click(timeout=ACTION_TIMEOUT_MS)
                if not await locator.evaluate(FOCUS_IS_EDITABLE_JS):
                    raise ValueError(
                        f"Clicking element {element_id} did not focus a text field, "
                        "so nothing was typed."
                    )
                await browser.page.keyboard.press("ControlOrMeta+a")
                await browser.page.keyboard.type(text)
            else:
                elem = browser.get_element_map().get(element_id, {})
                raise ValueError(
                    f"Element {element_id} ({elem.get('tag', 'element')}"
                    f"[{elem.get('type', '')}]) is not a text field. Use click, "
                    "check_checkbox, select_option, or upload_file for it instead."
                )

            browser.log_action("fill", target, text=text)
            image, summary = await get_screenshot_with_summary(browser)
            return f"Typed '{text}' into element {element_id}\n\n{summary}", image

        except Exception as e:
            logger.error(f"Type text failed: {e}")
            raise RuntimeError(f"Type text failed: {e}")

    @mcp.tool()
    async def press_key(key: str) -> tuple[str, Image]:
        """
        Press a keyboard key or key combination on the focused element.

        Args:
            key: Key to press (e.g., "Enter", "Tab", "Escape", "ArrowDown", "Backspace"),
                 or a combination joined with "+" (e.g., "Control+A", "Shift+Tab",
                 "ControlOrMeta+C" for copy on any OS, "Control+Shift+T")
        """
        try:
            await browser.ensure_started()
            logger.info(f"Pressing key: {key}")
            await browser.page.keyboard.press(key)
            await browser.settle()
            browser.log_action("press", key=key)
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
            target = await browser.codegen_target(locator)
            await locator.hover(timeout=ACTION_TIMEOUT_MS)
            browser.log_action("hover", target)
            await browser.page.wait_for_timeout(300)

            image, summary = await get_screenshot_with_summary(browser)
            return f"Hovering over element {element_id}\n\n{summary}", image

        except Exception as e:
            logger.error(f"Hover failed: {e}")
            raise RuntimeError(f"Hover failed: {e}")

    async def _click_variant(
        element_id: int, verb: str, button: str, click_count: int
    ) -> tuple[str, Image]:
        await browser.ensure_started()
        try:
            locator = await browser.resolve_element(element_id)
        except ElementError as e:
            return await element_error_result(browser, e)
        if await locator.is_disabled():
            return await disabled_result(browser, element_id, verb)

        logger.info(f"{verb.capitalize()} element {element_id}")
        target = await browser.codegen_target(locator)
        await locator.click(
            button=button,  # type: ignore[arg-type]
            click_count=click_count,
            timeout=ACTION_TIMEOUT_MS,
        )
        browser.log_action("click", target, button=button, click_count=click_count)
        await browser.settle()
        image, summary = await get_screenshot_with_summary(browser)
        return f"{verb.capitalize()} element {element_id}\n\n{summary}", image

    @mcp.tool()
    async def double_click(element_id: int) -> tuple[str, Image]:
        """
        Double-click an element by its ID number (e.g. to open an item or select a word).

        Args:
            element_id: The number label shown on the element in the screenshot
        """
        try:
            return await _click_variant(element_id, "double-clicked", "left", 2)
        except Exception as e:
            logger.error(f"Double click failed: {e}")
            raise RuntimeError(f"Double click failed: {e}")

    @mcp.tool()
    async def right_click(element_id: int) -> tuple[str, Image]:
        """
        Right-click an element by its ID number to open its context menu.

        Args:
            element_id: The number label shown on the element in the screenshot
        """
        try:
            return await _click_variant(element_id, "right-clicked", "right", 1)
        except Exception as e:
            logger.error(f"Right click failed: {e}")
            raise RuntimeError(f"Right click failed: {e}")

    @mcp.tool()
    async def drag(source_id: int, target_id: int) -> tuple[str, Image]:
        """
        Drag one element and drop it onto another (sortable lists, kanban cards, sliders).

        Both IDs come from the same, latest screenshot.

        Args:
            source_id: The number label of the element to drag
            target_id: The number label of the element to drop onto
        """
        try:
            await browser.ensure_started()
            try:
                source = await browser.resolve_element(source_id)
                dest = await browser.resolve_element(target_id)
            except ElementError as e:
                return await element_error_result(browser, e)

            logger.info(f"Dragging element {source_id} onto element {target_id}")
            source_desc = await browser.codegen_target(source)
            dest_desc = await browser.codegen_target(dest)
            await source.drag_to(dest, timeout=ACTION_TIMEOUT_MS)
            browser.log_action("drag", source_desc, dest=dest_desc)
            await browser.settle()

            image, summary = await get_screenshot_with_summary(browser)
            return f"Dragged element {source_id} onto element {target_id}\n\n{summary}", image
        except Exception as e:
            logger.error(f"Drag failed: {e}")
            raise RuntimeError(f"Drag failed: {e}")

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
            browser.log_action("wait", ms=int(seconds * 1000))
            image, summary = await get_screenshot_with_summary(browser)
            return f"Waited {seconds}s\n\n{summary}", image
        except Exception as e:
            logger.error(f"Wait failed: {e}")
            raise RuntimeError(f"Wait failed: {e}")

    logger.debug("Registered interaction tools")

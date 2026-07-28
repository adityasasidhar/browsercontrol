import logging
from typing import Any

from fastmcp import FastMCP
from fastmcp.utilities.types import Image
from playwright.async_api import ElementHandle

from browsercontrol.browser import browser, get_element_map

logger = logging.getLogger(__name__)


async def _resolve_element(elem: dict[str, Any], element_id: int) -> ElementHandle:
    """Resolve the DOM element sitting at a mapped element's center point."""
    handle = await browser.page.evaluate_handle(
        f"document.elementFromPoint({elem['centerX']}, {elem['centerY']})"
    )
    element = handle.as_element()
    if element is None:
        raise RuntimeError(f"Could not find DOM element at ID {element_id}")
    return element


async def _get_screenshot_with_summary() -> tuple[Image, str]:
    """Helper to get annotated screenshot with element summary."""
    screenshot_bytes, elem_map = await browser.screenshot_with_som()
    image = Image(data=screenshot_bytes, format="png")

    summary_lines = [f"Found {len(elem_map)} interactive elements:"]
    for eid, elem in list(elem_map.items())[:30]:
        tag = elem.get("tag", "unknown")
        elem_type = elem.get("type", "")
        # Show the input type so checkboxes, radios and file inputs are
        # distinguishable instead of all rendering as a bare "input".
        label = f"{tag}[{elem_type}]" if elem_type and elem_type != tag else tag
        # Collapse whitespace so multi-line text (e.g. a <select>'s options)
        # cannot break the one-line-per-element format.
        text = " ".join((elem.get("text") or "").split())[:40]
        summary_lines.append(f"  [{eid}] {label} - {text}" if text else f"  [{eid}] {label}")

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

            element = await _resolve_element(elem, element_id)

            tag = await element.evaluate("el => el.tagName.toLowerCase()")
            if tag != "select":
                raise ValueError(
                    f"Element {element_id} is a <{tag}>, not a <select>. "
                    "select_option only works on dropdowns."
                )

            # Match against the dropdown's own options rather than page-wide text,
            # so a miss can never click an unrelated element elsewhere on the page.
            options = await element.evaluate(
                "el => Array.from(el.options).map(o => ({value: o.value, label: o.label || o.text}))"
            )
            match = next(
                (o for o in options if option in (o["value"], o["label"])),
                None,
            )
            if match is None:
                available = ", ".join(f"{o['label']!r} (value={o['value']!r})" for o in options)
                raise ValueError(
                    f"Element {element_id} has no option matching {option!r}. "
                    f"Available options: {available or '(none)'}"
                )

            await element.scroll_into_view_if_needed()
            await element.select_option(value=match["value"])

            selected = await element.evaluate("el => el.value")
            image, summary = await _get_screenshot_with_summary()
            return (
                f"Selected {match['label']!r} from element {element_id} "
                f"(value is now {selected!r})\n\n{summary}",
                image,
            )

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

            element = await _resolve_element(elem, element_id)

            input_type = await element.evaluate(
                "el => el.tagName.toLowerCase() === 'input' ? (el.type || '').toLowerCase() : ''"
            )
            if input_type not in ("checkbox", "radio"):
                raise ValueError(
                    f"Element {element_id} is not a checkbox or radio button. "
                    "check_checkbox only works on those inputs."
                )
            if not check and input_type == "radio":
                raise ValueError(
                    f"Element {element_id} is a radio button, which cannot be unchecked. "
                    "Select a different radio in the group instead."
                )

            await element.scroll_into_view_if_needed()
            # check()/uncheck() are idempotent state setters, unlike a raw click.
            if check:
                await element.check()
            else:
                await element.uncheck()

            is_checked = await element.evaluate("el => el.checked")
            image, summary = await _get_screenshot_with_summary()
            action = "Checked" if check else "Unchecked"
            return (
                f"{action} element {element_id} (checked is now {is_checked})\n\n{summary}",
                image,
            )

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

            elem_handle = await _resolve_element(elem, element_id)
            await elem_handle.set_input_files(str(path))

            image, summary = await _get_screenshot_with_summary()
            return f"Uploaded '{path.name}' to element {element_id}\n\n{summary}", image

        except Exception as e:
            logger.error(f"Upload file failed: {e}")
            raise RuntimeError(f"Upload file failed: {e}")

    logger.debug("Registered form tools")

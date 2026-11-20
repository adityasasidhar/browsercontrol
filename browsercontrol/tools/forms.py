import logging

from fastmcp import FastMCP
from fastmcp.utilities.types import Image

from browsercontrol.browser import browser
from browsercontrol.elements import ACTION_TIMEOUT_MS, ElementError
from browsercontrol.tools._summary import element_error_result, get_screenshot_with_summary

logger = logging.getLogger(__name__)


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
            try:
                element = await browser.resolve_element(element_id)
            except ElementError as e:
                return await element_error_result(browser, e)

            logger.info(f"Selecting option '{option}' from element {element_id}")

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

            await element.select_option(value=match["value"], timeout=ACTION_TIMEOUT_MS)

            selected = await element.evaluate("el => el.value")
            image, summary = await get_screenshot_with_summary(browser)
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
            try:
                element = await browser.resolve_element(element_id)
            except ElementError as e:
                return await element_error_result(browser, e)

            logger.info(f"{'Checking' if check else 'Unchecking'} element {element_id}")

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

            # check()/uncheck() are idempotent state setters, unlike a raw click.
            # force skips the hit-test, since sites often hide the real input under
            # a styled stand-in that would otherwise "intercept" the click.
            if check:
                await element.check(timeout=ACTION_TIMEOUT_MS, force=True)
            else:
                await element.uncheck(timeout=ACTION_TIMEOUT_MS, force=True)

            is_checked = await element.evaluate("el => el.checked")
            image, summary = await get_screenshot_with_summary(browser)
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
            try:
                element = await browser.resolve_element(element_id)
            except ElementError as e:
                return await element_error_result(browser, e)

            logger.info(f"Uploading file '{file_path}' to element {element_id}")

            await element.set_input_files(str(path), timeout=ACTION_TIMEOUT_MS)

            image, summary = await get_screenshot_with_summary(browser)
            return f"Uploaded '{path.name}' to element {element_id}\n\n{summary}", image

        except Exception as e:
            logger.error(f"Upload file failed: {e}")
            raise RuntimeError(f"Upload file failed: {e}")

    logger.debug("Registered form tools")

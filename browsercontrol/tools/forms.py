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

# What a real click at the input's centre would hit: "self" (the input or one of
# its labels), "standin" (a styled replacement right next to it), or "covered"
# (something unrelated, such as a modal, sits on top).
CHECK_HIT_JS = """
el => {
    const parentOf = (n) =>
        n.parentElement || (n.parentNode instanceof ShadowRoot ? n.parentNode.host : null);
    const contains = (a, n) => {
        for (let c = n; c; c = c instanceof ShadowRoot ? c.host : (c.assignedSlot || c.parentNode)) {
            if (c === a) return true;
        }
        return false;
    };
    const r = el.getBoundingClientRect();
    const root = el.getRootNode();
    const probe = typeof root.elementFromPoint === 'function' ? root : document;
    const hit = probe.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
    if (!hit) return 'covered';
    if (contains(el, hit)) return 'self';
    if (Array.from(el.labels || []).some((l) => contains(l, hit))) return 'self';
    let anc = el;
    for (let i = 0; i < 3; i++) {
        const up = parentOf(anc);
        if (!up || up === document.body || up === document.documentElement) break;
        anc = up;
    }
    return anc !== el && contains(anc, hit) ? 'standin' : 'covered';
}
"""


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

            if await element.is_disabled():
                return await disabled_result(browser, element_id, "changed")

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

            target = await browser.codegen_target(element)
            await element.select_option(value=match["value"], timeout=ACTION_TIMEOUT_MS)
            browser.log_action("select", target, option=match["value"])

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
        Check or uncheck a checkbox (or select a radio button) by element ID.

        Idempotent: it sets the state rather than toggling. Works on inputs hidden
        under a styled replacement, but refuses one covered by a dialog or banner.

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

            if await element.is_disabled():
                return await disabled_result(browser, element_id, "changed")

            await element.scroll_into_view_if_needed(timeout=ACTION_TIMEOUT_MS)
            target = await browser.codegen_target(element)
            hit = await element.evaluate(CHECK_HIT_JS)
            if hit == "self":
                # check()/uncheck() are idempotent state setters, unlike a raw click.
                if check:
                    await element.check(timeout=ACTION_TIMEOUT_MS)
                else:
                    await element.uncheck(timeout=ACTION_TIMEOUT_MS)
            elif hit == "standin":
                # The real input is hidden under a styled replacement, so a mouse
                # click would land on the replacement. Click the input directly,
                # only when its state needs to change, so it stays idempotent.
                if await element.evaluate("el => el.checked") != check:
                    await element.dispatch_event("click")
            else:
                raise ValueError(
                    f"Element {element_id} is covered by another element (for example a "
                    "dialog or banner). Close or dismiss it first."
                )

            is_checked = await element.evaluate("el => el.checked")
            if is_checked != check:
                raise ValueError(
                    f"Element {element_id} did not change: checked is still {is_checked}. "
                    "The page may be preventing the change."
                )
            browser.log_action("check", target, checked=check)
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

            target = await browser.codegen_target(element)
            await element.set_input_files(str(path), timeout=ACTION_TIMEOUT_MS)
            browser.log_action("upload", target, path=str(path))

            image, summary = await get_screenshot_with_summary(browser)
            return f"Uploaded '{path.name}' to element {element_id}\n\n{summary}", image

        except Exception as e:
            logger.error(f"Upload file failed: {e}")
            raise RuntimeError(f"Upload file failed: {e}")

    logger.debug("Registered form tools")

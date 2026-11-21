"""act(): run several steps in one call and return a single screenshot."""

import logging
from typing import Any

from fastmcp import FastMCP
from fastmcp.utilities.types import Image

from browsercontrol.browser import browser
from browsercontrol.elements import ACTION_TIMEOUT_MS
from browsercontrol.pointer import track_pointer
from browsercontrol.tools._summary import get_screenshot_with_summary
from browsercontrol.tools.interaction import EDIT_KIND_JS

logger = logging.getLogger(__name__)

MAX_STEPS = 25
SCROLL_AMOUNTS = {"small": 100, "medium": 400, "large": 800, "page": 720}

STEP_ACTIONS = (
    "click",
    "double_click",
    "right_click",
    "hover",
    "type",
    "press",
    "select",
    "check",
    "drag",
    "scroll",
    "navigate",
    "wait",
    "wait_for",
)


def _need(step: dict[str, Any], key: str) -> Any:
    if step.get(key) is None:
        raise ValueError(f"'{step.get('action')}' needs '{key}'")
    return step[key]


async def _run_step(step: dict[str, Any]) -> str:
    """Execute one step against the current page. Raises on failure."""
    action = step.get("action")
    page = browser.page

    if action == "navigate":
        url = _need(step, "url")
        await page.goto(url, wait_until="domcontentloaded")
        await browser.settle()
        browser.log_action("navigate", url=url)
        return f"navigated to {url}"
    if action == "press":
        key = _need(step, "key")
        await page.keyboard.press(key)
        await browser.settle(1500)
        browser.log_action("press", key=key)
        return f"pressed {key}"
    if action == "wait":
        ms = int(float(step.get("seconds", 1)) * 1000)
        await page.wait_for_timeout(ms)
        browser.log_action("wait", ms=ms)
        return f"waited {ms}ms"
    if action == "wait_for":
        timeout = int(float(step.get("timeout_seconds", 10)) * 1000)
        if step.get("text"):
            await page.get_by_text(step["text"]).first.wait_for(timeout=timeout)
            browser.log_action("wait_for_text", text=step["text"])
            return f"saw text {step['text']!r}"
        selector = _need(step, "selector")
        await page.locator(selector).first.wait_for(timeout=timeout)
        return f"saw selector {selector!r}"
    if action == "scroll":
        direction = step.get("direction", "down")
        amount = step.get("amount", "medium")
        pixels = SCROLL_AMOUNTS.get(str(amount)) or int(amount)
        dx = {"left": -pixels, "right": pixels}.get(direction, 0)
        dy = {"up": -pixels, "down": pixels}.get(direction, 0)
        await page.evaluate("([x, y]) => window.scrollBy(x, y)", [dx, dy])
        browser.log_action("scroll", dx=dx, dy=dy)
        return f"scrolled {direction} {pixels}px"

    element_id = int(_need(step, "element_id"))
    locator = await browser.resolve_element(element_id)
    target = await browser.codegen_target(locator)

    if action in ("click", "double_click", "right_click"):
        if await locator.is_disabled():
            raise ValueError(f"element {element_id} is disabled")
        button = "right" if action == "right_click" else "left"
        count = 2 if action == "double_click" else 1
        async with track_pointer(page):
            await locator.click(
                button=button,  # type: ignore[arg-type]
                click_count=count,
                timeout=ACTION_TIMEOUT_MS,
            )
        browser.log_action("click", target, button=button, click_count=count)
        await browser.settle(1500)
        return f"{action.replace('_', '-')}ed [{element_id}]"
    if action == "hover":
        async with track_pointer(page):
            await locator.hover(timeout=ACTION_TIMEOUT_MS)
        browser.log_action("hover", target)
        return f"hovered [{element_id}]"
    if action == "type":
        text = str(_need(step, "text"))
        if await locator.evaluate(EDIT_KIND_JS) == "none":
            raise ValueError(f"element {element_id} is not a text field")
        await locator.fill(text, timeout=ACTION_TIMEOUT_MS)
        browser.log_action("fill", target, text=text)
        shown = "*" * len(text) if target and target.get("password") else repr(text)
        return f"typed {shown} into [{element_id}]"
    if action == "select":
        option = str(_need(step, "option"))
        await locator.select_option(option, timeout=ACTION_TIMEOUT_MS)
        browser.log_action("select", target, option=option)
        return f"selected {option!r} in [{element_id}]"
    if action == "check":
        checked = bool(step.get("checked", True))
        async with track_pointer(page):
            await locator.set_checked(checked, timeout=ACTION_TIMEOUT_MS)
        browser.log_action("check", target, checked=checked)
        return f"{'checked' if checked else 'unchecked'} [{element_id}]"
    if action == "drag":
        target_id = int(_need(step, "target_id"))
        dest = await browser.resolve_element(target_id)
        dest_desc = await browser.codegen_target(dest)
        async with track_pointer(page):
            await locator.drag_to(dest, timeout=ACTION_TIMEOUT_MS)
        browser.log_action("drag", target, dest=dest_desc)
        await browser.settle(1500)
        return f"dragged [{element_id}] onto [{target_id}]"
    raise ValueError(f"unknown action {action!r}; use one of: {', '.join(STEP_ACTIONS)}")


def register_batch_tools(mcp: FastMCP) -> None:
    """Register the act batching tool with the MCP server."""

    @mcp.tool()
    async def act(steps: list[dict[str, Any]], stop_on_error: bool = True) -> tuple[str, Image]:
        """
        Run several steps in one call and return one screenshot at the end.

        Element IDs all refer to the screenshot taken BEFORE this call. A step whose
        element was removed or replaced (e.g. after navigation) fails as stale, so
        batch steps on the current page and navigate last.

        Each step is an object with "action" plus its fields:
          {"action": "click"|"double_click"|"right_click"|"hover", "element_id": 3}
          {"action": "type", "element_id": 4, "text": "hello"}
          {"action": "select", "element_id": 5, "option": "Canada"}
          {"action": "check", "element_id": 6, "checked": true}
          {"action": "drag", "element_id": 7, "target_id": 8}
          {"action": "press", "key": "Enter"}
          {"action": "scroll", "direction": "down", "amount": "medium"}
          {"action": "navigate", "url": "https://example.com"}
          {"action": "wait", "seconds": 1}
          {"action": "wait_for", "text": "Saved"}  (or "selector")

        Args:
            steps: The steps to run in order (at most 25)
            stop_on_error: Stop at the first failing step (default True)
        """
        try:
            await browser.ensure_started()
            if not steps:
                raise ValueError("steps is empty")
            if len(steps) > MAX_STEPS:
                raise ValueError(f"at most {MAX_STEPS} steps per call")

            lines: list[str] = []
            failed = ran = 0
            for index, step in enumerate(steps, start=1):
                ran = index
                try:
                    result = await _run_step(step)
                    lines.append(f"  {index}. ok: {result}")
                except Exception as e:
                    failed += 1
                    lines.append(f"  {index}. FAILED ({step.get('action')}): {e}")
                    if stop_on_error:
                        skipped = len(steps) - index
                        if skipped:
                            lines.append(f"  ... {skipped} remaining step(s) skipped")
                        break

            header = f"Ran {ran} of {len(steps)} step(s), {failed} failed:"
            image, summary = await get_screenshot_with_summary(browser)
            return header + "\n" + "\n".join(lines) + f"\n\n{summary}", image
        except Exception as e:
            logger.error(f"act failed: {e}")
            raise RuntimeError(f"act failed: {e}")

    logger.debug("Registered batch tools")

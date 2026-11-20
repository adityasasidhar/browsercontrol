"""Waiting for page conditions, answering JS dialogs, and listing downloads."""

import logging

from fastmcp import FastMCP
from fastmcp.utilities.types import Image
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from browsercontrol.browser import browser
from browsercontrol.tools._summary import get_screenshot_with_summary

logger = logging.getLogger(__name__)

WAIT_STATES = ("visible", "hidden", "attached", "detached")


def register_waiting_tools(mcp: FastMCP) -> None:
    """Register wait, dialog, and download tools with the MCP server."""

    @mcp.tool()
    async def wait_for(
        text: str | None = None,
        selector: str | None = None,
        state: str = "visible",
        network_idle: bool = False,
        timeout_seconds: float = 10.0,
    ) -> tuple[str, Image]:
        """
        Wait until a condition holds instead of sleeping a fixed time.

        Give text, a CSS selector, and/or network_idle. With none, it waits for the
        page to settle (load, network quiet, DOM quiet). Returns the screenshot
        either way and says whether the wait timed out.

        Args:
            text: Wait for an element containing this text
            selector: Wait for an element matching this CSS selector
            state: "visible" (default), "hidden", "attached", or "detached"
            network_idle: Also wait until no request has been in flight for 500ms
            timeout_seconds: Give up after this long (default 10)
        """
        try:
            await browser.ensure_started()
            if state not in WAIT_STATES:
                raise ValueError(f"state must be one of {', '.join(WAIT_STATES)}")
            timeout_ms = int(timeout_seconds * 1000)
            page = browser.page
            waited: list[str] = []
            timed_out: list[str] = []

            for label, locator in (
                (f"text {text!r}", page.get_by_text(text).first if text else None),
                (f"selector {selector!r}", page.locator(selector).first if selector else None),
            ):
                if locator is None:
                    continue
                waited.append(f"{label} to be {state}")
                try:
                    await locator.wait_for(state=state, timeout=timeout_ms)  # type: ignore[arg-type]
                except PlaywrightTimeoutError:
                    timed_out.append(label)

            if network_idle:
                waited.append("network idle")
                if not await browser.wait_for_network_idle(timeout_ms):
                    timed_out.append("network idle")

            if not waited:
                waited.append("the page to settle")
                await browser.settle(timeout_ms)

            if text and state == "visible" and f"text {text!r}" not in timed_out:
                browser.log_action("wait_for_text", text=text)

            image, summary = await get_screenshot_with_summary(browser)
            if timed_out:
                status = f"Timed out after {timeout_seconds}s waiting for {', '.join(timed_out)}"
            else:
                status = f"Done waiting for {', '.join(waited)}"
            return f"{status}\n\n{summary}", image
        except Exception as e:
            logger.error(f"Wait for failed: {e}")
            raise RuntimeError(f"Wait for failed: {e}")

    @mcp.tool()
    async def handle_dialog(accept: bool = True, prompt_text: str | None = None) -> str:
        """
        Choose how to answer the next JS dialog (alert, confirm, prompt, beforeunload).

        Call it before the action that opens the dialog. Without it, confirms and
        prompts are dismissed and alerts acknowledged; either way the next
        screenshot's text reports the dialog and how it was answered.

        Args:
            accept: True to press OK, False to press Cancel
            prompt_text: Text to enter into a prompt() dialog (only used when accepting)
        """
        await browser.ensure_started()
        browser.session.dialog_policy = {"accept": accept, "prompt_text": prompt_text}
        browser.log_action("dialog", accept=accept, prompt_text=prompt_text)
        answer = "accept" if accept else "dismiss"
        if accept and prompt_text is not None:
            answer += f" with {prompt_text!r}"
        recent = browser.session.dialogs[-5:]
        lines = [f"The next JS dialog will be answered: {answer}."]
        if recent:
            lines.append("Recent dialogs:")
            lines += [f"  {d['type']}: {d['message'][:100]!r} -> {d['outcome']}" for d in recent]
        return "\n".join(lines)

    @mcp.tool()
    async def list_downloads() -> str:
        """List files downloaded in this session, with where they were saved."""
        await browser.ensure_started()
        downloads = browser.session.downloads
        if not downloads:
            return "No downloads yet. Clicking a download link saves the file automatically."
        lines = ["Downloads:"]
        lines += [f"  {d['filename']} -> {d['path']} (from {d['url'][:100]})" for d in downloads]
        return "\n".join(lines)

    logger.debug("Registered waiting tools")

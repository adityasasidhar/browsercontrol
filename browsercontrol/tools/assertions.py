"""Verification tools: check text, URL, and field values, and record passing checks.

Each passing check is logged to the session's action log, so ``export_test``
turns it into an ``expect()`` line in the generated Playwright test.
"""

import logging

from fastmcp import FastMCP

from browsercontrol.browser import browser
from browsercontrol.elements import ElementError
from browsercontrol.session import url_matches

logger = logging.getLogger(__name__)


def register_assertion_tools(mcp: FastMCP) -> None:
    """Register verify_text, verify_url, and verify_value with the MCP server."""

    @mcp.tool()
    async def verify_text(text: str, element_id: int | None = None, present: bool = True) -> str:
        """
        Check that text is (or is not) on the page, or inside one element.

        Returns "PASS: ..." or "FAIL: ...". A passing check is recorded, so
        export_test turns it into an expect() assertion.

        Args:
            text: The text to look for
            element_id: Only look inside this element's text (from the latest screenshot)
            present: False to check that the text is NOT there
        """
        try:
            await browser.ensure_started()
            target = None
            if element_id is None:
                found = await browser.page.get_by_text(text).first.is_visible()
                where = "on the page"
            else:
                try:
                    locator = await browser.resolve_element(element_id)
                except ElementError as e:
                    return f"Error: {e}"
                inner = await locator.inner_text()
                found = text in inner
                where = f"in element {element_id}"
            ok = found == present
            expectation = "visible" if element_id is None else "contained"
            state = f"{text!r} is {'' if found else 'not '}{expectation} {where}"
            if not ok:
                return f"FAIL: {state}"
            if element_id is not None:
                target = await browser.codegen_target(locator)
            browser.log_action("assert_text", target, text=text, present=present)
            return f"PASS: {state}"
        except Exception as e:
            logger.error(f"verify_text failed: {e}")
            return f"Error verifying text: {e}"

    @mcp.tool()
    async def verify_url(pattern: str) -> str:
        """
        Check that the current URL matches a pattern.

        Returns "PASS: ..." or "FAIL: ...". A passing check is recorded, so
        export_test turns it into an expect(page).to_have_url() assertion.

        Args:
            pattern: A plain substring, a glob with * or ?, or "re:<regex>"
        """
        try:
            await browser.ensure_started()
            url = browser.page.url
            if not url_matches(pattern, url):
                return f"FAIL: URL {url} does not match {pattern!r}"
            browser.log_action("assert_url", pattern=pattern)
            return f"PASS: URL {url} matches {pattern!r}"
        except Exception as e:
            logger.error(f"verify_url failed: {e}")
            return f"Error verifying URL: {e}"

    @mcp.tool()
    async def verify_value(element_id: int, expected: str) -> str:
        """
        Check that an input, textarea, or select has exactly the expected value.

        Returns "PASS: ..." or "FAIL: ...". A passing check is recorded, so
        export_test turns it into an expect().to_have_value() assertion.

        Args:
            element_id: The field's number from the latest screenshot
            expected: The value the field should hold
        """
        try:
            await browser.ensure_started()
            try:
                locator = await browser.resolve_element(element_id)
            except ElementError as e:
                return f"Error: {e}"
            actual = await locator.input_value()
            if actual != expected:
                return f"FAIL: element {element_id} has value {actual!r}, expected {expected!r}"
            target = await browser.codegen_target(locator)
            browser.log_action("assert_value", target, text=expected)
            return f"PASS: element {element_id} has value {expected!r}"
        except Exception as e:
            logger.error(f"verify_value failed: {e}")
            return f"Error verifying value: {e}"

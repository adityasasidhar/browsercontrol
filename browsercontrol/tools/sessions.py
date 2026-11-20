"""Isolated sessions and attaching to the user's own Chrome over CDP."""

import logging

from fastmcp import FastMCP
from fastmcp.utilities.types import Image

from browsercontrol.browser import browser
from browsercontrol.tools._summary import get_screenshot_with_summary

logger = logging.getLogger(__name__)

CDP_HELP = (
    "Start Chrome with remote debugging first, e.g.\n"
    '  google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-agent"\n'
    "(Chrome 136+ ignores the flag on the default profile, so use a dedicated "
    "--user-data-dir and sign in there once.)"
)


def register_session_tools(mcp: FastMCP) -> None:
    """Register session and CDP tools with the MCP server."""

    @mcp.tool()
    async def create_session(
        name: str, device: str | None = None, url: str | None = None
    ) -> tuple[str, Image]:
        """
        Open an isolated browser session (its own cookies, storage, tabs) and switch to it.

        Use it to log in as a second user, test signed-out flows, or keep agents
        apart. The session is in memory only and is lost when closed.

        Args:
            name: A name for the session, used by switch_session and close_session
            device: Optional device to emulate for the whole session (see list_devices)
            url: Optional URL to open in the session
        """
        try:
            session = await browser.create_session(name, device)
            if url and session.page is not None:
                await session.page.goto(url, wait_until="domcontentloaded")
                browser.log_action("navigate", url=url)
                await browser.settle()
            image, summary = await get_screenshot_with_summary(browser)
            extra = f" emulating {device}" if device else ""
            return (
                f"Created isolated session {name!r}{extra} and switched to it\n\n{summary}",
                image,
            )
        except Exception as e:
            logger.error(f"Create session failed: {e}")
            raise RuntimeError(f"Create session failed: {e}")

    @mcp.tool()
    async def switch_session(name: str) -> tuple[str, Image]:
        """
        Switch to another session. "default" is the persistent, logged-in profile.

        Args:
            name: The session name (see list_sessions)
        """
        try:
            await browser.ensure_started()
            browser.bind(name)
            image, summary = await get_screenshot_with_summary(browser)
            return f"Switched to session {name!r}\n\n{summary}", image
        except Exception as e:
            logger.error(f"Switch session failed: {e}")
            raise RuntimeError(f"Switch session failed: {e}")

    @mcp.tool()
    async def list_sessions() -> str:
        """List browser sessions, their tabs, and which one you are using."""
        await browser.ensure_started()
        lines = ["Sessions:"]
        for s in browser.list_sessions():
            kind = "isolated" if s["isolated"] else "persistent profile"
            if not s["isolated"] and browser.cdp_url:
                kind = f"attached Chrome at {browser.cdp_url}"
            marker = "  <- current" if s["current"] else ""
            lines.append(f"  {s['name']} ({kind}, {s['tabs']} tab(s)) {s['url']}{marker}")
        return "\n".join(lines)

    @mcp.tool()
    async def close_session(name: str) -> str:
        """
        Close an isolated session and discard its cookies and tabs.

        Args:
            name: The session to close (the default session cannot be closed)
        """
        try:
            await browser.close_session(name)
            return f"Closed session {name!r}. Now using {browser.session.name!r}."
        except Exception as e:
            logger.error(f"Close session failed: {e}")
            raise RuntimeError(f"Close session failed: {e}")

    @mcp.tool()
    async def connect_to_chrome(cdp_url: str = "http://localhost:9222") -> tuple[str, Image]:
        """
        Attach to your own running Chrome so the agent uses its logged-in sessions.

        The agent works in a new tab of that Chrome; list_tabs/switch_tab reach the
        others. Disconnecting never closes your Chrome. Isolated sessions created
        afterwards open as incognito-like contexts in it.

        Args:
            cdp_url: Chrome's remote debugging endpoint (default http://localhost:9222)
        """
        try:
            await browser.connect_over_cdp(cdp_url)
        except Exception as e:
            logger.error(f"Connect to Chrome failed: {e}")
            raise RuntimeError(f"Could not attach to Chrome at {cdp_url}: {e}\n\n{CDP_HELP}")
        image, summary = await get_screenshot_with_summary(browser)
        return f"Attached to Chrome at {cdp_url}\n\n{summary}", image

    @mcp.tool()
    async def disconnect_chrome() -> tuple[str, Image]:
        """Detach from an attached Chrome (leaving it open) and go back to the managed browser."""
        try:
            if browser.cdp_url is None:
                await browser.ensure_started()
                note = "Not attached to Chrome; using the managed browser."
            else:
                await browser.connect_over_cdp(None)
                note = "Detached from Chrome (it is still running); using the managed browser."
            image, summary = await get_screenshot_with_summary(browser)
            return f"{note}\n\n{summary}", image
        except Exception as e:
            logger.error(f"Disconnect Chrome failed: {e}")
            raise RuntimeError(f"Disconnect Chrome failed: {e}")

    logger.debug("Registered session tools")

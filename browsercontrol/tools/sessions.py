"""Isolated sessions and attaching to the user's own Chrome over CDP."""

import json
import logging
import os
import re
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.utilities.types import Image

from browsercontrol.browser import browser
from browsercontrol.config import config
from browsercontrol.navigation_policy import check_navigation_allowed
from browsercontrol.tools._summary import get_screenshot_with_summary

logger = logging.getLogger(__name__)

CDP_HELP = (
    "Start Chrome with remote debugging first, e.g.\n"
    '  google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-agent"\n'
    "(Chrome 136+ ignores the flag on the default profile, so use a dedicated "
    "--user-data-dir and sign in there once.)"
)

_AUTH_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")


def auth_state_path(name: str) -> Path:
    """The file for a saved auth state. Names are plain words, never paths."""
    if not _AUTH_NAME.fullmatch(name) or ".." in name:
        raise ValueError(
            f"Invalid auth state name {name!r}: use letters, digits, '.', '_' or '-' "
            "(up to 64 characters)"
        )
    return config.auth_dir / f"{name}.json"


def saved_auth_states() -> list[str]:
    if not config.auth_dir.is_dir():
        return []
    return sorted(p.stem for p in config.auth_dir.glob("*.json"))


def register_session_tools(mcp: FastMCP) -> None:
    """Register session and CDP tools with the MCP server."""

    @mcp.tool()
    async def create_session(
        name: str,
        device: str | None = None,
        url: str | None = None,
        auth_state: str | None = None,
    ) -> tuple[str, Image]:
        """
        Open an isolated browser session (its own cookies, storage, tabs) and switch to it.

        Use it to log in as a second user, test signed-out flows, or keep agents
        apart. The session is in memory only and is lost when closed. Pass
        auth_state to start it already signed in from a save_auth_state file.

        Args:
            name: A name for the session, used by switch_session and close_session
            device: Optional device to emulate for the whole session (see list_devices)
            url: Optional URL to open in the session
            auth_state: Optional saved login state to load (see list_auth_states)
        """
        try:
            if url:
                check_navigation_allowed(url)
            state_file = None
            if auth_state:
                state_file = auth_state_path(auth_state)
                if not state_file.is_file():
                    saved = ", ".join(saved_auth_states()) or "none"
                    raise ValueError(f"No saved auth state {auth_state!r}. Saved: {saved}")
            session = await browser.create_session(name, device, state_file)
            if url and session.page is not None:
                await session.page.goto(url, wait_until="domcontentloaded")
                browser.log_action("navigate", url=url)
                await browser.settle()
            image, summary = await get_screenshot_with_summary(browser)
            extra = f" emulating {device}" if device else ""
            if auth_state:
                extra += f" with auth state {auth_state!r}"
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
    async def save_auth_state(name: str) -> str:
        """
        Save the current session's login state (cookies, localStorage, IndexedDB) to a file.

        Log in once, save it, then start isolated sessions already signed in with
        create_session(name, auth_state=...). The file holds session tokens: treat
        it like a password. Saving again under the same name overwrites it.

        Args:
            name: A name for the saved state (letters, digits, '.', '_', '-')
        """
        try:
            path = auth_state_path(name)
            await browser.ensure_started()
            context = browser.session.context
            if context is None:
                raise RuntimeError("The current session has no browser context")
            path.parent.mkdir(parents=True, exist_ok=True)
            state = await context.storage_state(indexed_db=True)
            # Owner-only permissions: the file is as sensitive as the logins it holds.
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
            cookies = len(state.get("cookies", []))
            origins = [o["origin"] for o in state.get("origins", [])]
            shown = ", ".join(origins[:5]) + (", ..." if len(origins) > 5 else "")
            return (
                f"Saved auth state {name!r} to {path}\n"
                f"  {cookies} cookie(s); storage for {len(origins)} origin(s)"
                + (f": {shown}" if origins else "")
                + f"\nLoad it with create_session(name, auth_state={name!r})."
            )
        except Exception as e:
            logger.error(f"Save auth state failed: {e}")
            raise RuntimeError(f"Save auth state failed: {e}")

    @mcp.tool()
    async def list_auth_states() -> str:
        """List login states saved with save_auth_state."""
        names = saved_auth_states()
        if not names:
            return f"No saved auth states in {config.auth_dir}."
        lines = [f"Saved auth states ({config.auth_dir}):"]
        for name in names:
            try:
                state = json.loads((config.auth_dir / f"{name}.json").read_text("utf-8"))
                cookies = len(state.get("cookies", []))
                origins = len(state.get("origins", []))
                lines.append(f"  {name} ({cookies} cookie(s), {origins} origin(s))")
            except (OSError, ValueError):
                lines.append(f"  {name} (unreadable)")
        return "\n".join(lines)

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

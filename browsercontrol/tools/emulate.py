"""Emulation tools: devices, geolocation, timezone, color scheme, network throttling.

Settings apply to every open tab of the caller's session and are re-applied to
tabs opened later. reset_emulation() undoes all of them.
"""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from fastmcp import FastMCP
from fastmcp.utilities.types import Image
from playwright.async_api import Page

from browsercontrol import emulation
from browsercontrol.browser import browser
from browsercontrol.tools._summary import get_screenshot_with_summary

logger = logging.getLogger(__name__)

NETWORK_CHOICES = (*emulation.NETWORK_PROFILES, "offline", "none")


async def _each_tab(apply: Callable[[Page], Awaitable[None]]) -> None:
    """Apply a setting to every open tab of the caller's session."""
    context = browser.page.context
    for page in context.pages:
        if not page.is_closed():
            await apply(page)


def register_emulation_tools(mcp: FastMCP) -> None:
    """Register emulation tools with the MCP server."""

    @mcp.tool()
    async def list_devices(contains: str = "") -> str:
        """
        List device names accepted by emulate_device and create_session.

        Args:
            contains: Only names containing this (case-insensitive), e.g. "iphone"
        """
        await browser.ensure_started()
        names = sorted(n for n in browser.devices() if contains.lower() in n.lower())
        if not names:
            return f"No devices match {contains!r}."
        return f"{len(names)} device(s):\n" + "\n".join(f"  {n}" for n in names)

    @mcp.tool()
    async def emulate_device(name: str) -> tuple[str, Image]:
        """
        Emulate a phone or tablet's screen size, user agent, and touch input.

        Pass "none" to go back to the desktop viewport. Pixel ratio and the mobile
        layout viewport need a new context: use create_session(name, device) for a
        fully faithful device.

        Args:
            name: A device from list_devices(), e.g. "iPhone 13" or "Pixel 7"
        """
        try:
            await browser.ensure_started()
            if name.lower() in ("", "none", "desktop"):
                descriptor: dict[str, Any] | None = None
                browser.session.emulation.pop("device", None)
            else:
                descriptor = browser.device_descriptor(name)
                browser.session.emulation["device"] = descriptor

            async def apply(page: Page) -> None:
                await emulation.apply_device(page, descriptor)

            await _each_tab(apply)
            await browser.page.reload()
            await browser.settle()
            image, summary = await get_screenshot_with_summary(browser)
            what = f"Emulating {name}" if descriptor else "Device emulation cleared"
            return f"{what} (page reloaded)\n\n{summary}", image
        except Exception as e:
            logger.error(f"Emulate device failed: {e}")
            raise RuntimeError(f"Emulate device failed: {e}")

    @mcp.tool()
    async def set_geolocation(latitude: float, longitude: float, accuracy: float = 10.0) -> str:
        """
        Report a fake location to sites, and grant them the geolocation permission.

        Args:
            latitude: Latitude in degrees, e.g. 51.5074
            longitude: Longitude in degrees, e.g. -0.1278
            accuracy: Accuracy radius in meters (default 10)
        """
        try:
            await browser.ensure_started()
            context = browser.page.context
            await context.grant_permissions(["geolocation"])
            await context.set_geolocation(
                {"latitude": latitude, "longitude": longitude, "accuracy": accuracy}
            )
            browser.session.emulation["geolocation"] = (latitude, longitude, accuracy)
            return f"Geolocation set to {latitude}, {longitude} (±{accuracy}m)."
        except Exception as e:
            logger.error(f"Set geolocation failed: {e}")
            raise RuntimeError(f"Set geolocation failed: {e}")

    @mcp.tool()
    async def set_timezone(timezone_id: str) -> str:
        """
        Make pages see a different timezone (Date, Intl).

        Args:
            timezone_id: IANA name such as "America/New_York" or "Asia/Tokyo"; "" resets
        """
        try:
            await browser.ensure_started()
            if timezone_id:
                browser.session.emulation["timezone"] = timezone_id
            else:
                browser.session.emulation.pop("timezone", None)

            async def apply(page: Page) -> None:
                await emulation.apply_timezone(page, timezone_id or None)

            await _each_tab(apply)
            return f"Timezone set to {timezone_id}." if timezone_id else "Timezone reset."
        except Exception as e:
            logger.error(f"Set timezone failed: {e}")
            raise RuntimeError(f"Set timezone failed: {e}")

    @mcp.tool()
    async def set_color_scheme(scheme: str = "dark") -> tuple[str, Image]:
        """
        Emulate prefers-color-scheme to check dark or light mode.

        Args:
            scheme: "dark", "light", or "no-preference"
        """
        try:
            await browser.ensure_started()
            if scheme not in emulation.COLOR_SCHEMES:
                raise ValueError(f"scheme must be one of {', '.join(emulation.COLOR_SCHEMES)}")
            browser.session.emulation["color_scheme"] = scheme

            async def apply(page: Page) -> None:
                await page.emulate_media(color_scheme=scheme)  # type: ignore[arg-type]

            await _each_tab(apply)
            await browser.settle(1000)
            image, summary = await get_screenshot_with_summary(browser)
            return f"Color scheme set to {scheme}\n\n{summary}", image
        except Exception as e:
            logger.error(f"Set color scheme failed: {e}")
            raise RuntimeError(f"Set color scheme failed: {e}")

    @mcp.tool()
    async def throttle_network(profile: str = "slow-3g") -> str:
        """
        Slow the network down or take it offline, to test loading and offline states.

        Args:
            profile: "slow-3g", "fast-3g", "4g", "offline", or "none" to remove throttling
        """
        try:
            await browser.ensure_started()
            if profile not in NETWORK_CHOICES:
                raise ValueError(f"profile must be one of {', '.join(NETWORK_CHOICES)}")
            context = browser.page.context
            await context.set_offline(profile == "offline")
            speed = profile if profile in emulation.NETWORK_PROFILES else None
            if speed:
                browser.session.emulation["network"] = speed
            else:
                browser.session.emulation.pop("network", None)

            async def apply(page: Page) -> None:
                await emulation.apply_network(page, speed)

            # Offline is Playwright's; a CDP "no throttling" call would turn it back on.
            if profile != "offline":
                await _each_tab(apply)
            if profile == "offline":
                return "Network is offline. throttle_network('none') restores it."
            return "Network throttling removed." if not speed else f"Network throttled to {speed}."
        except Exception as e:
            logger.error(f"Throttle network failed: {e}")
            raise RuntimeError(f"Throttle network failed: {e}")

    @mcp.tool()
    async def reset_emulation() -> tuple[str, Image]:
        """Undo all emulation: device, geolocation, timezone, color scheme, and throttling."""
        try:
            await browser.ensure_started()
            context = browser.page.context
            browser.session.emulation.clear()
            await context.clear_permissions()
            await context.set_offline(False)

            async def apply(page: Page) -> None:
                await emulation.apply_device(page, None)
                await emulation.apply_timezone(page, None)
                await emulation.apply_network(page, None)
                await page.emulate_media(color_scheme=None)

            await _each_tab(apply)
            await browser.page.reload()
            await browser.settle()
            image, summary = await get_screenshot_with_summary(browser)
            return f"Emulation reset (page reloaded)\n\n{summary}", image
        except Exception as e:
            logger.error(f"Reset emulation failed: {e}")
            raise RuntimeError(f"Reset emulation failed: {e}")

    logger.debug("Registered emulation tools")

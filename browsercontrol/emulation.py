"""Emulation applied to a page: device metrics, timezone, color scheme, throttling.

Settings are stored on the session and re-applied to every new tab it opens.
User agent, touch, timezone, and throttling go through a CDP session because
Playwright only sets them when a context is created; screen size uses
Playwright's viewport and color scheme ``page.emulate_media``. Geolocation and offline mode are context
wide and set directly by the tools.
"""

import logging
from typing import Any

from playwright.async_api import CDPSession, Page

from browsercontrol.config import config

logger = logging.getLogger(__name__)

# Chrome DevTools' presets. Throughput is bytes per second, latency in ms.
NETWORK_PROFILES: dict[str, dict[str, float]] = {
    "slow-3g": {"latency": 2000, "download": 50_000, "upload": 50_000},
    "fast-3g": {"latency": 563, "download": 180_000, "upload": 84_375},
    "4g": {"latency": 170, "download": 1_500_000, "upload": 750_000},
}

COLOR_SCHEMES = ("dark", "light", "no-preference")

_cdp_sessions: dict[Page, CDPSession] = {}


async def cdp(page: Page) -> CDPSession:
    """A CDP session for ``page``, created once and reused."""
    for stale in [p for p in _cdp_sessions if p.is_closed()]:
        _cdp_sessions.pop(stale, None)
    session = _cdp_sessions.get(page)
    if session is None:
        session = await page.context.new_cdp_session(page)
        _cdp_sessions[page] = session
    return session


async def apply_device(page: Page, device: dict[str, Any] | None) -> None:
    """Emulate a device's screen size, user agent, and touch; None restores the desktop.

    The size goes through Playwright's viewport, not CDP device metrics: Playwright
    re-applies its own viewport on every screenshot, which would undo a CDP
    override. Pixel ratio and the mobile layout viewport can only be set when a
    context is created (create_session with a device).
    """
    client = await cdp(page)
    if device is None:
        await page.set_viewport_size(
            {"width": config.viewport_width, "height": config.viewport_height}
        )
        await client.send("Emulation.setTouchEmulationEnabled", {"enabled": False})
        # An empty user agent removes the override.
        await client.send("Emulation.setUserAgentOverride", {"userAgent": ""})
        return
    await page.set_viewport_size(device["viewport"])
    await client.send(
        "Emulation.setTouchEmulationEnabled",
        {"enabled": bool(device.get("has_touch")), "maxTouchPoints": 5},
    )
    if device.get("user_agent"):
        await client.send("Emulation.setUserAgentOverride", {"userAgent": device["user_agent"]})


async def apply_timezone(page: Page, timezone_id: str | None) -> None:
    client = await cdp(page)
    # An empty timezoneId restores the host's timezone.
    await client.send("Emulation.setTimezoneOverride", {"timezoneId": timezone_id or ""})


async def apply_network(page: Page, profile: str | None) -> None:
    """Throttle with a named profile from NETWORK_PROFILES, or remove throttling when None."""
    client = await cdp(page)
    await client.send("Network.enable")
    conditions = NETWORK_PROFILES.get(profile or "")
    await client.send(
        "Network.emulateNetworkConditions",
        {
            "offline": False,
            "latency": conditions["latency"] if conditions else 0,
            "downloadThroughput": conditions["download"] if conditions else -1,
            "uploadThroughput": conditions["upload"] if conditions else -1,
        },
    )


async def apply_emulation(page: Page, settings: dict[str, Any]) -> None:
    """Apply every stored emulation setting to a page (used for newly opened tabs)."""
    try:
        if "device" in settings:
            await apply_device(page, settings["device"])
        if "timezone" in settings:
            await apply_timezone(page, settings["timezone"])
        if "network" in settings:
            await apply_network(page, settings["network"])
        if "color_scheme" in settings:
            await page.emulate_media(color_scheme=settings["color_scheme"])
    except Exception as e:
        logger.debug(f"Applying emulation to a new tab failed: {e}")

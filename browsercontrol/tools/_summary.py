"""Annotated screenshot + element summary shared by every tool module."""

from typing import Any

from fastmcp.utilities.types import Image

from browsercontrol.browser import BrowserManager
from browsercontrol.elements import ElementError

MAX_SUMMARY_ELEMENTS = 30


def format_element_summary(elem_map: dict[int, dict[str, Any]]) -> str:
    """Render the element map as one line per element, capped at MAX_SUMMARY_ELEMENTS."""
    summary_lines = [f"Found {len(elem_map)} interactive elements:"]
    for eid, elem in list(elem_map.items())[:MAX_SUMMARY_ELEMENTS]:
        tag = elem.get("tag", "unknown")
        elem_type = elem.get("type", "")
        # Show the input type so checkboxes, radios and file inputs are
        # distinguishable instead of all rendering as a bare "input".
        label = f"{tag}[{elem_type}]" if elem_type and elem_type != tag else tag
        # Collapse whitespace so multi-line text (e.g. a <select>'s options)
        # cannot break the one-line-per-element format.
        text = " ".join((elem.get("text") or "").split())[:40]
        if elem.get("disabled"):
            label += " (disabled)"
        summary_lines.append(f"  [{eid}] {label} - {text}" if text else f"  [{eid}] {label}")

    if len(elem_map) > MAX_SUMMARY_ELEMENTS:
        summary_lines.append(f"  ... and {len(elem_map) - MAX_SUMMARY_ELEMENTS} more")

    return "\n".join(summary_lines)


async def get_screenshot_with_summary(manager: BrowserManager) -> tuple[Image, str]:
    """Take an annotated SoM screenshot and summarize its elements.

    The manager is passed in (rather than imported here) so each tool module
    uses its own ``browser`` reference, which is what tests patch.
    """
    screenshot_bytes, elem_map = await manager.screenshot_with_som()
    image = Image(data=screenshot_bytes, format="png")
    summary = format_element_summary(elem_map)
    # Dialogs and downloads happen outside any tool's view; report them here so
    # the agent learns about them with its next screenshot.
    notices = manager.drain_notices()
    if isinstance(notices, list) and notices:
        summary = "\n".join(f"Notice: {n}" for n in notices) + "\n\n" + summary
    return image, summary


async def element_error_result(manager: BrowserManager, error: ElementError) -> tuple[str, Image]:
    """Report an unknown or stale element ID alongside a fresh screenshot to retry from."""
    image, summary = await get_screenshot_with_summary(manager)
    return f"Error: {error}\n\n{summary}", image


async def disabled_result(
    manager: BrowserManager, element_id: int, action: str
) -> tuple[str, Image]:
    """Report that an element is disabled instead of waiting out the action timeout on it."""
    image, summary = await get_screenshot_with_summary(manager)
    return (
        f"Error: element {element_id} is disabled, so it cannot be {action}. "
        "It may need other input first (for example a required form field).\n\n"
        f"{summary}",
        image,
    )

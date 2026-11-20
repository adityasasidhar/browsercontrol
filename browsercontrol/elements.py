"""Set of Marks element collection and resolution.

Collection runs inside every frame of the page (cross-origin frames included,
via Playwright's ``page.frames``), recurses into open shadow roots, and tags each
kept element with a ``data-bc-id`` attribute. Resolution later finds the element
again by that attribute through a frame-scoped locator, which pierces shadow DOM,
so an action reaches the element that was numbered rather than whatever happens
to sit at its old screen position.
"""

import logging
from typing import Any

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Frame, Locator, Page

logger = logging.getLogger(__name__)

ATTR = "data-bc-id"

# A box that drifts further than this between screenshot and action counts as moved.
MOVE_TOLERANCE_PX = 3.0

# Upper bound for one element action, so an overlay that appears after the
# screenshot fails fast instead of waiting out Playwright's 30s default.
ACTION_TIMEOUT_MS = 10_000

ElementMap = dict[int, dict[str, Any]]

# Runs inside one frame. Takes a ref prefix, returns that frame's viewport size
# and the visible, unobscured interactive elements in frame-local coordinates.
COLLECT_JS = """
(prefix) => {
    const ATTR = 'data-bc-id';
    const SELECTOR = [
        'a[href]', 'button', 'input:not([type="hidden"])', 'select', 'textarea', 'summary',
        '[role="button"]', '[role="link"]', '[role="menuitem"]', '[role="tab"]',
        '[role="checkbox"]', '[role="radio"]', '[role="switch"]', '[role="option"]',
        '[role="combobox"]', '[role="textbox"]', '[onclick]',
        '[tabindex]:not([tabindex="-1"])', 'label[for]',
        '[contenteditable=""]', '[contenteditable="true"]'
    ].join(',');
    const SKIP = new Set(['HTML', 'HEAD', 'BODY', 'SCRIPT', 'STYLE', 'META', 'LINK',
                          'NOSCRIPT', 'TEMPLATE', 'TITLE', 'BR']);
    // Inputs that sites routinely make transparent and cover with a styled
    // stand-in; they still work through check()/set_input_files().
    const TRANSPARENT_OK = new Set(['checkbox', 'radio', 'file']);
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const out = [];
    let n = 0;

    const parentOf = (el) =>
        el.parentElement || (el.parentNode instanceof ShadowRoot ? el.parentNode.host : null);

    function isCandidate(el) {
        if (el.matches(SELECTOR)) return true;
        // Framework click handlers leave no attribute behind. A pointer cursor that
        // starts on this element, rather than being inherited, marks a clickable root.
        if (getComputedStyle(el).cursor !== 'pointer') return false;
        const parent = parentOf(el);
        return !parent || getComputedStyle(parent).cursor !== 'pointer';
    }

    const isTransparentOk = (el) =>
        el.tagName === 'INPUT' && TRANSPARENT_OK.has((el.type || '').toLowerCase());

    function isRendered(el, rect, transparentOk) {
        if (rect.width < 1 || rect.height < 1) return false;
        if (rect.bottom <= 0 || rect.right <= 0 || rect.top >= vh || rect.left >= vw) return false;
        if (typeof el.checkVisibility === 'function') {
            return el.checkVisibility({visibilityProperty: true, opacityProperty: !transparentOk});
        }
        const style = getComputedStyle(el);
        if (style.visibility === 'hidden' || style.visibility === 'collapse') return false;
        return transparentOk || style.opacity !== '0';
    }

    // Flat-tree containment: follows slots and shadow hosts, unlike Node.contains.
    function composedContains(el, node) {
        for (let cur = node; cur; cur = cur instanceof ShadowRoot ? cur.host : (cur.assignedSlot || cur.parentNode)) {
            if (cur === el) return true;
        }
        return false;
    }

    function isUnobscured(el, rect) {
        const root = el.getRootNode();
        const probe = typeof root.elementFromPoint === 'function' ? root : document;
        const l = Math.max(rect.left, 0), r = Math.min(rect.right, vw);
        const t = Math.max(rect.top, 0), b = Math.min(rect.bottom, vh);
        const ix = Math.min(4, (r - l) / 4), iy = Math.min(4, (b - t) / 4);
        const points = [[(l + r) / 2, (t + b) / 2], [l + ix, t + iy], [r - ix, t + iy],
                        [l + ix, b - iy], [r - ix, b - iy]];
        for (const [x, y] of points) {
            const hit = probe.elementFromPoint(x, y);
            if (hit && composedContains(el, hit)) return true;
        }
        return false;
    }

    function describe(el, rect, ref) {
        const text = (el.innerText || '').trim().substring(0, 80);
        const className = typeof el.className === 'string' ? el.className : el.getAttribute('class');
        return {
            ref: ref,
            x: rect.left, y: rect.top, width: rect.width, height: rect.height,
            tag: el.tagName.toLowerCase(),
            type: el.type || el.tagName.toLowerCase(),
            text: text || el.placeholder || el.getAttribute('aria-label') || el.title || '',
            href: el.href || '',
            id: el.id || null,
            className: className || null,
            disabled: el.matches(':disabled') || el.getAttribute('aria-disabled') === 'true'
        };
    }

    function consider(el) {
        if (SKIP.has(el.tagName) || !isCandidate(el)) return;
        const rect = el.getBoundingClientRect();
        const transparentOk = isTransparentOk(el);
        if (!isRendered(el, rect, transparentOk)) return;
        if (!transparentOk && !isUnobscured(el, rect)) return;
        n += 1;
        const ref = prefix + '-' + n;
        el.setAttribute(ATTR, ref);
        out.push(describe(el, rect, ref));
    }

    function walk(root) {
        for (const el of root.querySelectorAll('*')) {
            if (el.hasAttribute(ATTR)) el.removeAttribute(ATTR);
            consider(el);
            if (el.shadowRoot) walk(el.shadowRoot);
        }
    }

    walk(document);
    return {vw: vw, vh: vh, elements: out};
}
"""

# Runs in the parent frame on an <iframe>: border + padding before its content box.
FRAME_INSET_JS = """
(el) => {
    const s = getComputedStyle(el);
    return [el.clientLeft + parseFloat(s.paddingLeft || '0'),
            el.clientTop + parseFloat(s.paddingTop || '0')];
}
"""


class ElementError(Exception):
    """An element ID could not be turned into a live element."""


class ElementNotFoundError(ElementError):
    """The ID is not in the current page's element map."""

    def __init__(self, element_id: int, valid_ids: list[int]) -> None:
        super().__init__(f"Element {element_id} not found. Valid IDs: {valid_ids[:20]}")


class StaleElementError(ElementError):
    """The ID was valid for the last screenshot, but the page has changed since."""

    def __init__(self, element_id: int, reason: str) -> None:
        super().__init__(
            f"Element {element_id} is stale ({reason}). "
            "The page changed since the last screenshot; use the IDs in the fresh one below."
        )


async def _frame_offset(frame: Frame) -> tuple[float, float] | None:
    """Return where a frame's content box starts in main-viewport coordinates.

    None means the frame is not displayed (or vanished mid-collection) and should be skipped.
    """
    if frame.parent_frame is None:
        return (0.0, 0.0)
    try:
        owner = await frame.frame_element()
        box = await owner.bounding_box()
        if box is None or box["width"] < 1 or box["height"] < 1:
            return None
        inset_x, inset_y = await owner.evaluate(FRAME_INSET_JS)
    except PlaywrightError as e:
        logger.debug(f"Skipping frame {frame.url}: {e}")
        return None
    return box["x"] + inset_x, box["y"] + inset_y


def _place(raw: dict[str, Any], offset: tuple[float, float], frame: Frame) -> dict[str, Any]:
    """Shift a frame-local element into main-viewport coordinates and attach its frame."""
    elem = {k: v for k, v in raw.items() if k != "ref"}
    elem["x"] = raw["x"] + offset[0]
    elem["y"] = raw["y"] + offset[1]
    elem["centerX"] = elem["x"] + raw["width"] / 2
    elem["centerY"] = elem["y"] + raw["height"] / 2
    elem["_ref"] = raw["ref"]
    elem["_frame"] = frame
    # Frame-local box, for the staleness check. Comparing in the element's own
    # frame avoids Playwright's bounding_box(), which misplaces elements inside
    # cross-origin iframes by the iframe's border width.
    elem["_local"] = (raw["x"], raw["y"], raw["width"], raw["height"])
    return elem


def _on_screen(elem: dict[str, Any], viewport: tuple[float, float]) -> bool:
    """True when any part of the element lies inside the main viewport."""
    vw, vh = viewport
    x, y = float(elem["x"]), float(elem["y"])
    w, h = float(elem["width"]), float(elem["height"])
    return x + w > 0 and y + h > 0 and x < vw and y < vh


async def collect_elements(page: Page, generation: int) -> list[dict[str, Any]]:
    """Collect and tag interactive elements across every frame of the page."""
    collected: list[dict[str, Any]] = []
    viewport: tuple[float, float] | None = None
    for index, frame in enumerate(page.frames):
        offset = await _frame_offset(frame)
        if offset is None:
            continue
        try:
            result = await frame.evaluate(COLLECT_JS, f"g{generation}f{index}")
        except PlaywrightError as e:
            logger.debug(f"Element collection failed in frame {frame.url}: {e}")
            continue
        if frame.parent_frame is None:
            viewport = (result["vw"], result["vh"])
        for raw in result["elements"]:
            elem = _place(raw, offset, frame)
            if viewport is None or _on_screen(elem, viewport):
                collected.append(elem)
    return collected


# Frame-local [x, y, width, height] of an element, measured in its own frame.
LOCAL_RECT_JS = (
    "el => { const r = el.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; }"
)


def _moved(recorded: tuple[float, ...], live: list[float]) -> bool:
    """True when the live frame-local box differs from the recorded one beyond the tolerance."""
    return any(abs(a - b) > MOVE_TOLERANCE_PX for a, b in zip(live, recorded, strict=True))


async def locate(element_id: int, elem_map: ElementMap) -> Locator:
    """Resolve an element ID to a locator, verifying it is still where the screenshot showed.

    Raises ElementNotFoundError for unknown IDs and StaleElementError when the
    element was removed, hidden, or moved after the screenshot was taken.
    """
    entry = elem_map.get(element_id)
    if entry is None:
        raise ElementNotFoundError(element_id, list(elem_map))

    frame: Frame = entry["_frame"]
    if frame.is_detached():
        raise StaleElementError(element_id, "its frame was removed")

    locator = frame.locator(f'[{ATTR}="{entry["_ref"]}"]').first
    try:
        if await locator.count() == 0:
            raise StaleElementError(element_id, "it is no longer on the page")
        live = await locator.evaluate(LOCAL_RECT_JS, timeout=ACTION_TIMEOUT_MS)
    except PlaywrightError as e:
        raise StaleElementError(element_id, "it could not be located") from e

    if live[2] < 1 or live[3] < 1:
        raise StaleElementError(element_id, "it is no longer visible")
    if _moved(entry["_local"], live):
        raise StaleElementError(element_id, "it moved")
    return locator

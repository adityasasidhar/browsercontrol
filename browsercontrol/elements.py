"""Set of Marks element collection and resolution.

Collection runs inside every frame of the page (cross-origin frames included,
via Playwright's ``page.frames``), recurses into open shadow roots, and tags each
kept element with a ``data-bc-id`` attribute. Resolution later finds the element
again by that attribute through a frame-scoped locator, which pierces shadow DOM,
so an action reaches the element that was numbered rather than whatever happens
to sit at its old screen position.
"""

import asyncio
import logging
import re
from collections.abc import Sequence
from typing import Any

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Frame, Locator, Page

logger = logging.getLogger(__name__)

ATTR = "data-bc-id"

# A box that drifts further than this between screenshot and action counts as moved.
MOVE_TOLERANCE_PX = 3.0

# Pause before re-measuring a moved element, to tell an element that is still
# animating (acceptable) from one that moved and settled somewhere else (stale).
SETTLE_DELAY_S = 0.15

# Upper bound for one element action, so an overlay that appears after the
# screenshot fails fast instead of waiting out Playwright's 30s default.
ACTION_TIMEOUT_MS = 10_000

ElementMap = dict[int, dict[str, Any]]

# JS expression (over ``el``) identifying what an element is, recorded at
# collection and compared at resolution, so a node a framework recycled for
# different content is refused. Digits are masked so counters and relative
# timestamps ("3 min ago") do not make every element stale.
FINGERPRINT_EXPR = """[
    el.tagName, el.id || '', el.getAttribute('role') || '', el.getAttribute('href') || '',
    el.getAttribute('name') || '', el.getAttribute('aria-label') || '',
    (el.innerText || el.placeholder || '').trim().substring(0, 80)
].join('|').replace(/[0-9]+/g, '#')"""

# Runs inside one frame. Takes a ref prefix, returns that frame's viewport size
# and the visible, unobscured interactive elements in frame-local coordinates.
COLLECT_JS = (
    """
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

    // A styled stand-in for a transparent input lives next to it; anything that
    // covers it from further away (a modal, a cookie banner) hides it for real.
    function isNearby(el, hit) {
        if (Array.from(el.labels || []).some((l) => composedContains(l, hit))) return true;
        let anc = el;
        for (let i = 0; i < 3; i++) {
            const up = parentOf(anc);
            if (!up || up === document.body || up === document.documentElement) break;
            anc = up;
        }
        return anc !== el && composedContains(anc, hit);
    }

    function isUnobscured(el, rect, transparentOk) {
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
            if (hit && transparentOk && isNearby(el, hit)) return true;
        }
        return false;
    }

    const fingerprint = (el) => """
    + FINGERPRINT_EXPR
    + """;

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
            disabled: el.matches(':disabled') || el.getAttribute('aria-disabled') === 'true',
            fp: fingerprint(el)
        };
    }

    function consider(el) {
        if (SKIP.has(el.tagName) || !isCandidate(el)) return;
        // Leave rich-text editors' own DOM alone: tagging nodes inside them
        // trips their mutation observers, which re-render and drop the tag.
        const parent = parentOf(el);
        if (parent && parent.isContentEditable) return;
        const rect = el.getBoundingClientRect();
        const transparentOk = isTransparentOk(el);
        if (!isRendered(el, rect, transparentOk)) return;
        if (!isUnobscured(el, rect, transparentOk)) return;
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
)

# Runs in the parent frame on an <iframe>. Takes boxes in the iframe's content
# coordinates and maps them into the parent frame's coordinates. A box counts as
# visible only if the parent shows the iframe itself at one of its sample points,
# so an overlay in the parent (a modal over an embed) hides the frame's elements,
# as does a box scrolled outside the iframe or outside the parent's viewport.
FRAME_HIT_JS = """
(owner, boxes) => {
    const s = getComputedStyle(owner);
    const r = owner.getBoundingClientRect();
    const ox = r.left + owner.clientLeft + parseFloat(s.paddingLeft || '0');
    const oy = r.top + owner.clientTop + parseFloat(s.paddingTop || '0');
    const cw = owner.clientWidth - parseFloat(s.paddingLeft || '0') - parseFloat(s.paddingRight || '0');
    const ch = owner.clientHeight - parseFloat(s.paddingTop || '0') - parseFloat(s.paddingBottom || '0');
    const root = owner.getRootNode();
    const probe = typeof root.elementFromPoint === 'function' ? root : document;
    const vw = window.innerWidth, vh = window.innerHeight;
    return boxes.map(([x, y, w, h]) => {
        const box = [x + ox, y + oy, w, h];
        const l = Math.max(box[0], ox, 0), rr = Math.min(box[0] + w, ox + cw, vw);
        const t = Math.max(box[1], oy, 0), b = Math.min(box[1] + h, oy + ch, vh);
        if (rr - l < 1 || b - t < 1) return {box: box, visible: false};
        const ix = Math.min(4, (rr - l) / 4), iy = Math.min(4, (b - t) / 4);
        const points = [[(l + rr) / 2, (t + b) / 2], [l + ix, t + iy], [rr - ix, t + iy],
                        [l + ix, b - iy], [rr - ix, b - iy]];
        const visible = points.some(([px, py]) => probe.elementFromPoint(px, py) === owner);
        return {box: box, visible: visible};
    });
}
"""

# Matches the tag attribute as page.content() serializes it.
# find() tags its matches with this attribute; strip it alongside the SoM tags.
FIND_ATTR = "data-bc-find"

_ATTR_RE = re.compile(r"\s(?:" + ATTR + "|" + FIND_ATTR + r')="[^"]*"')


def strip_marks(html: str) -> str:
    """Remove the Set of Marks tags from serialized HTML before showing or saving it."""
    return _ATTR_RE.sub("", html)


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


async def _to_main_viewport(
    frame: Frame, boxes: list[list[float]]
) -> list[tuple[list[float], bool]] | None:
    """Map frame-local boxes into main-viewport coordinates, hit-testing every ancestor.

    Walks up the frame chain, measuring each <iframe> from inside its own parent
    frame (getBoundingClientRect, not Playwright's bounding_box(), which is off by
    the border for frames nested in cross-origin frames). Returns each box with
    whether it is actually visible through every ancestor, or None when a frame
    in the chain is gone.
    """
    visible = [True] * len(boxes)
    current = frame
    while current.parent_frame is not None and any(visible):
        try:
            owner = await current.frame_element()
            hits = await owner.evaluate(FRAME_HIT_JS, boxes)
        except PlaywrightError as e:
            logger.debug(f"Skipping frame {frame.url}: {e}")
            return None
        boxes = [hit["box"] for hit in hits]
        visible = [v and hit["visible"] for v, hit in zip(visible, hits, strict=True)]
        current = current.parent_frame
    return list(zip(boxes, visible, strict=True))


def _place(raw: dict[str, Any], box: list[float], frame: Frame) -> dict[str, Any]:
    """Build a map entry from a frame-local element and its main-viewport box."""
    elem = {k: v for k, v in raw.items() if k not in ("ref", "fp")}
    elem["x"], elem["y"] = box[0], box[1]
    elem["centerX"] = elem["x"] + raw["width"] / 2
    elem["centerY"] = elem["y"] + raw["height"] / 2
    elem["_ref"] = raw["ref"]
    elem["_fp"] = raw.get("fp")
    elem["_frame"] = frame
    # Frame-local box, for the staleness check. Comparing in the element's own
    # frame avoids Playwright's bounding_box(), which misplaces elements inside
    # cross-origin iframes by the iframe's border width.
    elem["_local"] = (raw["x"], raw["y"], raw["width"], raw["height"])
    return elem


async def collect_elements(page: Page, generation: int) -> list[dict[str, Any]]:
    """Collect and tag interactive elements across every frame of the page.

    Elements inside iframes are kept only where the iframe itself shows through
    every ancestor frame, so nothing hidden behind a parent-page overlay or
    scrolled out of the main viewport gets a number.
    """
    collected: list[dict[str, Any]] = []
    for index, frame in enumerate(page.frames):
        try:
            result = await frame.evaluate(COLLECT_JS, f"g{generation}f{index}")
        except PlaywrightError as e:
            logger.debug(f"Element collection failed in frame {frame.url}: {e}")
            continue
        raws = result["elements"]
        if not raws:
            continue
        local = [[r["x"], r["y"], r["width"], r["height"]] for r in raws]
        placed = await _to_main_viewport(frame, local)
        if placed is None:
            continue
        for raw, (box, visible) in zip(raws, placed, strict=True):
            if visible:
                collected.append(_place(raw, box, frame))
    return collected


# Frame-local [x, y, width, height] of an element plus its fingerprint.
LOCATE_JS = (
    "el => { const r = el.getBoundingClientRect(); return {rect: [r.x, r.y, r.width, r.height], "
    "fp: " + FINGERPRINT_EXPR + "}; }"
)


def _moved(recorded: Sequence[float], live: Sequence[float]) -> bool:
    """True when the live frame-local box differs from the recorded one beyond the tolerance."""
    return any(abs(a - b) > MOVE_TOLERANCE_PX for a, b in zip(live, recorded, strict=True))


async def _measure(locator: Locator) -> dict[str, Any]:
    result: dict[str, Any] = await locator.evaluate(LOCATE_JS, timeout=ACTION_TIMEOUT_MS)
    return result


async def locate(element_id: int, elem_map: ElementMap) -> Locator:
    """Resolve an element ID to a locator, verifying it is still the element the screenshot showed.

    Raises ElementNotFoundError for unknown IDs and StaleElementError when the
    element was removed, duplicated, hidden, replaced by different content, or
    moved to a new resting place after the screenshot was taken. An element that
    is still animating is accepted.
    """
    entry = elem_map.get(element_id)
    if entry is None:
        raise ElementNotFoundError(element_id, list(elem_map))

    frame: Frame = entry["_frame"]
    if frame.is_detached():
        raise StaleElementError(element_id, "its frame was removed")

    locator = frame.locator(f'[{ATTR}="{entry["_ref"]}"]')
    try:
        count = await locator.count()
        if count == 0:
            raise StaleElementError(element_id, "it is no longer on the page")
        if count > 1:
            raise StaleElementError(element_id, "the page copied it, so the ID is ambiguous")
        locator = locator.first
        live = await _measure(locator)
    except PlaywrightError as e:
        raise StaleElementError(element_id, "it could not be located") from e

    rect = live["rect"]
    if rect[2] < 1 or rect[3] < 1:
        raise StaleElementError(element_id, "it is no longer visible")
    recorded_fp = entry.get("_fp")
    if recorded_fp is not None and live["fp"] != recorded_fp:
        raise StaleElementError(element_id, "its content changed")
    if _moved(entry["_local"], rect):
        await asyncio.sleep(SETTLE_DELAY_S)
        try:
            again = (await _measure(locator))["rect"]
        except PlaywrightError as e:
            raise StaleElementError(element_id, "it could not be located") from e
        # Still in motion: an animation, not a layout change. Let the action
        # proceed; Playwright waits for the element to be stable before acting.
        if not _moved(rect, again) and _moved(entry["_local"], again):
            raise StaleElementError(element_id, "it moved")
    return locator

"""find(): search the whole page, off-screen content included, and scroll to a match."""

import logging
from typing import Any

from fastmcp import FastMCP
from fastmcp.utilities.types import Image

from browsercontrol.browser import browser
from browsercontrol.elements import ACTION_TIMEOUT_MS, FIND_ATTR
from browsercontrol.tools._summary import get_screenshot_with_summary

logger = logging.getLogger(__name__)

MAX_MATCHES = 50
MAX_LISTED = 15

# Runs in one frame. Tags matching, rendered elements (scrolled away or not)
# with FIND_ATTR and describes them. Text matches are the deepest elements
# holding the text; role matches use the element's explicit or implicit role.
FIND_JS = r"""
({query, role, attr, prefix, limit}) => {
    const all = [];
    const walk = root => {
        for (const el of root.querySelectorAll('*')) {
            all.push(el);
            if (el.shadowRoot) walk(el.shadowRoot);
        }
    };
    walk(document);
    for (const el of all) el.removeAttribute(attr);

    const SKIP = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'HEAD', 'META', 'TITLE',
                          'LINK', 'HTML', 'BODY']);
    const clean = s => (s || '').replace(/\s+/g, ' ').trim();
    const roleOf = el => {
        const explicit = (el.getAttribute('role') || '').split(' ')[0];
        if (explicit) return explicit;
        const tag = el.tagName.toLowerCase();
        const type = (el.getAttribute('type') || 'text').toLowerCase();
        if (tag === 'a' && el.hasAttribute('href')) return 'link';
        if (tag === 'button') return 'button';
        if (tag === 'select') return 'combobox';
        if (tag === 'textarea') return 'textbox';
        if (/^h[1-6]$/.test(tag)) return 'heading';
        if (tag === 'img') return 'img';
        if (tag === 'table') return 'table';
        if (tag === 'nav') return 'navigation';
        if (tag === 'input') {
            if (['button', 'submit', 'reset', 'image'].includes(type)) return 'button';
            if (['checkbox', 'radio'].includes(type)) return type;
            if (type === 'search') return 'searchbox';
            return 'textbox';
        }
        return '';
    };
    const attrs = el => [el.getAttribute('aria-label'), el.getAttribute('placeholder'),
                         el.getAttribute('title'), el.getAttribute('alt'),
                         ['INPUT', 'TEXTAREA'].includes(el.tagName) ? el.value : null];
    const rendered = el => {
        const style = getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden') return false;
        const r = el.getBoundingClientRect();
        return r.width > 0 && r.height > 0;
    };
    const q = query.toLowerCase();
    const hits = text => !q || text.toLowerCase().includes(q);

    let matches = [];
    for (const el of all) {
        if (SKIP.has(el.tagName)) continue;
        if (role) {
            if (roleOf(el) !== role) continue;
            if (!hits(clean([el.innerText, ...attrs(el)].join(' ')))) continue;
        } else {
            if (!q) continue;
            const inAttrs = hits(clean(attrs(el).join(' ')));
            // Deepest holder of the text: its own text matches, but no child's does.
            const text = clean(el.innerText);
            const inText = hits(text) && !Array.from(el.children).some(c => hits(clean(c.innerText)));
            if (!inAttrs && !inText) continue;
        }
        if (rendered(el)) matches.push(el);
    }
    matches = matches.slice(0, limit);
    return matches.map((el, i) => {
        const tagValue = prefix + i;
        el.setAttribute(attr, tagValue);
        return {
            tag: tagValue,
            name: el.tagName.toLowerCase(),
            role: roleOf(el),
            text: clean(el.innerText || attrs(el).find(Boolean) || '').substring(0, 80),
        };
    });
}
"""

# Runs on a match after the screenshot: the SoM ref of the match itself, its
# closest marked ancestor (across shadow roots), or its first marked descendant,
# plus whether it is inside the frame's viewport.
REF_JS = """
el => {
    let ref = null;
    for (let n = el; n && !ref; ) {
        if (n.nodeType === 1 && n.hasAttribute('data-bc-id')) ref = n.getAttribute('data-bc-id');
        n = n.parentNode instanceof ShadowRoot ? n.parentNode.host : n.parentNode;
    }
    if (!ref) {
        const inner = el.querySelector('[data-bc-id]');
        ref = inner ? inner.getAttribute('data-bc-id') : null;
    }
    const r = el.getBoundingClientRect();
    const inView = r.bottom > 0 && r.right > 0 && r.top < window.innerHeight
        && r.left < window.innerWidth;
    return {ref, inView};
}
"""


def register_search_tools(mcp: FastMCP) -> None:
    """Register the find tool with the MCP server."""

    @mcp.tool()
    async def find(query: str, role: str | None = None, nth: int = 1) -> tuple[str, Image]:
        """
        Search the whole page, including content scrolled out of view, and scroll to a match.

        Matches visible text and aria-label/placeholder/title/alt/value. With role
        (e.g. "button", "link", "textbox", "heading", "checkbox"), only elements
        of that role match, and query filters them by name (may be empty).
        Returns every match with the element ID it maps to in the new screenshot.

        Args:
            query: Text to look for (case-insensitive substring)
            role: Optional ARIA role to restrict matches to
            nth: Which match to scroll to, 1-based (default 1)
        """
        try:
            await browser.ensure_started()
            if not query and not role:
                raise ValueError("Give a query, a role, or both.")
            page = browser.page

            matches: list[dict[str, Any]] = []
            for index, frame in enumerate(page.frames):
                try:
                    found = await frame.evaluate(
                        FIND_JS,
                        {
                            "query": query,
                            "role": role or "",
                            "attr": FIND_ATTR,
                            "prefix": f"f{index}-",
                            "limit": MAX_MATCHES,
                        },
                    )
                except Exception as e:
                    logger.debug(f"find skipped frame {frame.url}: {e}")
                    continue
                matches += [{**m, "frame": frame} for m in found]
                if len(matches) >= MAX_MATCHES:
                    break

            what = f"{role} " if role else ""
            what += repr(query) if query else "elements"
            if not matches:
                image, summary = await get_screenshot_with_summary(browser)
                return f"No matches for {what}.\n\n{summary}", image

            nth = min(max(nth, 1), len(matches))
            chosen = matches[nth - 1]
            chosen_loc = chosen["frame"].locator(f'[{FIND_ATTR}="{chosen["tag"]}"]')
            await chosen_loc.scroll_into_view_if_needed(timeout=ACTION_TIMEOUT_MS)
            await browser.settle(1000)

            image, summary = await get_screenshot_with_summary(browser)
            ref_to_id = {entry.get("_ref"): eid for eid, entry in browser.get_element_map().items()}
            lines = [f"Found {len(matches)} match(es) for {what}; scrolled to match {nth}."]
            for i, match in enumerate(matches[:MAX_LISTED], start=1):
                loc = match["frame"].locator(f'[{FIND_ATTR}="{match["tag"]}"]')
                try:
                    info = await loc.evaluate(REF_JS)
                except Exception:
                    info = {"ref": None, "inView": False}
                element_id = ref_to_id.get(info["ref"]) if info["ref"] else None
                label = f"{match['role'] or match['name']} {match['text']!r}"
                if element_id is not None:
                    where = f"element [{element_id}]"
                elif info["inView"]:
                    where = "on screen, not clickable by ID"
                else:
                    role_arg = f", role={role!r}" if role else ""
                    where = f"off-screen; find({query!r}{role_arg}, nth={i}) scrolls to it"
                marker = "  <- scrolled here" if i == nth else ""
                lines.append(f"  {i}. {label} -> {where}{marker}")
            if len(matches) > MAX_LISTED:
                lines.append(f"  ... and {len(matches) - MAX_LISTED} more")
            return "\n".join(lines) + f"\n\n{summary}", image

        except Exception as e:
            logger.error(f"Find failed: {e}")
            raise RuntimeError(f"Find failed: {e}")

    logger.debug("Registered search tools")

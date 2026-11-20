"""Structured extraction: tables, links, and schema-driven JSON."""

import csv
import io
import json
import logging
from typing import Any

from fastmcp import FastMCP

from browsercontrol.browser import browser
from browsercontrol.elements import ElementError

logger = logging.getLogger(__name__)

MAX_OUTPUT_CHARS = 30_000
TABLE_SELECTOR = 'table, [role="table"], [role="grid"]'

# Defines parseTable(table) -> {headers, rows}. HTML tables honour thead,
# a leading all-<th> row, and colspan; ARIA tables use row/cell roles.
_PARSE_TABLE = r"""
const clean = s => (s || '').replace(/\s+/g, ' ').trim();
const parseTable = table => {
    if (table.tagName !== 'TABLE') {
        const rows = Array.from(table.querySelectorAll('[role="row"]'));
        const cells = r => Array.from(r.querySelectorAll(
            '[role="cell"], [role="gridcell"], [role="columnheader"], [role="rowheader"]'
        )).map(c => clean(c.innerText));
        let headers = [];
        if (rows.length && rows[0].querySelector('[role="columnheader"]')) {
            headers = cells(rows.shift());
        }
        return {headers, rows: rows.map(cells).filter(r => r.length)};
    }
    const cells = r => Array.from(r.cells).flatMap(
        c => Array(Math.min(c.colSpan || 1, 50)).fill(clean(c.innerText)));
    const head = table.tHead;
    const body = Array.from(table.rows).filter(r => r.parentElement !== head);
    let headRow = head && head.rows.length ? head.rows[head.rows.length - 1] : null;
    if (!headRow && body.length && Array.from(body[0].cells).every(c => c.tagName === 'TH')) {
        headRow = body.shift();
    }
    return {headers: headRow ? cells(headRow) : [], rows: body.map(cells).filter(r => r.length)};
};
"""

TABLE_BY_INDEX_JS = (
    "({index, selector}) => {"
    + _PARSE_TABLE
    + """
    const tables = Array.from(document.querySelectorAll(selector))
        .filter(t => !t.parentElement || !t.parentElement.closest(selector));
    if (index < 1 || index > tables.length) return {count: tables.length};
    return {count: tables.length, ...parseTable(tables[index - 1])};
}"""
)

TABLE_FROM_ELEMENT_JS = (
    "(el, selector) => {"
    + _PARSE_TABLE
    + """
    const table = el.closest(selector) || el.querySelector(selector);
    return table ? {count: 1, ...parseTable(table)} : {count: 0};
}"""
)

LINKS_JS = r"""
() => {
    const clean = s => (s || '').replace(/\s+/g, ' ').trim();
    const out = [];
    const walk = root => {
        for (const el of root.querySelectorAll('*')) {
            if (el.tagName === 'A' && el.href) {
                const r = el.getBoundingClientRect();
                out.push({
                    text: clean(el.innerText || el.getAttribute('aria-label') || el.title),
                    href: el.href,
                    visible: r.width > 0 && r.height > 0,
                });
            }
            if (el.shadowRoot) walk(el.shadowRoot);
        }
    };
    walk(document);
    return out;
}
"""

# Evaluates a schema against the document. A string is "selector" or
# "selector@attr" (empty selector = the scoped element itself); a one-item list
# means "all matches"; an object with "_selector" scopes its fields to the
# first match of that selector (or to each match, inside a list).
EXTRACT_JS = r"""
(schema) => {
    const clean = s => (s || '').replace(/\s+/g, ' ').trim();
    const split = spec => {
        const at = spec.lastIndexOf('@');
        return at < 0 ? [spec.trim(), null] : [spec.slice(0, at).trim(), spec.slice(at + 1).trim()];
    };
    const value = (el, attr) => {
        if (!el) return null;
        if (attr) return ['href', 'src'].includes(attr) && el[attr] ? el[attr] : el.getAttribute(attr);
        if (['INPUT', 'TEXTAREA', 'SELECT'].includes(el.tagName)) return el.value;
        return clean(el.innerText || el.textContent);
    };
    const pick = (root, sel) => sel ? root.querySelector(sel) : root;
    const readObject = (root, obj) => {
        const out = {};
        for (const [key, spec] of Object.entries(obj)) {
            if (key !== '_selector') out[key] = read(root, spec);
        }
        return out;
    };
    const read = (root, spec) => {
        if (typeof spec === 'string') {
            const [sel, attr] = split(spec);
            return value(pick(root, sel), attr);
        }
        if (Array.isArray(spec)) {
            const inner = spec[0];
            if (typeof inner === 'string') {
                const [sel, attr] = split(inner);
                return Array.from(root.querySelectorAll(sel)).map(el => value(el, attr));
            }
            if (inner && typeof inner === 'object' && inner._selector) {
                return Array.from(root.querySelectorAll(inner._selector))
                    .map(el => readObject(el, inner));
            }
            throw new Error('a list must hold one selector string or one object with _selector');
        }
        if (spec && typeof spec === 'object') {
            if (!spec._selector) return readObject(root, spec);
            const el = root.querySelector(spec._selector);
            return el ? readObject(el, spec) : null;
        }
        throw new Error('schema values must be strings, one-item lists, or objects');
    };
    return read(document, schema);
}
"""


def _clip(text: str) -> str:
    if len(text) > MAX_OUTPUT_CHARS:
        return text[:MAX_OUTPUT_CHARS] + "\n... [truncated]"
    return text


def format_table(headers: list[str], rows: list[list[str]], output_format: str) -> str:
    """Render a parsed table as json (objects keyed by header), markdown, or csv."""
    if output_format == "csv":
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        if headers:
            writer.writerow(headers)
        writer.writerows(rows)
        return buffer.getvalue()
    if output_format == "markdown":
        width = max([len(headers), *(len(r) for r in rows)])
        head = headers + [""] * (width - len(headers)) if headers else [""] * width

        def line(cells: list[str]) -> str:
            padded = cells + [""] * (width - len(cells))
            return "| " + " | ".join(c.replace("|", "\\|") for c in padded) + " |"

        return "\n".join([line(head), "|" + " --- |" * width, *(line(r) for r in rows)])
    if output_format != "json":
        raise ValueError("output_format must be 'json', 'markdown', or 'csv'")
    if not headers:
        return json.dumps(rows, indent=2, ensure_ascii=False)
    keys: list[str] = []
    for i, header in enumerate(headers):
        key = header or f"column_{i + 1}"
        while key in keys:
            key += "_"
        keys.append(key)
    records = [
        {keys[i] if i < len(keys) else f"column_{i + 1}": cell for i, cell in enumerate(row)}
        for row in rows
    ]
    return json.dumps(records, indent=2, ensure_ascii=False)


def register_extract_tools(mcp: FastMCP) -> None:
    """Register structured extraction tools with the MCP server."""

    @mcp.tool()
    async def extract_table(
        element_id: int | None = None, index: int = 1, output_format: str = "json"
    ) -> str:
        """
        Extract a table (HTML <table> or ARIA table/grid) as structured data.

        Args:
            element_id: An element inside (or containing) the table; omit to pick by index
            index: Which table on the page, 1-based, when element_id is omitted
            output_format: "json" (rows keyed by header), "markdown", or "csv"
        """
        try:
            await browser.ensure_started()
            if element_id is not None:
                try:
                    locator = await browser.resolve_element(element_id)
                except ElementError as e:
                    return f"Error: {e}"
                result = await locator.evaluate(TABLE_FROM_ELEMENT_JS, TABLE_SELECTOR)
                if not result["count"]:
                    return f"Element {element_id} is not inside a table."
            else:
                result = await browser.page.evaluate(
                    TABLE_BY_INDEX_JS, {"index": index, "selector": TABLE_SELECTOR}
                )
                if "rows" not in result:
                    return f"No table #{index}: the page has {result['count']} table(s)."

            headers, rows = result["headers"], result["rows"]
            data = format_table(headers, rows, output_format)
            where = f"element {element_id}" if element_id is not None else f"table #{index}"
            return _clip(f"{where}: {len(rows)} row(s), {len(headers)} header(s)\n{data}")
        except Exception as e:
            logger.error(f"Extract table failed: {e}")
            raise RuntimeError(f"Extract table failed: {e}")

    @mcp.tool()
    async def extract_links(contains: str = "", limit: int = 100) -> str:
        """
        List the page's links as JSON: text, absolute href, and whether each is visible.

        Args:
            contains: Only links whose text or URL contains this (case-insensitive)
            limit: Maximum number of links to return (default 100)
        """
        try:
            await browser.ensure_started()
            links: list[dict[str, Any]] = await browser.page.evaluate(LINKS_JS)
            needle = contains.lower()
            seen: set[tuple[str, str]] = set()
            kept = []
            for link in links:
                key = (link["text"], link["href"])
                if key in seen:
                    continue
                if (
                    needle
                    and needle not in link["text"].lower()
                    and needle not in link["href"].lower()
                ):
                    continue
                seen.add(key)
                kept.append(link)
            total = len(kept)
            body = json.dumps(kept[:limit], indent=2, ensure_ascii=False)
            return _clip(f"{total} link(s), showing {min(total, limit)}:\n{body}")
        except Exception as e:
            logger.error(f"Extract links failed: {e}")
            raise RuntimeError(f"Extract links failed: {e}")

    @mcp.tool()
    async def extract(schema: dict[str, Any]) -> str:
        """
        Extract structured JSON from the page with a selector schema.

        Each value is a CSS selector, optionally with "@attr" to read an attribute
        ("a@href", "img@src"; href/src come back absolute). Without @attr you get
        the text (or a form field's value). A one-item list returns every match,
        and an object with "_selector" scopes its fields to that element. Example:

          {"title": "h1",
           "products": [{"_selector": ".product", "name": "h3", "price": ".price",
                         "url": "a@href"}],
           "tags": [".tag"]}

        Selectors use the main document (not iframes or shadow DOM).

        Args:
            schema: The fields to extract, as described above
        """
        try:
            await browser.ensure_started()
            if not isinstance(schema, dict) or not schema:
                raise ValueError("schema must be a non-empty object")
            data = await browser.page.evaluate(EXTRACT_JS, schema)
            return _clip(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Extract failed: {e}")
            raise RuntimeError(f"Extract failed: {e}")

    logger.debug("Registered extract tools")

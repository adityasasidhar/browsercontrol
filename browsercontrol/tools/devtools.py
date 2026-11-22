import logging
from typing import Any

from fastmcp import FastMCP
from fastmcp.utilities.types import Image

from browsercontrol.browser import browser
from browsercontrol.elements import ElementError
from browsercontrol.tools._summary import get_screenshot_with_summary

logger = logging.getLogger(__name__)

STORAGE_VALUE_PREVIEW = 100

# Every user value travels as an evaluate() argument, never spliced into the source.
# Storage access throws on opaque origins (about:blank, data:, sandboxed frames).
STORAGE_JS = """
([kind, op, key, value]) => {
    let store;
    try {
        store = kind === 'session' ? window.sessionStorage : window.localStorage;
        store.length;
    } catch (e) {
        return {error: String((e && e.message) || e), origin: location.origin};
    }
    const origin = location.origin;
    if (op === 'get') {
        if (key !== null) return {origin, value: store.getItem(key)};
        const items = [];
        for (let i = 0; i < store.length; i++) {
            const k = store.key(i);
            items.push([k, store.getItem(k)]);
        }
        return {origin, items};
    }
    if (op === 'set') { store.setItem(key, value); return {origin}; }
    if (key !== null) {
        const existed = store.getItem(key) !== null;
        store.removeItem(key);
        return {origin, existed};
    }
    const count = store.length;
    store.clear();
    return {origin, count};
}
"""


def register_devtools(mcp: FastMCP) -> None:
    """Register developer tools with the MCP server."""

    @mcp.tool()
    async def get_console_logs(clear: bool = False) -> str:
        """
        Get browser console logs (errors, warnings, info, log messages).

        Args:
            clear: If True, clear the captured logs after returning them

        Returns:
            Console logs
        """
        try:
            await browser.ensure_started()

            # Get console messages from our captured logs
            logs = browser.get_console_logs()

            if not logs:
                log_text = "No console logs captured."
            else:
                log_lines = []
                for log in logs[-50:]:  # Last 50 logs
                    level = log.get("level", "log").upper()
                    text = log.get("text", "")
                    location = log.get("location", "")
                    if location:
                        log_lines.append(f"[{level}] {text} ({location})")
                    else:
                        log_lines.append(f"[{level}] {text}")
                log_text = "\n".join(log_lines)

            if clear:
                browser.clear_console_logs()

            return f"Console Logs:\n{log_text}"

        except Exception as e:
            logger.error(f"Get console logs failed: {e}")
            raise RuntimeError(f"Get console logs failed: {e}")

    @mcp.tool()
    async def get_network_requests(num_requests: int | None = None, clear: bool = False) -> str:
        """
        Get captured network requests (API calls, resources, etc.).

        Each line starts with a #id; pass it to get_request_details for headers and body.

        Args:
            num_requests: Number of recent requests to return. Defaults to 30.
            clear: If True, clear the captured requests after returning them

        Returns:
            Network requests
        """
        try:
            await browser.ensure_started()

            requests = browser.get_network_requests()

            if not requests:
                request_text = "No network requests captured."
            else:
                num_to_show = num_requests if num_requests is not None else 30
                request_lines = []
                for req in requests[-num_to_show:]:
                    method = req.get("method", "GET")
                    url = req.get("url", "")
                    status = req.get("status", "pending")
                    duration = req.get("duration", "")

                    # Truncate long URLs
                    if len(url) > 80:
                        url = url[:77] + "..."

                    line = f"{method} {url} -> {status}"
                    if req.get("id") is not None:
                        line = f"#{req['id']} {line}"
                    if duration:
                        line += f" ({duration}ms)"
                    request_lines.append(line)

                request_text = "\n".join(request_lines)

            if clear:
                browser.clear_network_requests()

            return f"Network Requests:\n{request_text}"

        except Exception as e:
            logger.error(f"Get network requests failed: {e}")
            raise RuntimeError(f"Get network requests failed: {e}")

    @mcp.tool()
    async def get_page_errors() -> str:
        """
        Get JavaScript errors that occurred on the page.

        Returns:
            Page errors
        """
        try:
            await browser.ensure_started()

            errors = browser.get_page_errors()

            if not errors:
                error_text = "No JavaScript errors detected."
            else:
                error_lines = []
                for err in errors[-20:]:
                    message = err.get("message", "Unknown error")
                    stack = err.get("stack", "")
                    if stack:
                        # Just first line of stack
                        stack_first = stack.split("\n")[0] if "\n" in stack else stack
                        error_lines.append(f" {message}\n   {stack_first}")
                    else:
                        error_lines.append(f" {message}")

                error_text = "\n".join(error_lines)

            return f"Page Errors:\n{error_text}"

        except Exception as e:
            logger.error(f"Get page errors failed: {e}")
            raise RuntimeError(f"Get page errors failed: {e}")

    @mcp.tool()
    async def run_in_console(code: str) -> tuple[str, Image]:
        """
        Execute JavaScript code in the browser console and return the result.
        Useful for debugging, inspecting variables, or manipulating the page.

        Args:
            code: JavaScript code to execute in the console

        Returns:
            Result of the code execution and screenshot
        """
        try:
            await browser.ensure_started()
            logger.info(f"Executing in console: {code[:100]}...")

            wrapped_code = f"""
            (() => {{
                try {{
                    const result = eval({code!r});
                    if (result === undefined) return 'undefined';
                    if (result === null) return 'null';
                    if (typeof result === 'object') {{
                        try {{
                            return JSON.stringify(result, null, 2);
                        }} catch (e) {{
                            return String(result);
                        }}
                    }}
                    return String(result);
                }} catch (error) {{
                    return 'Error: ' + error.message;
                }}
            }})()
            """

            result = await browser.page.evaluate(wrapped_code)

            image, summary = await get_screenshot_with_summary(browser)
            return f"Console Result:\n{result}\n\n{summary}", image

        except Exception as e:
            logger.error(f"Run in console failed: {e}")
            try:
                image, summary = await get_screenshot_with_summary(browser)
                return f"Error executing code: {e}\n\n{summary}", image
            except Exception:
                raise RuntimeError(f"Run in console failed: {e}")

    @mcp.tool()
    async def inspect_element(element_id: int) -> str:
        """
        Inspect an element to get its computed styles, dimensions, and properties.

        Args:
            element_id: The number label of the element to inspect

        Returns:
            Element details
        """
        try:
            await browser.ensure_started()
            try:
                locator = await browser.resolve_element(element_id)
            except ElementError as e:
                return f"Error: {e}"

            # Get detailed info about the element
            inspect_code = """
            (el) => {
                const rect = el.getBoundingClientRect();
                const styles = window.getComputedStyle(el);

                return {
                    tag: el.tagName.toLowerCase(),
                    id: el.id || null,
                    classes: Array.from(el.classList),
                    text: el.innerText?.substring(0, 200) || '',
                    href: el.href || null,
                    src: el.src || null,
                    value: el.value || null,
                    dimensions: {
                        width: Math.round(rect.width),
                        height: Math.round(rect.height),
                        top: Math.round(rect.top),
                        left: Math.round(rect.left)
                    },
                    styles: {
                        color: styles.color,
                        backgroundColor: styles.backgroundColor,
                        fontSize: styles.fontSize,
                        fontFamily: styles.fontFamily,
                        display: styles.display,
                        position: styles.position,
                        zIndex: styles.zIndex
                    },
                    attributes: Array.from(el.attributes).filter(a => a.name !== 'data-bc-id').map(a => ({ name: a.name, value: a.value })).slice(0, 10)
                };
            }
            """

            info = await locator.evaluate(inspect_code)

            # Format the info nicely
            lines = [f"Element {element_id} Inspection:"]
            lines.append(f"  Tag: <{info.get('tag', 'unknown')}>")
            if info.get("id"):
                lines.append(f"  ID: #{info['id']}")
            if info.get("classes"):
                lines.append(f"  Classes: .{', .'.join(info['classes'])}")
            if info.get("text"):
                lines.append(f"  Text: {info['text'][:100]}...")
            if info.get("href"):
                lines.append(f"  Href: {info['href']}")

            dims = info.get("dimensions", {})
            lines.append(f"  Size: {dims.get('width', '?')}x{dims.get('height', '?')}px")
            lines.append(f"  Position: ({dims.get('left', '?')}, {dims.get('top', '?')})")

            styles = info.get("styles", {})
            lines.append("  Styles:")
            lines.append(f"    color: {styles.get('color', '?')}")
            lines.append(f"    background: {styles.get('backgroundColor', '?')}")
            lines.append(
                f"    font: {styles.get('fontSize', '?')} {styles.get('fontFamily', '?')[:30]}"
            )

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Inspect element failed: {e}")
            raise RuntimeError(f"Inspect element failed: {e}")

    @mcp.tool()
    async def get_page_performance() -> str:
        """
        Get page performance metrics (load time, Core Web Vitals).

        Returns:
            Performance metrics
        """
        try:
            await browser.ensure_started()

            perf_code = """
            (() => {
                const perf = performance.getEntriesByType('navigation')[0] || {};
                const paint = performance.getEntriesByType('paint');
                const fcp = paint.find(p => p.name === 'first-contentful-paint');

                return {
                    // Navigation timing
                    domContentLoaded: Math.round(perf.domContentLoadedEventEnd - perf.startTime),
                    loadComplete: Math.round(perf.loadEventEnd - perf.startTime),
                    ttfb: Math.round(perf.responseStart - perf.startTime),

                    // Paint timing
                    firstPaint: paint.find(p => p.name === 'first-paint')?.startTime?.toFixed(0) || null,
                    firstContentfulPaint: fcp?.startTime?.toFixed(0) || null,

                    // Resource count
                    resourceCount: performance.getEntriesByType('resource').length,

                    // Memory (if available)
                    memory: performance.memory ? {
                        usedJSHeapSize: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
                        totalJSHeapSize: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024)
                    } : null
                };
            })()
            """

            metrics = await browser.page.evaluate(perf_code)

            lines = ["Page Performance:"]
            lines.append(f" Time to First Byte: {metrics.get('ttfb', '?')}ms")
            if metrics.get("firstContentfulPaint"):
                lines.append(f" First Contentful Paint: {metrics['firstContentfulPaint']}ms")
            lines.append(f" DOM Content Loaded: {metrics.get('domContentLoaded', '?')}ms")
            lines.append(f" Load Complete: {metrics.get('loadComplete', '?')}ms")
            lines.append(f" Resources Loaded: {metrics.get('resourceCount', '?')}")

            if metrics.get("memory"):
                mem = metrics["memory"]
                lines.append(f" JS Heap: {mem['usedJSHeapSize']}MB / {mem['totalJSHeapSize']}MB")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Get performance failed: {e}")
            raise RuntimeError(f"Get performance failed: {e}")

    @mcp.tool()
    async def get_cookies() -> str:
        """Get all cookies for the current context."""
        try:
            await browser.ensure_started()
            cookies = await browser._context.cookies()  # type: ignore[union-attr]

            if not cookies:
                return "No cookies found."

            lines = ["Cookies:"]
            for c in cookies:
                lines.append(f"  {c['name']}={c['value'][:20]}... (domain={c['domain']})")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Get cookies failed: {e}")
            raise RuntimeError(f"Get cookies failed: {e}")

    @mcp.tool()
    async def set_cookie(name: str, value: str, domain: str | None = None, path: str = "/") -> str:
        """
        Set a cookie.

        Args:
            name: Cookie name
            value: Cookie value
            domain: Cookie domain (optional, defaults to current page domain)
            path: Cookie path (default: "/")
        """
        try:
            await browser.ensure_started()

            if not domain:
                # Try to infer domain from current URL
                from urllib.parse import urlparse

                current_url = browser.page.url
                if current_url:
                    domain = urlparse(current_url).hostname

            if not domain:
                raise ValueError("Domain is required and could not be inferred.")

            cookie: dict[str, str] = {"name": name, "value": value, "domain": domain, "path": path}
            await browser._context.add_cookies([cookie])  # type: ignore[union-attr, list-item]

            return f"Cookie set: {name}={value} for {domain}"

        except Exception as e:
            logger.error(f"Set cookie failed: {e}")
            raise RuntimeError(f"Set cookie failed: {e}")

    @mcp.tool()
    async def delete_cookie(name: str) -> str:
        """
        Delete a cookie by name.
        Note: This deletes all cookies with this name across all domains in context.
        """
        try:
            await browser.ensure_started()
            await browser._context.clear_cookies(name=name)  # type: ignore[union-attr]
            return f"Deleted cookie(s) with name: {name}"

        except Exception as e:
            logger.error(f"Delete cookie failed: {e}")
            raise RuntimeError(f"Delete cookie failed: {e}")

    @mcp.tool()
    async def clear_cookies() -> str:
        """Clear all cookies."""
        try:
            await browser.ensure_started()
            await browser._context.clear_cookies()  # type: ignore[union-attr]
            return "All cookies cleared."

        except Exception as e:
            logger.error(f"Clear cookies failed: {e}")
            raise RuntimeError(f"Clear cookies failed: {e}")

    async def _storage(
        kind: str, op: str, key: str | None = None, value: str | None = None
    ) -> dict[str, Any]:
        if kind not in ("local", "session"):
            raise ValueError(f"Invalid kind {kind!r}: use 'local' or 'session'.")
        await browser.ensure_started()
        result: dict[str, Any] = await browser.page.evaluate(STORAGE_JS, [kind, op, key, value])
        if "error" in result:
            raise ValueError(
                f"{kind}Storage is not available on this page (origin "
                f"{result.get('origin')!r}): {result['error']}. Navigate to a regular "
                "http(s) page first."
            )
        return result

    @mcp.tool()
    async def get_storage(kind: str = "local", key: str | None = None) -> str:
        """
        Read localStorage or sessionStorage for the current page's origin.

        Args:
            kind: "local" for localStorage (default) or "session" for sessionStorage
            key: A single key to read. Omit to list every key with a value preview.
        """
        try:
            result = await _storage(kind, "get", key)
            origin = result["origin"]
            if key is not None:
                if result["value"] is None:
                    return f"{origin} {kind}Storage has no key {key!r}."
                return f"{origin} {kind}Storage[{key!r}] = {result['value']}"
            items = result["items"]
            if not items:
                return f"{origin} {kind}Storage is empty."
            lines = [f"{origin} {kind}Storage ({len(items)} keys):"]
            for k, v in items:
                if len(v) > STORAGE_VALUE_PREVIEW:
                    v = v[:STORAGE_VALUE_PREVIEW] + f"... ({len(v)} chars)"
                lines.append(f"  {k} = {v}")
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Get storage failed: {e}")
            raise RuntimeError(f"Get storage failed: {e}")

    @mcp.tool()
    async def set_storage(key: str, value: str, kind: str = "local") -> str:
        """
        Set a localStorage or sessionStorage item for the current page's origin.

        Args:
            key: Storage key
            value: String value to store
            kind: "local" for localStorage (default) or "session" for sessionStorage
        """
        try:
            result = await _storage(kind, "set", key, value)
            return f"Set {result['origin']} {kind}Storage[{key!r}] ({len(value)} chars)."
        except Exception as e:
            logger.error(f"Set storage failed: {e}")
            raise RuntimeError(f"Set storage failed: {e}")

    @mcp.tool()
    async def clear_storage(kind: str = "local", key: str | None = None) -> str:
        """
        Remove one key from, or clear all of, localStorage or sessionStorage for the current origin.

        Args:
            kind: "local" for localStorage (default) or "session" for sessionStorage
            key: The key to remove. Omit to clear every key.
        """
        try:
            result = await _storage(kind, "clear", key)
            origin = result["origin"]
            if key is not None:
                if not result["existed"]:
                    return f"{origin} {kind}Storage has no key {key!r}; nothing removed."
                return f"Removed {key!r} from {origin} {kind}Storage."
            return f"Cleared {result['count']} keys from {origin} {kind}Storage."
        except Exception as e:
            logger.error(f"Clear storage failed: {e}")
            raise RuntimeError(f"Clear storage failed: {e}")

    @mcp.tool()
    async def set_viewport(width: int, height: int) -> tuple[str, Image]:
        """
        Set the browser viewport size.

        Args:
            width: Width in pixels
            height: Height in pixels
        """
        try:
            # Validate before applying: a zero/negative viewport makes every
            # subsequent screenshot fail, which would break every other tool.
            if width < 1 or height < 1:
                raise ValueError(
                    f"Invalid viewport {width}x{height}: width and height must be at least 1."
                )

            await browser.ensure_started()
            await browser.page.set_viewport_size({"width": width, "height": height})

            image, summary = await get_screenshot_with_summary(browser)
            return f"Viewport set to {width}x{height}\n\n{summary}", image

        except Exception as e:
            logger.error(f"Set viewport failed: {e}")
            raise RuntimeError(f"Set viewport failed: {e}")

    logger.debug("Registered developer tools")

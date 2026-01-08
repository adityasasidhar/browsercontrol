"""Developer tools for browser control - console, network, errors."""

import logging
from fastmcp import FastMCP
from fastmcp.utilities.types import Image

from browsercontrol.browser import browser

logger = logging.getLogger(__name__)


async def _get_screenshot_with_summary() -> tuple[Image, str]:
    """Helper to get annotated screenshot with element summary."""
    screenshot_bytes, elem_map = await browser.screenshot_with_som()
    image = Image(data=screenshot_bytes, format="png")
    
    summary_lines = [f"Found {len(elem_map)} interactive elements:"]
    for eid, elem in list(elem_map.items())[:30]:
        desc = elem["text"][:40] if elem["text"] else elem["tag"]
        summary_lines.append(f"  [{eid}] {elem['tag']} - {desc}")
    
    if len(elem_map) > 30:
        summary_lines.append(f"  ... and {len(elem_map) - 30} more")
    
    return image, "\n".join(summary_lines)


def register_devtools(mcp: FastMCP) -> None:
    """Register developer tools with the MCP server."""
    
    @mcp.tool()
    async def get_console_logs(clear: bool = False) -> tuple[str, Image]:
        """
        Get browser console logs (errors, warnings, info, log messages).
        
        Args:
            clear: If True, clear the captured logs after returning them
            
        Returns:
            Console logs and screenshot
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
            
            image, summary = await _get_screenshot_with_summary()
            return f"Console Logs:\n{log_text}\n\n{summary}", image
            
        except Exception as e:
            logger.error(f"Get console logs failed: {e}")
            raise RuntimeError(f"Get console logs failed: {e}")
    
    @mcp.tool()
    async def get_network_requests(clear: bool = False) -> tuple[str, Image]:
        """
        Get captured network requests (API calls, resources, etc.).
        
        Args:
            clear: If True, clear the captured requests after returning them
            
        Returns:
            Network requests and screenshot
        """
        try:
            await browser.ensure_started()
            
            requests = browser.get_network_requests()
            
            if not requests:
                request_text = "No network requests captured."
            else:
                request_lines = []
                for req in requests[-30:]:  # Last 30 requests
                    method = req.get("method", "GET")
                    url = req.get("url", "")
                    status = req.get("status", "pending")
                    duration = req.get("duration", "")
                    
                    # Truncate long URLs
                    if len(url) > 80:
                        url = url[:77] + "..."
                    
                    line = f"{method} {url} -> {status}"
                    if duration:
                        line += f" ({duration}ms)"
                    request_lines.append(line)
                
                request_text = "\n".join(request_lines)
            
            if clear:
                browser.clear_network_requests()
            
            image, summary = await _get_screenshot_with_summary()
            return f"Network Requests:\n{request_text}\n\n{summary}", image
            
        except Exception as e:
            logger.error(f"Get network requests failed: {e}")
            raise RuntimeError(f"Get network requests failed: {e}")
    
    @mcp.tool()
    async def get_page_errors() -> tuple[str, Image]:
        """
        Get JavaScript errors that occurred on the page.
        
        Returns:
            Page errors and screenshot
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
            
            image, summary = await _get_screenshot_with_summary()
            return f"Page Errors:\n{error_text}\n\n{summary}", image
            
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
            
            # Wrap in try-catch to capture errors nicely
            wrapped_code = f"""
            (() => {{
                try {{
                    const result = eval({repr(code)});
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
            
            image, summary = await _get_screenshot_with_summary()
            return f"Console Result:\n{result}\n\n{summary}", image
            
        except Exception as e:
            logger.error(f"Run in console failed: {e}")
            try:
                image, summary = await _get_screenshot_with_summary()
                return f"Error executing code: {e}\n\n{summary}", image
            except Exception:
                raise RuntimeError(f"Run in console failed: {e}")
    
    @mcp.tool()
    async def inspect_element(element_id: int) -> tuple[str, Image]:
        """
        Inspect an element to get its computed styles, dimensions, and properties.
        
        Args:
            element_id: The number label of the element to inspect
            
        Returns:
            Element details and screenshot
        """
        try:
            await browser.ensure_started()
            from browsercontrol.browser import get_element_map
            
            elem_map = get_element_map()
            if element_id not in elem_map:
                image, summary = await _get_screenshot_with_summary()
                return f"Error: Element {element_id} not found.\n\n{summary}", image
            
            elem = elem_map[element_id]
            
            # Get detailed info about the element
            inspect_code = f"""
            (() => {{
                const el = document.elementFromPoint({elem['centerX']}, {elem['centerY']});
                if (!el) return {{ error: 'Element not found at coordinates' }};
                
                const rect = el.getBoundingClientRect();
                const styles = window.getComputedStyle(el);
                
                return {{
                    tag: el.tagName.toLowerCase(),
                    id: el.id || null,
                    classes: Array.from(el.classList),
                    text: el.innerText?.substring(0, 200) || '',
                    href: el.href || null,
                    src: el.src || null,
                    value: el.value || null,
                    dimensions: {{
                        width: Math.round(rect.width),
                        height: Math.round(rect.height),
                        top: Math.round(rect.top),
                        left: Math.round(rect.left)
                    }},
                    styles: {{
                        color: styles.color,
                        backgroundColor: styles.backgroundColor,
                        fontSize: styles.fontSize,
                        fontFamily: styles.fontFamily,
                        display: styles.display,
                        position: styles.position,
                        zIndex: styles.zIndex
                    }},
                    attributes: Array.from(el.attributes).map(a => ({{ name: a.name, value: a.value }})).slice(0, 10)
                }};
            }})()
            """
            
            info = await browser.page.evaluate(inspect_code)
            
            # Format the info nicely
            lines = [f"Element {element_id} Inspection:"]
            lines.append(f"  Tag: <{info.get('tag', 'unknown')}>")
            if info.get('id'):
                lines.append(f"  ID: #{info['id']}")
            if info.get('classes'):
                lines.append(f"  Classes: .{', .'.join(info['classes'])}")
            if info.get('text'):
                lines.append(f"  Text: {info['text'][:100]}...")
            if info.get('href'):
                lines.append(f"  Href: {info['href']}")
            
            dims = info.get('dimensions', {})
            lines.append(f"  Size: {dims.get('width', '?')}x{dims.get('height', '?')}px")
            lines.append(f"  Position: ({dims.get('left', '?')}, {dims.get('top', '?')})")
            
            styles = info.get('styles', {})
            lines.append(f"  Styles:")
            lines.append(f"    color: {styles.get('color', '?')}")
            lines.append(f"    background: {styles.get('backgroundColor', '?')}")
            lines.append(f"    font: {styles.get('fontSize', '?')} {styles.get('fontFamily', '?')[:30]}")
            
            image, summary = await _get_screenshot_with_summary()
            return "\n".join(lines) + f"\n\n{summary}", image
            
        except Exception as e:
            logger.error(f"Inspect element failed: {e}")
            raise RuntimeError(f"Inspect element failed: {e}")
    
    @mcp.tool()
    async def get_page_performance() -> tuple[str, Image]:
        """
        Get page performance metrics (load time, Core Web Vitals).
        
        Returns:
            Performance metrics and screenshot
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
            if metrics.get('firstContentfulPaint'):
                lines.append(f" First Contentful Paint: {metrics['firstContentfulPaint']}ms")
            lines.append(f" DOM Content Loaded: {metrics.get('domContentLoaded', '?')}ms")
            lines.append(f" Load Complete: {metrics.get('loadComplete', '?')}ms")
            lines.append(f" Resources Loaded: {metrics.get('resourceCount', '?')}")
            
            if metrics.get('memory'):
                mem = metrics['memory']
                lines.append(f" JS Heap: {mem['usedJSHeapSize']}MB / {mem['totalJSHeapSize']}MB")
            
            image, summary = await _get_screenshot_with_summary()
            return "\n".join(lines) + f"\n\n{summary}", image
            
        except Exception as e:
            logger.error(f"Get performance failed: {e}")
            raise RuntimeError(f"Get performance failed: {e}")
    
    logger.debug("Registered developer tools")

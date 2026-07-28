import logging
import time
from io import BytesIO
from typing import Any, cast

from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    Request,
    async_playwright,
)

from browsercontrol.config import config

logger = logging.getLogger(__name__)

# Store element mapping for click-by-ID
element_map: dict[int, dict[str, Any]] = {}

# Module-level cached font (loaded once, reused across screenshots)
_cached_font: ImageFont.FreeTypeFont | ImageFont.ImageFont | None = None


def _get_label_font() -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load and cache the label font for SoM overlays (loaded once per process)."""
    global _cached_font
    if _cached_font is not None:
        return _cached_font
    font_names = [
        "Arial.ttf",
        "arial.ttf",  # Windows/macOS
        "Helvetica.ttf",
        "helvetica.ttf",  # macOS
        "DejaVuSans-Bold.ttf",  # Linux
        "FreeSansBold.ttf",  # Linux
        "LiberationSans-Bold.ttf",  # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux specific path
        "/System/Library/Fonts/Helvetica.ttc",  # macOS specific path
    ]
    for font_name in font_names:
        try:
            _cached_font = ImageFont.truetype(font_name, 14)
            return _cached_font
        except OSError:
            continue
    _cached_font = ImageFont.load_default()
    return _cached_font


class BrowserManager:
    """Manages the browser lifecycle and provides access to pages."""

    def __init__(self) -> None:
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._started = False

        # Developer tools storage
        self._console_logs: list[dict[str, Any]] = []
        self._network_requests: list[dict[str, Any]] = []
        self._page_errors: list[dict[str, Any]] = []
        # Keyed by Request object identity to avoid URL-collision mis-pairings
        self._request_map: dict[Any, dict[str, Any]] = {}

    @property
    def is_started(self) -> bool:
        """Check if browser is started."""
        return self._started and self._context is not None

    async def _install_chromium(self) -> None:
        """Install Chromium browser using Playwright."""
        import asyncio
        import sys

        logger.info("Installing Chromium browser (one-time setup)...")

        try:
            # Use playwright install command
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                "-m",
                "playwright",
                "install",
                "chromium",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                _, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
                if process.returncode == 0:
                    logger.info("Chromium installed successfully!")
                else:
                    logger.warning(f"Chromium installation output: {stderr.decode('utf-8')}")
            except TimeoutError:
                process.kill()
                logger.error(
                    "Chromium installation timed out. Please run: playwright install chromium"
                )

        except Exception as e:
            logger.error(f"Failed to install Chromium: {e}")
            logger.info("Please run manually: playwright install chromium")

    def _setup_page_listeners(self, page: Page) -> None:
        """Set up event listeners for console, network, and errors."""

        # Console messages
        def on_console(msg: Any) -> None:
            self._console_logs.append(
                {
                    "level": msg.type,
                    "text": msg.text,
                    "location": f"{msg.location.get('url', '')}:{msg.location.get('lineNumber', '')}"
                    if msg.location
                    else "",
                    "timestamp": time.time(),
                }
            )
            # Keep only last 200 logs
            if len(self._console_logs) > 200:
                self._console_logs = self._console_logs[-200:]

        # Page errors (uncaught exceptions)
        def on_page_error(error: Any) -> None:
            self._page_errors.append(
                {
                    "message": str(error),
                    "stack": getattr(error, "stack", ""),
                    "timestamp": time.time(),
                }
            )
            if len(self._page_errors) > 100:
                self._page_errors = self._page_errors[-100:]

        # Network request started — keyed by Request object to avoid URL collisions
        def on_request(request: Request) -> None:
            self._request_map[request] = {
                "method": request.method,
                "url": request.url,
                "start_time": time.time(),
                "status": "pending",
                "resource_type": request.resource_type,
            }

        # Network request completed
        def on_response(response: Any) -> None:
            req_obj = response.request
            if req_obj in self._request_map:
                req = self._request_map[req_obj]
                req["status"] = response.status
                req["duration"] = int((time.time() - req["start_time"]) * 1000)
                self._network_requests.append(req)
                del self._request_map[req_obj]
            else:
                self._network_requests.append(
                    {
                        "method": response.request.method,
                        "url": response.url,
                        "status": response.status,
                        "resource_type": response.request.resource_type,
                    }
                )

            # Keep only last 100 requests
            if len(self._network_requests) > 100:
                self._network_requests = self._network_requests[-100:]

        # Network request failed
        def on_request_failed(request: Request) -> None:
            if request in self._request_map:
                req = self._request_map[request]
                req["status"] = "failed"
                req["duration"] = int((time.time() - req["start_time"]) * 1000)
                self._network_requests.append(req)
                del self._request_map[request]

        page.on("console", on_console)
        page.on("pageerror", on_page_error)
        page.on("request", on_request)
        page.on("response", on_response)
        page.on("requestfailed", on_request_failed)

    async def start(self) -> None:
        """Start the browser with persistent context."""
        if self._started:
            logger.warning("Browser already started")
            return

        config.user_data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Starting browser with user data dir: {config.user_data_dir}")

        self._playwright = await async_playwright().start()

        # Build launch args
        # Add proxy bypass for localhost to fix connection refused errors
        args = [
            "--no-first-run",
            "--no-default-browser-check",
            "--proxy-bypass-list=<-loopback>",
            "--no-proxy-server",
        ]
        if config.extension_path and config.extension_path.exists():
            args.extend(
                [
                    f"--disable-extensions-except={config.extension_path}",
                    f"--load-extension={config.extension_path}",
                ]
            )
            logger.info(f"Loading extension from: {config.extension_path}")

        # Substrings that indicate the Chromium executable is missing
        missing_hints = ("executable doesn't exist", "playwright install", "looks like playwright")

        launch_kwargs: dict[str, Any] = {
            "user_data_dir": str(config.user_data_dir),
            "headless": config.headless,
            "args": args,
            "viewport": {"width": config.viewport_width, "height": config.viewport_height},
        }
        if config.executable_path:
            launch_kwargs["executable_path"] = str(config.executable_path)
            logger.info(f"Using Chromium executable: {config.executable_path}")

        try:
            try:
                self._context = await self._playwright.chromium.launch_persistent_context(
                    **launch_kwargs
                )
            except Exception as launch_exc:
                # Only retry after installing if the error is a missing-executable error.
                # A caller-supplied executable is theirs to fix, so don't install over it.
                if config.executable_path is None and any(
                    hint in str(launch_exc).lower() for hint in missing_hints
                ):
                    logger.info("Chromium executable not found, installing automatically...")
                    await self._install_chromium()
                    # Retry the launch exactly once after install
                    self._context = await self._playwright.chromium.launch_persistent_context(
                        **launch_kwargs
                    )
                else:
                    raise

            # Auto-attach listeners to new pages (including popups)
            self._context.on("page", self._setup_page_listeners)

            # Get or create initial page
            if self._context.pages:
                self._page = self._context.pages[0]
            else:
                self._page = await self._context.new_page()

            # Set up event listeners for the initial page(s)
            for page in self._context.pages:
                self._setup_page_listeners(page)

            self._started = True
            logger.info("Browser started successfully")

        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            await self.stop()
            raise

    async def stop(self) -> None:
        """Stop the browser."""
        logger.info("Stopping browser")
        self._started = False

        if self._context:
            try:
                await self._context.close()
            except Exception as e:
                logger.warning(f"Error closing context: {e}")
            self._context = None

        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception as e:
                logger.warning(f"Error stopping playwright: {e}")
            self._playwright = None

        self._page = None

        # Clear dev tools data
        self._console_logs.clear()
        self._network_requests.clear()
        self._page_errors.clear()
        self._request_map.clear()

    async def ensure_started(self) -> None:
        """Ensure browser is started, restart if needed."""
        if not self.is_started:
            logger.info("Browser not started, starting now")
            await self.start()

    @property
    def page(self) -> Page:
        """Get the current active page."""
        if not self.is_started:
            raise RuntimeError("Browser not started. Call start() first.")

        # If the explicit _page reference is stale (closed), try to fallback
        if self._page is None or self._page.is_closed():
            pages = self._context.pages  # type: ignore[union-attr]
            if pages:
                self._page = pages[-1]  # Default to last opened
            else:
                raise RuntimeError("No open pages.")

        return self._page

    async def create_tab(self, url: str | None = None) -> None:
        """Create a new tab and switch to it."""
        if not self.is_started:
            await self.start()

        self._page = await self._context.new_page()  # type: ignore[union-attr]
        if url:
            await self._page.goto(url)

    async def switch_to_tab(self, index: int) -> None:
        """Switch to a specific tab index."""
        if not self.is_started:
            raise RuntimeError("Browser not started.")

        pages = self._context.pages  # type: ignore[union-attr]
        if 0 <= index < len(pages):
            self._page = pages[index]
            await self._page.bring_to_front()
        else:
            raise ValueError(f"Tab index {index} out of range (0-{len(pages) - 1})")

    async def close_tab(self, index: int) -> None:
        """Close a specific tab index."""
        if not self.is_started:
            raise RuntimeError("Browser not started.")

        pages = self._context.pages  # type: ignore[union-attr]
        if 0 <= index < len(pages):
            await pages[index].close()
            # If we closed the active page, switch to the last available one
            if self._page.is_closed():  # type: ignore[union-attr]
                pages = self._context.pages  # type: ignore[union-attr]
                if pages:
                    self._page = pages[-1]
                else:
                    self._page = await self._context.new_page()  # type: ignore[union-attr]
        else:
            raise ValueError(f"Tab index {index} out of range (0-{len(pages) - 1})")

    async def list_tabs(self) -> list[dict[str, Any]]:
        """List all open tabs."""
        if not self.is_started:
            return []

        tabs = []
        for i, page in enumerate(self._context.pages):  # type: ignore[union-attr]
            title = await page.title()
            url = page.url
            is_active = page == self._page
            tabs.append({"index": i, "title": title, "url": url, "active": is_active})
        return tabs

    # Developer tools methods
    def get_console_logs(self) -> list[dict[str, Any]]:
        """Get captured console logs."""
        return self._console_logs.copy()

    def clear_console_logs(self) -> None:
        """Clear captured console logs."""
        self._console_logs.clear()

    def get_network_requests(self) -> list[dict[str, Any]]:
        """Get captured network requests."""
        return self._network_requests.copy()

    def clear_network_requests(self) -> None:
        """Clear captured network requests."""
        self._network_requests.clear()
        self._request_map.clear()

    def get_page_errors(self) -> list[dict[str, Any]]:
        """Get captured page errors."""
        return self._page_errors.copy()

    def clear_page_errors(self) -> None:
        """Clear captured page errors."""
        self._page_errors.clear()

    async def get_interactive_elements(self) -> list[dict[str, Any]]:
        """Get all interactive elements with their bounding boxes.

        Recurses into open shadow roots and same-origin iframes so that
        elements hidden behind a shadow boundary or a same-origin frame are
        included alongside top-document elements.
        """
        js_code = """
        () => {
            const interactiveSelectors = [
                'a[href]',
                'button',
                'input:not([type="hidden"])',
                'select',
                'textarea',
                '[role="button"]',
                '[role="link"]',
                '[role="menuitem"]',
                '[role="tab"]',
                '[onclick]',
                '[tabindex]:not([tabindex="-1"])',
                'label[for]',
                '[contenteditable="true"]'
            ];

            const elements = [];
            const seen = new Set();

            function collect(root, offsetX, offsetY) {
                let nodes = [];
                for (const selector of interactiveSelectors) {
                    try {
                        nodes = nodes.concat(Array.from(root.querySelectorAll(selector)));
                    } catch (e) {}
                }
                for (const el of nodes) {
                    if (seen.has(el)) continue;
                    seen.add(el);

                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) continue;

                    const x = rect.x + offsetX;
                    const y = rect.y + offsetY;

                    if (y + rect.height < 0 || y > window.innerHeight) continue;
                    if (x + rect.width < 0 || x > window.innerWidth) continue;

                    let text = el.innerText?.trim()?.substring(0, 50) || '';
                    let placeholder = el.placeholder || '';
                    let ariaLabel = el.getAttribute('aria-label') || '';
                    let title = el.title || '';
                    let type = el.type || el.tagName.toLowerCase();
                    let href = el.href || '';

                    elements.push({
                        x: x,
                        y: y,
                        width: rect.width,
                        height: rect.height,
                        centerX: x + rect.width / 2,
                        centerY: y + rect.height / 2,
                        tag: el.tagName.toLowerCase(),
                        type: type,
                        text: text || placeholder || ariaLabel || title,
                        href: href,
                        id: el.id || null,
                        className: el.className || null
                    });
                }

                // Open shadow roots report coordinates in the same viewport space
                try {
                    for (const el of root.querySelectorAll('*')) {
                        if (el.shadowRoot) collect(el.shadowRoot, offsetX, offsetY);
                    }
                } catch (e) {}

                // Same-origin iframes: add the iframe's on-screen position as an offset
                try {
                    for (const frame of root.querySelectorAll('iframe')) {
                        try {
                            const doc = frame.contentDocument;
                            if (doc) {
                                const frect = frame.getBoundingClientRect();
                                collect(doc, offsetX + frect.x, offsetY + frect.y);
                            }
                        } catch (e) { /* cross-origin frame — skip */ }
                    }
                } catch (e) {}
            }

            collect(document, 0, 0);
            return elements;
        }
        """
        return cast("list[dict[str, Any]]", await self.page.evaluate(js_code))

    async def screenshot_with_som(self) -> tuple[bytes, dict[int, dict[str, Any]]]:
        """
        Take a screenshot and overlay Set of Marks (numbered bounding boxes).
        Returns the annotated image bytes and the element mapping.
        """
        global element_map

        screenshot_bytes = await self.page.screenshot(type="png")
        elements = await self.get_interactive_elements()

        img = PILImage.open(BytesIO(screenshot_bytes))
        draw = ImageDraw.Draw(img, "RGBA")

        font = _get_label_font()

        element_map = {}

        for idx, elem in enumerate(elements):
            element_id = idx + 1
            element_map[element_id] = elem

            x, y = elem["x"], elem["y"]
            w, h = elem["width"], elem["height"]

            # Draw semi-transparent box
            box_color = (255, 0, 0, 60)
            draw.rectangle([x, y, x + w, y + h], outline="red", width=2, fill=box_color)

            # Draw label
            label = str(element_id)
            label_bbox = draw.textbbox((0, 0), label, font=font)
            label_w = label_bbox[2] - label_bbox[0] + 6
            label_h = label_bbox[3] - label_bbox[1] + 4

            label_x = max(0, x)
            label_y = max(0, y - label_h - 2)

            draw.rectangle([label_x, label_y, label_x + label_w, label_y + label_h], fill="red")
            draw.text((label_x + 3, label_y + 2), label, fill="white", font=font)

        output = BytesIO()
        img.save(output, format="PNG")

        logger.debug(f"Captured screenshot with {len(element_map)} elements")
        return output.getvalue(), element_map


# Global browser manager instance
browser = BrowserManager()


def get_element_map() -> dict[int, dict[str, Any]]:
    """Get the current element map."""
    return element_map

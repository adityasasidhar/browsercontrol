"""
Browser lifecycle management with Set of Marks (SoM) annotation.
"""

import logging
from io import BytesIO
from pathlib import Path

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from PIL import Image as PILImage, ImageDraw, ImageFont

from browsercontrol.config import config

logger = logging.getLogger(__name__)

# Store element mapping for click-by-ID
element_map: dict[int, dict] = {}


class BrowserManager:
    """Manages the browser lifecycle and provides access to pages."""
    
    def __init__(self):
        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._started = False
    
    @property
    def is_started(self) -> bool:
        """Check if browser is started."""
        return self._started and self._context is not None
    
    async def start(self) -> None:
        """Start the browser with persistent context."""
        if self._started:
            logger.warning("Browser already started")
            return
        
        config.user_data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Starting browser with user data dir: {config.user_data_dir}")
        
        self._playwright = await async_playwright().start()
        
        # Build launch args
        args = ["--no-first-run", "--no-default-browser-check"]
        if config.extension_path and config.extension_path.exists():
            args.extend([
                f"--disable-extensions-except={config.extension_path}",
                f"--load-extension={config.extension_path}",
            ])
            logger.info(f"Loading extension from: {config.extension_path}")
        
        try:
            self._context = await self._playwright.chromium.launch_persistent_context(
                user_data_dir=str(config.user_data_dir),
                headless=config.headless,
                args=args,
                viewport={"width": config.viewport_width, "height": config.viewport_height},
            )
            
            # Get or create initial page
            if self._context.pages:
                self._page = self._context.pages[0]
            else:
                self._page = await self._context.new_page()
            
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
    
    async def ensure_started(self) -> None:
        """Ensure browser is started, restart if needed."""
        if not self.is_started:
            logger.info("Browser not started, starting now")
            await self.start()
    
    @property
    def page(self) -> Page:
        """Get the current active page."""
        if not self._page:
            raise RuntimeError("Browser not started. Call start() first.")
        return self._page
    
    async def get_interactive_elements(self) -> list[dict]:
        """Get all interactive elements with their bounding boxes."""
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
            
            for (const selector of interactiveSelectors) {
                for (const el of document.querySelectorAll(selector)) {
                    if (seen.has(el)) continue;
                    seen.add(el);
                    
                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) continue;
                    if (rect.bottom < 0 || rect.top > window.innerHeight) continue;
                    if (rect.right < 0 || rect.left > window.innerWidth) continue;
                    
                    let text = el.innerText?.trim()?.substring(0, 50) || '';
                    let placeholder = el.placeholder || '';
                    let ariaLabel = el.getAttribute('aria-label') || '';
                    let title = el.title || '';
                    let type = el.type || el.tagName.toLowerCase();
                    let href = el.href || '';
                    
                    elements.push({
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height,
                        centerX: rect.x + rect.width / 2,
                        centerY: rect.y + rect.height / 2,
                        tag: el.tagName.toLowerCase(),
                        type: type,
                        text: text || placeholder || ariaLabel || title,
                        href: href,
                        id: el.id || null,
                        className: el.className || null
                    });
                }
            }
            
            return elements;
        }
        """
        return await self.page.evaluate(js_code)
    
    async def screenshot_with_som(self) -> tuple[bytes, dict[int, dict]]:
        """
        Take a screenshot and overlay Set of Marks (numbered bounding boxes).
        Returns the annotated image bytes and the element mapping.
        """
        global element_map
        
        screenshot_bytes = await self.page.screenshot(type="png")
        elements = await self.get_interactive_elements()
        
        img = PILImage.open(BytesIO(screenshot_bytes))
        draw = ImageDraw.Draw(img, "RGBA")
        
        # Try to use a reasonable font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
        except Exception:
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except Exception:
                font = ImageFont.load_default()
        
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
            
            draw.rectangle(
                [label_x, label_y, label_x + label_w, label_y + label_h],
                fill="red"
            )
            draw.text((label_x + 3, label_y + 2), label, fill="white", font=font)
        
        output = BytesIO()
        img.save(output, format="PNG")
        
        logger.debug(f"Captured screenshot with {len(element_map)} elements")
        return output.getvalue(), element_map


# Global browser manager instance
browser = BrowserManager()


def get_element_map() -> dict[int, dict]:
    """Get the current element map."""
    return element_map

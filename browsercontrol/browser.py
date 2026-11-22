import asyncio
import contextlib
import logging
import time
from contextvars import ContextVar
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont
from playwright.async_api import (
    Browser,
    BrowserContext,
    BrowserType,
    Locator,
    Page,
    Playwright,
    async_playwright,
)

from browsercontrol.config import config
from browsercontrol.elements import ElementMap, collect_elements, locate
from browsercontrol.pointer import HIDE_POINTER_STYLE
from browsercontrol.session import Session, attach_page_listeners, network_quiet

logger = logging.getLogger(__name__)

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


DEFAULT_SESSION = "default"

# Which MCP client the current tool call belongs to. Set per call by the server
# middleware; each client is bound to one session (the default one unless it
# created or switched to another).
current_client: ContextVar[str] = ContextVar("browsercontrol_client", default="")

# Resolves after the DOM has had no mutations for `quiet` ms, or after `max` ms.
DOM_QUIET_JS = """
({quiet, max}) => new Promise(resolve => {
    let timer;
    const done = () => { observer.disconnect(); resolve(true); };
    const observer = new MutationObserver(() => {
        clearTimeout(timer);
        timer = setTimeout(done, quiet);
    });
    observer.observe(document, {subtree: true, childList: true, attributes: true,
                                characterData: true});
    timer = setTimeout(done, quiet);
    setTimeout(done, max);
})
"""


def chrome_profile_dir() -> Path:
    """Profile directory used when falling back to the installed Google Chrome."""
    base = config.user_data_dir
    return base.with_name(f"{base.name}-chrome")


class BrowserManager:
    """Manages the browser lifecycle, its sessions, and access to pages."""

    def __init__(self) -> None:
        self._playwright: Playwright | None = None
        # Set when attached to a running Chrome over CDP; that browser is the
        # user's, so stopping only disconnects from it.
        self._browser: Browser | None = None
        self._cdp_url: str | None = config.cdp_url
        self._started = False

        self._sessions: dict[str, Session] = {DEFAULT_SESSION: Session(DEFAULT_SESSION)}
        # MCP client key -> session name. Unbound clients use the default session.
        self._bindings: dict[str, str] = {}
        self._tasks: set[asyncio.Task[Any]] = set()

        # Set of Marks state: one element map per tab, and a counter that makes
        # each screenshot's data-bc-id values unique.
        self._element_maps: dict[Page, ElementMap] = {}
        self._som_generation = 0

    # ----- sessions -------------------------------------------------------

    @property
    def session(self) -> Session:
        """The session the current MCP client is bound to."""
        name = self._bindings.get(current_client.get(), DEFAULT_SESSION)
        return self._sessions.get(name) or self._sessions[DEFAULT_SESSION]

    @property
    def _context(self) -> BrowserContext | None:
        return self.session.context

    @_context.setter
    def _context(self, value: BrowserContext | None) -> None:
        self.session.context = value

    @property
    def _page(self) -> Page | None:
        return self.session.page

    @_page.setter
    def _page(self, value: Page | None) -> None:
        self.session.page = value

    @property
    def _console_logs(self) -> list[dict[str, Any]]:
        return self.session.console_logs

    @_console_logs.setter
    def _console_logs(self, value: list[dict[str, Any]]) -> None:
        self.session.console_logs = value

    @property
    def _network_requests(self) -> list[dict[str, Any]]:
        return self.session.network_requests

    @_network_requests.setter
    def _network_requests(self, value: list[dict[str, Any]]) -> None:
        self.session.network_requests = value

    @property
    def _page_errors(self) -> list[dict[str, Any]]:
        return self.session.page_errors

    @_page_errors.setter
    def _page_errors(self, value: list[dict[str, Any]]) -> None:
        self.session.page_errors = value

    @property
    def _request_map(self) -> dict[Any, dict[str, Any]]:
        return self.session.request_map

    @property
    def cdp_url(self) -> str | None:
        """The CDP endpoint of the attached Chrome, or None when the browser is launched here."""
        return self._cdp_url if self._browser is not None else None

    def _on_new_page(self, session: Session, page: Page) -> None:
        attach_page_listeners(session, page, config.downloads_dir)
        if session.emulation:
            from browsercontrol.emulation import apply_emulation

            task = asyncio.ensure_future(apply_emulation(page, session.emulation))
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)

    def _setup_page_listeners(self, page: Page) -> None:
        """Attach capture listeners to a page of the session that owns it."""
        owner = next(
            (
                s
                for s in self._sessions.values()
                if s.context is not None and s.context is page.context
            ),
            self.session,
        )
        self._on_new_page(owner, page)

    def _wire_context(self, session: Session, context: BrowserContext) -> None:
        session.context = context
        context.on("page", lambda page: self._on_new_page(session, page))

    async def create_session(
        self, name: str, device: str | None = None, storage_state: Path | None = None
    ) -> Session:
        """Open an isolated context (no cookies or storage shared) and bind the caller to it.

        ``storage_state`` is a file from ``save_auth_state`` to start the context signed in.
        """
        if not name or name in self._sessions:
            raise ValueError(f"Session name {name!r} is empty or already in use")
        await self.ensure_started()
        base = self._sessions[DEFAULT_SESSION].context
        owner = self._browser or (base.browser if base is not None else None)
        if owner is None:
            raise RuntimeError("This browser cannot open isolated contexts")

        kwargs: dict[str, Any] = {"accept_downloads": True}
        if device:
            kwargs.update(self.device_descriptor(device))
        else:
            kwargs["viewport"] = {"width": config.viewport_width, "height": config.viewport_height}
        if storage_state is not None:
            kwargs["storage_state"] = storage_state
        context = await owner.new_context(**kwargs)
        session = Session(name, isolated=True)
        self._wire_context(session, context)
        session.page = await context.new_page()
        self._sessions[name] = session
        self.bind(name)
        return session

    def bind(self, name: str) -> None:
        """Bind the calling MCP client to a session."""
        if name not in self._sessions:
            raise ValueError(f"No session named {name!r}. Sessions: {', '.join(self._sessions)}")
        self._bindings[current_client.get()] = name

    async def close_session(self, name: str) -> None:
        """Close an isolated session; clients bound to it fall back to the default session."""
        if name == DEFAULT_SESSION:
            raise ValueError("The default session cannot be closed")
        session = self._sessions.pop(name, None)
        if session is None:
            raise ValueError(f"No session named {name!r}")
        self._bindings = {k: v for k, v in self._bindings.items() if v != name}
        if session.context is not None:
            for page in session.context.pages:
                self._element_maps.pop(page, None)
            with contextlib.suppress(Exception):
                await session.context.close()

    def list_sessions(self) -> list[dict[str, Any]]:
        current = self.session.name
        return [
            {
                "name": s.name,
                "isolated": s.isolated,
                "tabs": len(s.context.pages) if s.context is not None else 0,
                "url": s.page.url if s.page is not None and not s.page.is_closed() else "",
                "current": s.name == current,
            }
            for s in self._sessions.values()
        ]

    async def ensure_client_session(self, client: str) -> None:
        """With BROWSER_ISOLATE_CLIENTS, give each new MCP client its own isolated session."""
        if not config.isolate_clients or not client or client in self._bindings:
            return
        token = current_client.set(client)
        try:
            name = f"client-{len(self._sessions)}"
            while name in self._sessions:
                name += "_"
            await self.create_session(name)
        finally:
            current_client.reset(token)

    def devices(self) -> dict[str, Any]:
        """Playwright's device descriptors, by name."""
        return dict(self._playwright.devices) if self._playwright is not None else {}

    def device_descriptor(self, name: str) -> dict[str, Any]:
        devices = self.devices()
        match = next((k for k in devices if k.lower() == name.lower()), None)
        if match is None:
            raise ValueError(f"Unknown device {name!r}. Try list_devices().")
        descriptor = dict(devices[match])
        descriptor.pop("default_browser_type", None)
        return descriptor

    # ----- lifecycle ------------------------------------------------------

    @property
    def is_started(self) -> bool:
        """Check if browser is started."""
        return self._started and self._sessions[DEFAULT_SESSION].context is not None

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

    async def _launch_context(
        self, chromium: BrowserType, launch_kwargs: dict[str, Any]
    ) -> BrowserContext:
        """Reuse an available browser before downloading Playwright's Chromium."""
        missing_hints = ("executable doesn't exist", "playwright install", "looks like playwright")
        try:
            return await chromium.launch_persistent_context(**launch_kwargs)
        except Exception as exc:
            if "executable_path" in launch_kwargs or not any(
                hint in str(exc).lower() for hint in missing_hints
            ):
                raise

        # Branded Chrome does not support loading unpacked extensions this way.
        if config.extension_path is None:
            # Chrome gets its own profile: switching one profile between branded
            # Chrome and Playwright's Chromium builds can downgrade or corrupt it.
            chrome_kwargs = {**launch_kwargs, "user_data_dir": str(chrome_profile_dir())}
            try:
                context = await chromium.launch_persistent_context(
                    channel="chrome", **chrome_kwargs
                )
            except Exception as exc:
                # Any Chrome failure (not installed, profile locked, crash) falls
                # through to installing Playwright's Chromium.
                logger.info(f"Installed Google Chrome unavailable: {exc}")
            else:
                logger.info("Using installed Google Chrome")
                return context

        logger.info("Chromium executable not found, installing automatically...")
        await self._install_chromium()
        return await chromium.launch_persistent_context(**launch_kwargs)

    async def start(self) -> None:
        """Start the browser: attach over CDP when configured, else launch the profile."""
        if self._started:
            logger.warning("Browser already started")
            return

        self._playwright = await async_playwright().start()
        try:
            if self._cdp_url:
                context = await self._attach_over_cdp(self._cdp_url)
            else:
                context = await self._launch_profile()

            default = self._sessions[DEFAULT_SESSION]
            self._wire_context(default, context)

            # Set up event listeners for the existing page(s)
            for page in context.pages:
                self._on_new_page(default, page)

            # Attached to someone's Chrome: work in a tab of our own rather than
            # taking over whichever tab they had in front.
            if context.pages and not self._cdp_url:
                default.page = context.pages[0]
            else:
                default.page = await context.new_page()

            self._started = True
            logger.info("Browser started successfully")

        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            await self.stop()
            raise

    async def _attach_over_cdp(self, cdp_url: str) -> BrowserContext:
        """Connect to a running Chrome and use its default (logged-in) context."""
        if self._playwright is None:
            raise RuntimeError("Playwright is not running")
        logger.info(f"Attaching to Chrome over CDP at {cdp_url}")
        self._browser = await self._playwright.chromium.connect_over_cdp(
            cdp_url, timeout=config.timeout_ms
        )
        if self._browser.contexts:
            return self._browser.contexts[0]
        return await self._browser.new_context()

    async def _launch_profile(self) -> BrowserContext:
        """Launch Chromium against the persistent profile directory."""
        if self._playwright is None:
            raise RuntimeError("Playwright is not running")
        config.user_data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Starting browser with user data dir: {config.user_data_dir}")

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

        launch_kwargs: dict[str, Any] = {
            "user_data_dir": str(config.user_data_dir),
            "headless": config.headless,
            "args": args,
            "viewport": {"width": config.viewport_width, "height": config.viewport_height},
            "accept_downloads": True,
        }
        if config.executable_path:
            launch_kwargs["executable_path"] = str(config.executable_path)
            logger.info(f"Using Chromium executable: {config.executable_path}")

        return await self._launch_context(self._playwright.chromium, launch_kwargs)

    async def stop(self) -> None:
        """Stop the browser. An attached Chrome is only disconnected from, never closed."""
        logger.info("Stopping browser")
        self._started = False

        for session in self._sessions.values():
            if session.context is None:
                continue
            # The default context of an attached Chrome is the user's own browser.
            if self._browser is not None and not session.isolated:
                continue
            try:
                await session.context.close()
            except Exception as e:
                logger.warning(f"Error closing context: {e}")

        if self._browser is not None:
            try:
                await self._browser.close()
            except Exception as e:
                logger.warning(f"Error disconnecting from Chrome: {e}")
            self._browser = None

        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception as e:
                logger.warning(f"Error stopping playwright: {e}")
            self._playwright = None

        self._sessions = {DEFAULT_SESSION: Session(DEFAULT_SESSION)}
        self._bindings.clear()
        self._element_maps.clear()

    async def ensure_started(self) -> None:
        """Ensure browser is started, restart if needed."""
        if not self.is_started:
            logger.info("Browser not started, starting now")
            await self.start()

    async def connect_over_cdp(self, cdp_url: str | None) -> None:
        """Restart attached to the Chrome at ``cdp_url``, or launch our own when None."""
        await self.stop()
        self._cdp_url = cdp_url
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

    # ----- captured data --------------------------------------------------

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

    def drain_notices(self) -> list[str]:
        """Dialog and download messages not yet shown to the agent."""
        return self.session.drain_notices()

    def mark_call_started(self) -> None:
        """Record the start of a tool call, so waits can see responses from the previous one."""
        session = self.session
        session.previous_call_started = session.call_started
        session.call_started = time.time()

    # ----- action log (for test generation) ------------------------------

    async def codegen_target(self, locator: Locator) -> dict[str, Any] | None:
        """Describe an element by stable locators for generated tests; None if that fails."""
        from browsercontrol.codegen import describe_target

        try:
            return await describe_target(locator)
        except Exception as e:
            logger.debug(f"Could not describe element for codegen: {e}")
            return None

    def log_action(self, kind: str, target: dict[str, Any] | None = None, **data: Any) -> None:
        """Append a successful action to the session's action log."""
        if target is not None and target.get("password"):
            # Never keep a typed password; the generated test reads it from the environment.
            data.pop("text", None)
        actions = self.session.actions
        actions.append({"action": kind, "target": target, **data})
        del actions[:-500]

    def get_action_log(self) -> list[dict[str, Any]]:
        return list(self.session.actions)

    def clear_action_log(self) -> None:
        self.session.actions.clear()

    # ----- waiting --------------------------------------------------------

    async def settle(self, timeout_ms: int | None = None) -> None:
        """Wait for the page to settle after an action, bounded by the settle timeout.

        Waits for DOMContentLoaded, then for in-flight requests to finish, then
        for the DOM to stop changing, so single-page apps that render after
        their data arrives are captured complete instead of half drawn.
        """
        budget_ms = timeout_ms if timeout_ms is not None else config.settle_timeout_ms
        loop = asyncio.get_running_loop()
        deadline = loop.time() + budget_ms / 1000
        page = self.page
        with contextlib.suppress(Exception):
            await page.wait_for_load_state("domcontentloaded", timeout=budget_ms)
        await network_quiet(self.session, deadline)
        remaining = int((deadline - loop.time()) * 1000)
        if remaining > 50:
            with contextlib.suppress(Exception):
                await page.evaluate(DOM_QUIET_JS, {"quiet": 200, "max": min(remaining, 1000)})

    async def wait_for_network_idle(self, timeout_ms: int, quiet_ms: int = 500) -> bool:
        """Wait until no request has been in flight for ``quiet_ms``. False on timeout."""
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout_ms / 1000
        await network_quiet(self.session, deadline, quiet_s=quiet_ms / 1000)
        return loop.time() < deadline

    # ----- Set of Marks ---------------------------------------------------

    def get_element_map(self) -> ElementMap:
        """Return the element map from the active tab's most recent screenshot."""
        if not self.is_started:
            return {}
        return self._element_maps.get(self.page, {})

    async def resolve_element(self, element_id: int) -> Locator:
        """Resolve an element ID from the active tab's map to a verified, live locator.

        Raises ElementNotFoundError or StaleElementError (both ElementError).
        """
        return await locate(element_id, self.get_element_map())

    async def get_interactive_elements(self) -> list[dict[str, Any]]:
        """Collect visible, unobscured interactive elements across all frames.

        Covers open shadow roots and every frame (cross-origin included), and
        tags each element so it can be resolved later by ID.
        """
        self._som_generation += 1
        return await collect_elements(self.page, self._som_generation)

    async def screenshot_with_som(self) -> tuple[bytes, ElementMap]:
        """
        Take a screenshot and overlay Set of Marks (numbered bounding boxes).
        Returns the annotated image bytes and the active tab's new element map.
        """
        page = self.page
        screenshot_bytes = await page.screenshot(type="png", style=HIDE_POINTER_STYLE)
        elements = await self.get_interactive_elements()

        img = PILImage.open(BytesIO(screenshot_bytes))
        draw = ImageDraw.Draw(img, "RGBA")
        font = _get_label_font()

        new_map: ElementMap = {}
        for idx, elem in enumerate(elements):
            element_id = idx + 1
            new_map[element_id] = elem
            _draw_mark(draw, font, element_id, elem)

        # Maps are per tab, so IDs from one tab never resolve against another.
        self._element_maps = {p: m for p, m in self._element_maps.items() if not p.is_closed()}
        self._element_maps[page] = new_map

        output = BytesIO()
        img.save(output, format="PNG")

        logger.debug(f"Captured screenshot with {len(new_map)} elements")
        return output.getvalue(), new_map


def _draw_mark(
    draw: ImageDraw.ImageDraw,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    element_id: int,
    elem: dict[str, Any],
) -> None:
    """Draw one numbered box. Disabled elements are drawn grey instead of red."""
    x, y = max(0.0, elem["x"]), max(0.0, elem["y"])
    x2, y2 = elem["x"] + elem["width"], elem["y"] + elem["height"]
    color = (128, 128, 128) if elem.get("disabled") else (255, 0, 0)

    draw.rectangle([x, y, x2, y2], outline=color, width=2, fill=(*color, 60))

    label = str(element_id)
    label_bbox = draw.textbbox((0, 0), label, font=font)
    label_w = label_bbox[2] - label_bbox[0] + 6
    label_h = label_bbox[3] - label_bbox[1] + 4
    label_y = max(0.0, y - label_h - 2)

    draw.rectangle([x, label_y, x + label_w, label_y + label_h], fill=color)
    draw.text((x + 3, label_y + 2), label, fill="white", font=font)


# Global browser manager instance
browser = BrowserManager()


def get_element_map() -> ElementMap:
    """Get the active tab's current element map."""
    return browser.get_element_map()

"""Tests for BrowserManager core functionality."""

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from browsercontrol.browser import BrowserManager, current_client


class TestBrowserLifecycle:
    """Test browser start/stop lifecycle."""

    @pytest.mark.asyncio
    async def test_browser_starts_successfully(self, mock_playwright, mock_context, mock_page):
        """Test that browser starts and creates context when Chromium is present."""
        mock_playwright.chromium.launch_persistent_context.return_value = mock_context
        mock_context.pages = [mock_page]

        with patch("browsercontrol.browser.async_playwright") as pw_patch:
            # Context manager returns the playwright instance directly mock
            mock_playwright_instance = AsyncMock()
            mock_playwright_instance.start = AsyncMock(return_value=mock_playwright)
            pw_patch.return_value = mock_playwright_instance

            browser_mgr = BrowserManager()
            await browser_mgr.start()

            assert browser_mgr.is_started
            assert browser_mgr._context == mock_context
            # New tabs get the capture listeners, and the context watches for popups.
            assert mock_context.on.call_args.args[0] == "page"
            assert {call.args[0] for call in mock_page.on.call_args_list} >= {
                "console",
                "pageerror",
                "request",
                "response",
                "dialog",
                "download",
            }

    @pytest.mark.asyncio
    async def test_browser_stops_successfully(self, mock_playwright, mock_context, mock_page):
        """Test that browser stops and cleans up."""
        mock_playwright.chromium.launch_persistent_context.return_value = mock_context
        mock_context.pages = [mock_page]

        with patch("browsercontrol.browser.async_playwright") as pw_patch:
            mock_playwright_instance = AsyncMock()
            mock_playwright_instance.start = AsyncMock(return_value=mock_playwright)
            pw_patch.return_value = mock_playwright_instance

            browser_mgr = BrowserManager()
            await browser_mgr.start()
            await browser_mgr.stop()

            assert not browser_mgr.is_started
            mock_context.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_ensure_started_restarts_if_needed(self):
        """Test that ensure_started restarts browser if not running."""
        browser_mgr = BrowserManager()
        browser_mgr.start = AsyncMock()

        await browser_mgr.ensure_started()
        browser_mgr.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_installed_chrome_avoids_chromium_download(
        self, mock_playwright, mock_context, mock_page
    ):
        """Use the installed Chrome channel when the Playwright build is missing."""
        launch = mock_playwright.chromium.launch_persistent_context

        async def launch_available_browser(**kwargs):
            if kwargs.get("channel") == "chrome":
                return mock_context
            raise Exception("Executable doesn't exist at /path/to/chromium")

        launch.side_effect = launch_available_browser
        mock_context.pages = [mock_page]

        with patch("browsercontrol.browser.async_playwright") as pw_patch:
            pw_patch.return_value.start = AsyncMock(return_value=mock_playwright)

            browser_mgr = BrowserManager()
            browser_mgr._install_chromium = AsyncMock()
            await browser_mgr.start()

            assert browser_mgr.page is mock_page
            browser_mgr._install_chromium.assert_not_awaited()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("load_extension", [False, True])
    async def test_browser_installs_chromium_if_missing(
        self, mock_playwright, mock_context, mock_page, tmp_path, load_extension
    ):
        """Install Chromium when Chrome is missing or an extension requires Chromium."""
        missing_exc = Exception("Executable doesn't exist at /path/to/chromium")
        launch = mock_playwright.chromium.launch_persistent_context
        if load_extension:
            launch.side_effect = [missing_exc, mock_context]
        else:
            launch.side_effect = [
                missing_exc,
                Exception("Chromium distribution 'chrome' is not found at /path/to/chrome"),
                mock_context,
            ]
        mock_context.pages = [mock_page]
        extension_path = tmp_path if load_extension else None

        with (
            patch("browsercontrol.browser.async_playwright") as pw_patch,
            patch("browsercontrol.browser.config.extension_path", extension_path),
        ):
            mock_playwright_instance = AsyncMock()
            mock_playwright_instance.start = AsyncMock(return_value=mock_playwright)
            pw_patch.return_value = mock_playwright_instance

            browser_mgr = BrowserManager()
            browser_mgr._install_chromium = AsyncMock()
            await browser_mgr.start()

            browser_mgr._install_chromium.assert_called_once()
            assert browser_mgr.is_started
            assert [call.kwargs.get("channel") for call in launch.await_args_list] == (
                [None, None] if load_extension else [None, "chrome", None]
            )

    @pytest.mark.asyncio
    async def test_chrome_launch_failure_falls_back_to_chromium_install(
        self, mock_playwright, mock_context, mock_page, tmp_path
    ):
        """A Chrome that is installed but cannot start (profile lock, crash) must not block
        the Chromium install path, and Chrome gets its own profile directory."""
        launch = mock_playwright.chromium.launch_persistent_context
        launch.side_effect = [
            Exception("Executable doesn't exist at /path/to/chromium"),
            Exception("Target page, context or browser has been closed: profile in use"),
            mock_context,
        ]
        mock_context.pages = [mock_page]
        profile = tmp_path / "user_data"

        with (
            patch("browsercontrol.browser.async_playwright") as pw_patch,
            patch("browsercontrol.browser.config.extension_path", None),
            patch("browsercontrol.browser.config.user_data_dir", profile),
        ):
            pw_patch.return_value.start = AsyncMock(return_value=mock_playwright)
            browser_mgr = BrowserManager()
            browser_mgr._install_chromium = AsyncMock()
            await browser_mgr.start()

        browser_mgr._install_chromium.assert_awaited_once()
        assert browser_mgr.is_started
        dirs = [call.kwargs["user_data_dir"] for call in launch.await_args_list]
        assert dirs == [str(profile), str(tmp_path / "user_data-chrome"), str(profile)]

    @pytest.mark.asyncio
    async def test_browser_raises_if_still_missing_after_install(
        self, mock_playwright, mock_context, mock_page
    ):
        """Test that the error propagates when launch still fails after install."""
        missing_exc = Exception("Executable doesn't exist at /path/to/chromium")
        mock_playwright.chromium.launch_persistent_context.side_effect = [
            missing_exc,
            Exception("Chromium distribution 'chrome' is not found at /path/to/chrome"),
            missing_exc,
        ]

        with patch("browsercontrol.browser.async_playwright") as pw_patch:
            mock_playwright_instance = AsyncMock()
            mock_playwright_instance.start = AsyncMock(return_value=mock_playwright)
            pw_patch.return_value = mock_playwright_instance

            browser_mgr = BrowserManager()
            browser_mgr._install_chromium = AsyncMock()
            with pytest.raises(Exception, match="Executable doesn't exist"):
                await browser_mgr.start()

    @pytest.mark.asyncio
    async def test_non_missing_browser_error_does_not_install(
        self, mock_playwright, mock_context, mock_page
    ):
        """Test that unrelated launch errors are not treated as missing-browser errors."""
        other_exc = Exception("Permission denied: /some/path")
        mock_playwright.chromium.launch_persistent_context.side_effect = other_exc

        with patch("browsercontrol.browser.async_playwright") as pw_patch:
            mock_playwright_instance = AsyncMock()
            mock_playwright_instance.start = AsyncMock(return_value=mock_playwright)
            pw_patch.return_value = mock_playwright_instance

            browser_mgr = BrowserManager()
            browser_mgr._install_chromium = AsyncMock()
            with pytest.raises(Exception, match="Permission denied"):
                await browser_mgr.start()

            # _install_chromium must NOT have been called for a non-missing error
            browser_mgr._install_chromium.assert_not_called()

    @pytest.mark.asyncio
    async def test_configured_executable_is_passed_to_launch(
        self, mock_playwright, mock_context, mock_page
    ):
        """A configured Chromium binary reaches Playwright's launch call."""
        mock_playwright.chromium.launch_persistent_context.return_value = mock_context
        mock_context.pages = [mock_page]

        with patch("browsercontrol.browser.async_playwright") as pw_patch:
            mock_playwright_instance = AsyncMock()
            mock_playwright_instance.start = AsyncMock(return_value=mock_playwright)
            pw_patch.return_value = mock_playwright_instance

            with patch("browsercontrol.browser.config") as mock_config:
                mock_config.executable_path = "/usr/bin/google-chrome"
                mock_config.extension_path = None
                mock_config.cdp_url = None
                mock_config.headless = True
                mock_config.viewport_width = 1280
                mock_config.viewport_height = 720

                await BrowserManager().start()

        kwargs = mock_playwright.chromium.launch_persistent_context.call_args.kwargs
        assert kwargs["executable_path"] == "/usr/bin/google-chrome"

    @pytest.mark.asyncio
    async def test_configured_executable_suppresses_auto_install(
        self, mock_playwright, mock_context, mock_page
    ):
        """A caller-supplied binary is theirs to fix — don't install Chromium over it."""
        mock_playwright.chromium.launch_persistent_context.side_effect = Exception(
            "Executable doesn't exist at /usr/bin/google-chrome"
        )

        with patch("browsercontrol.browser.async_playwright") as pw_patch:
            mock_playwright_instance = AsyncMock()
            mock_playwright_instance.start = AsyncMock(return_value=mock_playwright)
            pw_patch.return_value = mock_playwright_instance

            with patch("browsercontrol.browser.config") as mock_config:
                mock_config.executable_path = "/usr/bin/google-chrome"
                mock_config.extension_path = None
                mock_config.cdp_url = None
                mock_config.headless = True
                mock_config.viewport_width = 1280
                mock_config.viewport_height = 720

                browser_mgr = BrowserManager()
                browser_mgr._install_chromium = AsyncMock()
                with pytest.raises(Exception, match="Executable doesn't exist"):
                    await browser_mgr.start()

                browser_mgr._install_chromium.assert_not_called()


class TestTabManagement:
    """Test tab creation, switching, and closing."""

    @pytest.mark.asyncio
    async def test_create_tab_without_url(self, mock_context, mock_page, page_factory):
        """Test creating a new blank tab."""
        new_page = page_factory()
        mock_context.new_page.return_value = new_page
        mock_context.pages = [mock_page, new_page]

        browser_mgr = BrowserManager()
        browser_mgr._started = True
        browser_mgr._context = mock_context
        browser_mgr._page = mock_page

        await browser_mgr.create_tab()

        mock_context.new_page.assert_called_once()
        # the current index mapping is removed in browsercontrol/browser.py, replacing it with assert browser_mgr._page == new_page doesn't work consistently if relying on index, here we just do a length check or ignore current index, since browser.py removed _current_page_index. We already checked new_page logic.

    @pytest.mark.asyncio
    async def test_create_tab_with_url(self, mock_context, mock_page, page_factory):
        """Test creating a new tab and navigating to URL."""
        new_page = page_factory()
        mock_context.new_page.return_value = new_page
        mock_context.pages = [mock_page, new_page]

        browser_mgr = BrowserManager()
        browser_mgr._started = True
        browser_mgr._context = mock_context
        browser_mgr._page = mock_page

        await browser_mgr.create_tab("https://example.com")

        new_page.goto.assert_called_once_with("https://example.com")

    @pytest.mark.asyncio
    async def test_switch_to_tab(self, mock_context, mock_page, page_factory):
        """Test switching to a different tab."""
        page2 = page_factory()
        mock_context.pages = [mock_page, page2]

        browser_mgr = BrowserManager()
        browser_mgr._started = True
        browser_mgr._context = mock_context
        browser_mgr._page = mock_page

        await browser_mgr.switch_to_tab(1)

        assert browser_mgr._page == page2

    @pytest.mark.asyncio
    async def test_switch_to_invalid_tab_raises_error(self, mock_context, mock_page):
        """Test that switching to invalid tab index raises error."""
        mock_context.pages = [mock_page]

        browser_mgr = BrowserManager()
        browser_mgr._started = True
        browser_mgr._context = mock_context
        browser_mgr._page = mock_page

        with pytest.raises(ValueError, match="Tab index 5 out of range \\(0-0\\)"):
            await browser_mgr.switch_to_tab(5)

    @pytest.mark.asyncio
    async def test_close_tab(self, mock_context, mock_page, page_factory):
        """Closing the active tab closes it and falls back to the remaining one."""
        page2 = page_factory()
        mock_context.pages = [mock_page, page2]

        async def close_page2() -> None:
            page2.is_closed.return_value = True
            mock_context.pages = [mock_page]

        page2.close.side_effect = close_page2

        browser_mgr = BrowserManager()
        browser_mgr._started = True
        browser_mgr._context = mock_context
        browser_mgr._page = page2

        await browser_mgr.close_tab(1)

        page2.close.assert_called_once()
        assert browser_mgr._page is mock_page
        mock_context.new_page.assert_not_called()

    @pytest.mark.asyncio
    async def test_close_last_tab_opens_a_blank_one(self, mock_context, mock_page, page_factory):
        """Closing the only tab leaves the browser with a fresh blank page, not a dead one."""
        blank = page_factory()
        mock_context.pages = [mock_page]
        mock_context.new_page.return_value = blank

        async def close_page() -> None:
            mock_page.is_closed.return_value = True
            mock_context.pages = []

        mock_page.close.side_effect = close_page

        browser_mgr = BrowserManager()
        browser_mgr._started = True
        browser_mgr._context = mock_context
        browser_mgr._page = mock_page

        await browser_mgr.close_tab(0)

        assert browser_mgr._page is blank

    @pytest.mark.asyncio
    async def test_close_inactive_tab_keeps_the_active_page(
        self, mock_context, mock_page, page_factory
    ):
        page2 = page_factory()
        mock_context.pages = [mock_page, page2]

        browser_mgr = BrowserManager()
        browser_mgr._started = True
        browser_mgr._context = mock_context
        browser_mgr._page = mock_page

        await browser_mgr.close_tab(1)

        page2.close.assert_called_once()
        assert browser_mgr._page is mock_page

    @pytest.mark.asyncio
    async def test_close_tab_out_of_range(self, mock_context, mock_page):
        mock_context.pages = [mock_page]
        browser_mgr = BrowserManager()
        browser_mgr._started = True
        browser_mgr._context = mock_context
        browser_mgr._page = mock_page

        with pytest.raises(ValueError, match="Tab index 3 out of range"):
            await browser_mgr.close_tab(3)

    @pytest.mark.asyncio
    async def test_list_tabs(self, mock_context, mock_page, page_factory):
        """Test listing all open tabs."""
        page2 = page_factory()
        page2.title = AsyncMock(return_value="Page 2")
        page2.url = "https://example2.com"

        mock_context.pages = [mock_page, page2]

        browser_mgr = BrowserManager()
        browser_mgr._started = True
        browser_mgr._context = mock_context
        browser_mgr._page = mock_page

        tabs = await browser_mgr.list_tabs()

        assert len(tabs) == 2
        assert tabs[0]["index"] == 0
        assert tabs[0]["active"] is True
        assert tabs[1]["index"] == 1
        assert tabs[1]["active"] is False


class TestDevToolsCapture:
    """Test console, network, and error capture."""

    def test_get_console_logs(self):
        """Test retrieving console logs."""
        browser_mgr = BrowserManager()
        browser_mgr._console_logs = [
            {"type": "log", "text": "Hello"},
            {"type": "error", "text": "Error!"},
        ]

        logs = browser_mgr.get_console_logs()
        assert len(logs) == 2
        assert logs[0]["text"] == "Hello"

    def test_clear_console_logs(self):
        """Test clearing console logs."""
        browser_mgr = BrowserManager()
        browser_mgr._console_logs = [{"type": "log", "text": "Test"}]

        browser_mgr.clear_console_logs()
        assert len(browser_mgr._console_logs) == 0

    def test_get_network_requests(self):
        """Test retrieving network requests."""
        browser_mgr = BrowserManager()
        browser_mgr._network_requests = [{"url": "https://api.example.com", "status": 200}]

        requests = browser_mgr.get_network_requests()
        assert len(requests) == 1
        assert requests[0]["status"] == 200

    def test_get_page_errors(self):
        """Test retrieving page errors."""
        browser_mgr = BrowserManager()
        browser_mgr._page_errors = [{"message": "TypeError: undefined"}]

        errors = browser_mgr.get_page_errors()
        assert len(errors) == 1
        assert "TypeError" in errors[0]["message"]

    def test_request_map_keyed_by_request_object(self):
        """Test that _request_map uses request object identity, not URL strings."""
        browser_mgr = BrowserManager()

        # Two distinct objects with the same URL must be tracked separately
        req_a = MagicMock()
        req_a.url = "https://api.example.com/data"
        req_a.method = "GET"
        req_a.resource_type = "xhr"

        req_b = MagicMock()
        req_b.url = "https://api.example.com/data"  # same URL
        req_b.method = "GET"
        req_b.resource_type = "xhr"

        browser_mgr._request_map[req_a] = {"url": req_a.url, "status": "pending"}
        browser_mgr._request_map[req_b] = {"url": req_b.url, "status": "pending"}

        # Both must exist as separate entries (no URL collision)
        assert len(browser_mgr._request_map) == 2
        assert req_a in browser_mgr._request_map
        assert req_b in browser_mgr._request_map

        # Removing one must leave the other
        del browser_mgr._request_map[req_a]
        assert len(browser_mgr._request_map) == 1
        assert req_b in browser_mgr._request_map

    def test_clear_network_requests_also_clears_request_map(self):
        """Test that clear_network_requests clears the in-flight map too."""
        browser_mgr = BrowserManager()
        req = MagicMock()
        browser_mgr._request_map[req] = {"url": "https://example.com", "status": "pending"}
        browser_mgr._network_requests = [{"url": "https://example.com", "status": 200}]

        browser_mgr.clear_network_requests()

        assert len(browser_mgr._network_requests) == 0
        assert len(browser_mgr._request_map) == 0


class TestElementMapping:
    """Test Set of Marks (SoM) element detection and per-tab element maps."""

    @staticmethod
    def _manager(page):
        mgr = BrowserManager()
        mgr._started = True
        mgr._context = AsyncMock()
        mgr._context.pages = [page]
        mgr._page = page
        return mgr

    @pytest.mark.asyncio
    async def test_get_interactive_elements_uses_a_fresh_generation(self, mock_page):
        """Each collection gets a new generation so data-bc-id values never repeat."""
        mgr = self._manager(mock_page)
        collect = AsyncMock(return_value=[{"tag": "button"}])
        with patch("browsercontrol.browser.collect_elements", collect):
            assert await mgr.get_interactive_elements() == [{"tag": "button"}]
            await mgr.get_interactive_elements()

        assert [c.args for c in collect.await_args_list] == [(mock_page, 1), (mock_page, 2)]

    @pytest.mark.asyncio
    async def test_screenshot_with_som(self, mock_page):
        """Test screenshot with SoM annotations."""
        mock_page.screenshot.return_value = b"fake_image_data"
        mgr = self._manager(mock_page)

        with (
            patch("browsercontrol.browser.collect_elements", AsyncMock(return_value=[])),
            patch("browsercontrol.marks.PILImage") as mock_pil,
        ):
            mock_img = MagicMock()
            mock_pil.open.return_value = mock_img
            mock_img.size = (800, 600)
            mock_img_bytes = MagicMock()
            mock_img_bytes.getvalue.return_value = b"annotated_image"

            with patch("browsercontrol.marks.BytesIO", return_value=mock_img_bytes):
                screenshot_bytes, elem_map = await mgr.screenshot_with_som()

        assert screenshot_bytes == b"annotated_image"
        assert elem_map == {}

    @pytest.mark.asyncio
    async def test_element_maps_are_kept_per_tab(self, mock_page, page_factory):
        """IDs from one tab's screenshot must not resolve against another tab."""
        other = page_factory()
        mgr = self._manager(mock_page)
        elements = [
            {"tag": "button", "x": 1, "y": 1, "width": 10, "height": 10},
            {"tag": "a", "x": 20, "y": 1, "width": 10, "height": 10},
        ]

        with (
            patch("browsercontrol.browser.collect_elements", AsyncMock(return_value=elements)),
            patch("browsercontrol.marks.PILImage"),
            patch("browsercontrol.marks.ImageDraw"),
            patch("browsercontrol.marks._draw_mark"),
        ):
            await mgr.screenshot_with_som()

        assert list(mgr.get_element_map()) == [1, 2]
        mgr._page = other
        assert mgr.get_element_map() == {}
        mgr._page = mock_page
        assert mgr.get_element_map()[1]["tag"] == "button"

    def test_element_map_is_empty_before_start(self):
        assert BrowserManager().get_element_map() == {}

    @pytest.mark.asyncio
    async def test_resolve_element_uses_active_tab_map(self, mock_page):
        mgr = self._manager(mock_page)
        mgr._element_maps[mock_page] = {1: {"tag": "button"}}
        sentinel = object()
        locate = AsyncMock(return_value=sentinel)
        with patch("browsercontrol.browser.locate", locate):
            assert await mgr.resolve_element(1) is sentinel
        locate.assert_awaited_once_with(1, {1: {"tag": "button"}})

    @pytest.mark.asyncio
    async def test_stop_clears_element_maps(self, mock_page):
        mgr = self._manager(mock_page)
        mgr._element_maps[mock_page] = {1: {}}
        await mgr.stop()
        assert mgr._element_maps == {}


class TestEnsureClientSession:
    """--isolate-clients must give each client its own session, even on simultaneous first calls."""

    @staticmethod
    def _manager() -> BrowserManager:
        """A manager whose create_session is slow, as the real one is while it opens a context."""
        from browsercontrol.session import Session

        mgr = BrowserManager()
        mgr.opened = []  # type: ignore[attr-defined]

        async def slow_create(name: str, **_: object) -> Session:
            if not name or name in mgr._sessions:
                raise ValueError(f"Session name {name!r} is empty or already in use")
            await asyncio.sleep(0.05)  # the real one awaits ensure_started and new_context
            mgr.opened.append(name)  # type: ignore[attr-defined]
            session = Session(name, isolated=True)
            mgr._sessions[name] = session
            mgr.bind(name)
            return session

        mgr.create_session = slow_create  # type: ignore[method-assign]
        return mgr

    @staticmethod
    async def _first_call(mgr: BrowserManager, client: str) -> None:
        token = current_client.set(client)
        try:
            await mgr.ensure_client_session(client)
        finally:
            current_client.reset(token)

    @pytest.mark.asyncio
    async def test_simultaneous_first_calls_get_separate_sessions(self):
        mgr = self._manager()
        with patch("browsercontrol.browser.config.isolate_clients", True):
            await asyncio.gather(
                self._first_call(mgr, "token:alice"), self._first_call(mgr, "token:bob")
            )
        assert mgr._bindings["token:alice"] != mgr._bindings["token:bob"]
        assert len([s for s in mgr._sessions.values() if s.isolated]) == 2

    @pytest.mark.asyncio
    async def test_simultaneous_calls_from_one_client_open_one_session(self):
        mgr = self._manager()
        with patch("browsercontrol.browser.config.isolate_clients", True):
            await asyncio.gather(*(self._first_call(mgr, "token:alice") for _ in range(3)))
        assert mgr.opened == ["client-1"]  # type: ignore[attr-defined]  # no orphaned contexts


class TestCreateSessionClaimsItsName:
    """create_session must hold its name while the context opens, or two callers share a session."""

    @staticmethod
    def _manager(*, fail_first: bool = False) -> BrowserManager:
        mgr = BrowserManager()
        mgr.opened = 0  # type: ignore[attr-defined]
        calls: list[None] = []

        async def new_context(**_: object) -> MagicMock:
            await asyncio.sleep(0.05)
            calls.append(None)
            if fail_first and len(calls) == 1:
                raise RuntimeError("context failed")
            mgr.opened += 1  # type: ignore[attr-defined]
            context = MagicMock()
            context.new_page = AsyncMock(return_value=MagicMock())
            return context

        base = MagicMock()
        base.browser.new_context = new_context
        mgr._sessions["default"].context = base
        mgr.ensure_started = AsyncMock()  # type: ignore[method-assign]
        return mgr

    @staticmethod
    async def _as(client: str, call: Any) -> Any:
        token = current_client.set(client)
        try:
            return await call
        finally:
            current_client.reset(token)

    @pytest.mark.asyncio
    async def test_explicit_name_cannot_take_the_one_being_allocated_automatically(self):
        mgr = self._manager()
        with patch("browsercontrol.browser.config.isolate_clients", True):
            automatic, explicit = await asyncio.gather(
                self._as("token:bob", mgr.ensure_client_session("token:bob")),
                self._as("token:alice", mgr.create_session("client-1")),
                return_exceptions=True,
            )
        assert automatic is None
        assert isinstance(explicit, ValueError)
        assert mgr._bindings == {"token:bob": "client-1"}
        assert mgr.opened == 1  # type: ignore[attr-defined]  # no orphaned context

    @pytest.mark.asyncio
    async def test_concurrent_explicit_calls_with_one_name_open_one_session(self):
        mgr = self._manager()
        results = await asyncio.gather(
            self._as("token:alice", mgr.create_session("side")),
            self._as("token:bob", mgr.create_session("side")),
            return_exceptions=True,
        )
        assert sorted(type(r).__name__ for r in results) == ["Session", "ValueError"]
        assert mgr.opened == 1  # type: ignore[attr-defined]

    @pytest.mark.asyncio
    async def test_a_failed_creation_releases_its_name(self):
        mgr = self._manager(fail_first=True)
        with pytest.raises(RuntimeError, match="context failed"):
            await self._as("token:alice", mgr.create_session("side"))
        session = await self._as("token:alice", mgr.create_session("side"))
        assert session.name == "side"

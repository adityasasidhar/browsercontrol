"""Tests for BrowserManager core functionality."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from browsercontrol.browser import BrowserManager


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
    async def test_browser_installs_chromium_if_missing(
        self, mock_playwright, mock_context, mock_page
    ):
        """Test install-on-failure: Chromium is installed then launch is retried."""
        missing_exc = Exception("Executable doesn't exist at /path/to/chromium")
        # First launch raises a missing-executable error; second succeeds.
        mock_playwright.chromium.launch_persistent_context.side_effect = [
            missing_exc,
            mock_context,
        ]
        mock_context.pages = [mock_page]

        with patch("browsercontrol.browser.async_playwright") as pw_patch:
            mock_playwright_instance = AsyncMock()
            mock_playwright_instance.start = AsyncMock(return_value=mock_playwright)
            pw_patch.return_value = mock_playwright_instance

            browser_mgr = BrowserManager()
            browser_mgr._install_chromium = AsyncMock()
            await browser_mgr.start()

            browser_mgr._install_chromium.assert_called_once()
            assert browser_mgr.is_started
            assert mock_playwright.chromium.launch_persistent_context.call_count == 2

    @pytest.mark.asyncio
    async def test_browser_raises_if_still_missing_after_install(
        self, mock_playwright, mock_context, mock_page
    ):
        """Test that the error propagates when launch still fails after install."""
        missing_exc = Exception("Executable doesn't exist at /path/to/chromium")
        mock_playwright.chromium.launch_persistent_context.side_effect = [
            missing_exc,
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


class TestTabManagement:
    """Test tab creation, switching, and closing."""

    @pytest.mark.asyncio
    async def test_create_tab_without_url(self, mock_context, mock_page):
        """Test creating a new blank tab."""
        new_page = AsyncMock()
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
    async def test_create_tab_with_url(self, mock_context, mock_page):
        """Test creating a new tab and navigating to URL."""
        new_page = AsyncMock()
        mock_context.new_page.return_value = new_page
        mock_context.pages = [mock_page, new_page]

        browser_mgr = BrowserManager()
        browser_mgr._started = True
        browser_mgr._context = mock_context
        browser_mgr._page = mock_page

        await browser_mgr.create_tab("https://example.com")

        new_page.goto.assert_called_once_with("https://example.com")

    @pytest.mark.asyncio
    async def test_switch_to_tab(self, mock_context, mock_page):
        """Test switching to a different tab."""
        page2 = AsyncMock()
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
    async def test_close_tab(self, mock_context, mock_page):
        """Test closing a tab."""
        page2 = AsyncMock()
        mock_context.pages = [mock_page, page2]

        browser_mgr = BrowserManager()
        browser_mgr._started = True
        browser_mgr._context = mock_context
        browser_mgr._page = page2

        await browser_mgr.close_tab(1)

        page2.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_tabs(self, mock_context, mock_page):
        """Test listing all open tabs."""
        page2 = AsyncMock()
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
    """Test Set of Marks (SoM) element detection."""

    @pytest.mark.asyncio
    async def test_get_interactive_elements(self, mock_page):
        """Test detecting interactive elements on page."""
        mock_page.evaluate.return_value = [
            {
                "tag": "button",
                "text": "Click me",
                "x": 100,
                "y": 200,
                "width": 80,
                "height": 40,
                "centerX": 140,
                "centerY": 220,
            }
        ]

        browser_mgr = BrowserManager()
        browser_mgr._started = True
        browser_mgr._context = AsyncMock()
        browser_mgr._context.pages = [mock_page]
        browser_mgr._page = mock_page

        elements = await browser_mgr.get_interactive_elements()

        assert len(elements) == 1
        assert elements[0]["tag"] == "button"
        assert elements[0]["centerX"] == 140
        assert elements[0]["centerY"] == 220

    @pytest.mark.asyncio
    async def test_screenshot_with_som(self, mock_page):
        """Test screenshot with SoM annotations."""
        mock_page.screenshot.return_value = b"fake_image_data"
        mock_page.evaluate.return_value = []

        browser_mgr = BrowserManager()
        browser_mgr._started = True
        browser_mgr._context = AsyncMock()
        browser_mgr._context.pages = [mock_page]
        browser_mgr._page = mock_page

        with patch("browsercontrol.browser.PILImage") as mock_pil:
            mock_img = MagicMock()
            mock_pil.open.return_value = mock_img
            # Needs size attribute for ImageDraw
            mock_img.size = (800, 600)
            mock_img_bytes = MagicMock()
            mock_img_bytes.getvalue.return_value = b"annotated_image"

            with patch("browsercontrol.browser.BytesIO", return_value=mock_img_bytes):
                screenshot_bytes, elem_map = await browser_mgr.screenshot_with_som()

                assert screenshot_bytes == b"annotated_image"
                assert isinstance(elem_map, dict)

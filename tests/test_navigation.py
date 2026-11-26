"""Tests for navigation tools."""

from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import FastMCP

from browsercontrol.tools.navigation import register_navigation_tools


@pytest.fixture
def mcp_server():
    """Create a FastMCP server instance for testing."""
    return FastMCP("test")


class TestNavigateTo:
    """Test navigate_to tool."""

    @pytest.mark.asyncio
    async def test_navigate_to_url(self, mcp_server, mock_browser_manager, mock_page):
        """Test navigating to a URL."""
        register_navigation_tools(mcp_server)

        with patch("browsercontrol.tools.navigation.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (
                b"screenshot",
                {1: {"tag": "button", "text": "Test"}},
            )

            # Get the registered tool
            tool = await mcp_server.get_tool("navigate_to")
            result = await tool.fn(url="https://example.com")

            mock_page.goto.assert_called_once()
            assert "Navigated to" in result[0]

    @pytest.mark.asyncio
    async def test_navigate_localhost_fallback(self, mcp_server, mock_browser_manager, mock_page):
        """Test localhost to 127.0.0.1 fallback on connection refused."""
        register_navigation_tools(mcp_server)

        # First call fails with localhost, second succeeds with 127.0.0.1
        mock_page.goto.side_effect = [Exception("ERR_CONNECTION_REFUSED"), None]

        with patch("browsercontrol.tools.navigation.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (b"screenshot", {})

            tool = await mcp_server.get_tool("navigate_to")
            await tool.fn(url="http://localhost:3000")

            assert mock_page.goto.call_count == 2
            assert "127.0.0.1" in str(mock_page.goto.call_args_list[1])


class TestNavigationActions:
    """Test go_back, go_forward, refresh_page."""

    @pytest.mark.asyncio
    async def test_go_back(self, mcp_server, mock_browser_manager, mock_page):
        """Test going back to previous page."""
        register_navigation_tools(mcp_server)

        with patch("browsercontrol.tools.navigation.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (b"screenshot", {})

            tool = await mcp_server.get_tool("go_back")
            result = await tool.fn()

            mock_page.go_back.assert_called_once()
            assert "Navigated back" in result[0]

    @pytest.mark.asyncio
    async def test_go_forward(self, mcp_server, mock_browser_manager, mock_page):
        """Test going forward to next page."""
        register_navigation_tools(mcp_server)

        with patch("browsercontrol.tools.navigation.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (b"screenshot", {})

            tool = await mcp_server.get_tool("go_forward")
            result = await tool.fn()

            mock_page.go_forward.assert_called_once()
            assert "Navigated forward" in result[0]

    @pytest.mark.asyncio
    async def test_refresh_page(self, mcp_server, mock_browser_manager, mock_page):
        """Test refreshing the current page."""
        register_navigation_tools(mcp_server)

        with patch("browsercontrol.tools.navigation.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (b"screenshot", {})

            tool = await mcp_server.get_tool("refresh_page")
            result = await tool.fn()

            mock_page.reload.assert_called_once()
            assert "Page refreshed" in result[0]


class TestScroll:
    """Test scroll tool with various directions and amounts."""

    @pytest.mark.asyncio
    async def test_scroll_down_medium(self, mcp_server, mock_browser_manager, mock_page):
        """Test scrolling down by medium amount."""
        register_navigation_tools(mcp_server)

        with patch("browsercontrol.tools.navigation.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (b"screenshot", {})

            tool = await mcp_server.get_tool("scroll")
            result = await tool.fn(direction="down", amount="medium")

            mock_page.evaluate.assert_called_with("window.scrollBy(0, 400)")
            assert "Scrolled down" in result[0]

    @pytest.mark.asyncio
    async def test_scroll_to_top(self, mcp_server, mock_browser_manager, mock_page):
        """Test scrolling to top of page."""
        register_navigation_tools(mcp_server)

        with patch("browsercontrol.tools.navigation.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (b"screenshot", {})

            tool = await mcp_server.get_tool("scroll")
            result = await tool.fn(direction="down", amount="top")

            mock_page.evaluate.assert_called_with("window.scrollTo(0, 0)")
            assert "Scrolled to top" in result[0]

    @pytest.mark.asyncio
    async def test_scroll_to_bottom(self, mcp_server, mock_browser_manager, mock_page):
        """Test scrolling to bottom of page."""
        register_navigation_tools(mcp_server)

        with patch("browsercontrol.tools.navigation.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (b"screenshot", {})

            tool = await mcp_server.get_tool("scroll")
            result = await tool.fn(direction="down", amount="bottom")

            mock_page.evaluate.assert_called_with("window.scrollTo(0, document.body.scrollHeight)")
            assert "Scrolled to bottom" in result[0]

    @pytest.mark.asyncio
    async def test_scroll_custom_pixels(self, mcp_server, mock_browser_manager, mock_page):
        """Test scrolling by custom pixel amount."""
        register_navigation_tools(mcp_server)

        with patch("browsercontrol.tools.navigation.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (b"screenshot", {})

            tool = await mcp_server.get_tool("scroll")
            await tool.fn(direction="down", amount="500")

            mock_page.evaluate.assert_called_with("window.scrollBy(0, 500)")


@pytest.fixture
def nav(mcp_server, mock_browser_manager, mock_page):
    """Navigation tools registered against the stubbed manager; yields a name -> callable lookup."""
    register_navigation_tools(mcp_server)
    mock_browser_manager.page = mock_page
    mock_browser_manager.screenshot_with_som.return_value = (b"screenshot", {})

    async def get(name: str):
        tool = await mcp_server.get_tool(name)
        assert tool is not None
        return tool.fn

    with patch("browsercontrol.tools.navigation.browser", mock_browser_manager):
        yield get


class TestNavigateToErrors:
    """navigate_to reports failures with a fresh screenshot instead of raising."""

    async def test_failure_returns_error_text_and_screenshot(self, nav, mock_page):
        mock_page.goto.side_effect = Exception("net::ERR_NAME_NOT_RESOLVED")

        navigate_to = await nav("navigate_to")
        text, image = await navigate_to(url="https://nope.invalid")

        assert text.startswith("Error navigating to https://nope.invalid: ")
        assert "ERR_NAME_NOT_RESOLVED" in text
        assert image.data == b"screenshot"
        mock_page.goto.assert_awaited_once()

    async def test_failure_is_not_logged_as_an_action(self, nav, mock_page, mock_browser_manager):
        mock_page.goto.side_effect = Exception("boom")

        navigate_to = await nav("navigate_to")
        await navigate_to(url="https://example.com")

        mock_browser_manager.log_action.assert_not_called()
        mock_browser_manager.settle.assert_not_awaited()

    async def test_connection_refused_on_a_remote_host_is_not_retried(self, nav, mock_page):
        mock_page.goto.side_effect = Exception("net::ERR_CONNECTION_REFUSED")

        navigate_to = await nav("navigate_to")
        text, _ = await navigate_to(url="https://example.com")

        mock_page.goto.assert_awaited_once()
        assert text.startswith("Error navigating to https://example.com")

    async def test_other_localhost_errors_are_not_retried(self, nav, mock_page):
        mock_page.goto.side_effect = Exception("net::ERR_TIMED_OUT")

        navigate_to = await nav("navigate_to")
        text, _ = await navigate_to(url="http://localhost:3000")

        mock_page.goto.assert_awaited_once()
        assert "Error navigating to http://localhost:3000" in text

    async def test_failed_localhost_fallback_reports_the_original_url(self, nav, mock_page):
        mock_page.goto.side_effect = Exception("net::ERR_CONNECTION_REFUSED")

        navigate_to = await nav("navigate_to")
        text, _ = await navigate_to(url="http://localhost:3000/app")

        assert [c.args[0] for c in mock_page.goto.await_args_list] == [
            "http://localhost:3000/app",
            "http://127.0.0.1:3000/app",
        ]
        assert text.startswith("Error navigating to http://localhost:3000/app: ")

    async def test_successful_fallback_reports_the_url_that_worked(self, nav, mock_page):
        mock_page.goto.side_effect = [Exception("net::ERR_CONNECTION_REFUSED"), None]

        navigate_to = await nav("navigate_to")
        text, _ = await navigate_to(url="http://localhost:3000")

        assert text.startswith("Navigated to http://127.0.0.1:3000")

    async def test_raises_when_even_the_error_screenshot_fails(
        self, nav, mock_page, mock_browser_manager
    ):
        mock_page.goto.side_effect = Exception("page crashed")
        mock_browser_manager.screenshot_with_som.side_effect = Exception("no screenshot")

        navigate_to = await nav("navigate_to")
        with pytest.raises(RuntimeError, match="Navigation failed: page crashed"):
            await navigate_to(url="https://example.com")

    async def test_browser_start_failure_surfaces_as_runtime_error(self, nav, mock_browser_manager):
        mock_browser_manager.ensure_started.side_effect = Exception("no chromium")
        mock_browser_manager.screenshot_with_som.side_effect = Exception("no page")

        navigate_to = await nav("navigate_to")
        with pytest.raises(RuntimeError, match="Navigation failed: no chromium"):
            await navigate_to(url="https://example.com")


class TestHistoryActionErrors:
    """go_back, go_forward and refresh_page report a failure as text with a screenshot."""

    @pytest.mark.parametrize(
        ("tool_name", "method", "message"),
        [
            ("go_back", "go_back", "Error going back: "),
            ("go_forward", "go_forward", "Error going forward: "),
            ("refresh_page", "reload", "Error refreshing: "),
        ],
    )
    async def test_failure_returns_error_text_and_screenshot(
        self, nav, mock_page, mock_browser_manager, tool_name, method, message
    ):
        getattr(mock_page, method).side_effect = Exception("Timeout 30000ms exceeded")

        tool = await nav(tool_name)
        text, image = await tool()

        assert text.startswith(message)
        assert "Timeout 30000ms exceeded" in text
        assert image.data == b"screenshot"
        mock_browser_manager.log_action.assert_not_called()

    @pytest.mark.parametrize("tool_name", ["go_back", "go_forward", "refresh_page"])
    async def test_failure_to_screenshot_the_error_propagates(
        self, nav, mock_browser_manager, tool_name
    ):
        mock_browser_manager.ensure_started.side_effect = Exception("no chromium")
        mock_browser_manager.screenshot_with_som.side_effect = Exception("no page")

        tool = await nav(tool_name)
        with pytest.raises(Exception, match="no page"):
            await tool()


class TestScrollDirectionsAndErrors:
    @pytest.mark.parametrize(
        ("direction", "script", "dx", "dy"),
        [
            ("up", "window.scrollBy(0, -100)", 0, -100),
            ("down", "window.scrollBy(0, 100)", 0, 100),
            ("left", "window.scrollBy(-100, 0)", -100, 0),
            ("right", "window.scrollBy(100, 0)", 100, 0),
        ],
    )
    async def test_each_direction(
        self, nav, mock_page, mock_browser_manager, direction, script, dx, dy
    ):
        scroll = await nav("scroll")
        text, _ = await scroll(direction=direction, amount="small")

        mock_page.evaluate.assert_awaited_once_with(script)
        mock_browser_manager.log_action.assert_called_once_with("scroll", dx=dx, dy=dy)
        assert text.startswith(f"Scrolled {direction} by 100px")

    async def test_unparseable_amount_falls_back_to_medium(self, nav, mock_page):
        scroll = await nav("scroll")
        text, _ = await scroll(direction="down", amount="lots")

        mock_page.evaluate.assert_awaited_once_with("window.scrollBy(0, 400)")
        assert "by 400px" in text

    async def test_unknown_direction_does_not_scroll(self, nav, mock_page, mock_browser_manager):
        scroll = await nav("scroll")
        await scroll(direction="diagonal", amount="small")

        mock_page.evaluate.assert_not_awaited()
        mock_browser_manager.log_action.assert_called_once_with("scroll", dx=0, dy=0)

    async def test_failure_raises_runtime_error(self, nav, mock_page):
        mock_page.evaluate.side_effect = Exception("Execution context was destroyed")

        scroll = await nav("scroll")
        with pytest.raises(RuntimeError, match="Scroll failed: Execution context was destroyed"):
            await scroll(direction="down")

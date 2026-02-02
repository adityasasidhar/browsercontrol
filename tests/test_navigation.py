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
            tool = mcp_server._tool_manager._tools["navigate_to"]
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

            tool = mcp_server._tool_manager._tools["navigate_to"]
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

            tool = mcp_server._tool_manager._tools["go_back"]
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

            tool = mcp_server._tool_manager._tools["go_forward"]
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

            tool = mcp_server._tool_manager._tools["refresh_page"]
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

            tool = mcp_server._tool_manager._tools["scroll"]
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

            tool = mcp_server._tool_manager._tools["scroll"]
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

            tool = mcp_server._tool_manager._tools["scroll"]
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

            tool = mcp_server._tool_manager._tools["scroll"]
            await tool.fn(direction="down", amount="500")

            mock_page.evaluate.assert_called_with("window.scrollBy(0, 500)")

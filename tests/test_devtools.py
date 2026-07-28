"""Tests for developer tools."""

from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import FastMCP

from browsercontrol.tools.devtools import register_devtools


@pytest.fixture
def mcp_server():
    """Create a FastMCP server instance for testing."""
    return FastMCP("test")


class TestConsoleLogs:
    """Test console log capture tools."""

    @pytest.mark.asyncio
    async def test_get_console_logs(self, mcp_server, mock_browser_manager):
        """Test getting console logs."""
        register_devtools(mcp_server)

        mock_browser_manager.get_console_logs.return_value = [
            {"type": "log", "text": "Hello", "timestamp": "2026-01-01T00:00:00"},
            {"type": "error", "text": "Error!", "timestamp": "2026-01-01T00:00:01"},
        ]

        with patch("browsercontrol.tools.devtools.browser", mock_browser_manager):
            tool = await mcp_server.get_tool("get_console_logs")
            result = await tool.fn()

            assert isinstance(result, str)
            assert "Hello" in result
            assert "Error!" in result


class TestNetworkRequests:
    """Test network request monitoring."""

    @pytest.mark.asyncio
    async def test_get_network_requests(self, mcp_server, mock_browser_manager):
        """Test getting network requests."""
        register_devtools(mcp_server)

        mock_browser_manager.get_network_requests.return_value = [
            {
                "url": "https://api.example.com/data",
                "method": "GET",
                "status": 200,
                "timestamp": "2026-01-01T00:00:00",
            }
        ]

        with patch("browsercontrol.tools.devtools.browser", mock_browser_manager):
            tool = await mcp_server.get_tool("get_network_requests")
            result = await tool.fn()

            assert isinstance(result, str)
            assert "api.example.com" in result
            assert "200" in result


class TestCookieManagement:
    """Test cookie get/set/delete/clear tools."""

    @pytest.mark.asyncio
    async def test_get_cookies(self, mcp_server, mock_browser_manager, mock_context):
        """Test getting all cookies."""
        register_devtools(mcp_server)

        mock_context.cookies.return_value = [
            {"name": "session", "value": "abc123", "domain": "example.com"}
        ]

        with patch("browsercontrol.tools.devtools.browser", mock_browser_manager):
            mock_browser_manager._context = mock_context

            tool = await mcp_server.get_tool("get_cookies")
            result = await tool.fn()

            assert isinstance(result, str)
            assert "session" in result
            assert "abc123" in result

    @pytest.mark.asyncio
    async def test_set_cookie(self, mcp_server, mock_browser_manager, mock_context, mock_page):
        """Test setting a cookie."""
        register_devtools(mcp_server)

        mock_page.url = "https://example.com"

        with patch("browsercontrol.tools.devtools.browser", mock_browser_manager):
            mock_browser_manager._context = mock_context
            mock_browser_manager.page = mock_page

            tool = await mcp_server.get_tool("set_cookie")
            result = await tool.fn(name="test", value="value123")

            mock_context.add_cookies.assert_called_once()
            assert isinstance(result, str)
            assert "Cookie set: test=value123" in result

    @pytest.mark.asyncio
    async def test_delete_cookie(self, mcp_server, mock_browser_manager, mock_context):
        """Test deleting a specific cookie by name using a targeted clear_cookies call."""
        register_devtools(mcp_server)

        with patch("browsercontrol.tools.devtools.browser", mock_browser_manager):
            mock_browser_manager._context = mock_context

            tool = await mcp_server.get_tool("delete_cookie")
            result = await tool.fn(name="session")

            # Should use targeted clear_cookies(name=...) — no read/wipe/re-add dance
            mock_context.clear_cookies.assert_called_once_with(name="session")
            mock_context.cookies.assert_not_called()
            mock_context.add_cookies.assert_not_called()

            assert isinstance(result, str)
            assert "Deleted cookie" in result
            assert "session" in result

    @pytest.mark.asyncio
    async def test_clear_cookies(self, mcp_server, mock_browser_manager, mock_context):
        """Test clearing all cookies."""
        register_devtools(mcp_server)

        with patch("browsercontrol.tools.devtools.browser", mock_browser_manager):
            mock_browser_manager._context = mock_context

            tool = await mcp_server.get_tool("clear_cookies")
            result = await tool.fn()

            mock_context.clear_cookies.assert_called_once()
            assert isinstance(result, str)
            assert "All cookies cleared" in result


class TestViewport:
    """Test viewport control."""

    @pytest.mark.asyncio
    async def test_set_viewport(self, mcp_server, mock_browser_manager, mock_page):
        """Test changing viewport size."""
        register_devtools(mcp_server)

        with patch("browsercontrol.tools.devtools.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page

            tool = await mcp_server.get_tool("set_viewport")
            result = await tool.fn(width=1920, height=1080)

            mock_page.set_viewport_size.assert_called_once_with({"width": 1920, "height": 1080})
            # set_viewport returns tuple[str, Image] — visual tool
            assert "1920x1080" in result[0]

    @pytest.mark.parametrize(
        ("width", "height"),
        [(0, 600), (800, 0), (0, 0), (-1, 600), (800, -1)],
    )
    @pytest.mark.asyncio
    async def test_degenerate_viewport_rejected(
        self, mcp_server, mock_browser_manager, mock_page, width, height
    ):
        """A zero/negative viewport must be rejected before it is applied.

        Applying it would make every later screenshot fail, breaking every
        other tool in the server until the viewport is manually restored.
        """
        register_devtools(mcp_server)

        with patch("browsercontrol.tools.devtools.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page

            tool = await mcp_server.get_tool("set_viewport")
            with pytest.raises(RuntimeError, match="must be at least 1"):
                await tool.fn(width=width, height=height)

            mock_page.set_viewport_size.assert_not_called()


class TestPageErrors:
    """Test page error capture."""

    @pytest.mark.asyncio
    async def test_get_page_errors(self, mcp_server, mock_browser_manager):
        """Test getting page errors."""
        register_devtools(mcp_server)

        mock_browser_manager.get_page_errors.return_value = [
            {
                "message": "TypeError: Cannot read property 'x' of undefined",
                "timestamp": "2026-01-01T00:00:00",
            }
        ]

        with patch("browsercontrol.tools.devtools.browser", mock_browser_manager):
            tool = await mcp_server.get_tool("get_page_errors")
            result = await tool.fn()

            assert isinstance(result, str)
            assert "TypeError" in result


class TestPerformance:
    """Test performance metrics."""

    @pytest.mark.asyncio
    async def test_get_page_performance(self, mcp_server, mock_browser_manager, mock_page):
        """Test getting page performance metrics."""
        register_devtools(mcp_server)

        mock_page.evaluate.return_value = {
            "loadComplete": 1234,
            "domContentLoaded": 500,
            "ttfb": 300,
            "resourceCount": 5,
        }

        with patch("browsercontrol.tools.devtools.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page

            tool = await mcp_server.get_tool("get_page_performance")
            result = await tool.fn()

            assert isinstance(result, str)
            assert "1234" in result

"""Tests for tab management tools."""

from unittest.mock import patch

import pytest
from fastmcp import FastMCP

from browsercontrol.tools.tabs import register_tab_tools


@pytest.fixture
def mcp_server():
    """Create a FastMCP server instance for testing."""
    return FastMCP("test")


class TestCreateTab:
    """Test create_tab tool."""

    @pytest.mark.asyncio
    async def test_create_tab_without_url(self, mcp_server, mock_browser_manager):
        """Test creating a blank tab."""
        register_tab_tools(mcp_server)

        with patch("browsercontrol.tools.tabs.browser", mock_browser_manager):
            with patch("browsercontrol.tools.tabs._get_screenshot_with_summary") as mock_screenshot:
                mock_screenshot.return_value = (None, "Summary")

                tool = await mcp_server.get_tool("create_tab")
                result = await tool.fn()

                mock_browser_manager.create_tab.assert_called_once_with(None)
                assert "Created new tab" in result[0]

    @pytest.mark.asyncio
    async def test_create_tab_with_url(self, mcp_server, mock_browser_manager):
        """Test creating a tab with URL."""
        register_tab_tools(mcp_server)

        with patch("browsercontrol.tools.tabs.browser", mock_browser_manager):
            with patch("browsercontrol.tools.tabs._get_screenshot_with_summary") as mock_screenshot:
                mock_screenshot.return_value = (None, "Summary")

                tool = await mcp_server.get_tool("create_tab")
                result = await tool.fn(url="https://example.com")

                mock_browser_manager.create_tab.assert_called_once_with("https://example.com")
                assert "navigated to https://example.com" in result[0]


class TestSwitchTab:
    """Test switch_tab tool."""

    @pytest.mark.asyncio
    async def test_switch_to_tab(self, mcp_server, mock_browser_manager):
        """Test switching to a different tab."""
        register_tab_tools(mcp_server)

        with patch("browsercontrol.tools.tabs.browser", mock_browser_manager):
            with patch("browsercontrol.tools.tabs._get_screenshot_with_summary") as mock_screenshot:
                mock_screenshot.return_value = (None, "Summary")

                tool = await mcp_server.get_tool("switch_tab")
                result = await tool.fn(index=1)

                mock_browser_manager.switch_to_tab.assert_called_once_with(1)
                assert "Switched to tab 1" in result[0]


class TestCloseTab:
    """Test close_tab tool."""

    @pytest.mark.asyncio
    async def test_close_tab(self, mcp_server, mock_browser_manager):
        """Test closing a tab."""
        register_tab_tools(mcp_server)

        with patch("browsercontrol.tools.tabs.browser", mock_browser_manager):
            with patch("browsercontrol.tools.tabs._get_screenshot_with_summary") as mock_screenshot:
                mock_screenshot.return_value = (None, "Summary")

                tool = await mcp_server.get_tool("close_tab")
                result = await tool.fn(index=1)

                mock_browser_manager.close_tab.assert_called_once_with(1)
                assert "Closed tab 1" in result[0]


class TestListTabs:
    """Test list_tabs tool."""

    @pytest.mark.asyncio
    async def test_list_tabs(self, mcp_server, mock_browser_manager):
        """Test listing all open tabs."""
        register_tab_tools(mcp_server)

        mock_browser_manager.list_tabs.return_value = [
            {"index": 0, "title": "Tab 1", "url": "https://example.com", "active": True},
            {"index": 1, "title": "Tab 2", "url": "https://example2.com", "active": False},
        ]

        with patch("browsercontrol.tools.tabs.browser", mock_browser_manager):
            tool = await mcp_server.get_tool("list_tabs")
            result = await tool.fn()

            assert "Open Tabs:" in result
            assert "[0] Tab 1" in result
            assert "[1] Tab 2" in result
            assert "*" in result  # Active marker

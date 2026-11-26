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
            with patch("browsercontrol.tools.tabs.get_screenshot_with_summary") as mock_screenshot:
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
            with patch("browsercontrol.tools.tabs.get_screenshot_with_summary") as mock_screenshot:
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
            with patch("browsercontrol.tools.tabs.get_screenshot_with_summary") as mock_screenshot:
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
            with patch("browsercontrol.tools.tabs.get_screenshot_with_summary") as mock_screenshot:
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


@pytest.fixture
def tabs(mcp_server, mock_browser_manager):
    """Tab tools registered against the stubbed manager; yields a name -> callable lookup."""
    register_tab_tools(mcp_server)

    async def get(name: str):
        tool = await mcp_server.get_tool(name)
        assert tool is not None
        return tool.fn

    with patch("browsercontrol.tools.tabs.browser", mock_browser_manager):
        yield get


class TestTabErrorPaths:
    """Every tab tool wraps a failure in a RuntimeError the agent can read."""

    @pytest.mark.parametrize(
        ("tool_name", "args", "method", "message"),
        [
            ("create_tab", {"url": "https://example.com"}, "create_tab", "Create tab failed"),
            ("switch_tab", {"index": 4}, "switch_to_tab", "Switch tab failed"),
            ("close_tab", {"index": 4}, "close_tab", "Close tab failed"),
            ("list_tabs", {}, "list_tabs", "List tabs failed"),
        ],
    )
    async def test_manager_error_is_wrapped(
        self, tabs, mock_browser_manager, tool_name, args, method, message
    ):
        getattr(mock_browser_manager, method).side_effect = ValueError(
            "Tab index 4 out of range (0-1)"
        )

        tool = await tabs(tool_name)
        with pytest.raises(RuntimeError, match=rf"{message}: Tab index 4 out of range \(0-1\)"):
            await tool(**args)

    @pytest.mark.parametrize(
        ("tool_name", "args", "message"),
        [
            ("create_tab", {}, "Create tab failed"),
            ("switch_tab", {"index": 0}, "Switch tab failed"),
            ("close_tab", {"index": 0}, "Close tab failed"),
            ("list_tabs", {}, "List tabs failed"),
        ],
    )
    async def test_browser_start_failure_is_wrapped(
        self, tabs, mock_browser_manager, tool_name, args, message
    ):
        mock_browser_manager.ensure_started.side_effect = RuntimeError("no chromium")

        tool = await tabs(tool_name)
        with pytest.raises(RuntimeError, match=f"{message}: no chromium"):
            await tool(**args)

    @pytest.mark.parametrize(
        ("tool_name", "args", "method"),
        [
            ("create_tab", {}, "create_tab"),
            ("switch_tab", {"index": 0}, "switch_to_tab"),
            ("close_tab", {"index": 0}, "close_tab"),
        ],
    )
    async def test_screenshot_failure_after_the_action_is_wrapped(
        self, tabs, mock_browser_manager, tool_name, args, method
    ):
        mock_browser_manager.screenshot_with_som.side_effect = RuntimeError("page crashed")

        tool = await tabs(tool_name)
        with pytest.raises(RuntimeError, match="failed: page crashed"):
            await tool(**args)

        getattr(mock_browser_manager, method).assert_awaited_once()

    async def test_failed_create_tab_does_not_take_a_screenshot(self, tabs, mock_browser_manager):
        mock_browser_manager.create_tab.side_effect = RuntimeError("context closed")

        tool = await tabs("create_tab")
        with pytest.raises(RuntimeError, match="Create tab failed: context closed"):
            await tool()

        mock_browser_manager.screenshot_with_som.assert_not_awaited()

    async def test_list_tabs_with_no_tabs_returns_only_the_header(self, tabs, mock_browser_manager):
        mock_browser_manager.list_tabs.return_value = []

        tool = await tabs("list_tabs")
        assert await tool() == "Open Tabs:"

    async def test_list_tabs_marks_only_the_active_tab(self, tabs, mock_browser_manager):
        mock_browser_manager.list_tabs.return_value = [
            {"index": 0, "title": "A", "url": "https://a.test", "active": False},
            {"index": 1, "title": "B", "url": "https://b.test", "active": True},
        ]

        tool = await tabs("list_tabs")
        lines = (await tool()).splitlines()

        assert lines[1] == "  [0] A - https://a.test"
        assert lines[2] == "* [1] B - https://b.test"

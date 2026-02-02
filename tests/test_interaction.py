"""Tests for interaction tools."""

from unittest.mock import patch

import pytest
from fastmcp import FastMCP

from browsercontrol.tools.interaction import register_interaction_tools


@pytest.fixture
def mcp_server():
    """Create a FastMCP server instance for testing."""
    return FastMCP("test")


class TestClick:
    """Test click and click_at tools."""

    @pytest.mark.asyncio
    async def test_click_valid_element(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """Test clicking a valid element by ID."""
        register_interaction_tools(mcp_server)

        with (
            patch("browsercontrol.tools.interaction.browser", mock_browser_manager),
            patch(
                "browsercontrol.tools.interaction.get_element_map", return_value=sample_element_map
            ),
        ):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (
                b"screenshot",
                sample_element_map,
            )

            tool = mcp_server._tool_manager._tools["click"]
            result = await tool.fn(element_id=1)

            mock_page.mouse.click.assert_called_once_with(140, 220)
            assert "Clicked element 1" in result[0]

    @pytest.mark.asyncio
    async def test_click_invalid_element(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """Test clicking an invalid element ID returns error."""
        register_interaction_tools(mcp_server)

        with (
            patch("browsercontrol.tools.interaction.browser", mock_browser_manager),
            patch(
                "browsercontrol.tools.interaction.get_element_map", return_value=sample_element_map
            ),
        ):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (
                b"screenshot",
                sample_element_map,
            )

            tool = mcp_server._tool_manager._tools["click"]
            result = await tool.fn(element_id=999)

            assert "Error: Element 999 not found" in result[0]

    @pytest.mark.asyncio
    async def test_click_at_coordinates(self, mcp_server, mock_browser_manager, mock_page):
        """Test clicking at specific coordinates."""
        register_interaction_tools(mcp_server)

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (b"screenshot", {})

            tool = mcp_server._tool_manager._tools["click_at"]
            result = await tool.fn(x=100, y=200)

            mock_page.mouse.click.assert_called_once_with(100, 200)
            assert "Clicked at (100, 200)" in result[0]


class TestTypeText:
    """Test type_text tool."""

    @pytest.mark.asyncio
    async def test_type_text_into_input(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """Test typing text into an input element."""
        register_interaction_tools(mcp_server)

        with (
            patch("browsercontrol.tools.interaction.browser", mock_browser_manager),
            patch(
                "browsercontrol.tools.interaction.get_element_map", return_value=sample_element_map
            ),
        ):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (
                b"screenshot",
                sample_element_map,
            )

            tool = mcp_server._tool_manager._tools["type_text"]
            result = await tool.fn(element_id=2, text="Hello World")

            mock_page.keyboard.type.assert_called_once_with("Hello World")
            assert "Typed 'Hello World'" in result[0]


class TestKeyboard:
    """Test press_key tool."""

    @pytest.mark.asyncio
    async def test_press_enter_key(self, mcp_server, mock_browser_manager, mock_page):
        """Test pressing Enter key."""
        register_interaction_tools(mcp_server)

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (b"screenshot", {})

            tool = mcp_server._tool_manager._tools["press_key"]
            result = await tool.fn(key="Enter")

            mock_page.keyboard.press.assert_called_once_with("Enter")
            assert "Pressed key 'Enter'" in result[0]


class TestHover:
    """Test hover tool."""

    @pytest.mark.asyncio
    async def test_hover_over_element(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """Test hovering over an element."""
        register_interaction_tools(mcp_server)

        with (
            patch("browsercontrol.tools.interaction.browser", mock_browser_manager),
            patch(
                "browsercontrol.tools.interaction.get_element_map", return_value=sample_element_map
            ),
        ):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (
                b"screenshot",
                sample_element_map,
            )

            tool = mcp_server._tool_manager._tools["hover"]
            result = await tool.fn(element_id=3)

            mock_page.mouse.move.assert_called_once_with(330, 60)
            assert "Hovering over element 3" in result[0]


class TestScrollToElement:
    """Test scroll_to_element tool."""

    @pytest.mark.asyncio
    async def test_scroll_to_element(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """Test scrolling to bring element into view."""
        register_interaction_tools(mcp_server)

        with (
            patch("browsercontrol.tools.interaction.browser", mock_browser_manager),
            patch(
                "browsercontrol.tools.interaction.get_element_map", return_value=sample_element_map
            ),
        ):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (
                b"screenshot",
                sample_element_map,
            )

            tool = mcp_server._tool_manager._tools["scroll_to_element"]
            await tool.fn(element_id=1)

            # Element at y=200, should scroll to y=100 (200-100)
            mock_page.evaluate.assert_called_once_with("window.scrollTo(0, 100)")


class TestWait:
    """Test wait tool."""

    @pytest.mark.asyncio
    async def test_wait_default_duration(self, mcp_server, mock_browser_manager, mock_page):
        """Test waiting for default 1 second."""
        register_interaction_tools(mcp_server)

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (b"screenshot", {})

            tool = mcp_server._tool_manager._tools["wait"]
            result = await tool.fn()

            mock_page.wait_for_timeout.assert_called_once_with(1000)
            assert "Waited 1.0s" in result[0]

    @pytest.mark.asyncio
    async def test_wait_custom_duration(self, mcp_server, mock_browser_manager, mock_page):
        """Test waiting for custom duration."""
        register_interaction_tools(mcp_server)

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (b"screenshot", {})

            tool = mcp_server._tool_manager._tools["wait"]
            result = await tool.fn(seconds=2.5)

            mock_page.wait_for_timeout.assert_called_once_with(2500)
            assert "Waited 2.5s" in result[0]

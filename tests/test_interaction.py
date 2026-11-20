"""Tests for interaction tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp import FastMCP
from playwright.async_api import Error as PlaywrightError

from browsercontrol.elements import ACTION_TIMEOUT_MS, ElementNotFoundError, StaleElementError
from browsercontrol.tools.interaction import register_interaction_tools


def _wire(manager, elem_map):
    """Give the mocked manager an element map and a resolver that honours it.

    Returns the locator that every known ID resolves to.
    """
    locator = AsyncMock()

    async def resolve(element_id):
        if element_id not in elem_map:
            raise ElementNotFoundError(element_id, list(elem_map))
        return locator

    manager.get_element_map = MagicMock(return_value=elem_map)
    manager.resolve_element = AsyncMock(side_effect=resolve)
    manager.screenshot_with_som.return_value = (b"screenshot", elem_map)
    return locator


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
        """Clicking resolves the ID to a locator and clicks it (not a screen position)."""
        register_interaction_tools(mcp_server)
        locator = _wire(mock_browser_manager, sample_element_map)
        mock_page.wait_for_load_state = AsyncMock()

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            tool = await mcp_server.get_tool("click")
            result = await tool.fn(element_id=1)

        mock_browser_manager.resolve_element.assert_awaited_once_with(1)
        locator.click.assert_awaited_once_with(timeout=ACTION_TIMEOUT_MS)
        mock_page.mouse.click.assert_not_called()
        assert "Clicked element 1 (button: Sign In)" in result[0]

    @pytest.mark.asyncio
    async def test_click_invalid_element(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """Test clicking an invalid element ID returns error."""
        register_interaction_tools(mcp_server)
        _wire(mock_browser_manager, sample_element_map)

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            tool = await mcp_server.get_tool("click")
            result = await tool.fn(element_id=999)

        assert "Error: Element 999 not found. Valid IDs: [1, 2, 3]" in result[0]

    @pytest.mark.asyncio
    async def test_click_stale_element_does_not_click(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """A stale ID is reported with a fresh screenshot, and nothing is clicked."""
        register_interaction_tools(mcp_server)
        locator = _wire(mock_browser_manager, sample_element_map)
        mock_browser_manager.resolve_element.side_effect = StaleElementError(
            1, "it is no longer on the page"
        )

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            tool = await mcp_server.get_tool("click")
            result = await tool.fn(element_id=1)

        locator.click.assert_not_awaited()
        assert "Element 1 is stale (it is no longer on the page)" in result[0]
        assert "Found 3 interactive elements" in result[0]

    @pytest.mark.asyncio
    async def test_click_at_coordinates(self, mcp_server, mock_browser_manager, mock_page):
        """Test clicking at specific coordinates."""
        register_interaction_tools(mcp_server)

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (b"screenshot", {})

            tool = await mcp_server.get_tool("click_at")
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
        locator = _wire(mock_browser_manager, sample_element_map)

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            tool = await mcp_server.get_tool("type_text")
            result = await tool.fn(element_id=2, text="Hello World")

        locator.fill.assert_awaited_once_with("Hello World", timeout=ACTION_TIMEOUT_MS)
        mock_page.keyboard.type.assert_not_called()
        assert "Typed 'Hello World'" in result[0]

    @pytest.mark.asyncio
    async def test_type_text_falls_back_to_keyboard_when_not_fillable(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """Custom widgets that reject fill() get focused by a click and typed into."""
        register_interaction_tools(mcp_server)
        locator = _wire(mock_browser_manager, sample_element_map)
        locator.fill.side_effect = PlaywrightError("Element is not an <input>")

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            tool = await mcp_server.get_tool("type_text")
            await tool.fn(element_id=2, text="Hi")

        locator.click.assert_awaited_once()
        mock_page.keyboard.type.assert_awaited_once_with("Hi")


class TestKeyboard:
    """Test press_key tool."""

    @pytest.mark.asyncio
    async def test_press_enter_key(self, mcp_server, mock_browser_manager, mock_page):
        """Test pressing Enter key."""
        register_interaction_tools(mcp_server)

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (b"screenshot", {})

            tool = await mcp_server.get_tool("press_key")
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
        locator = _wire(mock_browser_manager, sample_element_map)

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            tool = await mcp_server.get_tool("hover")
            result = await tool.fn(element_id=3)

        locator.hover.assert_awaited_once_with(timeout=ACTION_TIMEOUT_MS)
        mock_page.mouse.move.assert_not_called()
        assert "Hovering over element 3" in result[0]


class TestScrollToElement:
    """Test scroll_to_element tool."""

    @pytest.mark.asyncio
    async def test_scroll_to_element(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """Scrolling acts on the element itself, so nested scroll containers work too."""
        register_interaction_tools(mcp_server)
        locator = _wire(mock_browser_manager, sample_element_map)

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            tool = await mcp_server.get_tool("scroll_to_element")
            await tool.fn(element_id=1)

        locator.evaluate.assert_awaited_once()
        assert "scrollIntoView" in locator.evaluate.call_args.args[0]


class TestWait:
    """Test wait tool."""

    @pytest.mark.asyncio
    async def test_wait_default_duration(self, mcp_server, mock_browser_manager, mock_page):
        """Test waiting for default 1 second."""
        register_interaction_tools(mcp_server)

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            mock_browser_manager.screenshot_with_som.return_value = (b"screenshot", {})

            tool = await mcp_server.get_tool("wait")
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

            tool = await mcp_server.get_tool("wait")
            result = await tool.fn(seconds=2.5)

            mock_page.wait_for_timeout.assert_called_once_with(2500)
            assert "Waited 2.5s" in result[0]

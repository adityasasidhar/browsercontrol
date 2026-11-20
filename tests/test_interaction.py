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
    locator.is_disabled = AsyncMock(return_value=False)

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
        locator.evaluate = AsyncMock(return_value="fill")

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            tool = await mcp_server.get_tool("type_text")
            result = await tool.fn(element_id=2, text="Hello World")

        locator.fill.assert_awaited_once_with("Hello World", timeout=ACTION_TIMEOUT_MS)
        mock_page.keyboard.type.assert_not_called()
        assert "Typed 'Hello World'" in result[0]

    @pytest.mark.asyncio
    async def test_fill_errors_are_not_swallowed(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """A failing fill() on a real field must not fall back to clicking and typing."""
        register_interaction_tools(mcp_server)
        locator = _wire(mock_browser_manager, sample_element_map)
        locator.evaluate = AsyncMock(return_value="fill")
        locator.fill.side_effect = PlaywrightError("Element is not editable")

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            tool = await mcp_server.get_tool("type_text")
            with pytest.raises(RuntimeError, match="not editable"):
                await tool.fn(element_id=2, text="Hi")

        locator.click.assert_not_awaited()
        mock_page.keyboard.type.assert_not_called()

    @pytest.mark.asyncio
    async def test_non_text_element_is_rejected_without_clicking(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """type_text on a checkbox or button must not click (and toggle) it."""
        register_interaction_tools(mcp_server)
        locator = _wire(mock_browser_manager, sample_element_map)
        locator.evaluate = AsyncMock(return_value="none")

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            tool = await mcp_server.get_tool("type_text")
            with pytest.raises(RuntimeError, match="not a text field"):
                await tool.fn(element_id=2, text="yes")

        locator.click.assert_not_awaited()
        locator.fill.assert_not_awaited()
        mock_page.keyboard.type.assert_not_called()

    @pytest.mark.asyncio
    async def test_custom_textbox_is_focused_cleared_and_typed_into(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """role=textbox widgets get a click, select-all (to replace), then typing."""
        register_interaction_tools(mcp_server)
        locator = _wire(mock_browser_manager, sample_element_map)
        locator.evaluate = AsyncMock(side_effect=["custom", True])

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            tool = await mcp_server.get_tool("type_text")
            await tool.fn(element_id=2, text="Hi")

        locator.click.assert_awaited_once()
        mock_page.keyboard.press.assert_awaited_once_with("ControlOrMeta+a")
        mock_page.keyboard.type.assert_awaited_once_with("Hi")

    @pytest.mark.asyncio
    async def test_custom_textbox_that_takes_no_focus_types_nothing(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        register_interaction_tools(mcp_server)
        locator = _wire(mock_browser_manager, sample_element_map)
        locator.evaluate = AsyncMock(side_effect=["custom", False])

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            tool = await mcp_server.get_tool("type_text")
            with pytest.raises(RuntimeError, match="did not focus"):
                await tool.fn(element_id=2, text="Hi")

        mock_page.keyboard.type.assert_not_called()


class TestDisabled:
    """Disabled elements get an immediate explanation instead of a 10s timeout."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool_name", ["click", "type_text"])
    async def test_disabled_element_is_reported(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map, tool_name
    ):
        register_interaction_tools(mcp_server)
        locator = _wire(mock_browser_manager, sample_element_map)
        locator.is_disabled = AsyncMock(return_value=True)

        with patch("browsercontrol.tools.interaction.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page
            tool = await mcp_server.get_tool(tool_name)
            kwargs = {"element_id": 1} if tool_name == "click" else {"element_id": 1, "text": "x"}
            result = await tool.fn(**kwargs)

        assert "element 1 is disabled" in result[0]
        assert "Found" in result[0], "a fresh element summary accompanies the error"
        locator.click.assert_not_awaited()
        locator.fill.assert_not_awaited()


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

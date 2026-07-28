"""Tests for form handling tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp import FastMCP

from browsercontrol.tools.forms import register_form_tools


@pytest.fixture
def mcp_server():
    """Create a FastMCP server instance for testing."""
    return FastMCP("test")


SELECT_MAP_ENTRY = {
    "tag": "select",
    "text": "",
    "x": 100,
    "y": 300,
    "width": 150,
    "height": 30,
    "centerX": 175,
    "centerY": 315,
}

CHECKBOX_MAP_ENTRY = {
    "tag": "input",
    "text": "",
    "x": 50,
    "y": 400,
    "width": 20,
    "height": 20,
    "centerX": 60,
    "centerY": 410,
}


def _attach_element(mock_page, element):
    """Wire an element handle up to the page's evaluate_handle call."""
    handle = MagicMock()
    handle.as_element = MagicMock(return_value=element)
    mock_page.evaluate_handle = AsyncMock(return_value=handle)


class TestSelectOption:
    """Test select_option tool."""

    @pytest.mark.asyncio
    async def test_select_dropdown_option(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """Test selecting an option from dropdown."""
        register_form_tools(mcp_server)

        select_map = {**sample_element_map, 4: SELECT_MAP_ENTRY}

        element = AsyncMock()
        # tagName -> options list -> resulting value
        element.evaluate = AsyncMock(
            side_effect=[
                "select",
                [{"value": "opt1", "label": "Option 1"}],
                "opt1",
            ]
        )
        _attach_element(mock_page, element)

        with patch("browsercontrol.tools.forms.browser", mock_browser_manager):
            with patch("browsercontrol.tools.forms.get_element_map", return_value=select_map):
                mock_browser_manager.page = mock_page
                mock_browser_manager.screenshot_with_som.return_value = (b"screenshot", select_map)

                tool = await mcp_server.get_tool("select_option")
                result = await tool.fn(element_id=4, option="Option 1")

                element.select_option.assert_awaited_once_with(value="opt1")
                assert "Selected 'Option 1'" in result[0]

    @pytest.mark.asyncio
    async def test_missing_option_raises_without_clicking(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """An option that isn't in the dropdown must error, never click elsewhere."""
        register_form_tools(mcp_server)

        select_map = {**sample_element_map, 4: SELECT_MAP_ENTRY}

        element = AsyncMock()
        element.evaluate = AsyncMock(
            side_effect=["select", [{"value": "opt1", "label": "Option 1"}]]
        )
        _attach_element(mock_page, element)

        with patch("browsercontrol.tools.forms.browser", mock_browser_manager):
            with patch("browsercontrol.tools.forms.get_element_map", return_value=select_map):
                mock_browser_manager.page = mock_page
                mock_browser_manager.screenshot_with_som.return_value = (b"screenshot", select_map)

                tool = await mcp_server.get_tool("select_option")
                with pytest.raises(RuntimeError, match="no option matching"):
                    await tool.fn(element_id=4, option="Not An Option")

                element.select_option.assert_not_awaited()
                mock_page.get_by_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_non_select_element_raises(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """Targeting something that isn't a <select> must error."""
        register_form_tools(mcp_server)

        element = AsyncMock()
        element.evaluate = AsyncMock(return_value="button")
        _attach_element(mock_page, element)

        with patch("browsercontrol.tools.forms.browser", mock_browser_manager):
            with patch(
                "browsercontrol.tools.forms.get_element_map", return_value=sample_element_map
            ):
                mock_browser_manager.page = mock_page
                mock_browser_manager.screenshot_with_som.return_value = (
                    b"screenshot",
                    sample_element_map,
                )

                tool = await mcp_server.get_tool("select_option")
                with pytest.raises(RuntimeError, match="not a <select>"):
                    await tool.fn(element_id=1, option="anything")

                element.select_option.assert_not_awaited()


class TestCheckCheckbox:
    """Test check_checkbox tool."""

    @pytest.mark.asyncio
    async def test_check_uses_check_not_click(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """Checking must use the idempotent check(), not a raw toggle click."""
        register_form_tools(mcp_server)

        checkbox_map = {**sample_element_map, 5: CHECKBOX_MAP_ENTRY}

        element = AsyncMock()
        element.evaluate = AsyncMock(side_effect=["checkbox", True])
        _attach_element(mock_page, element)

        with patch("browsercontrol.tools.forms.browser", mock_browser_manager):
            with patch("browsercontrol.tools.forms.get_element_map", return_value=checkbox_map):
                mock_browser_manager.page = mock_page
                mock_browser_manager.screenshot_with_som.return_value = (
                    b"screenshot",
                    checkbox_map,
                )

                tool = await mcp_server.get_tool("check_checkbox")
                result = await tool.fn(element_id=5)

                element.check.assert_awaited_once()
                element.click.assert_not_awaited()
                assert "Checked element 5" in result[0]

    @pytest.mark.asyncio
    async def test_uncheck_uses_uncheck(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """check=False must uncheck, not toggle."""
        register_form_tools(mcp_server)

        checkbox_map = {**sample_element_map, 5: CHECKBOX_MAP_ENTRY}

        element = AsyncMock()
        element.evaluate = AsyncMock(side_effect=["checkbox", False])
        _attach_element(mock_page, element)

        with patch("browsercontrol.tools.forms.browser", mock_browser_manager):
            with patch("browsercontrol.tools.forms.get_element_map", return_value=checkbox_map):
                mock_browser_manager.page = mock_page
                mock_browser_manager.screenshot_with_som.return_value = (
                    b"screenshot",
                    checkbox_map,
                )

                tool = await mcp_server.get_tool("check_checkbox")
                result = await tool.fn(element_id=5, check=False)

                element.uncheck.assert_awaited_once()
                element.check.assert_not_awaited()
                assert "Unchecked element 5" in result[0]

    @pytest.mark.asyncio
    async def test_non_checkbox_raises(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """A text input must be rejected rather than reported as checked."""
        register_form_tools(mcp_server)

        element = AsyncMock()
        element.evaluate = AsyncMock(return_value="text")
        _attach_element(mock_page, element)

        with patch("browsercontrol.tools.forms.browser", mock_browser_manager):
            with patch(
                "browsercontrol.tools.forms.get_element_map", return_value=sample_element_map
            ):
                mock_browser_manager.page = mock_page
                mock_browser_manager.screenshot_with_som.return_value = (
                    b"screenshot",
                    sample_element_map,
                )

                tool = await mcp_server.get_tool("check_checkbox")
                with pytest.raises(RuntimeError, match="not a checkbox or radio"):
                    await tool.fn(element_id=2)

                element.check.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_uncheck_radio_raises(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """Radios cannot be unchecked; say so instead of silently toggling."""
        register_form_tools(mcp_server)

        checkbox_map = {**sample_element_map, 5: CHECKBOX_MAP_ENTRY}

        element = AsyncMock()
        element.evaluate = AsyncMock(return_value="radio")
        _attach_element(mock_page, element)

        with patch("browsercontrol.tools.forms.browser", mock_browser_manager):
            with patch("browsercontrol.tools.forms.get_element_map", return_value=checkbox_map):
                mock_browser_manager.page = mock_page
                mock_browser_manager.screenshot_with_som.return_value = (
                    b"screenshot",
                    checkbox_map,
                )

                tool = await mcp_server.get_tool("check_checkbox")
                with pytest.raises(RuntimeError, match="cannot be unchecked"):
                    await tool.fn(element_id=5, check=False)

                element.uncheck.assert_not_awaited()


class TestUploadFile:
    """Test upload_file tool."""

    @pytest.mark.asyncio
    async def test_upload_file_to_input(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map, tmp_path
    ):
        """Test uploading a file to file input."""
        register_form_tools(mcp_server)

        # Create a temporary file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        file_input_map = {
            **sample_element_map,
            6: {
                "tag": "input",
                "text": "",
                "x": 100,
                "y": 500,
                "width": 200,
                "height": 30,
                "centerX": 200,
                "centerY": 515,
            },
        }

        mock_element = AsyncMock()
        mock_handle = MagicMock()
        mock_handle.as_element.return_value = mock_element
        mock_page.evaluate_handle.return_value = mock_handle

        with patch("browsercontrol.tools.forms.browser", mock_browser_manager):
            with patch("browsercontrol.tools.forms.get_element_map", return_value=file_input_map):
                mock_browser_manager.page = mock_page
                mock_browser_manager.screenshot_with_som.return_value = (
                    b"screenshot",
                    file_input_map,
                )

                tool = await mcp_server.get_tool("upload_file")
                result = await tool.fn(element_id=6, file_path=str(test_file))

                mock_element.set_input_files.assert_called_once_with(str(test_file))
                assert "Uploaded" in result[0]

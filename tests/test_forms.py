"""Tests for form handling tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp import FastMCP

from browsercontrol.tools.forms import register_form_tools


@pytest.fixture
def mcp_server():
    """Create a FastMCP server instance for testing."""
    return FastMCP("test")


class TestSelectOption:
    """Test select_option tool."""

    @pytest.mark.asyncio
    async def test_select_dropdown_option(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """Test selecting an option from dropdown."""
        register_form_tools(mcp_server)

        # Add a select element to the map
        select_map = {
            **sample_element_map,
            4: {
                "tag": "select",
                "text": "",
                "x": 100,
                "y": 300,
                "width": 150,
                "height": 30,
                "centerX": 175,
                "centerY": 315,
            },
        }

        mock_locator = AsyncMock()
        mock_locator.select_option = AsyncMock()
        mock_page.locator.return_value = mock_locator

        with patch("browsercontrol.tools.forms.browser", mock_browser_manager):
            with patch("browsercontrol.tools.forms.get_element_map", return_value=select_map):
                mock_browser_manager.page = mock_page
                mock_browser_manager.screenshot_with_som.return_value = (b"screenshot", select_map)

                tool = mcp_server._tool_manager._tools["select_option"]
                result = await tool.fn(element_id=4, option="Option 1")

                assert "Selected 'Option 1'" in result[0]


class TestCheckCheckbox:
    """Test check_checkbox tool."""

    @pytest.mark.asyncio
    async def test_toggle_checkbox(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """Test toggling a checkbox."""
        register_form_tools(mcp_server)

        checkbox_map = {
            **sample_element_map,
            5: {
                "tag": "input",
                "text": "",
                "x": 50,
                "y": 400,
                "width": 20,
                "height": 20,
                "centerX": 60,
                "centerY": 410,
            },
        }

        with patch("browsercontrol.tools.forms.browser", mock_browser_manager):
            with patch("browsercontrol.tools.forms.get_element_map", return_value=checkbox_map):
                mock_browser_manager.page = mock_page
                mock_browser_manager.screenshot_with_som.return_value = (
                    b"screenshot",
                    checkbox_map,
                )

                tool = mcp_server._tool_manager._tools["check_checkbox"]
                result = await tool.fn(element_id=5)

                mock_page.mouse.click.assert_called_once_with(60, 410)
                assert "element 5" in result[0]


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

                tool = mcp_server._tool_manager._tools["upload_file"]
                result = await tool.fn(element_id=6, file_path=str(test_file))

                mock_element.set_input_files.assert_called_once_with(str(test_file))
                assert "Uploaded" in result[0]

"""Tests for content extraction tools."""

from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import FastMCP

from browsercontrol.tools.content import register_content_tools


@pytest.fixture
def mcp_server():
    """Create a FastMCP server instance for testing."""
    return FastMCP("test")


class TestGetPageContent:
    """Test get_page_content tool."""

    @pytest.mark.asyncio
    async def test_get_page_content_as_markdown(self, mcp_server, mock_browser_manager, mock_page):
        """Test getting page content as markdown."""
        register_content_tools(mcp_server)

        mock_page.content.return_value = "<html><body><h1>Test</h1><p>Content</p></body></html>"

        with patch("browsercontrol.tools.content.browser", mock_browser_manager):
            with patch("markdownify.markdownify") as mock_md:
                mock_md.return_value = "# Test\n\nContent"
                mock_browser_manager.page = mock_page

                tool = mcp_server._tool_manager._tools["get_page_content"]
                result = await tool.fn()

                assert "# Test" in result[0]
                assert "Content" in result[0]


class TestGetText:
    """Test get_text tool."""

    @pytest.mark.asyncio
    async def test_get_text_from_element(
        self, mcp_server, mock_browser_manager, mock_page, sample_element_map
    ):
        """Test getting text from an element."""
        register_content_tools(mcp_server)

        with (
            patch("browsercontrol.tools.content.browser", mock_browser_manager),
            patch("browsercontrol.tools.content.get_element_map", return_value=sample_element_map),
        ):
            mock_browser_manager.page = mock_page

            tool = mcp_server._tool_manager._tools["get_text"]
            result = await tool.fn(element_id=1)

            assert "Sign In" in result[0]


class TestGetPageInfo:
    """Test get_page_info tool."""

    @pytest.mark.asyncio
    async def test_get_page_info(self, mcp_server, mock_browser_manager, mock_page):
        """Test getting page URL and title."""
        register_content_tools(mcp_server)

        mock_page.url = "https://example.com"
        mock_page.title.return_value = "Example Page"

        with patch("browsercontrol.tools.content.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page

            tool = mcp_server._tool_manager._tools["get_page_info"]
            result = await tool.fn()

            assert "https://example.com" in result[0]
            assert "Example Page" in result[0]


class TestRunJavaScript:
    """Test run_javascript tool."""

    @pytest.mark.asyncio
    async def test_run_javascript(self, mcp_server, mock_browser_manager, mock_page):
        """Test executing JavaScript code."""
        register_content_tools(mcp_server)

        mock_page.evaluate.return_value = {"result": "success"}

        with patch("browsercontrol.tools.content.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page

            tool = mcp_server._tool_manager._tools["run_javascript"]
            result = await tool.fn(script="return 1 + 1")

            mock_page.evaluate.assert_called_once_with("return 1 + 1")
            assert "success" in str(result)


class TestScreenshot:
    """Test screenshot tool."""

    @pytest.mark.asyncio
    async def test_screenshot_with_annotation(self, mcp_server, mock_browser_manager):
        """Test taking screenshot with SoM annotations."""
        register_content_tools(mcp_server)

        with patch("browsercontrol.tools.content.browser", mock_browser_manager):
            mock_browser_manager.screenshot_with_som.return_value = (
                b"screenshot",
                {1: {"tag": "button"}},
            )

            tool = mcp_server._tool_manager._tools["screenshot"]
            result = await tool.fn(annotate=True)

            mock_browser_manager.screenshot_with_som.assert_called_once()
            assert "Found 1 interactive" in result[0]

    @pytest.mark.asyncio
    async def test_screenshot_without_annotation(self, mcp_server, mock_browser_manager, mock_page):
        """Test taking plain screenshot without annotations."""
        register_content_tools(mcp_server)

        mock_page.screenshot.return_value = b"plain_screenshot"

        with patch("browsercontrol.tools.content.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page

            tool = mcp_server._tool_manager._tools["screenshot"]
            await tool.fn(annotate=False)

            mock_page.screenshot.assert_called_once()

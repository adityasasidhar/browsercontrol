"""Tests for content extraction tools."""

from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import FastMCP

from browsercontrol.elements import ElementNotFoundError
from browsercontrol.tools.content import MAX_TEXT_CHARS, register_content_tools


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

                tool = await mcp_server.get_tool("get_page_content")
                result = await tool.fn()

                assert "# Test" in result[0]
                assert "Content" in result[0]


class TestGetText:
    """Test get_text tool."""

    @pytest.mark.asyncio
    async def test_get_text_reads_the_live_element(self, mcp_server, mock_browser_manager):
        """get_text reads the page, not the truncated label cached in the element map."""
        register_content_tools(mcp_server)
        full_text = "Sign In " + "x" * 200
        locator = AsyncMock()
        locator.evaluate = AsyncMock(return_value=full_text)
        mock_browser_manager.resolve_element = AsyncMock(return_value=locator)

        with patch("browsercontrol.tools.content.browser", mock_browser_manager):
            tool = await mcp_server.get_tool("get_text")
            result = await tool.fn(element_id=1)

        mock_browser_manager.resolve_element.assert_awaited_once_with(1)
        assert result == f"Element 1 text: {full_text}"

    @pytest.mark.asyncio
    async def test_get_text_truncates_huge_text(self, mcp_server, mock_browser_manager):
        register_content_tools(mcp_server)
        locator = AsyncMock()
        locator.evaluate = AsyncMock(return_value="y" * (MAX_TEXT_CHARS + 50))
        mock_browser_manager.resolve_element = AsyncMock(return_value=locator)

        with patch("browsercontrol.tools.content.browser", mock_browser_manager):
            tool = await mcp_server.get_tool("get_text")
            result = await tool.fn(element_id=1)

        assert result.endswith("[text truncated]")

    @pytest.mark.asyncio
    async def test_get_text_unknown_element(self, mcp_server, mock_browser_manager):
        register_content_tools(mcp_server)
        mock_browser_manager.resolve_element = AsyncMock(
            side_effect=ElementNotFoundError(9, [1, 2])
        )

        with patch("browsercontrol.tools.content.browser", mock_browser_manager):
            tool = await mcp_server.get_tool("get_text")
            result = await tool.fn(element_id=9)

        assert result == "Error: Element 9 not found. Valid IDs: [1, 2]"


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

            tool = await mcp_server.get_tool("get_page_info")
            result = await tool.fn()

            assert "https://example.com" in result
            assert "Example Page" in result


class TestRunJavaScript:
    """Test run_javascript tool."""

    @pytest.mark.asyncio
    async def test_run_javascript(self, mcp_server, mock_browser_manager, mock_page):
        """Test executing JavaScript code."""
        register_content_tools(mcp_server)

        mock_page.evaluate.return_value = {"result": "success"}

        with patch("browsercontrol.tools.content.browser", mock_browser_manager):
            mock_browser_manager.page = mock_page

            tool = await mcp_server.get_tool("run_javascript")
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

            tool = await mcp_server.get_tool("screenshot")
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

            tool = await mcp_server.get_tool("screenshot")
            await tool.fn(annotate=False)

            mock_page.screenshot.assert_called_once()


class TestSavePdf:
    """Test save_pdf tool."""

    @pytest.mark.asyncio
    async def test_save_pdf_default_name(
        self, mcp_server, mock_browser_manager, mock_page, tmp_path
    ):
        register_content_tools(mcp_server)
        mock_page.title = AsyncMock(return_value="My: Page/Title")
        mock_page.pdf = AsyncMock(return_value=b"%PDF-1.4 data")
        with (
            patch("browsercontrol.tools.content.browser", mock_browser_manager),
            patch("browsercontrol.tools.content.config.downloads_dir", tmp_path / "dl"),
        ):
            tool = await mcp_server.get_tool("save_pdf")
            result = await tool.fn(landscape=True)
            again = await tool.fn(landscape=True)
        saved = tmp_path / "dl" / "My PageTitle.pdf"
        assert saved.read_bytes() == b"%PDF-1.4 data"
        assert str(saved) in result and "13 bytes" in result
        assert "My PageTitle (1).pdf" in again
        mock_page.pdf.assert_called_with(landscape=True, print_background=True)

    @pytest.mark.asyncio
    async def test_save_pdf_sanitizes_name(
        self, mcp_server, mock_browser_manager, mock_page, tmp_path
    ):
        register_content_tools(mcp_server)
        mock_page.title = AsyncMock(return_value="")
        mock_page.pdf = AsyncMock(return_value=b"%PDF")
        with (
            patch("browsercontrol.tools.content.browser", mock_browser_manager),
            patch("browsercontrol.tools.content.config.downloads_dir", tmp_path),
        ):
            tool = await mcp_server.get_tool("save_pdf")
            await tool.fn(file_name="../../etc/report")
            await tool.fn(file_name="..\\evil.PDF")
            await tool.fn()
        assert sorted(p.name for p in tmp_path.iterdir()) == ["evil.PDF", "page.pdf", "report.pdf"]

    @pytest.mark.asyncio
    async def test_save_pdf_headed_failure(
        self, mcp_server, mock_browser_manager, mock_page, tmp_path
    ):
        register_content_tools(mcp_server)
        mock_page.title = AsyncMock(return_value="t")
        mock_page.pdf = AsyncMock(side_effect=Exception("PrintToPDF is not implemented"))
        with (
            patch("browsercontrol.tools.content.browser", mock_browser_manager),
            patch("browsercontrol.tools.content.config.downloads_dir", tmp_path),
        ):
            tool = await mcp_server.get_tool("save_pdf")
            with pytest.raises(RuntimeError, match="BROWSER_HEADLESS=true"):
                await tool.fn()
        assert list(tmp_path.iterdir()) == []

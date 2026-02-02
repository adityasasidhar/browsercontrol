"""Tests for session recording tools."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp import FastMCP

from browsercontrol.tools.recording import register_recording_tools


@pytest.fixture
def mcp_server():
    """Create a FastMCP server instance for testing."""
    return FastMCP("test")


class TestRecording:
    """Test start/stop recording tools."""

    @pytest.mark.asyncio
    async def test_start_recording(self, mcp_server, mock_browser_manager, mock_context):
        """Test starting a recording session."""
        register_recording_tools(mcp_server)

        with patch("browsercontrol.tools.recording.browser", mock_browser_manager):
            mock_browser_manager._context = mock_context

            tool = mcp_server._tool_manager._tools["start_recording"]
            result = await tool.fn()

            mock_context.tracing.start.assert_called_once()
            assert "Started recording" in result

    @pytest.mark.asyncio
    async def test_stop_recording(
        self, mcp_server, mock_browser_manager, mock_context, temp_recordings_dir
    ):
        """Test stopping and saving a recording."""
        register_recording_tools(mcp_server)

        with patch("browsercontrol.tools.recording.browser", mock_browser_manager):
            with patch("browsercontrol.tools.recording.config") as mock_config:
                mock_config.user_data_dir = temp_recordings_dir
                mock_browser_manager._context = mock_context
                mock_browser_manager._recording = True

                tool = mcp_server._tool_manager._tools["stop_recording"]
                result = await tool.fn()

                mock_context.tracing.stop.assert_called_once()
                assert "Stopped recording" in result


class TestSnapshot:
    """Test take_snapshot tool."""

    @pytest.mark.asyncio
    async def test_take_snapshot(
        self, mcp_server, mock_browser_manager, mock_page, temp_recordings_dir
    ):
        """Test taking a snapshot of current page."""
        register_recording_tools(mcp_server)

        mock_page.screenshot.return_value = b"screenshot_data"
        mock_page.content.return_value = "<html><body>Test</body></html>"
        mock_page.url = "https://example.com"

        with patch("browsercontrol.tools.recording.browser", mock_browser_manager):
            with patch("browsercontrol.tools.recording.config") as mock_config:
                mock_config.user_data_dir = temp_recordings_dir
                mock_browser_manager.page = mock_page

                tool = mcp_server._tool_manager._tools["take_snapshot"]
                result = await tool.fn()

                assert "Saved snapshot" in result


class TestListRecordings:
    """Test list_recordings tool."""

    @pytest.mark.asyncio
    async def test_list_recordings(self, mcp_server, temp_recordings_dir):
        """Test listing all saved recordings."""
        register_recording_tools(mcp_server)

        # Create some fake recording files
        recordings_dir = temp_recordings_dir / "recordings"
        recordings_dir.mkdir()
        (recordings_dir / "session_20260101.zip").write_bytes(b"fake_recording")
        (recordings_dir / "session_20260102.zip").write_bytes(b"fake_recording")

        with patch("browsercontrol.tools.recording.config") as mock_config:
            mock_config.user_data_dir = temp_recordings_dir

            tool = mcp_server._tool_manager._tools["list_recordings"]
            result = await tool.fn()

            assert "session_20260101.zip" in result
            assert "session_20260102.zip" in result

    @pytest.mark.asyncio
    async def test_list_recordings_empty(self, mcp_server, temp_recordings_dir):
        """Test listing recordings when directory is empty."""
        register_recording_tools(mcp_server)

        with patch("browsercontrol.tools.recording.config") as mock_config:
            mock_config.user_data_dir = temp_recordings_dir

            tool = mcp_server._tool_manager._tools["list_recordings"]
            result = await tool.fn()

            assert "No recordings found" in result

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

        mock_cdp = AsyncMock()
        mock_browser_manager.page.context.new_cdp_session.return_value = mock_cdp

        with patch("browsercontrol.tools.recording.browser", mock_browser_manager):
            tool = mcp_server._tool_manager._tools["start_recording"]
            result = await tool.fn()

            mock_cdp.send.assert_called_once()
            assert "Recording started" in result[0]

    @pytest.mark.asyncio
    async def test_stop_recording(
        self, mcp_server, mock_browser_manager, mock_context, temp_recordings_dir
    ):
        """Test stopping and saving a recording."""
        register_recording_tools(mcp_server)

        with patch("browsercontrol.tools.recording.browser", mock_browser_manager):
            with patch("browsercontrol.tools.recording.config") as mock_config:
                mock_config.user_data_dir = temp_recordings_dir
                mock_browser_manager.page.context = mock_context
                mock_browser_manager._recording = True

                tool = mcp_server._tool_manager._tools["stop_recording"]
                result = await tool.fn()

                mock_context.tracing.stop.assert_called_once()
                assert "Recording saved" in result[0]


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

                assert "Snapshot saved" in result[0]


class TestListRecordings:
    """Test list_recordings tool."""

    @pytest.mark.asyncio
    async def test_list_recordings(self, mcp_server, temp_recordings_dir):
        """Test listing all saved recordings."""
        register_recording_tools(mcp_server)

        # Create some fake recording files
        recordings_dir = temp_recordings_dir.parent / "recordings"
        recordings_dir.mkdir(parents=True, exist_ok=True)
        (recordings_dir / "session_20260101.zip").write_bytes(b"fake_recording")
        (recordings_dir / "session_20260102.zip").write_bytes(b"fake_recording")

        with patch("browsercontrol.tools.recording.config") as mock_config:
            mock_config.user_data_dir = temp_recordings_dir

            tool = mcp_server._tool_manager._tools["list_recordings"]
            result = await tool.fn()

            assert "session_20260101.zip" in result[0]
            assert "session_20260102.zip" in result[0]

    @pytest.mark.asyncio
    async def test_list_recordings_empty(self, mcp_server, temp_recordings_dir):
        """Test listing recordings when directory is empty."""
        register_recording_tools(mcp_server)

        with patch("browsercontrol.tools.recording.config") as mock_config:
            mock_config.user_data_dir = temp_recordings_dir

            tool = mcp_server._tool_manager._tools["list_recordings"]
            result = await tool.fn()

            assert "No recordings" in result[0]

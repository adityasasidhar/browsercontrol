"""Tests for session recording tools."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import FastMCP

import browsercontrol.tools.recording as recording_module
from browsercontrol.tools.recording import register_recording_tools


@pytest.fixture
def mcp_server() -> FastMCP:
    """Create a FastMCP server instance for testing."""
    return FastMCP("test")


class TestRecording:
    """Test start/stop recording tools."""

    @pytest.mark.asyncio
    async def test_start_recording(
        self, mcp_server: FastMCP, mock_browser_manager: object, temp_recordings_dir: Path
    ) -> None:
        """Test starting a recording session."""
        register_recording_tools(mcp_server)

        mock_tracing = AsyncMock()
        mock_browser_manager.page.context.tracing = mock_tracing  # type: ignore[attr-defined]

        with patch("browsercontrol.tools.recording.browser", mock_browser_manager):
            with patch("browsercontrol.tools.recording.config") as mock_config:
                mock_config.user_data_dir = temp_recordings_dir
                with patch.object(recording_module, "_recording_active", False):
                    tool = await mcp_server.get_tool("start_recording")
                    result = await tool.fn()

                    mock_tracing.start.assert_called_once_with(
                        screenshots=True, snapshots=True, sources=True
                    )
                    assert isinstance(result, str)
                    assert "Recording started" in result

    @pytest.mark.asyncio
    async def test_start_recording_already_active(
        self, mcp_server: FastMCP, mock_browser_manager: object
    ) -> None:
        """Test start_recording when a recording is already in progress."""
        register_recording_tools(mcp_server)

        with patch("browsercontrol.tools.recording.browser", mock_browser_manager):
            with patch.object(recording_module, "_recording_active", True):
                tool = await mcp_server.get_tool("start_recording")
                result = await tool.fn()

                assert isinstance(result, str)
                assert "already in progress" in result

    @pytest.mark.asyncio
    async def test_stop_recording(
        self, mcp_server: FastMCP, mock_browser_manager: object, temp_recordings_dir: Path
    ) -> None:
        """Test stopping and saving a recording."""
        register_recording_tools(mcp_server)

        mock_tracing = AsyncMock()
        mock_browser_manager.page.context.tracing = mock_tracing  # type: ignore[attr-defined]
        test_path = temp_recordings_dir / "test_recording.zip"

        with patch("browsercontrol.tools.recording.browser", mock_browser_manager):
            with patch.object(recording_module, "_recording_active", True):
                with patch.object(recording_module, "_recording_path", test_path):
                    tool = await mcp_server.get_tool("stop_recording")
                    result = await tool.fn()

                    mock_tracing.stop.assert_called_once_with(path=str(test_path))
                    assert isinstance(result, str)
                    assert "Recording saved" in result

    @pytest.mark.asyncio
    async def test_stop_recording_not_active(
        self, mcp_server: FastMCP, mock_browser_manager: object
    ) -> None:
        """Test stop_recording when no recording is in progress."""
        register_recording_tools(mcp_server)

        with patch("browsercontrol.tools.recording.browser", mock_browser_manager):
            with patch.object(recording_module, "_recording_active", False):
                tool = await mcp_server.get_tool("stop_recording")
                result = await tool.fn()

                assert isinstance(result, str)
                assert "No recording in progress" in result


class TestSnapshot:
    """Test take_snapshot tool."""

    @pytest.mark.asyncio
    async def test_take_snapshot(
        self,
        mcp_server: FastMCP,
        mock_browser_manager: object,
        mock_page: object,
        temp_recordings_dir: Path,
    ) -> None:
        """Test taking a snapshot of current page."""
        register_recording_tools(mcp_server)

        mock_page.screenshot.return_value = b"screenshot_data"  # type: ignore[attr-defined]
        mock_page.content.return_value = "<html><body>Test</body></html>"  # type: ignore[attr-defined]
        mock_page.url = "https://example.com"  # type: ignore[attr-defined]

        with patch("browsercontrol.tools.recording.browser", mock_browser_manager):
            with patch("browsercontrol.tools.recording.config") as mock_config:
                mock_config.user_data_dir = temp_recordings_dir
                mock_browser_manager.page = mock_page  # type: ignore[attr-defined]

                tool = await mcp_server.get_tool("take_snapshot")
                result = await tool.fn()

                assert isinstance(result, str)
                assert "Snapshot saved" in result


class TestListRecordings:
    """Test list_recordings tool."""

    @pytest.mark.asyncio
    async def test_list_recordings(self, mcp_server: FastMCP, tmp_path: Path) -> None:
        """Test listing all saved recordings."""
        register_recording_tools(mcp_server)

        # user_data_dir.parent == tmp_path, so recordings land inside tmp_path
        user_data_dir = tmp_path / "profile"
        user_data_dir.mkdir()
        recordings_dir = tmp_path / "recordings"
        recordings_dir.mkdir()
        (recordings_dir / "session_20260101.zip").write_bytes(b"fake_recording")
        (recordings_dir / "session_20260102.zip").write_bytes(b"fake_recording")

        with patch("browsercontrol.tools.recording.config") as mock_config:
            mock_config.user_data_dir = user_data_dir

            tool = await mcp_server.get_tool("list_recordings")
            result = await tool.fn()

            assert isinstance(result, str)
            assert "session_20260101.zip" in result
            assert "session_20260102.zip" in result

    @pytest.mark.asyncio
    async def test_list_recordings_empty(self, mcp_server: FastMCP, tmp_path: Path) -> None:
        """Test listing recordings when directory is empty."""
        register_recording_tools(mcp_server)

        user_data_dir = tmp_path / "profile"
        user_data_dir.mkdir()

        with patch("browsercontrol.tools.recording.config") as mock_config:
            mock_config.user_data_dir = user_data_dir

            tool = await mcp_server.get_tool("list_recordings")
            result = await tool.fn()

            assert isinstance(result, str)
            assert "No recordings" in result

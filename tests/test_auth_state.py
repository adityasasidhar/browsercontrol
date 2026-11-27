"""Tests for saving login state and loading it into isolated sessions."""

import json
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp import FastMCP

from browsercontrol.tools.sessions import auth_state_path, register_session_tools

STATE = {
    "cookies": [{"name": "sid", "value": "secret", "domain": "example.com"}],
    "origins": [{"origin": "https://example.com", "localStorage": []}],
}


@pytest.fixture
def mcp_server() -> FastMCP:
    server = FastMCP("test")
    register_session_tools(server)
    return server


@pytest.fixture
def auth_dir(tmp_path):
    with patch("browsercontrol.tools.sessions.config") as cfg:
        cfg.auth_dir = tmp_path / "auth"
        yield cfg.auth_dir


class TestAuthStatePath:
    @pytest.mark.parametrize("name", ["../evil", "a/b", "", ".hidden", "x" * 65, "a..b"])
    def test_rejects_path_like_names(self, name, auth_dir):
        with pytest.raises(ValueError):
            auth_state_path(name)

    def test_accepts_plain_names(self, auth_dir):
        assert auth_state_path("admin-user_1") == auth_dir / "admin-user_1.json"


class TestSaveAuthState:
    async def test_saves_state_with_owner_only_permissions(
        self, mcp_server, mock_browser_manager, auth_dir
    ):
        context = MagicMock()
        context.storage_state = AsyncMock(return_value=STATE)
        mock_browser_manager.session = MagicMock(context=context)

        with patch("browsercontrol.tools.sessions.browser", mock_browser_manager):
            tool = await mcp_server.get_tool("save_auth_state")
            result = await tool.fn(name="admin")

        path = auth_dir / "admin.json"
        assert json.loads(path.read_text()) == STATE
        context.storage_state.assert_awaited_once_with(indexed_db=True)
        if sys.platform != "win32":
            assert os.stat(path).st_mode & 0o777 == 0o600
        assert "1 cookie(s); storage for 1 origin(s): https://example.com\n" in result
        assert "secret" not in result

    async def test_bad_name_is_reported(self, mcp_server, mock_browser_manager, auth_dir):
        with patch("browsercontrol.tools.sessions.browser", mock_browser_manager):
            tool = await mcp_server.get_tool("save_auth_state")
            with pytest.raises(RuntimeError, match="Invalid auth state name"):
                await tool.fn(name="../x")


class TestListAuthStates:
    async def test_empty(self, mcp_server, auth_dir):
        tool = await mcp_server.get_tool("list_auth_states")
        assert "No saved auth states" in await tool.fn()

    async def test_lists_counts_and_unreadable_files(self, mcp_server, auth_dir):
        auth_dir.mkdir()
        (auth_dir / "admin.json").write_text(json.dumps(STATE))
        (auth_dir / "broken.json").write_text("{not json")
        tool = await mcp_server.get_tool("list_auth_states")
        result = await tool.fn()
        assert "admin (1 cookie(s), 1 origin(s))" in result
        assert "broken (unreadable)" in result


class TestCreateSessionWithAuthState:
    async def test_passes_state_file_to_manager(self, mcp_server, mock_browser_manager, auth_dir):
        auth_dir.mkdir()
        (auth_dir / "admin.json").write_text(json.dumps(STATE))
        mock_browser_manager.create_session = AsyncMock(return_value=MagicMock(page=None))

        with patch("browsercontrol.tools.sessions.browser", mock_browser_manager):
            tool = await mcp_server.get_tool("create_session")
            text, _ = await tool.fn(name="s1", auth_state="admin")

        mock_browser_manager.create_session.assert_awaited_once_with(
            "s1", None, auth_dir / "admin.json"
        )
        assert "with auth state 'admin'" in text

    async def test_missing_state_lists_saved(self, mcp_server, mock_browser_manager, auth_dir):
        auth_dir.mkdir()
        (auth_dir / "other.json").write_text("{}")
        mock_browser_manager.create_session = AsyncMock()

        with patch("browsercontrol.tools.sessions.browser", mock_browser_manager):
            tool = await mcp_server.get_tool("create_session")
            with pytest.raises(RuntimeError, match="Saved: other"):
                await tool.fn(name="s1", auth_state="admin")
        mock_browser_manager.create_session.assert_not_awaited()

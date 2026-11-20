"""Unit tests (no browser) for the agent-capability features."""

import json
from pathlib import Path
from typing import Any, ClassVar
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp import FastMCP

from browsercontrol.__main__ import _is_loopback, parse_args
from browsercontrol.browser import BrowserManager, current_client
from browsercontrol.codegen import render_test
from browsercontrol.config import Config
from browsercontrol.session import Session, answer_dialog, url_matches
from browsercontrol.tools._summary import get_screenshot_with_summary
from browsercontrol.tools.batch import register_batch_tools
from browsercontrol.tools.extract import format_table, register_extract_tools
from browsercontrol.tools.network import har_entry, register_network_tools
from browsercontrol.tools.sessions import register_session_tools
from browsercontrol.tools.waiting import register_waiting_tools


async def _tool(register: Any, name: str) -> Any:
    mcp = FastMCP("test")
    register(mcp)
    tool = await mcp.get_tool(name)
    assert tool is not None
    return tool.fn


class TestUrlMatches:
    @pytest.mark.parametrize(
        ("pattern", "url", "expected"),
        [
            ("/api/", "https://x.com/api/users", True),
            ("/api/", "https://x.com/web", False),
            ("**/api/*", "https://x.com/api/users", True),
            ("re:users/\\d+$", "https://x.com/users/12", True),
            ("re:users/\\d+$", "https://x.com/users/me", False),
        ],
    )
    def test_patterns(self, pattern: str, url: str, expected: bool) -> None:
        assert url_matches(pattern, url) is expected


class TestDialogs:
    def _dialog(self, kind: str) -> MagicMock:
        dialog = MagicMock(type=kind, message="Sure?")
        dialog.accept, dialog.dismiss = AsyncMock(), AsyncMock()
        return dialog

    @pytest.mark.asyncio
    async def test_default_policy_dismisses_confirm_and_tells_the_agent(self) -> None:
        session, dialog = Session("s"), self._dialog("confirm")
        await answer_dialog(session, dialog)
        dialog.dismiss.assert_awaited_once()
        (notice,) = session.drain_notices()
        assert "confirm('Sure?'), dismissed" in notice and "handle_dialog" in notice
        assert session.drain_notices() == []

    @pytest.mark.asyncio
    async def test_policy_applies_once(self) -> None:
        session = Session("s", dialog_policy={"accept": True, "prompt_text": "Bob"})
        dialog = self._dialog("prompt")
        await answer_dialog(session, dialog)
        dialog.accept.assert_awaited_once_with("Bob")
        assert session.dialog_policy is None
        assert session.dialogs[-1]["outcome"] == "accepted with 'Bob'"


class TestCodegen:
    TARGET: ClassVar[dict[str, Any]] = {
        "kind": "role",
        "role": "button",
        "name": "Go",
        "frames": [],
    }

    def test_python_test_is_valid_and_hides_passwords(self) -> None:
        actions = [
            {"action": "navigate", "url": "https://x.com"},
            {"action": "fill", "target": {"kind": "label", "value": "Pw", "password": True}},
            {"action": "click", "target": self.TARGET, "click_count": 2},
            {"action": "mock", "pattern": "re:api", "status": 500, "body": "{}"},
            {"action": "click", "target": None},
        ]
        code = render_test(actions, "My Flow!")
        compile(code, "generated.py", "exec")
        assert "def test_my_flow(page: Page) -> None:" in code
        assert 'os.environ["BC_SECRET_1"]' in code
        assert 'get_by_role("button", name="Go", exact=True).dblclick()' in code
        assert 're.compile("api")' in code and "import re" in code
        assert "# click: not replayable" in code

    def test_frames_and_typescript(self) -> None:
        target = {
            **self.TARGET,
            "frames": [{"kind": "css", "value": "#pay"}],
            "first": True,
        }
        code = render_test([{"action": "click", "target": target}], "t", "typescript")
        assert 'page.frameLocator("#pay").getByRole("button"' in code
        assert ".first().click();" in code

    def test_unknown_language(self) -> None:
        with pytest.raises(ValueError, match="Unsupported language"):
            render_test([], "t", "ruby")

    def test_empty_log(self) -> None:
        assert "pass  # no actions were recorded" in render_test([], "")


class TestFormatTable:
    def test_json_dedupes_and_fills_headers(self) -> None:
        data = json.loads(format_table(["A", "A", ""], [["1", "2", "3"]], "json"))
        assert data == [{"A": "1", "A_": "2", "column_3": "3"}]

    def test_markdown_and_csv(self) -> None:
        assert "| x \\| y |" in format_table(["h"], [["x | y"]], "markdown")
        assert format_table(["h"], [["v"]], "csv").splitlines() == ["h", "v"]

    def test_bad_format(self) -> None:
        with pytest.raises(ValueError):
            format_table([], [], "xml")


class TestHar:
    @pytest.mark.asyncio
    async def test_entry_shape(self) -> None:
        response = MagicMock()
        response.body = AsyncMock(return_value=b'{"a": 1}')
        entry = {
            "method": "POST",
            "url": "https://x.com/api?q=1",
            "status": 201,
            "start_time": 1.0,
            "duration": 5,
            "request_headers": {"content-type": "application/json"},
            "response_headers": {"content-type": "application/json"},
            "post_data": "{}",
            "_response": response,
        }
        har = await har_entry(entry, include_body=True)
        assert har["request"]["queryString"] == [{"name": "q", "value": "1"}]
        assert har["request"]["postData"]["text"] == "{}"
        assert har["response"]["content"]["text"] == '{"a": 1}'
        failed = await har_entry({"url": "u", "status": "failed"}, include_body=True)
        assert failed["response"]["status"] == 0


class TestSummaryNotices:
    @pytest.mark.asyncio
    async def test_notices_lead_the_summary(self) -> None:
        manager = MagicMock()
        manager.screenshot_with_som = AsyncMock(return_value=(b"png", {}))
        manager.drain_notices = MagicMock(return_value=["Downloaded a.txt to /d/a.txt"])
        _, summary = await get_screenshot_with_summary(manager)
        assert summary.startswith("Notice: Downloaded a.txt")


class TestToolErrors:
    @pytest.mark.asyncio
    async def test_act_validates_steps(self, mock_browser_manager: Any) -> None:
        with patch("browsercontrol.tools.batch.browser", mock_browser_manager):
            act = await _tool(register_batch_tools, "act")
            with pytest.raises(RuntimeError, match="steps is empty"):
                await act(steps=[])
            text, _ = await act(steps=[{"action": "type", "element_id": 1}])
            assert "FAILED (type): 'type' needs 'text'" in text

    @pytest.mark.asyncio
    async def test_act_continues_when_asked(self, mock_browser_manager: Any) -> None:
        with patch("browsercontrol.tools.batch.browser", mock_browser_manager):
            act = await _tool(register_batch_tools, "act")
            text, _ = await act(
                steps=[{"action": "nope"}, {"action": "press", "key": "Enter"}],
                stop_on_error=False,
            )
            assert "Ran 2 of 2 step(s), 1 failed" in text
            mock_browser_manager.page.keyboard.press.assert_awaited_with("Enter")

    @pytest.mark.asyncio
    async def test_wait_for_rejects_bad_state(self, mock_browser_manager: Any) -> None:
        with patch("browsercontrol.tools.waiting.browser", mock_browser_manager):
            wait_for = await _tool(register_waiting_tools, "wait_for")
            with pytest.raises(RuntimeError, match="state must be one of"):
                await wait_for(text="x", state="sideways")

    @pytest.mark.asyncio
    async def test_extract_rejects_empty_schema(self, mock_browser_manager: Any) -> None:
        with patch("browsercontrol.tools.extract.browser", mock_browser_manager):
            extract = await _tool(register_extract_tools, "extract")
            with pytest.raises(RuntimeError, match="non-empty object"):
                await extract(schema={})

    @pytest.mark.asyncio
    async def test_unknown_request_id(self, mock_browser_manager: Any) -> None:
        mock_browser_manager.session = Session("s")
        with patch("browsercontrol.tools.network.browser", mock_browser_manager):
            details = await _tool(register_network_tools, "get_request_details")
            assert "No captured request #7" in await details(request_id=7)

    @pytest.mark.asyncio
    async def test_connect_failure_explains_setup(self, mock_browser_manager: Any) -> None:
        mock_browser_manager.connect_over_cdp = AsyncMock(side_effect=OSError("refused"))
        with patch("browsercontrol.tools.sessions.browser", mock_browser_manager):
            connect = await _tool(register_session_tools, "connect_to_chrome")
            with pytest.raises(RuntimeError, match="--remote-debugging-port"):
                await connect()


class TestSessions:
    def test_clients_are_bound_independently(self) -> None:
        manager = BrowserManager()
        manager._sessions["other"] = Session("other", isolated=True)
        token = current_client.set("client-a")
        try:
            manager.bind("other")
            assert manager.session.name == "other"
        finally:
            current_client.reset(token)
        assert manager.session.name == "default"
        with pytest.raises(ValueError, match="No session named"):
            manager.bind("missing")

    @pytest.mark.asyncio
    async def test_default_session_cannot_be_closed(self) -> None:
        with pytest.raises(ValueError, match="cannot be closed"):
            await BrowserManager().close_session("default")

    def test_password_text_is_never_logged(self) -> None:
        manager = BrowserManager()
        manager.log_action("fill", {"kind": "css", "value": "#pw", "password": True}, text="s")
        assert "text" not in manager.get_action_log()[0]


class TestEntryPoint:
    def test_defaults_and_flags(self) -> None:
        assert parse_args([]).transport == "stdio"
        args = parse_args(["--transport", "http", "--port", "9000", "--isolate-clients"])
        assert (args.transport, args.port, args.isolate_clients) == ("http", 9000, True)

    @pytest.mark.parametrize(
        ("host", "expected"), [("127.0.0.1", True), ("localhost", True), ("0.0.0.0", False)]
    )
    def test_loopback(self, host: str, expected: bool) -> None:
        assert _is_loopback(host) is expected


def test_config_reads_new_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("BROWSER_USER_DATA_DIR", str(tmp_path / "p"))
    monkeypatch.setenv("BROWSER_CDP_URL", "http://localhost:9222")
    monkeypatch.setenv("BROWSER_ISOLATE_CLIENTS", "true")
    monkeypatch.setenv("BROWSER_TRANSPORT", "HTTP")
    monkeypatch.setenv("BROWSER_SETTLE_TIMEOUT", "500")
    cfg = Config.from_env()
    assert cfg.cdp_url == "http://localhost:9222"
    assert cfg.isolate_clients and cfg.transport == "http" and cfg.settle_timeout_ms == 500
    assert cfg.downloads_dir == tmp_path / "downloads"
    assert cfg.generated_tests_dir == tmp_path / "generated_tests"

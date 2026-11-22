"""Unit tests (no browser) for the verify_* tools and their export_test renderers."""

from collections.abc import Iterator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp import FastMCP

from browsercontrol.codegen import render_test
from browsercontrol.elements import ElementNotFoundError
from browsercontrol.tools.assertions import register_assertion_tools

TARGET = {"kind": "label", "value": "Name", "frames": [], "password": False}


async def _tool(name: str) -> Any:
    mcp = FastMCP("test")
    register_assertion_tools(mcp)
    tool = await mcp.get_tool(name)
    assert tool is not None
    return tool.fn


@pytest.fixture
def mgr(mock_browser_manager: Any) -> Iterator[Any]:
    with patch("browsercontrol.tools.assertions.browser", mock_browser_manager):
        yield mock_browser_manager


def _page_text(mgr: Any, visible: bool) -> None:
    visible_matches = MagicMock()
    visible_matches.count = AsyncMock(return_value=1 if visible else 0)
    matches = MagicMock()
    matches.filter = MagicMock(return_value=visible_matches)
    mgr.page.get_by_text = MagicMock(return_value=matches)


class TestVerifyText:
    @pytest.mark.asyncio
    async def test_page_text_pass(self, mgr: Any) -> None:
        _page_text(mgr, True)
        result = await (await _tool("verify_text"))(text="Hello")
        assert result.startswith("PASS:")
        mgr.log_action.assert_called_once_with("assert_text", None, text="Hello", present=True)

    @pytest.mark.asyncio
    async def test_absent_text_pass(self, mgr: Any) -> None:
        _page_text(mgr, False)
        result = await (await _tool("verify_text"))(text="Error", present=False)
        assert result.startswith("PASS:")
        mgr.log_action.assert_called_once_with("assert_text", None, text="Error", present=False)

    @pytest.mark.asyncio
    async def test_page_text_fail_not_logged(self, mgr: Any) -> None:
        _page_text(mgr, True)
        result = await (await _tool("verify_text"))(text="Hello", present=False)
        assert result.startswith("FAIL:")
        mgr.log_action.assert_not_called()

    @pytest.mark.asyncio
    async def test_element_text(self, mgr: Any) -> None:
        locator = MagicMock()
        locator.inner_text = AsyncMock(return_value="Total: 42 items")
        mgr.resolve_element = AsyncMock(return_value=locator)
        mgr.codegen_target = AsyncMock(return_value=TARGET)
        fn = await _tool("verify_text")
        assert (await fn(text="42", element_id=3)).startswith("PASS:")
        mgr.log_action.assert_called_once_with("assert_text", TARGET, text="42", present=True)
        mgr.log_action.reset_mock()
        assert (await fn(text="99", element_id=3)).startswith("FAIL:")
        mgr.log_action.assert_not_called()

    @pytest.mark.asyncio
    async def test_element_error(self, mgr: Any) -> None:
        mgr.resolve_element = AsyncMock(side_effect=ElementNotFoundError(9, [1, 2]))
        result = await (await _tool("verify_text"))(text="x", element_id=9)
        assert result.startswith("Error:")
        assert "9" in result
        mgr.log_action.assert_not_called()


class TestVerifyUrl:
    @pytest.mark.asyncio
    async def test_pass_and_fail(self, mgr: Any) -> None:
        mgr.page.url = "https://example.com/cart?id=1"
        fn = await _tool("verify_url")
        assert (await fn(pattern="/cart")).startswith("PASS:")
        mgr.log_action.assert_called_once_with("assert_url", pattern="/cart")
        mgr.log_action.reset_mock()
        assert (await fn(pattern="re:/checkout$")).startswith("FAIL:")
        mgr.log_action.assert_not_called()


class TestVerifyValue:
    @pytest.mark.asyncio
    async def test_pass_and_fail(self, mgr: Any) -> None:
        locator = MagicMock()
        locator.input_value = AsyncMock(return_value="alice")
        mgr.resolve_element = AsyncMock(return_value=locator)
        mgr.codegen_target = AsyncMock(return_value=TARGET)
        fn = await _tool("verify_value")
        assert (await fn(element_id=2, expected="alice")).startswith("PASS:")
        mgr.log_action.assert_called_once_with("assert_value", TARGET, text="alice")
        mgr.log_action.reset_mock()
        assert (await fn(element_id=2, expected="bob")).startswith("FAIL:")
        mgr.log_action.assert_not_called()

    @pytest.mark.asyncio
    async def test_element_error(self, mgr: Any) -> None:
        mgr.resolve_element = AsyncMock(side_effect=ElementNotFoundError(4, [1]))
        result = await (await _tool("verify_value"))(element_id=4, expected="x")
        assert result.startswith("Error:")
        mgr.log_action.assert_not_called()


class TestRenderAssertions:
    def test_text_python(self) -> None:
        code = render_test(
            [
                {"action": "assert_text", "target": None, "text": "Hi", "present": True},
                {"action": "assert_text", "target": None, "text": "Bye", "present": False},
                {"action": "assert_text", "target": TARGET, "text": "42", "present": True},
                {"action": "assert_text", "target": TARGET, "text": "0", "present": False},
            ],
            "t",
        )
        assert 'expect(page.get_by_text("Hi").filter(visible=True).first).to_be_visible()' in code
        assert 'expect(page.get_by_text("Bye").filter(visible=True)).to_have_count(0)' in code
        assert 'expect(page.get_by_label("Name", exact=True)).to_contain_text("42")' in code
        assert ').not_to_contain_text("0")' in code

    def test_text_typescript(self) -> None:
        code = render_test(
            [
                {"action": "assert_text", "target": None, "text": "Hi", "present": True},
                {"action": "assert_text", "target": None, "text": "Bye", "present": False},
                {"action": "assert_text", "target": TARGET, "text": "0", "present": False},
            ],
            "t",
            "typescript",
        )
        assert (
            'await expect(page.getByText("Hi").filter({ visible: true }).first()).toBeVisible();'
            in code
        )
        assert (
            'await expect(page.getByText("Bye").filter({ visible: true })).toHaveCount(0);' in code
        )
        assert ').not.toContainText("0");' in code

    def test_url(self) -> None:
        actions = [
            {"action": "assert_url", "target": None, "pattern": "/cart?x"},
            {"action": "assert_url", "target": None, "pattern": "re:/done$"},
            {"action": "assert_url", "target": None, "pattern": "example.com/a.b"},
        ]
        py = render_test(actions, "t")
        assert "import re" in py
        assert 'expect(page).to_have_url("/cart?x")' in py
        assert 'expect(page).to_have_url(re.compile("/done$"))' in py
        assert 'to_have_url(re.compile(re.escape("example.com/a.b")))' in py
        ts = render_test(actions, "t", "typescript")
        assert 'await expect(page).toHaveURL(new RegExp("/done$"));' in ts
        assert 'toHaveURL(new RegExp("example\\\\.com/a\\\\.b"));' in ts

    def test_value_and_password(self) -> None:
        pw = {**TARGET, "password": True}
        actions = [
            {"action": "assert_value", "target": TARGET, "text": "alice"},
            {"action": "assert_value", "target": pw},
        ]
        py = render_test(actions, "t")
        assert 'expect(page.get_by_label("Name", exact=True)).to_have_value("alice")' in py
        assert "# assert_value: password field value not recorded" in py
        ts = render_test(actions, "t", "typescript")
        assert 'await expect(page.getByLabel("Name", { exact: true })).toHaveValue("alice");' in ts

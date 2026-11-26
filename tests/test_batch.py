"""Tests for the ``act`` batching tool and its per-step executor (tools/batch.py)."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp import FastMCP

from browsercontrol.elements import ACTION_TIMEOUT_MS, ElementNotFoundError, StaleElementError
from browsercontrol.tools.batch import (
    MAX_STEPS,
    SCROLL_AMOUNTS,
    STEP_ACTIONS,
    _need,
    _run_step,
    register_batch_tools,
)

# Every argument any step could need, so only an unhandled action can fail.
FULL_STEP: dict[str, Any] = {
    "element_id": 1,
    "target_id": 2,
    "url": "https://example.com",
    "key": "Enter",
    "text": "hello",
    "option": "Canada",
    "selector": "#done",
    "seconds": 0,
}


@pytest.fixture
def locator() -> AsyncMock:
    """A live, enabled text field, which is what most element steps act on."""
    loc = AsyncMock()
    loc.is_disabled.return_value = False
    loc.evaluate.return_value = "fill"
    return loc


@pytest.fixture
def manager(mock_browser_manager: Any, mock_page: Any, locator: AsyncMock) -> Any:
    """The stubbed manager patched into ``tools.batch``, resolving every ID to ``locator``."""
    mock_browser_manager.page = mock_page
    mock_page.get_by_text.return_value.first.wait_for = AsyncMock()
    mock_page.locator.return_value.first.wait_for = AsyncMock()
    mock_browser_manager.resolve_element = AsyncMock(return_value=locator)
    mock_browser_manager.screenshot_with_som = AsyncMock(return_value=(b"png", {}))
    with patch("browsercontrol.tools.batch.browser", mock_browser_manager):
        yield mock_browser_manager


async def _act() -> Any:
    mcp = FastMCP("test")
    register_batch_tools(mcp)
    tool = await mcp.get_tool("act")
    assert tool is not None
    return tool.fn


class TestNeed:
    def test_returns_the_value(self) -> None:
        assert _need({"action": "press", "key": "Enter"}, "key") == "Enter"

    def test_falsy_values_are_still_present(self) -> None:
        assert _need({"action": "click", "element_id": 0}, "element_id") == 0

    @pytest.mark.parametrize("step", [{"action": "press"}, {"action": "press", "key": None}])
    def test_missing_or_none_raises_naming_action_and_key(self, step: dict[str, Any]) -> None:
        with pytest.raises(ValueError, match="'press' needs 'key'"):
            _need(step, "key")


class TestStepActionsAreHandled:
    """Every advertised action must have an executor, so a new one cannot be forgotten."""

    @pytest.mark.parametrize("action", STEP_ACTIONS)
    async def test_run_step_handles_every_action(self, manager: Any, action: str) -> None:
        result = await _run_step({"action": action, **FULL_STEP})
        assert isinstance(result, str)
        assert result

    def test_step_actions_has_no_duplicates(self) -> None:
        assert len(set(STEP_ACTIONS)) == len(STEP_ACTIONS)

    async def test_unknown_action_lists_every_valid_action(self, manager: Any) -> None:
        with pytest.raises(ValueError, match="unknown action 'teleport'") as exc:
            await _run_step({"action": "teleport", "element_id": 1})
        for action in STEP_ACTIONS:
            assert action in str(exc.value)

    async def test_missing_action_is_unknown(self, manager: Any) -> None:
        with pytest.raises(ValueError, match="unknown action None"):
            await _run_step({"element_id": 1})

    async def test_tool_description_documents_every_action(self) -> None:
        """The act tool's docstring is what the agent reads; it must mention each action."""
        mcp = FastMCP("test")
        register_batch_tools(mcp)
        tool = await mcp.get_tool("act")
        assert tool is not None
        for action in STEP_ACTIONS:
            assert f'"{action}"' in (tool.description or ""), action


class TestPageSteps:
    """Steps that act on the page itself and need no element."""

    async def test_navigate(self, manager: Any, mock_page: Any) -> None:
        result = await _run_step({"action": "navigate", "url": "https://example.com/a"})

        mock_page.goto.assert_awaited_once_with(
            "https://example.com/a", wait_until="domcontentloaded"
        )
        manager.settle.assert_awaited_once()
        manager.log_action.assert_called_once_with("navigate", url="https://example.com/a")
        assert result == "navigated to https://example.com/a"
        manager.resolve_element.assert_not_awaited()

    async def test_press(self, manager: Any, mock_page: Any) -> None:
        result = await _run_step({"action": "press", "key": "Control+A"})

        mock_page.keyboard.press.assert_awaited_once_with("Control+A")
        manager.settle.assert_awaited_once_with(1500)
        manager.log_action.assert_called_once_with("press", key="Control+A")
        assert result == "pressed Control+A"

    @pytest.mark.parametrize(
        ("step", "expected_ms"),
        [
            ({"action": "wait"}, 1000),
            ({"action": "wait", "seconds": 2}, 2000),
            ({"action": "wait", "seconds": "0.25"}, 250),
        ],
    )
    async def test_wait(
        self, manager: Any, mock_page: Any, step: dict[str, Any], expected_ms: int
    ) -> None:
        result = await _run_step(step)

        mock_page.wait_for_timeout.assert_awaited_once_with(expected_ms)
        manager.log_action.assert_called_once_with("wait", ms=expected_ms)
        assert result == f"waited {expected_ms}ms"

    async def test_wait_for_text(self, manager: Any, mock_page: Any) -> None:
        waiter = AsyncMock()
        mock_page.get_by_text.return_value.first.wait_for = waiter

        result = await _run_step({"action": "wait_for", "text": "Saved", "timeout_seconds": 3})

        mock_page.get_by_text.assert_called_once_with("Saved")
        waiter.assert_awaited_once_with(timeout=3000)
        manager.log_action.assert_called_once_with("wait_for_text", text="Saved")
        assert result == "saw text 'Saved'"

    async def test_wait_for_selector_uses_default_timeout(
        self, manager: Any, mock_page: Any
    ) -> None:
        waiter = AsyncMock()
        mock_page.locator.return_value.first.wait_for = waiter

        result = await _run_step({"action": "wait_for", "selector": "#done"})

        mock_page.locator.assert_called_once_with("#done")
        waiter.assert_awaited_once_with(timeout=10_000)
        assert result == "saw selector '#done'"

    async def test_wait_for_needs_text_or_selector(self, manager: Any) -> None:
        with pytest.raises(ValueError, match="'wait_for' needs 'selector'"):
            await _run_step({"action": "wait_for"})

    async def test_wait_for_timeout_propagates(self, manager: Any, mock_page: Any) -> None:
        mock_page.get_by_text.return_value.first.wait_for = AsyncMock(
            side_effect=TimeoutError("Timeout 1000ms exceeded")
        )
        with pytest.raises(TimeoutError, match="Timeout 1000ms"):
            await _run_step({"action": "wait_for", "text": "Never", "timeout_seconds": 1})
        manager.log_action.assert_not_called()

    @pytest.mark.parametrize(
        ("step", "dx", "dy"),
        [
            ({"action": "scroll"}, 0, 400),
            ({"action": "scroll", "direction": "up", "amount": "small"}, 0, -100),
            ({"action": "scroll", "direction": "down", "amount": "large"}, 0, 800),
            ({"action": "scroll", "direction": "down", "amount": "page"}, 0, 720),
            ({"action": "scroll", "direction": "left", "amount": "medium"}, -400, 0),
            ({"action": "scroll", "direction": "right", "amount": "small"}, 100, 0),
            ({"action": "scroll", "direction": "down", "amount": 250}, 0, 250),
            ({"action": "scroll", "direction": "down", "amount": "500"}, 0, 500),
            ({"action": "scroll", "direction": "sideways", "amount": "small"}, 0, 0),
        ],
    )
    async def test_scroll(
        self, manager: Any, mock_page: Any, step: dict[str, Any], dx: int, dy: int
    ) -> None:
        result = await _run_step(step)

        mock_page.evaluate.assert_awaited_once_with("([x, y]) => window.scrollBy(x, y)", [dx, dy])
        manager.log_action.assert_called_once_with("scroll", dx=dx, dy=dy)
        assert result.startswith("scrolled ")

    def test_scroll_amounts_match_the_scroll_tool(self) -> None:
        assert SCROLL_AMOUNTS == {"small": 100, "medium": 400, "large": 800, "page": 720}

    async def test_scroll_rejects_a_non_numeric_amount(self, manager: Any) -> None:
        with pytest.raises(ValueError, match="invalid literal"):
            await _run_step({"action": "scroll", "amount": "huge"})


class TestElementSteps:
    """Steps that resolve an element ID and act through its locator."""

    @pytest.mark.parametrize(
        ("action", "button", "count", "text"),
        [
            ("click", "left", 1, "clicked [4]"),
            ("double_click", "left", 2, "double-clicked [4]"),
            ("right_click", "right", 1, "right-clicked [4]"),
        ],
    )
    async def test_click_variants(
        self,
        manager: Any,
        locator: AsyncMock,
        action: str,
        button: str,
        count: int,
        text: str,
    ) -> None:
        manager.codegen_target.return_value = {"css": "#go"}

        result = await _run_step({"action": action, "element_id": 4})

        manager.resolve_element.assert_awaited_once_with(4)
        locator.click.assert_awaited_once_with(
            button=button, click_count=count, timeout=ACTION_TIMEOUT_MS
        )
        manager.log_action.assert_called_once_with(
            "click", {"css": "#go"}, button=button, click_count=count
        )
        manager.settle.assert_awaited_once_with(1500)
        assert result == text

    async def test_element_id_is_coerced_to_int(self, manager: Any) -> None:
        await _run_step({"action": "hover", "element_id": "7"})
        manager.resolve_element.assert_awaited_once_with(7)

    @pytest.mark.parametrize("action", ["click", "double_click", "right_click"])
    async def test_clicking_a_disabled_element_fails_without_clicking(
        self, manager: Any, locator: AsyncMock, action: str
    ) -> None:
        locator.is_disabled.return_value = True

        with pytest.raises(ValueError, match="element 3 is disabled"):
            await _run_step({"action": action, "element_id": 3})

        locator.click.assert_not_awaited()
        manager.log_action.assert_not_called()

    async def test_hover(self, manager: Any, locator: AsyncMock) -> None:
        manager.codegen_target.return_value = {"css": "#menu"}

        result = await _run_step({"action": "hover", "element_id": 2})

        locator.hover.assert_awaited_once_with(timeout=ACTION_TIMEOUT_MS)
        manager.log_action.assert_called_once_with("hover", {"css": "#menu"})
        assert result == "hovered [2]"

    async def test_type(self, manager: Any, locator: AsyncMock) -> None:
        manager.codegen_target.return_value = {"css": "#q"}

        result = await _run_step({"action": "type", "element_id": 5, "text": "hello"})

        locator.fill.assert_awaited_once_with("hello", timeout=ACTION_TIMEOUT_MS)
        manager.log_action.assert_called_once_with("fill", {"css": "#q"}, text="hello")
        assert result == "typed 'hello' into [5]"

    async def test_type_coerces_non_string_text(self, manager: Any, locator: AsyncMock) -> None:
        await _run_step({"action": "type", "element_id": 5, "text": 42})
        locator.fill.assert_awaited_once_with("42", timeout=ACTION_TIMEOUT_MS)

    async def test_type_masks_password_text_in_the_result(
        self, manager: Any, locator: AsyncMock
    ) -> None:
        manager.codegen_target.return_value = {"css": "#pw", "password": True}

        result = await _run_step({"action": "type", "element_id": 5, "text": "hunter2"})

        assert "hunter2" not in result
        assert result == "typed ******* into [5]"
        locator.fill.assert_awaited_once_with("hunter2", timeout=ACTION_TIMEOUT_MS)

    async def test_type_into_a_non_text_element_fails(
        self, manager: Any, locator: AsyncMock
    ) -> None:
        locator.evaluate.return_value = "none"

        with pytest.raises(ValueError, match="element 5 is not a text field"):
            await _run_step({"action": "type", "element_id": 5, "text": "x"})

        locator.fill.assert_not_awaited()
        manager.log_action.assert_not_called()

    async def test_select(self, manager: Any, locator: AsyncMock) -> None:
        manager.codegen_target.return_value = {"css": "#country"}

        result = await _run_step({"action": "select", "element_id": 6, "option": "Canada"})

        locator.select_option.assert_awaited_once_with("Canada", timeout=ACTION_TIMEOUT_MS)
        manager.log_action.assert_called_once_with("select", {"css": "#country"}, option="Canada")
        assert result == "selected 'Canada' in [6]"

    @pytest.mark.parametrize(
        ("step_extra", "checked", "word"),
        [
            ({}, True, "checked"),
            ({"checked": True}, True, "checked"),
            ({"checked": False}, False, "unchecked"),
        ],
    )
    async def test_check(
        self,
        manager: Any,
        locator: AsyncMock,
        step_extra: dict[str, Any],
        checked: bool,
        word: str,
    ) -> None:
        result = await _run_step({"action": "check", "element_id": 8, **step_extra})

        locator.set_checked.assert_awaited_once_with(checked, timeout=ACTION_TIMEOUT_MS)
        manager.log_action.assert_called_once_with("check", None, checked=checked)
        assert result == f"{word} [8]"

    async def test_drag_resolves_both_elements(self, manager: Any, locator: AsyncMock) -> None:
        dest = AsyncMock()
        manager.resolve_element = AsyncMock(side_effect=[locator, dest])
        manager.codegen_target = AsyncMock(side_effect=[{"css": "#a"}, {"css": "#b"}])

        result = await _run_step({"action": "drag", "element_id": 1, "target_id": 2})

        assert [c.args for c in manager.resolve_element.await_args_list] == [(1,), (2,)]
        locator.drag_to.assert_awaited_once_with(dest, timeout=ACTION_TIMEOUT_MS)
        manager.log_action.assert_called_once_with("drag", {"css": "#a"}, dest={"css": "#b"})
        manager.settle.assert_awaited_once_with(1500)
        assert result == "dragged [1] onto [2]"

    @pytest.mark.parametrize(
        "error", [ElementNotFoundError(9, [1, 2]), StaleElementError(9, "gone")]
    )
    async def test_element_errors_propagate(self, manager: Any, error: Exception) -> None:
        manager.resolve_element = AsyncMock(side_effect=error)
        with pytest.raises(type(error), match="Element 9"):
            await _run_step({"action": "click", "element_id": 9})
        manager.log_action.assert_not_called()

    async def test_playwright_failure_propagates_without_logging(
        self, manager: Any, locator: AsyncMock
    ) -> None:
        locator.click.side_effect = TimeoutError("Timeout 5000ms exceeded")
        with pytest.raises(TimeoutError, match="Timeout 5000ms"):
            await _run_step({"action": "click", "element_id": 1})
        manager.log_action.assert_not_called()


class TestMissingArguments:
    """Each action names the argument it lacks, before touching the page."""

    @pytest.mark.parametrize(
        ("step", "missing"),
        [
            ({"action": "navigate"}, "url"),
            ({"action": "press"}, "key"),
            ({"action": "wait_for"}, "selector"),
            ({"action": "click"}, "element_id"),
            ({"action": "double_click"}, "element_id"),
            ({"action": "right_click"}, "element_id"),
            ({"action": "hover"}, "element_id"),
            ({"action": "type"}, "element_id"),
            ({"action": "select"}, "element_id"),
            ({"action": "check"}, "element_id"),
            ({"action": "drag"}, "element_id"),
            ({"action": "type", "element_id": 1}, "text"),
            ({"action": "select", "element_id": 1}, "option"),
            ({"action": "drag", "element_id": 1}, "target_id"),
        ],
    )
    async def test_missing_argument(
        self, manager: Any, mock_page: Any, step: dict[str, Any], missing: str
    ) -> None:
        with pytest.raises(ValueError, match=f"'{step['action']}' needs '{missing}'"):
            await _run_step(step)

        mock_page.goto.assert_not_awaited()
        mock_page.keyboard.press.assert_not_awaited()
        manager.log_action.assert_not_called()

    async def test_drag_without_target_does_not_resolve_a_destination(
        self, manager: Any, locator: AsyncMock
    ) -> None:
        with pytest.raises(ValueError, match="needs 'target_id'"):
            await _run_step({"action": "drag", "element_id": 1})
        locator.drag_to.assert_not_awaited()


class TestAct:
    """The ``act`` tool: validation, step limit, and failure reporting."""

    async def test_runs_all_steps_and_returns_one_screenshot(self, manager: Any) -> None:
        act = await _act()

        text, image = await act(
            steps=[
                {"action": "type", "element_id": 1, "text": "hi"},
                {"action": "press", "key": "Enter"},
            ]
        )

        assert "Ran 2 of 2 step(s), 0 failed:" in text
        assert "1. ok: typed 'hi' into [1]" in text
        assert "2. ok: pressed Enter" in text
        assert "Found 0 interactive elements:" in text
        manager.screenshot_with_som.assert_awaited_once()
        assert image.data == b"png"

    async def test_empty_steps_are_rejected(self, manager: Any) -> None:
        act = await _act()
        with pytest.raises(RuntimeError, match="act failed: steps is empty"):
            await act(steps=[])
        manager.screenshot_with_som.assert_not_awaited()

    async def test_max_steps_is_allowed(self, manager: Any, mock_page: Any) -> None:
        act = await _act()
        text, _ = await act(steps=[{"action": "press", "key": "a"}] * MAX_STEPS)

        assert f"Ran {MAX_STEPS} of {MAX_STEPS} step(s), 0 failed:" in text
        assert mock_page.keyboard.press.await_count == MAX_STEPS

    async def test_more_than_max_steps_is_rejected_before_running_any(
        self, manager: Any, mock_page: Any
    ) -> None:
        act = await _act()
        with pytest.raises(RuntimeError, match=f"at most {MAX_STEPS} steps per call"):
            await act(steps=[{"action": "press", "key": "a"}] * (MAX_STEPS + 1))

        mock_page.keyboard.press.assert_not_awaited()
        manager.screenshot_with_som.assert_not_awaited()

    def test_max_steps_matches_the_documented_limit(self) -> None:
        assert MAX_STEPS == 25

    async def test_failure_stops_the_run_and_reports_which_step(
        self, manager: Any, mock_page: Any, locator: AsyncMock
    ) -> None:
        locator.is_disabled.return_value = True
        act = await _act()

        text, _ = await act(
            steps=[
                {"action": "press", "key": "a"},
                {"action": "click", "element_id": 3},
                {"action": "press", "key": "b"},
                {"action": "press", "key": "c"},
            ]
        )

        assert "Ran 2 of 4 step(s), 1 failed:" in text
        assert "1. ok: pressed a" in text
        assert "2. FAILED (click): element 3 is disabled" in text
        assert "2 remaining step(s) skipped" in text
        assert [c.args for c in mock_page.keyboard.press.await_args_list] == [("a",)]

    async def test_failure_on_the_last_step_reports_no_skipped_steps(self, manager: Any) -> None:
        act = await _act()
        text, _ = await act(
            steps=[{"action": "press", "key": "a"}, {"action": "nope", "element_id": 1}]
        )

        assert "Ran 2 of 2 step(s), 1 failed:" in text
        assert "2. FAILED (nope): unknown action 'nope'" in text
        assert "skipped" not in text

    async def test_stale_element_failure_is_reported_in_the_step_line(self, manager: Any) -> None:
        manager.resolve_element = AsyncMock(side_effect=StaleElementError(4, "page changed"))
        act = await _act()

        text, _ = await act(steps=[{"action": "click", "element_id": 4}])

        assert "1. FAILED (click): Element 4 is stale (page changed)" in text

    async def test_stop_on_error_false_keeps_going_and_counts_failures(
        self, manager: Any, mock_page: Any
    ) -> None:
        act = await _act()

        text, _ = await act(
            steps=[
                {"action": "nope"},
                {"action": "press"},
                {"action": "press", "key": "Enter"},
            ],
            stop_on_error=False,
        )

        assert "Ran 3 of 3 step(s), 2 failed:" in text
        assert "1. FAILED (nope)" in text
        assert "2. FAILED (press): 'press' needs 'key'" in text
        assert "3. ok: pressed Enter" in text
        assert "skipped" not in text
        mock_page.keyboard.press.assert_awaited_once_with("Enter")

    async def test_a_step_without_an_action_is_reported_not_raised(self, manager: Any) -> None:
        act = await _act()
        text, _ = await act(steps=[{"element_id": 1}])
        assert "1. FAILED (None): unknown action None" in text

    async def test_screenshot_is_still_taken_after_a_failure(self, manager: Any) -> None:
        act = await _act()
        await act(steps=[{"action": "nope"}])
        manager.screenshot_with_som.assert_awaited_once()

    async def test_browser_start_failure_is_wrapped(self, manager: Any) -> None:
        manager.ensure_started = AsyncMock(side_effect=RuntimeError("no chromium"))
        act = await _act()
        with pytest.raises(RuntimeError, match="act failed: no chromium"):
            await act(steps=[{"action": "press", "key": "a"}])

    async def test_screenshot_failure_is_wrapped(self, manager: Any) -> None:
        manager.screenshot_with_som = AsyncMock(side_effect=RuntimeError("page crashed"))
        act = await _act()
        with pytest.raises(RuntimeError, match="act failed: page crashed"):
            await act(steps=[{"action": "press", "key": "a"}])

    async def test_notices_lead_the_summary(self, manager: Any) -> None:
        manager.drain_notices = MagicMock(return_value=["Downloaded a.txt to /d/a.txt"])
        act = await _act()
        text, _ = await act(steps=[{"action": "press", "key": "a"}])
        assert "Notice: Downloaded a.txt to /d/a.txt" in text

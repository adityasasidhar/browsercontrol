"""Unit tests for Set of Marks element collection and resolution (mocked Playwright).

tests/test_som_real_browser.py covers the same behaviour against a real Chromium.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from playwright.async_api import Error as PlaywrightError

from browsercontrol.elements import (
    ATTR,
    MOVE_TOLERANCE_PX,
    ElementNotFoundError,
    StaleElementError,
    collect_elements,
    locate,
)


def _raw(ref: str, x: float = 10, y: float = 20, w: float = 30, h: float = 40) -> dict:
    return {"ref": ref, "x": x, "y": y, "width": w, "height": h, "tag": "button", "text": "ok"}


def _frame(*, parent=None, result=None, error=None, owner_box=None, inset=(0, 0)):
    frame = MagicMock()
    frame.url = "https://example.com/frame"
    frame.parent_frame = parent
    frame.evaluate = AsyncMock(side_effect=error, return_value=result)
    owner = AsyncMock()
    owner.bounding_box = AsyncMock(return_value=owner_box)
    owner.evaluate = AsyncMock(return_value=list(inset))
    frame.frame_element = AsyncMock(return_value=owner)
    return frame


def _page(*frames):
    page = MagicMock()
    page.frames = list(frames)
    return page


class TestCollectElements:
    @pytest.mark.asyncio
    async def test_main_frame_elements_keep_their_coordinates(self):
        main = _frame(result={"vw": 800, "vh": 600, "elements": [_raw("g1f0-1")]})
        [elem] = await collect_elements(_page(main), 1)

        main.evaluate.assert_awaited_once()
        assert main.evaluate.await_args.args[1] == "g1f0"
        assert (elem["x"], elem["y"], elem["centerX"], elem["centerY"]) == (10, 20, 25, 40)
        assert elem["_ref"] == "g1f0-1"
        assert elem["_frame"] is main
        assert elem["_local"] == (10, 20, 30, 40)
        assert "ref" not in elem

    @pytest.mark.asyncio
    async def test_child_frame_elements_are_offset_by_frame_content_box(self):
        main = _frame(result={"vw": 800, "vh": 600, "elements": []})
        child = _frame(
            parent=main,
            result={"vw": 300, "vh": 100, "elements": [_raw("g1f1-1")]},
            owner_box={"x": 100, "y": 200, "width": 300, "height": 100},
            inset=(5, 7),
        )
        [elem] = await collect_elements(_page(main, child), 1)

        assert (elem["x"], elem["y"]) == (115, 227)
        assert elem["_local"] == (10, 20, 30, 40), "frame-local box is kept for staleness"
        assert elem["_frame"] is child

    @pytest.mark.asyncio
    async def test_child_frame_elements_outside_main_viewport_are_dropped(self):
        main = _frame(result={"vw": 800, "vh": 600, "elements": []})
        child = _frame(
            parent=main,
            result={"vw": 300, "vh": 300, "elements": [_raw("a", y=0), _raw("b", y=250)]},
            owner_box={"x": 0, "y": 400, "width": 300, "height": 300},
        )
        elems = await collect_elements(_page(main, child), 1)
        assert [e["_ref"] for e in elems] == ["a"]

    @pytest.mark.asyncio
    async def test_hidden_and_broken_frames_are_skipped(self):
        main = _frame(result={"vw": 800, "vh": 600, "elements": [_raw("m")]})
        hidden = _frame(parent=main, owner_box=None)
        broken = _frame(
            parent=main,
            error=PlaywrightError("Frame was detached"),
            owner_box={"x": 0, "y": 0, "width": 10, "height": 10},
        )
        elems = await collect_elements(_page(main, hidden, broken), 1)

        assert [e["_ref"] for e in elems] == ["m"]
        hidden.evaluate.assert_not_awaited()


def _locator(count=1, rect=(10, 20, 30, 40), error=None):
    locator = MagicMock()
    locator.first = locator
    locator.count = AsyncMock(return_value=count)
    locator.evaluate = AsyncMock(side_effect=error, return_value=list(rect))
    return locator


def _entry(locator, detached=False):
    frame = MagicMock()
    frame.is_detached = MagicMock(return_value=detached)
    frame.locator = MagicMock(return_value=locator)
    return {"_ref": "g3f0-7", "_frame": frame, "_local": (10, 20, 30, 40)}


class TestLocate:
    @pytest.mark.asyncio
    async def test_returns_frame_scoped_locator_by_tag(self):
        locator = _locator()
        entry = _entry(locator)
        assert await locate(5, {5: entry}) is locator
        entry["_frame"].locator.assert_called_once_with(f'[{ATTR}="g3f0-7"]')

    @pytest.mark.asyncio
    async def test_unknown_id_lists_valid_ids(self):
        with pytest.raises(ElementNotFoundError, match=r"Element 9 not found. Valid IDs: \[1, 2\]"):
            await locate(9, {1: {}, 2: {}})

    @pytest.mark.asyncio
    async def test_detached_frame_is_stale(self):
        with pytest.raises(StaleElementError, match="frame was removed"):
            await locate(1, {1: _entry(_locator(), detached=True)})

    @pytest.mark.asyncio
    async def test_removed_element_is_stale(self):
        with pytest.raises(StaleElementError, match="no longer on the page"):
            await locate(1, {1: _entry(_locator(count=0))})

    @pytest.mark.asyncio
    async def test_zero_size_element_is_stale(self):
        with pytest.raises(StaleElementError, match="no longer visible"):
            await locate(1, {1: _entry(_locator(rect=(10, 20, 0, 0)))})

    @pytest.mark.asyncio
    async def test_moved_element_is_stale(self):
        moved = (10, 20 + MOVE_TOLERANCE_PX + 1, 30, 40)
        with pytest.raises(StaleElementError, match="it moved"):
            await locate(1, {1: _entry(_locator(rect=moved))})

    @pytest.mark.asyncio
    async def test_small_jitter_is_tolerated(self):
        jitter = (10.5, 20 + MOVE_TOLERANCE_PX - 0.5, 30, 40)
        locator = _locator(rect=jitter)
        assert await locate(1, {1: _entry(locator)}) is locator

    @pytest.mark.asyncio
    async def test_playwright_error_is_reported_as_stale(self):
        with pytest.raises(StaleElementError, match="could not be located"):
            await locate(1, {1: _entry(_locator(error=PlaywrightError("context destroyed")))})

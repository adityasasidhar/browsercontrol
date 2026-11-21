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
    strip_marks,
)


def _raw(ref: str, x: float = 10, y: float = 20, w: float = 30, h: float = 40) -> dict:
    return {
        "ref": ref,
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "tag": "button",
        "text": "ok",
        "fp": "BUTTON|ok",
    }


def _owner_hits(offset=(0, 0), visible=True):
    """Fake FRAME_HIT_JS: shift each box by offset; visible is a bool or a per-box list."""

    async def evaluate(_js, boxes):
        flags = visible if isinstance(visible, list) else [visible] * len(boxes)
        return [
            {"box": [x + offset[0], y + offset[1], w, h], "visible": v}
            for (x, y, w, h), v in zip(boxes, flags, strict=True)
        ]

    return evaluate


def _frame(*, parent=None, result=None, error=None, owner_eval=None, owner_error=None):
    frame = MagicMock()
    frame.url = "https://example.com/frame"
    frame.parent_frame = parent
    frame.evaluate = AsyncMock(side_effect=error, return_value=result)
    owner = AsyncMock()
    owner.evaluate = AsyncMock(side_effect=owner_error or owner_eval or _owner_hits())
    frame.frame_element = AsyncMock(return_value=owner)
    frame.owner = owner
    return frame


def _page(*frames):
    page = MagicMock()
    page.frames = list(frames)
    return page


def _res(*elements, vw=800, vh=600):
    return {"vw": vw, "vh": vh, "elements": list(elements)}


class TestCollectElements:
    @pytest.mark.asyncio
    async def test_main_frame_elements_keep_their_coordinates(self):
        main = _frame(result=_res(_raw("g1f0-1")))
        [elem] = await collect_elements(_page(main), 1)

        main.evaluate.assert_awaited_once()
        assert main.evaluate.await_args.args[1] == "g1f0"
        assert (elem["x"], elem["y"], elem["centerX"], elem["centerY"]) == (10, 20, 25, 40)
        assert elem["_ref"] == "g1f0-1"
        assert elem["_fp"] == "BUTTON|ok"
        assert elem["_frame"] is main
        assert elem["_local"] == (10, 20, 30, 40)
        assert "ref" not in elem and "fp" not in elem
        main.frame_element.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_child_frame_elements_are_mapped_through_the_owner_iframe(self):
        main = _frame(result=_res())
        child = _frame(
            parent=main, result=_res(_raw("g1f1-1"), vw=300), owner_eval=_owner_hits((105, 207))
        )
        [elem] = await collect_elements(_page(main, child), 1)

        assert (elem["x"], elem["y"]) == (115, 227)
        assert elem["_local"] == (10, 20, 30, 40), "frame-local box is kept for staleness"
        assert elem["_frame"] is child
        child.owner.evaluate.assert_awaited_once()
        assert child.owner.evaluate.await_args.args[1] == [[10, 20, 30, 40]]

    @pytest.mark.asyncio
    async def test_nested_frames_chain_offsets_through_every_ancestor(self):
        main = _frame(result=_res())
        middle = _frame(parent=main, result=_res(), owner_eval=_owner_hits((100, 0)))
        inner = _frame(parent=middle, result=_res(_raw("x")), owner_eval=_owner_hits((5, 50)))
        [elem] = await collect_elements(_page(main, middle, inner), 1)

        assert (elem["x"], elem["y"]) == (115, 70)
        assert middle.owner.evaluate.await_args.args[1] == [[15, 70, 30, 40]]

    @pytest.mark.asyncio
    async def test_elements_hidden_by_an_ancestor_overlay_are_dropped(self):
        """A parent-page modal over the iframe (or a box off-screen) hides frame elements."""
        main = _frame(result=_res())
        child = _frame(
            parent=main,
            result=_res(_raw("shown"), _raw("covered")),
            owner_eval=_owner_hits(visible=[True, False]),
        )
        elems = await collect_elements(_page(main, child), 1)
        assert [e["_ref"] for e in elems] == ["shown"]

    @pytest.mark.asyncio
    async def test_child_frames_do_not_depend_on_main_frame_collection(self):
        """A failed main-frame evaluate must not disable visibility filtering for iframes."""
        main = _frame(error=PlaywrightError("Execution context was destroyed"))
        child = _frame(
            parent=main,
            result=_res(_raw("in"), _raw("below-fold")),
            owner_eval=_owner_hits(visible=[True, False]),
        )
        elems = await collect_elements(_page(main, child), 1)
        assert [e["_ref"] for e in elems] == ["in"]

    @pytest.mark.asyncio
    async def test_broken_frames_are_skipped(self):
        main = _frame(result=_res(_raw("m")))
        detached = _frame(
            parent=main, result=_res(_raw("d")), owner_error=PlaywrightError("Frame was detached")
        )
        broken = _frame(parent=main, error=PlaywrightError("Frame was detached"))
        elems = await collect_elements(_page(main, detached, broken), 1)

        assert [e["_ref"] for e in elems] == ["m"]
        broken.owner.evaluate.assert_not_awaited()


class TestStripMarks:
    def test_removes_tags_from_serialized_html(self):
        html = f'<a href="/x" {ATTR}="g3f0-1">x</a><button class="b" {ATTR}="g3f1-12">ok</button>'
        assert strip_marks(html) == '<a href="/x">x</a><button class="b">ok</button>'


def _locator(count=1, rect=(10, 20, 30, 40), fp="BUTTON|ok", error=None, rects=None):
    """Fake locator; rects, if given, are returned by successive measurements."""
    locator = MagicMock()
    locator.first = locator
    locator.count = AsyncMock(return_value=count)
    if rects is not None:
        locator.evaluate = AsyncMock(side_effect=[{"rect": list(r), "fp": fp} for r in rects])
    else:
        locator.evaluate = AsyncMock(side_effect=error, return_value={"rect": list(rect), "fp": fp})
    return locator


def _entry(locator, detached=False):
    frame = MagicMock()
    frame.is_detached = MagicMock(return_value=detached)
    frame.locator = MagicMock(return_value=locator)
    return {"_ref": "g3f0-7", "_frame": frame, "_local": (10, 20, 30, 40), "_fp": "BUTTON|ok"}


@pytest.fixture(autouse=True)
def _no_settle_delay(monkeypatch):
    monkeypatch.setattr("browsercontrol.elements.SETTLE_DELAY_S", 0)
    monkeypatch.setattr("browsercontrol.elements.CONFIRM_DELAY_S", 0)


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
    async def test_cloned_tag_is_ambiguous(self):
        with pytest.raises(StaleElementError, match="ambiguous"):
            await locate(1, {1: _entry(_locator(count=2))})

    @pytest.mark.asyncio
    async def test_zero_size_element_is_stale(self):
        with pytest.raises(StaleElementError, match="no longer visible"):
            await locate(1, {1: _entry(_locator(rect=(10, 20, 0, 0)))})

    @pytest.mark.asyncio
    async def test_recycled_node_with_new_content_is_stale(self):
        with pytest.raises(StaleElementError, match="content changed"):
            await locate(1, {1: _entry(_locator(fp="BUTTON|Delete account"))})

    @pytest.mark.asyncio
    async def test_moved_and_settled_element_is_stale(self):
        moved = (10, 20 + MOVE_TOLERANCE_PX + 1, 30, 40)
        with pytest.raises(StaleElementError, match="it moved"):
            await locate(1, {1: _entry(_locator(rects=[moved, moved, moved]))})

    @pytest.mark.asyncio
    async def test_element_reversing_direction_is_accepted(self):
        """A back-and-forth animation can be at the same spot either side of its turnaround.

        Two samples that happen to match must not pass for a settled element.
        """
        locator = _locator(rects=[(60, 20, 30, 40), (60, 20, 30, 40), (45, 20, 30, 40)])
        assert await locate(1, {1: _entry(locator)}) is locator

    @pytest.mark.asyncio
    async def test_element_still_animating_is_accepted(self):
        """A carousel or transition keeps moving; refusing it would loop the agent forever."""
        locator = _locator(rects=[(60, 20, 30, 40), (90, 20, 30, 40)])
        assert await locate(1, {1: _entry(locator)}) is locator

    @pytest.mark.asyncio
    async def test_element_that_moved_back_is_accepted(self):
        locator = _locator(rects=[(60, 20, 30, 40), (10, 20, 30, 40)])
        assert await locate(1, {1: _entry(locator)}) is locator

    @pytest.mark.asyncio
    async def test_small_jitter_is_tolerated(self):
        jitter = (10.5, 20 + MOVE_TOLERANCE_PX - 0.5, 30, 40)
        locator = _locator(rect=jitter)
        assert await locate(1, {1: _entry(locator)}) is locator
        assert locator.evaluate.await_count == 1, "no settle re-measure without a move"

    @pytest.mark.asyncio
    async def test_playwright_error_is_reported_as_stale(self):
        with pytest.raises(StaleElementError, match="could not be located"):
            await locate(1, {1: _entry(_locator(error=PlaywrightError("context destroyed")))})

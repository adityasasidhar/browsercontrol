"""Set of Marks against a real headless Chromium.

The unit tests mock Playwright, so they cannot tell whether an ID really reaches
the element it was drawn on. These tests serve fixture pages from a local server
(``127.0.0.1`` and ``localhost`` are different sites, so the iframe is truly
cross-origin) and drive the real tools. They use whichever browser the server
would (``BROWSER_EXECUTABLE_PATH``, Playwright's Chromium, or an installed Google
Chrome) and skip when none is available. They never download a browser.
"""

import threading
from collections.abc import AsyncIterator, Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from fastmcp import FastMCP
from playwright.sync_api import sync_playwright

from browsercontrol.browser import BrowserManager
from browsercontrol.config import config
from browsercontrol.elements import ElementNotFoundError, StaleElementError
from browsercontrol.tools import (
    register_content_tools,
    register_devtools,
    register_form_tools,
    register_interaction_tools,
)


def _browser_available() -> bool:
    """Mirror BrowserManager's launch order without ever downloading Chromium.

    Configured executable, then Playwright's bundled Chromium, then installed Chrome.
    """
    if config.executable_path is not None:
        return config.executable_path.exists()
    try:
        with sync_playwright() as pw:
            if Path(pw.chromium.executable_path).exists():
                return True
            pw.chromium.launch(channel="chrome").close()
            return True
    except Exception:
        return False


pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(not _browser_available(), reason="no Chromium or Chrome to drive"),
]

FRAME_PAGE = """<!doctype html><body style="margin:0">
<input id="framed" placeholder="framed input">
<button id="xbtn" onclick="this.textContent='x-clicked'">cross button</button>
</body>"""

MAIN_PAGE = """<!doctype html><html><body style="margin:0;font:16px sans-serif">
<div id="log"></div>
<div id="host"></div>
<script>
  const root = document.getElementById('host').attachShadow({mode: 'open'});
  root.innerHTML = '<button id="shadow-btn">shadow button</button>';
  root.getElementById('shadow-btn').addEventListener('click',
      () => document.getElementById('log').textContent = 'shadow-clicked');
</script>

<div id="card" style="cursor:pointer;width:200px;padding:4px">
  <span>card title</span><span>card body</span>
</div>
<script>
  document.getElementById('card').addEventListener('click',
      () => document.getElementById('log').textContent = 'card-clicked');
</script>

<button id="invisible" style="visibility:hidden">invisible</button>
<button id="transparent" style="opacity:0">transparent</button>
<input id="file" type="file" style="opacity:0">
<button id="disabled" disabled>disabled button</button>

<div style="position:relative;width:300px;height:40px">
  <button id="covered" style="position:absolute;top:0;left:0">covered button</button>
  <div style="position:absolute;top:0;left:0;width:300px;height:40px;background:#eee;
              z-index:5">cover</div>
</div>

<input id="filled" value="prefilled value">

<iframe id="same" style="border:5px solid #000;width:320px;height:60px"
        srcdoc='<input id="inner" placeholder="same-origin input">'></iframe>
<iframe id="cross" style="border:6px solid #000;width:320px;height:60px" src="__CROSS__/frame"></iframe>
</body></html>"""


@pytest.fixture(scope="module")
def server() -> Iterator[int]:
    pages: dict[str, str] = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            body = pages.get(self.path, "").encode()
            self.send_response(200 if body else 404)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            pass

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = httpd.server_address[1]
    pages["/frame"] = FRAME_PAGE
    pages["/"] = MAIN_PAGE.replace("__CROSS__", f"http://localhost:{port}")
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield port
    httpd.shutdown()


@pytest.fixture
async def manager(tmp_path: Path) -> AsyncIterator[BrowserManager]:
    mgr = BrowserManager()
    with patch("browsercontrol.browser.config.user_data_dir", tmp_path / "profile"):
        await mgr.start()
    try:
        yield mgr
    finally:
        await mgr.stop()


@pytest.fixture
async def tools(manager: BrowserManager) -> AsyncIterator[FastMCP]:
    mcp = FastMCP("test")
    register_interaction_tools(mcp)
    register_form_tools(mcp)
    register_content_tools(mcp)
    register_devtools(mcp)
    modules = ("interaction", "forms", "content", "devtools")
    patches = [patch(f"browsercontrol.tools.{m}.browser", manager) for m in modules]
    for p in patches:
        p.start()
    yield mcp
    for p in patches:
        p.stop()


async def _load(manager: BrowserManager, port: int) -> dict[int, dict[str, Any]]:
    await manager.page.goto(f"http://127.0.0.1:{port}/")
    await manager.page.wait_for_load_state("load")
    _, elem_map = await manager.screenshot_with_som()
    return elem_map


def _find(elem_map: dict[int, dict[str, Any]], text: str) -> int:
    for eid, elem in elem_map.items():
        if text in (elem.get("text") or ""):
            return eid
    raise AssertionError(f"no element with text {text!r} in {elem_map}")


def _texts(elem_map: dict[int, dict[str, Any]]) -> list[str]:
    return [e.get("text") or "" for e in elem_map.values()]


async def _call(mcp: FastMCP, name: str, **kwargs: Any) -> Any:
    tool = await mcp.get_tool(name)
    return await tool.fn(**kwargs)


async def test_click_reaches_button_inside_shadow_dom(manager, tools, server):
    elem_map = await _load(manager, server)
    result = await _call(tools, "click", element_id=_find(elem_map, "shadow button"))
    assert "Clicked" in result[0]
    assert await manager.page.text_content("#log") == "shadow-clicked"


async def test_type_reaches_input_inside_same_origin_iframe(manager, tools, server):
    elem_map = await _load(manager, server)
    eid = _find(elem_map, "same-origin input")
    await _call(tools, "type_text", element_id=eid, text="hello")
    frame = manager.page.frame_locator("#same")
    assert await frame.locator("#inner").input_value() == "hello"


async def test_cross_origin_iframe_elements_are_listed_and_clickable(manager, tools, server):
    elem_map = await _load(manager, server)
    eid = _find(elem_map, "cross button")
    # The 6px border exceeds the moved-tolerance, so this also guards against
    # resolving through bounding_box(), which ignores borders on cross-origin frames.
    # Box is in main-viewport coordinates: inside the cross-origin iframe's box.
    frame_box = await manager.page.locator("#cross").bounding_box()
    assert frame_box is not None
    assert elem_map[eid]["y"] >= frame_box["y"]
    await _call(tools, "click", element_id=eid)
    frame = manager.page.frame_locator("#cross")
    assert await frame.locator("#xbtn").text_content() == "x-clicked"


async def test_iframe_element_boxes_land_on_the_real_element(manager, server):
    """Hovering just inside both corners of a recorded box must hover that element.

    Uses real mouse events rather than Playwright's bounding_box(), which is itself
    off by the border width for elements inside cross-origin iframes.
    """
    elem_map = await _load(manager, server)
    for frame_id, inner_id, text in (
        ("#same", "#inner", "same-origin input"),
        ("#cross", "#xbtn", "cross button"),
    ):
        elem = elem_map[_find(elem_map, text)]
        frame = await (await manager.page.query_selector(frame_id)).content_frame()
        corners = (
            (elem["x"] + 2, elem["y"] + 2),
            (elem["x"] + elem["width"] - 2, elem["y"] + elem["height"] - 2),
        )
        for x, y in corners:
            await manager.page.mouse.move(x, y)
            hovered = await frame.evaluate(
                f"document.querySelector('{inner_id}').matches(':hover')"
            )
            assert hovered, f"{text}: ({x}, {y}) missed the element"


async def test_cursor_pointer_div_is_collected_once(manager, tools, server):
    elem_map = await _load(manager, server)
    texts = _texts(elem_map)
    card = [t for t in texts if "card title" in t]
    assert len(card) == 1, "card should be listed once, not once per child span"
    assert "card body" not in texts
    await _call(tools, "click", element_id=_find(elem_map, "card title"))
    assert await manager.page.text_content("#log") == "card-clicked"


async def test_hidden_and_covered_elements_are_excluded(manager, server):
    texts = _texts(await _load(manager, server))
    assert "invisible" not in texts
    assert "transparent" not in texts
    assert "covered button" not in texts


async def test_transparent_file_input_is_kept_for_uploads(manager, server):
    elem_map = await _load(manager, server)
    assert any(e["tag"] == "input" and e["type"] == "file" for e in elem_map.values())


async def test_disabled_element_is_flagged(manager, server):
    elem_map = await _load(manager, server)
    assert elem_map[_find(elem_map, "disabled button")]["disabled"] is True
    assert elem_map[_find(elem_map, "shadow button")]["disabled"] is False


async def test_removed_element_is_reported_stale(manager, tools, server):
    elem_map = await _load(manager, server)
    eid = _find(elem_map, "disabled button")
    await manager.page.evaluate("document.getElementById('disabled').remove()")
    with pytest.raises(StaleElementError, match="no longer on the page"):
        await manager.resolve_element(eid)
    result = await _call(tools, "click", element_id=eid)
    assert "stale" in result[0]
    assert "Found" in result[0], "a fresh element summary should accompany the error"


async def test_moved_element_is_reported_stale(manager, server):
    elem_map = await _load(manager, server)
    eid = _find(elem_map, "disabled button")
    await manager.page.evaluate("document.getElementById('disabled').style.marginLeft = '200px'")
    with pytest.raises(StaleElementError, match="moved"):
        await manager.resolve_element(eid)


async def test_element_maps_are_per_tab(manager, server):
    elem_map = await _load(manager, server)
    assert elem_map
    await manager.create_tab()
    assert manager.get_element_map() == {}
    with pytest.raises(ElementNotFoundError):
        await manager.resolve_element(1)
    await manager.switch_to_tab(0)
    assert manager.get_element_map() == elem_map


async def test_get_text_reads_live_page(manager, tools, server):
    elem_map = await _load(manager, server)
    filled = next(k for k, e in elem_map.items() if e.get("id") == "filled")
    await manager.page.fill("#filled", "edited value")
    assert await _call(tools, "get_text", element_id=filled) == (
        f"Element {filled} text: edited value"
    )

    long_text = await _call(tools, "get_text", element_id=_find(elem_map, "card title"))
    assert "card body" in long_text, "full text, not the truncated summary label"


async def test_inspect_element_inside_shadow_dom(manager, tools, server):
    elem_map = await _load(manager, server)
    result = await _call(tools, "inspect_element", element_id=_find(elem_map, "shadow button"))
    assert "Tag: <button>" in result
    assert "ID: #shadow-btn" in result

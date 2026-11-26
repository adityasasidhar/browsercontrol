"""The agent-capability tools against a real headless Chromium.

Covers find, act, the new actions, dialogs, downloads, waits and settling,
network control, extraction, emulation, isolated sessions, attaching over CDP,
and generated tests (which are replayed in a separate Playwright process).
Skips when no browser is available, like test_som_real_browser.py.
"""

import asyncio
import json
import socket
import subprocess
import sys
import threading
import time
from collections.abc import AsyncIterator, Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import FastMCP
from fastmcp.utilities.types import Image
from PIL import Image as PILImage
from PIL import ImageChops

from browsercontrol.browser import BrowserManager
from browsercontrol.tools import (
    register_batch_tools,
    register_emulation_tools,
    register_extract_tools,
    register_form_tools,
    register_interaction_tools,
    register_navigation_tools,
    register_network_tools,
    register_recording_tools,
    register_search_tools,
    register_session_tools,
    register_waiting_tools,
)
from tests.test_som_real_browser import _browser_available

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(not _browser_available(), reason="no Chromium or Chrome to drive"),
]

TOOL_MODULES = (
    "assertions",
    "batch",
    "emulate",
    "extract",
    "forms",
    "interaction",
    "navigation",
    "network",
    "recording",
    "search",
    "sessions",
    "waiting",
)

APP_PAGE = """<!doctype html><html><body style="margin:0;font:16px sans-serif">
<div id="log">ready</div>
<label for="name">Name</label><input id="name">
<label for="pw">Password</label><input id="pw" type="password">
<button id="go" onclick="document.getElementById('log').textContent =
  'hello ' + document.getElementById('name').value">Greet</button>
<button id="ask" onclick="document.getElementById('log').textContent =
  confirm('Really?') ? 'confirmed' : 'cancelled'">Ask</button>
<button id="dbl" ondblclick="document.getElementById('log').textContent='double'">Dbl</button>
<button id="ctx" oncontextmenu="event.preventDefault();
  document.getElementById('log').textContent='context'">Ctx</button>
<button id="load" onclick="fetch('/api/data').then(r => r.json()).then(d => {
  setTimeout(() => { const b = document.createElement('button');
    b.textContent = 'Loaded ' + d.value; document.getElementById('log').after(b); }, 150);
}).catch(() => { document.getElementById('log').textContent = 'load failed'; })">Load</button>
<a id="dl" href="/file.txt">Get file</a>
<div id="src" tabindex="0" draggable="true" style="width:80px;height:30px;background:#9cf">drag me</div>
<div id="dst" tabindex="0" style="width:120px;height:40px;background:#fc9">drop here</div>
<script>
  const src = document.getElementById('src'), dst = document.getElementById('dst');
  src.addEventListener('dragstart', e => e.dataTransfer.setData('text', 'x'));
  dst.addEventListener('dragover', e => e.preventDefault());
  dst.addEventListener('drop', e => { e.preventDefault();
    document.getElementById('log').textContent = 'dropped'; });
</script>
<table id="t"><thead><tr><th>Name</th><th>Price</th></tr></thead>
<tbody><tr><td>Apple</td><td>1</td></tr><tr><td>Pear</td><td>2</td></tr></tbody></table>
<div class="product"><h3>Widget</h3><span class="price">$5</span><a href="/w">more</a></div>
<div class="product"><h3>Gadget</h3><span class="price">$7</span><a href="/g">more</a></div>
<div style="height:3000px"></div>
<button id="deep" onclick="document.getElementById('log').textContent='deep'">Deep target</button>
</body></html>"""


@pytest.fixture(scope="module")
def server() -> Iterator[int]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path == "/api/data":
                body, ctype, extra = b'{"value": 42}', "application/json", {}
            elif self.path == "/file.txt":
                body, ctype = b"file contents", "text/plain"
                extra = {"Content-Disposition": 'attachment; filename="report.txt"'}
            elif self.path == "/":
                body, ctype, extra = APP_PAGE.encode(), "text/html", {}
            else:
                body, ctype, extra = b"<p>other</p>", "text/html", {}
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            for key, value in extra.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            pass

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield httpd.server_address[1]
    httpd.shutdown()


@pytest.fixture
async def manager(tmp_path: Path) -> AsyncIterator[BrowserManager]:
    mgr = BrowserManager()
    with (
        patch("browsercontrol.browser.config.user_data_dir", tmp_path / "profile"),
        patch("browsercontrol.browser.config.downloads_dir", tmp_path / "downloads"),
    ):
        await mgr.start()
        try:
            yield mgr
        finally:
            await mgr.stop()


@pytest.fixture
async def tools(manager: BrowserManager, tmp_path: Path) -> AsyncIterator[FastMCP]:
    mcp = FastMCP("test")
    for register in (
        register_batch_tools,
        register_emulation_tools,
        register_extract_tools,
        register_form_tools,
        register_interaction_tools,
        register_navigation_tools,
        register_network_tools,
        register_recording_tools,
        register_search_tools,
        register_session_tools,
        register_waiting_tools,
    ):
        register(mcp)
    patches = [patch(f"browsercontrol.tools.{m}.browser", manager) for m in TOOL_MODULES]
    patches += [
        patch("browsercontrol.config.config.recordings_dir", tmp_path / "rec"),
        patch("browsercontrol.config.config.generated_tests_dir", tmp_path / "gen"),
    ]
    for p in patches:
        p.start()
    yield mcp
    for p in patches:
        p.stop()


async def call(mcp: FastMCP, tool_name: str, /, **kwargs: Any) -> Any:
    tool = await mcp.get_tool(tool_name)
    assert tool is not None, tool_name
    return await tool.fn(**kwargs)


def element_id(summary: str, text: str) -> int:
    """The ID the summary gives the element whose label contains ``text``."""
    for line in summary.splitlines():
        if line.strip().startswith("[") and text in line:
            return int(line.strip()[1 : line.strip().index("]")])
    raise AssertionError(f"{text!r} not in summary:\n{summary}")


async def log_text(manager: BrowserManager) -> str:
    return str(await manager.page.locator("#log").inner_text())


async def open_app(mcp: FastMCP, port: int) -> str:
    text, image = await call(mcp, "navigate_to", url=f"http://127.0.0.1:{port}/")
    assert isinstance(image, Image)
    return str(text)


async def test_agent_pointer_tracks_clicks_without_intercepting_them(
    tools: FastMCP, manager: BrowserManager, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Chromium is already running headless. Exercise the visible-window behavior
    # against the same browser so this test also works on CI without a display.
    monkeypatch.setattr("browsercontrol.config.config.headless", False)
    page = manager.page
    await page.clock.install(time="2026-01-01T00:00:00Z")
    await page.emulate_media(reduced_motion="reduce")
    await page.set_content(
        '<button style="position:absolute;left:90px;top:90px" '
        "onclick=\"this.textContent = 'clicked'\">Click me</button>"
    )
    # Pause the idle timer while we inspect the live browser and the tool image.
    # The generic DOM settle also uses page timers, so bypass it in this test.
    await page.clock.pause_at("2026-01-01T01:00:00Z")
    monkeypatch.setattr(manager, "settle", AsyncMock())
    await call(tools, "click_at", x=100, y=100)
    assert await page.get_by_role("button").inner_text() == "clicked"

    pointer = page.locator("[data-bc-agent-pointer]")
    assert await pointer.count() == 1
    assert await page.evaluate("document.elementFromPoint(100, 100).tagName") == "BUTTON"

    # Compare a patch away from the button and its mark. The live browser has
    # the arrow at its new location, while the tool's screenshot is clean.
    _, image = await call(tools, "click_at", x=200, y=130)
    live = PILImage.open(BytesIO(await page.screenshot())).convert("RGB")
    captured = PILImage.open(BytesIO(image.data)).convert("RGB")
    patch_box = (198, 128, 225, 157)
    assert ImageChops.difference(live.crop(patch_box), captured.crop(patch_box)).getbbox()
    assert captured.crop(patch_box).getcolors() == [(783, (255, 255, 255))]
    await page.clock.fast_forward(2000)
    assert await pointer.count() == 0


async def test_find_scrolls_to_offscreen_match_and_maps_it_to_an_id(
    tools: FastMCP, manager: BrowserManager, server: int
) -> None:
    summary = await open_app(tools, server)
    assert "Deep target" not in summary

    text, _ = await call(tools, "find", query="deep target")
    assert "scrolled to match 1" in text
    deep = int(text.split("element [")[1].split("]")[0])
    await call(tools, "click", element_id=deep)
    assert await log_text(manager) == "deep"

    by_role, _ = await call(tools, "find", query="", role="button", nth=2)
    assert "match(es) for button elements" in by_role


async def test_act_runs_steps_with_one_screenshot(
    tools: FastMCP, manager: BrowserManager, server: int
) -> None:
    summary = await open_app(tools, server)
    name, greet = element_id(summary, "input[text]"), element_id(summary, "Greet")
    text, _ = await call(
        tools,
        "act",
        steps=[
            {"action": "type", "element_id": name, "text": "Ada"},
            {"action": "click", "element_id": greet},
            {"action": "bogus"},
            {"action": "press", "key": "Tab"},
        ],
    )
    assert "Ran 3 of 4 step(s), 1 failed" in text
    assert "remaining step(s) skipped" in text
    assert await log_text(manager) == "hello Ada"


async def test_double_right_click_and_drag(
    tools: FastMCP, manager: BrowserManager, server: int
) -> None:
    summary = await open_app(tools, server)
    await call(tools, "double_click", element_id=element_id(summary, "Dbl"))
    assert await log_text(manager) == "double"
    await call(tools, "right_click", element_id=element_id(summary, "Ctx"))
    assert await log_text(manager) == "context"

    text, _ = await call(
        tools,
        "drag",
        source_id=element_id(summary, "drag me"),
        target_id=element_id(summary, "drop here"),
    )
    assert "Dragged" in text
    assert await log_text(manager) == "dropped"


async def test_dialogs_are_reported_and_controllable(
    tools: FastMCP, manager: BrowserManager, server: int
) -> None:
    summary = await open_app(tools, server)
    ask = element_id(summary, "Ask")
    text, _ = await call(tools, "click", element_id=ask)
    assert "Notice: A JS dialog appeared: confirm('Really?'), dismissed." in text
    assert await log_text(manager) == "cancelled"

    await call(tools, "handle_dialog", accept=True)
    text, _ = await call(tools, "click", element_id=element_id(text, "Ask"))
    assert "confirm('Really?'), accepted." in text
    assert await log_text(manager) == "confirmed"


async def test_download_is_saved_and_listed(
    tools: FastMCP, manager: BrowserManager, server: int, tmp_path: Path
) -> None:
    summary = await open_app(tools, server)
    await call(tools, "click", element_id=element_id(summary, "Get file"))
    listing = await call(tools, "list_downloads")
    for _ in range(20):
        if "report.txt" in listing:
            break
        await asyncio.sleep(0.1)
        listing = await call(tools, "list_downloads")
    assert "report.txt" in listing
    assert (tmp_path / "downloads" / "report.txt").read_text() == "file contents"


async def test_settle_captures_content_rendered_after_fetch(
    tools: FastMCP, manager: BrowserManager, server: int
) -> None:
    summary = await open_app(tools, server)
    text, _ = await call(tools, "click", element_id=element_id(summary, "Load"))
    # No explicit wait: the fetch, then the 150ms render, are waited out.
    assert "Loaded 42" in text


async def test_network_details_wait_mock_and_har(
    tools: FastMCP, manager: BrowserManager, server: int, tmp_path: Path
) -> None:
    summary = await open_app(tools, server)
    manager.mark_call_started()
    await call(tools, "click", element_id=element_id(summary, "Load"))
    manager.mark_call_started()
    text, _ = await call(tools, "wait_for_response", url_pattern="**/api/data")
    assert "-> 200" in text and '"value": 42' in text
    request_id = int(text.split("#")[1].split()[0])

    details = await call(tools, "get_request_details", request_id=request_id)
    assert "content-type: application/json" in details
    assert '{"value": 42}' in details

    saved = await call(tools, "export_har", name="../escape", include_bodies=True)
    har_path = tmp_path / "rec" / "escape.har"
    assert str(har_path) in saved
    har = json.loads(har_path.read_text())
    api = [e for e in har["log"]["entries"] if e["request"]["url"].endswith("/api/data")]
    assert api and api[0]["response"]["content"]["text"] == '{"value": 42}'

    await call(tools, "mock_route", url_pattern="/api/data", status=500, body="{}")
    summary = await open_app(tools, server)
    await call(tools, "click", element_id=element_id(summary, "Load"))
    text, _ = await call(tools, "wait_for", text="Loaded", timeout_seconds=1)
    # A 500 still parses as JSON here ({}), so the page renders "Loaded undefined".
    assert "Done waiting" in text
    await call(tools, "mock_route", url_pattern="/api/data", abort=True)
    summary = await open_app(tools, server)
    await call(tools, "click", element_id=element_id(summary, "Load"))
    await call(tools, "wait_for", text="load failed", timeout_seconds=2)
    assert await log_text(manager) == "load failed"
    assert await call(tools, "clear_mocks") == "Removed 1 mock(s)."


async def test_extraction(tools: FastMCP, manager: BrowserManager, server: int) -> None:
    await open_app(tools, server)
    table = await call(tools, "extract_table")
    assert json.loads(table.split("\n", 1)[1]) == [
        {"Name": "Apple", "Price": "1"},
        {"Name": "Pear", "Price": "2"},
    ]
    assert "| Apple | 1 |" in await call(tools, "extract_table", output_format="markdown")

    links = await call(tools, "extract_links", contains="file")
    assert json.loads(links.split("\n", 1)[1])[0]["href"].endswith("/file.txt")

    data = json.loads(
        await call(
            tools,
            "extract",
            schema={
                "products": [
                    {"_selector": ".product", "name": "h3", "price": ".price", "url": "a@href"}
                ],
                "headers": ["th"],
            },
        )
    )
    assert data["headers"] == ["Name", "Price"]
    assert data["products"][1]["name"] == "Gadget"
    assert data["products"][1]["url"].endswith("/g")


async def test_emulation(tools: FastMCP, manager: BrowserManager, server: int) -> None:
    await open_app(tools, server)
    page = manager.page

    await call(tools, "emulate_device", name="iPhone 13")
    assert await page.evaluate("window.innerWidth") == 390
    assert "iPhone" in await page.evaluate("navigator.userAgent")
    assert await page.evaluate("navigator.maxTouchPoints") > 0

    await call(tools, "set_timezone", timezone_id="Asia/Tokyo")
    tz = await page.evaluate("Intl.DateTimeFormat().resolvedOptions().timeZone")
    assert tz == "Asia/Tokyo"

    await call(tools, "set_color_scheme", scheme="dark")
    assert await page.evaluate("matchMedia('(prefers-color-scheme: dark)').matches")

    await call(tools, "set_geolocation", latitude=48.85, longitude=2.35)
    lat = await page.evaluate(
        "new Promise(r => navigator.geolocation.getCurrentPosition(p => r(p.coords.latitude)))"
    )
    assert lat == pytest.approx(48.85)

    await call(tools, "throttle_network", profile="offline")
    assert await page.evaluate("navigator.onLine") is False
    await call(tools, "throttle_network", profile="slow-3g")

    await call(tools, "reset_emulation")
    assert await page.evaluate("window.innerWidth") == 1280
    assert await page.evaluate("navigator.onLine") is True
    assert "iPhone" not in await page.evaluate("navigator.userAgent")


async def test_isolated_sessions_do_not_share_cookies(
    tools: FastMCP, manager: BrowserManager, server: int
) -> None:
    await open_app(tools, server)
    await manager.page.evaluate("document.cookie = 'who=default'")

    await call(tools, "create_session", name="second", url=f"http://127.0.0.1:{server}/")
    assert manager.session.name == "second"
    assert await manager.page.evaluate("document.cookie") == ""
    assert "second" in await call(tools, "list_sessions")

    await call(tools, "switch_session", name="default")
    assert await manager.page.evaluate("document.cookie") == "who=default"
    await call(tools, "close_session", name="second")
    assert [s["name"] for s in manager.list_sessions()] == ["default"]


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


async def test_attach_over_cdp_leaves_the_users_chrome_running(
    manager: BrowserManager, server: int
) -> None:
    assert manager._playwright is not None
    port = _free_port()
    args = [f"--remote-debugging-port={port}"]
    # Same order the manager tries: Playwright's full Chromium, then installed Chrome.
    try:
        chrome = await manager._playwright.chromium.launch(args=args, channel="chromium")
    except Exception:
        chrome = await manager._playwright.chromium.launch(args=args, channel="chrome")
    try:
        user_page = await chrome.new_page()
        await user_page.goto(f"http://127.0.0.1:{server}/other")

        attached = BrowserManager()
        await attached.connect_over_cdp(f"http://127.0.0.1:{port}")
        assert attached.cdp_url is not None
        # The agent gets a tab of its own; the user's tab is untouched.
        assert attached.page.url == "about:blank"
        assert any(t["url"].endswith("/other") for t in await attached.list_tabs())
        await attached.stop()

        assert chrome.is_connected()
        assert not user_page.is_closed()
    finally:
        await chrome.close()


async def test_exported_test_replays_in_playwright(
    tools: FastMCP, manager: BrowserManager, server: int, tmp_path: Path
) -> None:
    summary = await open_app(tools, server)
    await call(tools, "type_text", element_id=element_id(summary, "input[text]"), text="Ada")
    await call(tools, "type_text", element_id=element_id(summary, "password"), text="s3cret")
    await call(tools, "handle_dialog", accept=True)
    await call(tools, "click", element_id=element_id(summary, "Greet"))
    await call(tools, "wait_for", text="hello Ada")

    output = await call(tools, "export_test", name="greet flow")
    path = tmp_path / "gen" / "test_greet_flow.py"
    code = path.read_text()
    assert "s3cret" not in code and 'os.environ["BC_SECRET_1"]' in code
    assert 'get_by_role("textbox", name="Name", exact=True).fill("Ada")' in code
    assert 'page.once("dialog", lambda dialog: dialog.accept())' in code
    assert 'get_by_role("button", name="Greet", exact=True).click()' in code
    assert str(path) in output

    ts = await call(tools, "export_test", name="greet flow", language="typescript")
    assert 'getByRole("button", { name: "Greet", exact: true }).click();' in ts

    # Replay the generated Python test against the same server with a fresh browser.
    runner = tmp_path / "run_generated.py"
    runner.write_text(
        "import importlib.util, os, sys\n"
        "from playwright.sync_api import sync_playwright\n"
        "spec = importlib.util.spec_from_file_location('gen', sys.argv[1])\n"
        "mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)\n"
        "os.environ['BC_SECRET_1'] = 'x'\n"
        "with sync_playwright() as pw:\n"
        "    try:\n"
        "        b = pw.chromium.launch(channel='chromium')\n"
        "    except Exception:\n"
        "        b = pw.chromium.launch(channel='chrome')\n"
        "    page = b.new_page()\n"
        "    mod.test_greet_flow(page)\n"
        "    print('LOG=' + page.locator('#log').inner_text())\n"
        "    b.close()\n"
    )
    result = await asyncio.to_thread(
        subprocess.run,
        [sys.executable, str(runner), str(path)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr
    assert "LOG=hello Ada" in result.stdout


async def test_http_transport_serves_tools(tmp_path: Path) -> None:
    from fastmcp import Client

    port = _free_port()
    env = {
        **__import__("os").environ,
        "BROWSER_HEADLESS": "true",
        "BROWSER_USER_DATA_DIR": str(tmp_path / "profile"),
    }
    proc = subprocess.Popen(
        [sys.executable, "-m", "browsercontrol", "--transport", "http", "--port", str(port)],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    try:
        deadline = time.time() + 60
        names: set[str] = set()
        while time.time() < deadline:
            try:
                async with Client(f"http://127.0.0.1:{port}/mcp") as client:
                    names = {t.name for t in await client.list_tools()}
                    resource = await client.read_resource("browser://sessions")
                    assert "default" in resource[0].text  # type: ignore[union-attr]
                break
            except Exception:
                if proc.poll() is not None:
                    raise AssertionError(proc.stderr.read().decode() if proc.stderr else "")
                await asyncio.sleep(0.5)
        assert {"find", "act", "connect_to_chrome", "export_test"} <= names
    finally:
        proc.terminate()
        proc.wait(timeout=30)


async def test_http_transport_requires_the_bearer_token(tmp_path: Path) -> None:
    import httpx
    from fastmcp import Client

    token = "test-token-1234"
    port = _free_port()
    env = {
        **__import__("os").environ,
        "BROWSER_HEADLESS": "true",
        "BROWSER_USER_DATA_DIR": str(tmp_path / "profile"),
        "BROWSER_AUTH_TOKEN": token,
    }
    proc = subprocess.Popen(
        [sys.executable, "-m", "browsercontrol", "--transport", "http", "--port", str(port)],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    url = f"http://127.0.0.1:{port}/mcp"
    try:
        deadline = time.time() + 60
        while True:
            try:
                async with Client(url, auth=token) as client:
                    names = {t.name for t in await client.list_tools()}
                break
            except Exception:
                if proc.poll() is not None or time.time() > deadline:
                    raise AssertionError(proc.stderr.read().decode() if proc.stderr else "")
                await asyncio.sleep(0.5)
        assert "navigate_to" in names

        async with httpx.AsyncClient() as http:
            for headers in ({}, {"Authorization": "Bearer wrong"}, {"Authorization": token}):
                r = await http.post(url, headers=headers, json={})
                assert r.status_code == 401, headers
        with pytest.raises(Exception):  # noqa: B017 - the client surfaces the 401 as an error
            async with Client(url) as client:
                await client.list_tools()
    finally:
        proc.terminate()
        proc.wait(timeout=30)


async def test_navigation_policy_blocks_in_a_real_browser(
    tools: FastMCP, manager: BrowserManager, server: int
) -> None:
    from browsercontrol.config import config

    base = f"http://127.0.0.1:{server}"
    with patch.object(config, "allowed_domains", ["127.0.0.1"]):
        text, _ = await call(tools, "navigate_to", url=f"{base}/")
        assert text.startswith(f"Navigated to {base}/")

        blocked = [
            f"http://localhost:{server}/",  # same server, but not an allowed host
            "file:///etc/hostname",
            "data:text/html,<h1>owned</h1>",
            "javascript:document.title='owned'",
        ]
        for url in blocked:
            with pytest.raises(RuntimeError, match="blocked"):
                await call(tools, "navigate_to", url=url)
        text, _ = await call(
            tools, "act", steps=[{"action": "navigate", "url": "file:///etc/hostname"}]
        )
        assert "FAILED (navigate)" in text and "BROWSER_ALLOW_UNSAFE_SCHEMES" in text
        with pytest.raises(RuntimeError, match="blocked"):
            await call(tools, "create_session", name="x", url="https://example.com/")

        # None of it moved the browser: it is still on the allowed page, in its one tab.
        assert manager.page.url == f"{base}/"
        assert await manager.page.title() == ""
        assert len(manager._context.pages) == 1
    # Without the allowlist, only the dangerous schemes are blocked.
    with pytest.raises(RuntimeError, match="BROWSER_ALLOW_UNSAFE_SCHEMES"):
        await call(tools, "navigate_to", url="file:///etc/hostname")
    text, _ = await call(tools, "navigate_to", url=f"{base}/other")
    assert text.startswith("Navigated to")


async def test_isolate_clients_gives_each_client_its_own_session(
    tmp_path: Path, server: int
) -> None:
    from fastmcp import Client

    from browsercontrol.browser import browser
    from browsercontrol.server import mcp

    with (
        patch("browsercontrol.browser.config.user_data_dir", tmp_path / "profile"),
        patch("browsercontrol.browser.config.isolate_clients", True),
    ):
        async with Client(mcp) as first, Client(mcp) as second:
            url = f"http://127.0.0.1:{server}/"
            await first.call_tool("navigate_to", {"url": url})
            await first.call_tool("run_javascript", {"script": "document.cookie = 'who=first'"})
            await second.call_tool("navigate_to", {"url": url})
            cookie = await second.call_tool("run_javascript", {"script": "document.cookie"})
            assert "who=first" not in str(cookie.content)

            listing = json.loads(
                (await first.read_resource("browser://sessions"))[0].text  # type: ignore[union-attr]
            )
            assert len([s for s in listing if s["isolated"]]) == 2
            network = json.loads(
                (await second.read_resource("browser://network"))[0].text  # type: ignore[union-attr]
            )
            assert any(e["url"] == url for e in network)
    assert not browser.is_started

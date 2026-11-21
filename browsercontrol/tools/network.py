"""Network control: request mocking, request details, waiting for responses, HAR export."""

import base64
import json
import logging
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit

from fastmcp import FastMCP
from fastmcp.utilities.types import Image
from playwright.async_api import Response, Route

from browsercontrol.browser import browser
from browsercontrol.config import config
from browsercontrol.session import Session, url_matches
from browsercontrol.tools._summary import get_screenshot_with_summary

logger = logging.getLogger(__name__)

MAX_BODY_CHARS = 10_000
MAX_HAR_BODY_BYTES = 1_000_000
TEXT_TYPES = ("text/", "json", "javascript", "xml", "html", "x-www-form-urlencoded", "graphql")


def _is_text(mime: str) -> bool:
    return any(t in mime.lower() for t in TEXT_TYPES)


async def _body(entry: dict[str, Any], limit: int | None = None) -> tuple[str | None, str]:
    """Read a captured response body: (text or base64, encoding). (None, reason) if unavailable."""
    response: Response | None = entry.get("_response")
    if response is None:
        return None, "no response"
    try:
        raw = await response.body()
    except Exception as e:
        return None, f"body unavailable ({e.__class__.__name__}; the page may have navigated)"
    if limit is not None and len(raw) > limit:
        return None, f"body is {len(raw)} bytes, over the {limit}-byte limit"
    mime = entry.get("response_headers", {}).get("content-type", "")
    if _is_text(mime) or not mime:
        try:
            return raw.decode("utf-8"), "text"
        except UnicodeDecodeError:
            pass
    return base64.b64encode(raw).decode("ascii"), "base64"


def _line(entry: dict[str, Any]) -> str:
    line = f"#{entry.get('id', '?')} {entry.get('method', 'GET')} {entry.get('url', '')}"
    line += f" -> {entry.get('status', 'pending')}"
    if entry.get("duration") is not None:
        line += f" ({entry['duration']}ms)"
    return line


def _headers(headers: dict[str, str]) -> list[dict[str, str]]:
    return [{"name": k, "value": v} for k, v in headers.items()]


async def har_entry(entry: dict[str, Any], include_body: bool) -> dict[str, Any]:
    """One captured request as a HAR 1.2 entry."""
    request_headers: dict[str, str] = entry.get("request_headers", {})
    response_headers: dict[str, str] = entry.get("response_headers", {})
    started = entry.get("start_time") or entry.get("end_time") or time.time()
    duration = entry.get("duration") or 0
    status = entry.get("status")
    request: dict[str, Any] = {
        "method": entry.get("method", "GET"),
        "url": entry.get("url", ""),
        "httpVersion": "HTTP/1.1",
        "headers": _headers(request_headers),
        "queryString": [
            {"name": k, "value": v}
            for k, v in parse_qsl(urlsplit(entry.get("url", "")).query, keep_blank_values=True)
        ],
        "cookies": [],
        "headersSize": -1,
        "bodySize": len(entry["post_data"]) if entry.get("post_data") else 0,
    }
    if entry.get("post_data"):
        request["postData"] = {
            "mimeType": request_headers.get("content-type", ""),
            "text": entry["post_data"],
        }
    mime = response_headers.get("content-type", "")
    content: dict[str, Any] = {"size": -1, "mimeType": mime}
    if include_body and isinstance(status, int):
        text, encoding = await _body(entry, MAX_HAR_BODY_BYTES)
        if text is not None:
            content["text"] = text
            content["size"] = len(text)
            if encoding == "base64":
                content["encoding"] = "base64"
    return {
        "startedDateTime": datetime.fromtimestamp(started, UTC).isoformat(),
        "time": duration,
        "request": request,
        "response": {
            "status": status if isinstance(status, int) else 0,
            "statusText": entry.get("status_text", "" if isinstance(status, int) else str(status)),
            "httpVersion": "HTTP/1.1",
            "headers": _headers(response_headers),
            "cookies": [],
            "content": content,
            "redirectURL": response_headers.get("location", ""),
            "headersSize": -1,
            "bodySize": -1,
        },
        "cache": {},
        "timings": {"send": 0, "wait": duration, "receive": 0},
        "_resourceType": entry.get("resource_type", ""),
    }


async def _remove_route(session: Session, route: dict[str, Any]) -> None:
    if session.context is not None:
        await session.context.unroute(route["predicate"], route["handler"])
    session.routes.remove(route)


def register_network_tools(mcp: FastMCP) -> None:
    """Register network control tools with the MCP server."""

    @mcp.tool()
    async def mock_route(
        url_pattern: str,
        status: int = 200,
        body: str = "",
        content_type: str = "application/json",
        headers: dict[str, str] | None = None,
        abort: bool = False,
    ) -> str:
        """
        Answer matching requests with a canned response, or block them, in every tab.

        Use it to test error states (status=500), stub an API, or block trackers
        (abort=True). Replaces any earlier mock with the same pattern.

        Args:
            url_pattern: Substring of the URL, a glob like "**/api/users*", or "re:<regex>"
            status: HTTP status to return (default 200)
            body: Response body (e.g. a JSON string)
            content_type: Content-Type of the body (default application/json)
            headers: Extra response headers
            abort: Fail matching requests with a network error instead of responding
        """
        try:
            await browser.ensure_started()
            session = browser.session
            context = browser.page.context
            for existing in [r for r in session.routes if r["pattern"] == url_pattern]:
                await _remove_route(session, existing)

            def predicate(url: str) -> bool:
                return url_matches(url_pattern, url)

            async def handler(route: Route) -> None:
                if abort:
                    await route.abort()
                else:
                    await route.fulfill(
                        status=status, body=body, content_type=content_type, headers=headers
                    )

            await context.route(predicate, handler)
            session.routes.append(
                {
                    "pattern": url_pattern,
                    "predicate": predicate,
                    "handler": handler,
                    "status": status,
                    "abort": abort,
                }
            )
            browser.log_action(
                "mock",
                pattern=url_pattern,
                status=status,
                body=body,
                content_type=content_type,
                abort=abort,
            )
            outcome = "blocked" if abort else f"answered with {status} ({content_type})"
            active = ", ".join(r["pattern"] for r in session.routes)
            return f"Requests matching {url_pattern!r} will be {outcome}.\nActive mocks: {active}"
        except Exception as e:
            logger.error(f"Mock route failed: {e}")
            raise RuntimeError(f"Mock route failed: {e}")

    @mcp.tool()
    async def clear_mocks(url_pattern: str | None = None) -> str:
        """
        Remove request mocks so requests reach the network again.

        Args:
            url_pattern: The pattern given to mock_route; omit to remove every mock
        """
        try:
            await browser.ensure_started()
            session = browser.session
            targets = [r for r in session.routes if url_pattern in (None, r["pattern"])]
            if not targets:
                return "No matching mocks are active."
            for route in targets:
                await _remove_route(session, route)
            return f"Removed {len(targets)} mock(s)."
        except Exception as e:
            logger.error(f"Clear mocks failed: {e}")
            raise RuntimeError(f"Clear mocks failed: {e}")

    @mcp.tool()
    async def get_request_details(request_id: int, include_body: bool = True) -> str:
        """
        Show one captured request in full: headers, POST data, response headers and body.

        Args:
            request_id: The #id shown by get_network_requests or wait_for_response
            include_body: Include the response body (text, truncated; binary as base64)
        """
        try:
            await browser.ensure_started()
            entry = browser.session.find_request(request_id)
            if entry is None:
                return f"No captured request #{request_id}. Only the last 100 are kept."
            lines = [_line(entry), f"Type: {entry.get('resource_type', '')}"]
            if entry.get("failure"):
                lines.append(f"Failure: {entry['failure']}")
            lines.append("\nRequest headers:")
            lines += [f"  {k}: {v}" for k, v in entry.get("request_headers", {}).items()]
            if entry.get("post_data"):
                lines.append(f"\nRequest body:\n{entry['post_data'][:MAX_BODY_CHARS]}")
            if entry.get("response_headers"):
                lines.append("\nResponse headers:")
                lines += [f"  {k}: {v}" for k, v in entry["response_headers"].items()]
            if include_body and isinstance(entry.get("status"), int):
                text, encoding = await _body(entry)
                if text is None:
                    lines.append(f"\nResponse body: {encoding}")
                else:
                    clipped = text[:MAX_BODY_CHARS]
                    more = (
                        f"\n... [{len(text) - MAX_BODY_CHARS} more chars]"
                        if len(text) > MAX_BODY_CHARS
                        else ""
                    )
                    lines.append(f"\nResponse body ({encoding}):\n{clipped}{more}")
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Get request details failed: {e}")
            raise RuntimeError(f"Get request details failed: {e}")

    @mcp.tool()
    async def wait_for_response(
        url_pattern: str, status: int | None = None, timeout_seconds: float = 10.0
    ) -> tuple[str, Image]:
        """
        Wait for a network response whose URL matches, e.g. the API call a click triggered.

        Responses that arrived during the previous tool call count, so call this
        right after the action that sends the request.

        Args:
            url_pattern: Substring of the URL, a glob like "**/api/save*", or "re:<regex>"
            status: Only accept this HTTP status
            timeout_seconds: Give up after this long (default 10)
        """
        try:
            await browser.ensure_started()
            session = browser.session

            def accepts(url: str, code: Any) -> bool:
                return url_matches(url_pattern, url) and (status is None or code == status)

            since = session.previous_call_started
            entry = next(
                (
                    e
                    for e in reversed(session.network_requests)
                    if isinstance(e.get("status"), int)
                    and e.get("start_time", e.get("end_time", 0)) >= since
                    and accepts(e.get("url", ""), e.get("status"))
                ),
                None,
            )
            if entry is None:
                try:
                    response = await browser.page.wait_for_event(
                        "response",
                        predicate=lambda r: accepts(r.url, r.status),
                        timeout=timeout_seconds * 1000,
                    )
                except Exception:
                    image, summary = await get_screenshot_with_summary(browser)
                    return (
                        f"Timed out after {timeout_seconds}s: no response matched "
                        f"{url_pattern!r}"
                        + (f" with status {status}" if status else "")
                        + f"\n\n{summary}",
                        image,
                    )
                # The capture listener records it as the same event fires.
                entry = next(
                    (
                        e
                        for e in reversed(session.network_requests)
                        if e.get("_response") is response
                    ),
                    {"url": response.url, "status": response.status, "_response": response},
                )

            preview, encoding = await _body(entry, MAX_BODY_CHARS * 10)
            text = _line(entry)
            if preview is not None and encoding == "text":
                text += f"\nBody: {preview[:2000]}" + ("..." if len(preview) > 2000 else "")
            await browser.settle(1500)
            image, summary = await get_screenshot_with_summary(browser)
            return f"Response received: {text}\n\n{summary}", image
        except Exception as e:
            logger.error(f"Wait for response failed: {e}")
            raise RuntimeError(f"Wait for response failed: {e}")

    @mcp.tool()
    async def export_har(name: str = "", include_bodies: bool = False) -> str:
        """
        Save the captured network traffic (last 100 requests) as a HAR file.

        Open it in Chrome DevTools (Network > Import) or any HAR viewer.

        Args:
            name: File name without extension (default: timestamp)
            include_bodies: Also save response bodies (up to 1MB each)
        """
        try:
            await browser.ensure_started()
            entries = [await har_entry(e, include_bodies) for e in browser.session.network_requests]
            har = {
                "log": {
                    "version": "1.2",
                    "creator": {"name": "BrowserControl", "version": "0.3.0"},
                    "pages": [],
                    "entries": entries,
                }
            }
            config.recordings_dir.mkdir(parents=True, exist_ok=True)
            # Only a file name: a name with path parts must not escape the directory.
            stem = Path(name).name or datetime.now().strftime("%Y%m%d_%H%M%S")
            path = config.recordings_dir / f"{stem}.har"
            path.write_text(json.dumps(har, indent=2), encoding="utf-8")
            return f"Saved {len(entries)} request(s) to {path}"
        except Exception as e:
            logger.error(f"Export HAR failed: {e}")
            raise RuntimeError(f"Export HAR failed: {e}")

    logger.debug("Registered network tools")

"""Per-session browser state and the page listeners that fill it.

A session is one browser context plus everything captured from it: console
logs, network traffic, page errors, dialogs, downloads, the action log used for
test generation, request mocks, and emulation settings. The default session is
the persistent profile (or the Chrome attached over CDP); isolated sessions are
fresh, cookie-free contexts so several agents can work side by side.
"""

import asyncio
import fnmatch
import itertools
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from playwright.async_api import BrowserContext, Dialog, Download, Page, Request, Response

logger = logging.getLogger(__name__)

MAX_CONSOLE_LOGS = 200
MAX_NETWORK_REQUESTS = 100
MAX_PAGE_ERRORS = 100
MAX_ACTIONS = 500
MAX_NOTICES = 20

_request_ids = itertools.count(1)


@dataclass
class Session:
    """One browser context and its captured state."""

    name: str
    context: BrowserContext | None = None
    page: Page | None = None
    isolated: bool = False

    console_logs: list[dict[str, Any]] = field(default_factory=list)
    network_requests: list[dict[str, Any]] = field(default_factory=list)
    page_errors: list[dict[str, Any]] = field(default_factory=list)
    # Keyed by Request object identity to avoid URL-collision mis-pairings
    request_map: dict[Any, dict[str, Any]] = field(default_factory=dict)

    # Messages for the agent (dialogs, downloads) shown with the next screenshot.
    notices: list[str] = field(default_factory=list)
    downloads: list[dict[str, Any]] = field(default_factory=list)
    dialogs: list[dict[str, Any]] = field(default_factory=list)
    # How to answer the next JS dialog; None means the default policy.
    dialog_policy: dict[str, Any] | None = None

    actions: list[dict[str, Any]] = field(default_factory=list)
    routes: list[dict[str, Any]] = field(default_factory=list)
    emulation: dict[str, Any] = field(default_factory=dict)

    # Start times of the current and previous tool calls, for wait_for_response.
    call_started: float = 0.0
    previous_call_started: float = 0.0

    def add_notice(self, text: str) -> None:
        self.notices.append(text)
        del self.notices[:-MAX_NOTICES]

    def drain_notices(self) -> list[str]:
        notices, self.notices = self.notices, []
        return notices

    def clear_captures(self) -> None:
        self.console_logs.clear()
        self.network_requests.clear()
        self.page_errors.clear()
        self.request_map.clear()
        self.notices.clear()

    def find_request(self, request_id: int) -> dict[str, Any] | None:
        for entry in self.network_requests:
            if entry.get("id") == request_id:
                return entry
        for entry in self.request_map.values():
            if entry.get("id") == request_id:
                return entry
        return None


def url_matches(pattern: str, url: str) -> bool:
    """Match a URL against ``re:<regex>``, a glob (with ``*``), or a plain substring."""
    if pattern.startswith("re:"):
        return re.search(pattern[3:], url) is not None
    if "*" in pattern or "?" in pattern:
        return fnmatch.fnmatchcase(url, pattern)
    return pattern in url


def _unique_path(directory: Path, filename: str) -> Path:
    """A path in ``directory`` for ``filename`` that does not overwrite an existing file."""
    name = Path(filename).name or "download"
    target = directory / name
    stem, suffix = target.stem, target.suffix
    for n in itertools.count(1):
        if not target.exists():
            return target
        target = directory / f"{stem} ({n}){suffix}"
    raise AssertionError("unreachable")  # pragma: no cover


def describe_dialog(dialog_type: str, message: str) -> str:
    text = " ".join(message.split())
    return f"{dialog_type}({text[:120]!r})"


async def answer_dialog(session: Session, dialog: Dialog) -> None:
    """Answer a JS dialog per the session's policy, and tell the agent what happened.

    Without a policy, alerts are acknowledged, confirms and prompts are
    dismissed, and beforeunload is accepted so navigation is never stuck.
    """
    policy, session.dialog_policy = session.dialog_policy, None
    if policy is not None:
        accept = bool(policy.get("accept", True))
    else:
        accept = dialog.type in ("alert", "beforeunload")
    prompt_text = policy.get("prompt_text") if policy else None

    try:
        if accept:
            if prompt_text is not None:
                await dialog.accept(prompt_text)
            else:
                await dialog.accept()
        else:
            await dialog.dismiss()
    except Exception as e:
        logger.debug(f"Answering dialog failed: {e}")

    summary = describe_dialog(dialog.type, dialog.message)
    outcome = "accepted" if accept else "dismissed"
    if accept and prompt_text is not None:
        outcome += f" with {prompt_text!r}"
    session.dialogs.append({"type": dialog.type, "message": dialog.message, "outcome": outcome})
    del session.dialogs[:-50]
    hint = "" if policy else " Call handle_dialog() before the action to choose the answer."
    session.add_notice(f"A JS dialog appeared: {summary}, {outcome}.{hint}")


async def save_download(session: Session, download: Download, directory: Path) -> None:
    """Save a download to the downloads directory and tell the agent where it went."""
    try:
        directory.mkdir(parents=True, exist_ok=True)
        target = _unique_path(directory, download.suggested_filename)
        await download.save_as(str(target))
    except Exception as e:
        session.add_notice(f"Download of {download.url} failed: {e}")
        return
    session.downloads.append(
        {"filename": target.name, "path": str(target), "url": download.url, "time": time.time()}
    )
    session.add_notice(f"Downloaded {target.name} to {target}")


def attach_page_listeners(session: Session, page: Page, downloads_dir: Path) -> None:
    """Capture console, errors, network, dialogs, and downloads from ``page`` into ``session``."""

    def on_console(msg: Any) -> None:
        location = msg.location or {}
        session.console_logs.append(
            {
                "level": msg.type,
                "text": msg.text,
                "location": f"{location.get('url', '')}:{location.get('lineNumber', '')}"
                if location
                else "",
                "timestamp": time.time(),
            }
        )
        del session.console_logs[:-MAX_CONSOLE_LOGS]

    def on_page_error(error: Any) -> None:
        session.page_errors.append(
            {"message": str(error), "stack": getattr(error, "stack", ""), "timestamp": time.time()}
        )
        del session.page_errors[:-MAX_PAGE_ERRORS]

    def on_request(request: Request) -> None:
        session.request_map[request] = {
            "id": next(_request_ids),
            "method": request.method,
            "url": request.url,
            "start_time": time.time(),
            "status": "pending",
            "resource_type": request.resource_type,
            "request_headers": dict(request.headers),
            "post_data": request.post_data,
        }

    def finish(entry: dict[str, Any]) -> None:
        entry["end_time"] = time.time()
        if "start_time" in entry:
            entry["duration"] = int((entry["end_time"] - entry["start_time"]) * 1000)
        session.network_requests.append(entry)
        del session.network_requests[:-MAX_NETWORK_REQUESTS]

    def on_response(response: Response) -> None:
        entry = session.request_map.pop(response.request, None) or {
            "id": next(_request_ids),
            "method": response.request.method,
            "url": response.url,
            "resource_type": response.request.resource_type,
        }
        entry["status"] = response.status
        entry["status_text"] = response.status_text
        entry["response_headers"] = dict(response.headers)
        # Kept so the body can be read on demand; not serialized.
        entry["_response"] = response
        finish(entry)

    def on_request_failed(request: Request) -> None:
        entry = session.request_map.pop(request, None)
        if entry is not None:
            entry["status"] = "failed"
            entry["failure"] = request.failure
            finish(entry)

    async def on_dialog(dialog: Dialog) -> None:
        await answer_dialog(session, dialog)

    async def on_download(download: Download) -> None:
        await save_download(session, download, downloads_dir)

    page.on("console", on_console)
    page.on("pageerror", on_page_error)
    page.on("request", on_request)
    page.on("response", on_response)
    page.on("requestfailed", on_request_failed)
    page.on("dialog", on_dialog)
    page.on("download", on_download)


async def network_quiet(session: Session, deadline: float, quiet_s: float = 0.2) -> None:
    """Wait until no ordinary request has been in flight for ``quiet_s``, or the deadline.

    Streams and requests open for over 10s (long polling) are ignored so they
    cannot hold every action to the deadline.
    """
    loop = asyncio.get_running_loop()
    quiet_since: float | None = None
    while loop.time() < deadline:
        now = time.time()
        busy = any(
            entry.get("resource_type") not in ("eventsource", "websocket", "media")
            and now - entry.get("start_time", now) < 10
            for entry in list(session.request_map.values())
        )
        if busy:
            quiet_since = None
        else:
            quiet_since = quiet_since if quiet_since is not None else loop.time()
            if loop.time() - quiet_since >= quiet_s:
                return
        await asyncio.sleep(0.05)

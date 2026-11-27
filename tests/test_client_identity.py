"""How the server tells MCP clients apart (BROWSER_AUTH_TOKENS and the client key).

fastmcp 4 negotiates the session-less 2026-07-28 protocol by default, where ``session_id`` is
new on every request. The client key decides which browser session a call runs in, so it must
stay stable across a client's calls.
"""

import logging
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import pytest
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from browsercontrol.__main__ import main
from browsercontrol.auth import CLIENT_STATE_KEY, BearerAuthMiddleware, auth_middleware
from browsercontrol.config import Config, config, parse_auth_tokens
from browsercontrol.resources import _client_key

ALICE, BOB = "alice-token-0001", "bob-token-0002"


class TestParseAuthTokens:
    def test_named_tokens(self) -> None:
        assert parse_auth_tokens(f"alice:{ALICE}, bob:{BOB}") == {"alice": ALICE, "bob": BOB}

    def test_token_may_contain_a_colon(self) -> None:
        assert parse_auth_tokens("alice:a:b:c") == {"alice": "a:b:c"}

    @pytest.mark.parametrize("raw", ["", " ", ",", " , "])
    def test_blank_means_none(self, raw: str) -> None:
        assert parse_auth_tokens(raw) == {}

    @pytest.mark.parametrize(
        "entry",
        [
            "no-separator",
            ":tok-without-name",
            "name-without-token:",
            "bad name:tok-1",
            "bad/name:tok-1",
            f"{'n' * 65}:tok-1",
        ],
    )
    def test_malformed_entries_are_skipped_without_logging_the_token(
        self, entry: str, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.WARNING, logger="browsercontrol.config"):
            assert parse_auth_tokens(f"{entry},alice:{ALICE}") == {"alice": ALICE}
        assert "BROWSER_AUTH_TOKENS" in caplog.text
        assert "tok-1" not in caplog.text and "tok-without-name" not in caplog.text

    def test_duplicate_names_and_tokens_are_skipped(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.WARNING, logger="browsercontrol.config"):
            tokens = parse_auth_tokens(f"alice:{ALICE},alice:{BOB},bob:{ALICE}")
        assert tokens == {"alice": ALICE}
        assert ALICE not in caplog.text and BOB not in caplog.text

    def test_from_env_keeps_tokens_out_of_repr(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BROWSER_AUTH_TOKENS", f"alice:{ALICE}")
        cfg = Config.from_env()
        assert cfg.auth_tokens == {"alice": ALICE}
        assert ALICE not in repr(cfg)


def _app(**kwargs: Any) -> Starlette:
    async def whoami(request: Request) -> PlainTextResponse:
        return PlainTextResponse(str(request.scope.get("state", {}).get(CLIENT_STATE_KEY)))

    return Starlette(
        routes=[Route("/mcp", whoami, methods=["GET", "POST"])],
        middleware=[Middleware(BearerAuthMiddleware, **kwargs)],
    )


class TestNamedTokenMiddleware:
    def test_each_named_token_tags_the_request_with_its_name(self) -> None:
        client = TestClient(_app(tokens={"alice": ALICE, "bob": BOB}))
        for name, token in (("alice", ALICE), ("bob", BOB)):
            response = client.get("/mcp", headers={"Authorization": f"Bearer {token}"})
            assert (response.status_code, response.text) == (200, name)

    def test_shared_token_still_works_and_names_nobody(self) -> None:
        client = TestClient(_app(token="shared-token-9", tokens={"alice": ALICE}))
        response = client.get("/mcp", headers={"Authorization": "Bearer shared-token-9"})
        assert (response.status_code, response.text) == (200, "None")
        response = client.get("/mcp", headers={"Authorization": f"Bearer {ALICE}"})
        assert (response.status_code, response.text) == (200, "alice")

    def test_a_client_cannot_name_itself(self) -> None:
        """A client-supplied state can't be smuggled in; only the matched token names it."""
        client = TestClient(_app(tokens={"alice": ALICE}))
        response = client.get("/mcp", headers={"Authorization": "Bearer nope"})
        assert response.status_code == 401

    def test_every_token_is_compared(self) -> None:
        """No early exit: the time taken does not reveal which name matched."""
        with patch("browsercontrol.auth.hmac.compare_digest", return_value=False) as compare:
            TestClient(_app(tokens={"alice": ALICE, "bob": BOB})).get(
                "/mcp", headers={"Authorization": f"Bearer {ALICE}"}
            )
        assert compare.call_count == 2

    def test_wiring_enables_auth_with_only_named_tokens(self) -> None:
        with (
            patch.object(config, "auth_token", None),
            patch.object(config, "auth_tokens", {"alice": ALICE}),
        ):
            (middleware,) = auth_middleware()
        assert middleware.cls is BearerAuthMiddleware
        assert middleware.kwargs == {"token": None, "tokens": {"alice": ALICE}}


def _context(
    *,
    protocol: str | None = "2026-07-28",
    session_id: str = "sid-1",
    transport: str | None = None,
) -> Any:
    request_context = None if protocol is None else SimpleNamespace(protocol_version=protocol)
    fastmcp_context = SimpleNamespace(
        request_context=request_context, session_id=session_id, transport=transport
    )
    return SimpleNamespace(fastmcp_context=fastmcp_context)


def _request(name: str | None) -> Any:
    state = {} if name is None else {CLIENT_STATE_KEY: name}
    return SimpleNamespace(scope={"type": "http", "state": state})


def _no_request() -> Any:
    raise RuntimeError("No active HTTP request found.")


class TestClientKey:
    @pytest.mark.parametrize("protocol", ["2026-07-28", "2025-11-25"])
    def test_named_token_wins_on_every_protocol(self, protocol: str) -> None:
        with patch("browsercontrol.resources.get_http_request", return_value=_request("alice")):
            ctx = _context(protocol=protocol, transport="streamable-http")
            assert _client_key(ctx) == "token:alice"

    @pytest.mark.parametrize("transport", ["stdio", "streamable-http", "sse", None])
    def test_legacy_connections_use_their_session_id(self, transport: str | None) -> None:
        with patch("browsercontrol.resources.get_http_request", return_value=_request(None)):
            ctx = _context(protocol="2025-11-25", transport=transport)
            assert _client_key(ctx) == "sid-1"

    @pytest.mark.parametrize("transport", ["stdio", None])
    def test_modern_single_client_transports_use_one_fixed_key(self, transport: str | None) -> None:
        with patch("browsercontrol.resources.get_http_request", side_effect=_no_request):
            first = _client_key(_context(session_id="a", transport=transport))
            second = _client_key(_context(session_id="b", transport=transport))
        assert first == second == "process"

    @pytest.mark.parametrize("transport", ["streamable-http", "sse"])
    def test_modern_http_without_a_named_token_is_unidentified(self, transport: str) -> None:
        with patch("browsercontrol.resources.get_http_request", return_value=_request(None)):
            assert _client_key(_context(transport=transport)) == ""

    def test_no_context_is_unidentified(self) -> None:
        assert _client_key(SimpleNamespace(fastmcp_context=None)) == ""  # type: ignore[arg-type]


class TestIsolateClientsWarning:
    @pytest.mark.parametrize("transport", ["http", "sse"])
    def test_warns_without_named_tokens(
        self, transport: str, caplog: pytest.LogCaptureFixture
    ) -> None:
        from browsercontrol.server import mcp

        with (
            patch.object(config, "auth_tokens", {}),
            patch.object(config, "isolate_clients", False),  # main() sets it from argv
            patch.object(mcp, "run"),
            caplog.at_level(logging.WARNING, logger="browsercontrol"),
        ):
            main(["--transport", transport, "--isolate-clients"])
        assert "BROWSER_AUTH_TOKENS" in caplog.text

    @pytest.mark.parametrize(
        ("argv", "tokens"),
        [
            (["--transport", "http", "--isolate-clients"], {"alice": ALICE}),
            (["--transport", "http"], {}),
            (["--transport", "stdio", "--isolate-clients"], {}),
        ],
    )
    def test_silent_otherwise(
        self, argv: list[str], tokens: dict[str, str], caplog: pytest.LogCaptureFixture
    ) -> None:
        from browsercontrol.server import mcp

        with (
            patch.object(config, "auth_tokens", tokens),
            patch.object(config, "isolate_clients", False),  # main() sets it from argv
            patch.object(mcp, "run"),
            caplog.at_level(logging.WARNING, logger="browsercontrol"),
        ):
            main(argv)
        assert "BROWSER_AUTH_TOKENS" not in caplog.text
        assert ALICE not in caplog.text

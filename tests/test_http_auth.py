"""Tests for BROWSER_AUTH_TOKEN bearer authentication on the network transports."""

import logging
from unittest.mock import patch

import pytest
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from browsercontrol.__main__ import main, non_loopback_warning
from browsercontrol.auth import BearerAuthMiddleware, auth_middleware, token_matches
from browsercontrol.config import Config, config

TOKEN = "s3cret-token-value"


def _app(token: str = TOKEN) -> Starlette:
    async def hello(request: Request) -> PlainTextResponse:
        return PlainTextResponse("hello")

    return Starlette(
        routes=[Route("/mcp", hello, methods=["GET", "POST"])],
        middleware=[Middleware(BearerAuthMiddleware, token=token)],
    )


class TestConfig:
    def test_unset_means_no_auth(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("BROWSER_AUTH_TOKEN", raising=False)
        assert Config.from_env().auth_token is None

    @pytest.mark.parametrize("value", ["", "   "])
    def test_blank_means_no_auth(self, monkeypatch: pytest.MonkeyPatch, value: str) -> None:
        monkeypatch.setenv("BROWSER_AUTH_TOKEN", value)
        assert Config.from_env().auth_token is None

    def test_reads_env_and_stays_out_of_repr(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BROWSER_AUTH_TOKEN", f" {TOKEN}\n")
        cfg = Config.from_env()
        assert cfg.auth_token == TOKEN
        assert TOKEN not in repr(cfg)

    def test_there_is_no_cli_flag(self) -> None:
        from browsercontrol.__main__ import parse_args

        with pytest.raises(SystemExit):
            parse_args(["--auth-token", TOKEN])


class TestTokenMatches:
    @pytest.mark.parametrize(
        "header", [f"Bearer {TOKEN}", f"bearer {TOKEN}", f"BEARER {TOKEN}", f"Bearer  {TOKEN} "]
    )
    def test_accepts(self, header: str) -> None:
        assert token_matches(header, TOKEN)

    @pytest.mark.parametrize(
        "header",
        [
            None,
            "",
            TOKEN,
            "Bearer",
            "Bearer ",
            "Bearer wrong",
            f"Bearer {TOKEN}x",
            f"Bearer {TOKEN[:-1]}",
            f"Basic {TOKEN}",
            f"Token {TOKEN}",
            "Bearer tökén",
        ],
    )
    def test_rejects(self, header: str | None) -> None:
        assert not token_matches(header, TOKEN)

    def test_uses_constant_time_comparison(self) -> None:
        with patch("browsercontrol.auth.hmac.compare_digest", return_value=True) as compare:
            assert token_matches(f"Bearer {TOKEN}", TOKEN)
        compare.assert_called_once_with(TOKEN.encode(), TOKEN.encode())


class TestMiddleware:
    def test_valid_token_passes_through(self) -> None:
        response = TestClient(_app()).get("/mcp", headers={"Authorization": f"Bearer {TOKEN}"})
        assert (response.status_code, response.text) == (200, "hello")

    @pytest.mark.parametrize(
        "headers",
        [
            {},
            {"Authorization": "Bearer wrong"},
            {"Authorization": f"Basic {TOKEN}"},
            {"Authorization": TOKEN},
            {"X-Api-Key": TOKEN},
        ],
    )
    def test_everything_else_is_rejected(self, headers: dict[str, str]) -> None:
        response = TestClient(_app()).post("/mcp", headers=headers)
        assert response.status_code == 401
        assert response.headers["www-authenticate"].startswith("Bearer")
        assert "hello" not in response.text
        assert TOKEN not in response.text

    def test_unknown_paths_need_the_token_too(self) -> None:
        assert TestClient(_app()).get("/anything").status_code == 401

    def test_rejection_is_logged_without_the_token(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.WARNING, logger="browsercontrol.auth"):
            TestClient(_app()).get("/mcp", headers={"Authorization": "Bearer guess-1"})
        assert "Rejected" in caplog.text
        assert "guess-1" not in caplog.text and TOKEN not in caplog.text

    def test_in_front_of_the_real_mcp_app(self) -> None:
        """The stack main() builds: FastMCP's HTTP app wrapped with the configured middleware."""
        with patch.object(config, "auth_token", TOKEN):
            app = FastMCP("t").http_app(middleware=auth_middleware())
        with TestClient(app) as client:  # runs the app's lifespan, as uvicorn would
            for method in (client.get, client.post, client.delete):
                assert method("/mcp").status_code == 401
            assert client.post("/mcp", headers={"Authorization": "Bearer nope"}).status_code == 401
            # A valid token reaches FastMCP itself, which answers (not with our 401).
            reached = client.post("/mcp", headers={"Authorization": f"Bearer {TOKEN}"})
            assert reached.status_code != 401


class TestWiring:
    def test_no_middleware_without_a_token(self) -> None:
        with patch.object(config, "auth_token", None), patch.object(config, "auth_tokens", {}):
            assert auth_middleware() == []

    def test_middleware_with_a_token(self) -> None:
        with patch.object(config, "auth_token", TOKEN):
            (middleware,) = auth_middleware()
        assert middleware.cls is BearerAuthMiddleware
        assert middleware.kwargs == {"token": TOKEN, "tokens": {}}

    @pytest.mark.parametrize("transport", ["http", "sse"])
    def test_main_passes_it_to_the_server(self, transport: str) -> None:
        from browsercontrol.server import mcp

        with (
            patch.object(config, "auth_token", TOKEN),
            patch.object(mcp, "run") as run,
        ):
            main(["--transport", transport])
        assert run.call_args.kwargs["middleware"][0].cls is BearerAuthMiddleware

    def test_stdio_is_untouched(self) -> None:
        from browsercontrol.server import mcp

        with patch.object(config, "auth_token", TOKEN), patch.object(mcp, "run") as run:
            main(["--transport", "stdio"])
        run.assert_called_once_with()


class TestNonLoopbackWarning:
    def test_says_the_token_is_not_set(self) -> None:
        with patch.object(config, "auth_token", None):
            message = non_loopback_warning("0.0.0.0")
        assert "0.0.0.0" in message
        assert "BROWSER_AUTH_TOKEN is not set" in message

    def test_with_a_token_it_still_warns_about_plain_http(self) -> None:
        with patch.object(config, "auth_token", TOKEN):
            message = non_loopback_warning("0.0.0.0")
        assert "0.0.0.0" in message
        assert "not set" not in message
        assert "plain HTTP" in message
        assert TOKEN not in message

    @pytest.mark.parametrize("token", [None, TOKEN])
    def test_main_warns_off_loopback_only(
        self, caplog: pytest.LogCaptureFixture, token: str | None
    ) -> None:
        from browsercontrol.server import mcp

        with (
            patch.object(config, "auth_token", token),
            patch.object(mcp, "run"),
            caplog.at_level(logging.INFO, logger="browsercontrol"),
        ):
            main(["--transport", "http", "--host", "0.0.0.0"])
            assert "reachable from other machines" in caplog.text
            caplog.clear()
            main(["--transport", "http", "--host", "127.0.0.1"])
            assert "reachable from other machines" not in caplog.text
        assert TOKEN not in caplog.text

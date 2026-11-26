"""Tests for the navigation policy: BROWSER_ALLOWED_DOMAINS and unsafe-scheme blocking."""

from collections.abc import Iterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp import FastMCP

from browsercontrol.config import Config, config
from browsercontrol.navigation_policy import NavigationBlockedError, check_navigation_allowed
from browsercontrol.tools.batch import register_batch_tools
from browsercontrol.tools.navigation import register_navigation_tools
from browsercontrol.tools.sessions import register_session_tools
from browsercontrol.tools.tabs import register_tab_tools


@pytest.fixture
def policy() -> Iterator[None]:
    """A restrictive policy; the default config (no allowlist) is covered separately."""
    with (
        patch.object(config, "allowed_domains", ["example.com", "localhost", "10.0.0.5"]),
        patch.object(config, "allow_unsafe_schemes", False),
    ):
        yield


class TestConfig:
    def test_defaults_are_unrestricted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("BROWSER_ALLOWED_DOMAINS", raising=False)
        monkeypatch.delenv("BROWSER_ALLOW_UNSAFE_SCHEMES", raising=False)
        cfg = Config.from_env()
        assert cfg.allowed_domains == []
        assert cfg.allow_unsafe_schemes is False

    def test_reads_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BROWSER_ALLOWED_DOMAINS", " Example.com, ,docs.python.org ")
        monkeypatch.setenv("BROWSER_ALLOW_UNSAFE_SCHEMES", "TRUE")
        cfg = Config.from_env()
        assert cfg.allowed_domains == ["example.com", "docs.python.org"]
        assert cfg.allow_unsafe_schemes is True


class TestUnrestrictedByDefault:
    """With nothing configured, behaviour is unchanged for ordinary URLs."""

    @pytest.mark.parametrize(
        "url", ["https://example.com", "http://localhost:3000/x", "about:blank", "example.com"]
    )
    def test_ordinary_urls_pass(self, url: str) -> None:
        with patch.object(config, "allowed_domains", []):
            check_navigation_allowed(url)


class TestUnsafeSchemes:
    @pytest.mark.parametrize(
        "url",
        [
            "javascript:alert(1)",
            "JavaScript:alert(1)",
            "  javascript:alert(1)",
            "java\tscript:alert(1)",
            "file:///etc/passwd",
            "data:text/html,<h1>hi</h1>",
            "chrome://settings",
            "chrome-extension://abc/page.html",
            "view-source:file:///etc/passwd",
            "about:config",
        ],
    )
    def test_blocked_without_allowlist(self, url: str) -> None:
        with (
            patch.object(config, "allowed_domains", []),
            patch.object(config, "allow_unsafe_schemes", False),
        ):
            with pytest.raises(NavigationBlockedError) as err:
                check_navigation_allowed(url)
        assert "BROWSER_ALLOW_UNSAFE_SCHEMES" in str(err.value)
        assert repr(url)[1:-1] in str(err.value)

    @pytest.mark.parametrize("url", ["javascript:void(0)", "file:///tmp/x.html", "data:,hi"])
    def test_opt_in_allows_them(self, url: str) -> None:
        with (
            patch.object(config, "allowed_domains", []),
            patch.object(config, "allow_unsafe_schemes", True),
        ):
            check_navigation_allowed(url)

    def test_opt_in_does_not_bypass_the_allowlist(self, policy: None) -> None:
        with patch.object(config, "allow_unsafe_schemes", True):
            with pytest.raises(NavigationBlockedError, match="BROWSER_ALLOWED_DOMAINS"):
                check_navigation_allowed("file:///etc/passwd")

    def test_error_names_the_url(self) -> None:
        with patch.object(config, "allow_unsafe_schemes", False):
            with pytest.raises(NavigationBlockedError) as err:
                check_navigation_allowed("file:///etc/passwd")
        assert "'file:///etc/passwd'" in str(err.value)


class TestAllowedDomains:
    @pytest.mark.parametrize(
        "url",
        [
            "https://example.com",
            "https://example.com/path?q=1#x",
            "http://EXAMPLE.com:8080/",
            "https://www.example.com/",
            "https://a.b.example.com/",
            "https://example.com./",
            "http://localhost:3000/",
            "http://10.0.0.5:9000/",
            "https://user:pw@example.com/",
            "about:blank",
        ],
    )
    def test_allowed(self, policy: None, url: str) -> None:
        check_navigation_allowed(url)

    @pytest.mark.parametrize(
        "url",
        [
            "https://evil.com",
            "https://notexample.com",
            "https://example.com.evil.com/",
            "https://evil.com/example.com",
            "https://evil.com/?u=example.com",
            "https://example.com@evil.com/",
            "https://evil.com\\@example.com/",
            "https://evil.com%2f.example.com/",
            "http://1.10.0.0.5/",
            "http://10.0.0.6/",
            "example.com",
            "ftp://evil.com/",
            "http://[::1]/",
        ],
    )
    def test_blocked(self, policy: None, url: str) -> None:
        with pytest.raises(NavigationBlockedError) as err:
            check_navigation_allowed(url)
        message = str(err.value)
        assert "BROWSER_ALLOWED_DOMAINS" in message
        assert "example.com" in message  # lists what is allowed
        assert repr(url)[1:-1] in message

    def test_entries_may_be_wildcards_urls_or_ports(self) -> None:
        with patch.object(
            config, "allowed_domains", ["*.docs.test", ".wiki.test", "https://app.test:8443/x"]
        ):
            check_navigation_allowed("https://docs.test/")
            check_navigation_allowed("https://x.docs.test/")
            check_navigation_allowed("https://wiki.test/")
            check_navigation_allowed("https://app.test/")
            with pytest.raises(NavigationBlockedError):
                check_navigation_allowed("https://other.test/")

    def test_a_list_with_no_usable_entry_blocks_everything(self) -> None:
        with patch.object(config, "allowed_domains", ["http://", "a b"]):
            with pytest.raises(NavigationBlockedError, match="none valid"):
                check_navigation_allowed("https://example.com")

    def test_long_urls_are_truncated_in_the_error(self, policy: None) -> None:
        with pytest.raises(NavigationBlockedError) as err:
            check_navigation_allowed("https://evil.com/" + "a" * 5000)
        assert len(str(err.value)) < 600


@pytest.fixture
def mcp_server() -> FastMCP:
    return FastMCP("test")


class TestTools:
    """Every tool that takes a URL refuses a blocked one before touching the browser."""

    async def test_navigate_to_blocked(
        self,
        policy: None,
        mcp_server: FastMCP,
        mock_browser_manager: MagicMock,
        mock_page: MagicMock,
    ) -> None:
        register_navigation_tools(mcp_server)
        with patch("browsercontrol.tools.navigation.browser", mock_browser_manager):
            tool = await mcp_server.get_tool("navigate_to")
            with pytest.raises(RuntimeError) as err:
                await tool.fn(url="https://evil.com/")
        assert "https://evil.com/" in str(err.value)
        assert "BROWSER_ALLOWED_DOMAINS" in str(err.value)
        mock_page.goto.assert_not_called()

    async def test_navigate_to_unsafe_scheme_names_the_setting(
        self, mcp_server: FastMCP, mock_browser_manager: MagicMock, mock_page: MagicMock
    ) -> None:
        register_navigation_tools(mcp_server)
        with patch("browsercontrol.tools.navigation.browser", mock_browser_manager):
            tool = await mcp_server.get_tool("navigate_to")
            with pytest.raises(RuntimeError, match="BROWSER_ALLOW_UNSAFE_SCHEMES"):
                await tool.fn(url="file:///etc/passwd")
        mock_page.goto.assert_not_called()

    async def test_navigate_to_allowed_subdomain(
        self,
        policy: None,
        mcp_server: FastMCP,
        mock_browser_manager: MagicMock,
        mock_page: MagicMock,
    ) -> None:
        register_navigation_tools(mcp_server)
        with (
            patch("browsercontrol.tools.navigation.browser", mock_browser_manager),
            patch(
                "browsercontrol.tools.navigation.get_screenshot_with_summary",
                AsyncMock(return_value=(None, "Summary")),
            ),
        ):
            tool = await mcp_server.get_tool("navigate_to")
            text, _ = await tool.fn(url="https://docs.example.com/")
        assert "Navigated to https://docs.example.com/" in text
        mock_page.goto.assert_called_once()

    async def test_localhost_fallback_cannot_escape_the_allowlist(
        self, mcp_server: FastMCP, mock_browser_manager: MagicMock, mock_page: MagicMock
    ) -> None:
        """Allowing only 'localhost' must not let the 127.0.0.1 retry through."""
        register_navigation_tools(mcp_server)
        mock_page.goto.side_effect = Exception("ERR_CONNECTION_REFUSED")
        with (
            patch.object(config, "allowed_domains", ["localhost"]),
            patch("browsercontrol.tools.navigation.browser", mock_browser_manager),
            patch(
                "browsercontrol.tools.navigation.get_screenshot_with_summary",
                AsyncMock(return_value=(None, "Summary")),
            ),
        ):
            tool = await mcp_server.get_tool("navigate_to")
            with pytest.raises(RuntimeError, match=r"127\.0\.0\.1"):
                await tool.fn(url="http://localhost:3000")
        assert mock_page.goto.call_count == 1

    async def test_act_navigate_step(
        self,
        policy: None,
        mcp_server: FastMCP,
        mock_browser_manager: MagicMock,
        mock_page: MagicMock,
    ) -> None:
        register_batch_tools(mcp_server)
        with (
            patch("browsercontrol.tools.batch.browser", mock_browser_manager),
            patch(
                "browsercontrol.tools.batch.get_screenshot_with_summary",
                AsyncMock(return_value=(None, "Summary")),
            ),
        ):
            tool = await mcp_server.get_tool("act")
            text, _ = await tool.fn(
                steps=[
                    {"action": "navigate", "url": "https://example.com/"},
                    {"action": "navigate", "url": "https://evil.com/"},
                    {"action": "navigate", "url": "https://example.com/never-reached"},
                ]
            )
        assert "1. ok: navigated to https://example.com/" in text
        assert "2. FAILED (navigate)" in text
        assert "https://evil.com/" in text and "BROWSER_ALLOWED_DOMAINS" in text
        assert "remaining step(s) skipped" in text
        assert mock_page.goto.call_count == 1

    async def test_create_tab_blocked_opens_no_tab(
        self, policy: None, mcp_server: FastMCP, mock_browser_manager: MagicMock
    ) -> None:
        register_tab_tools(mcp_server)
        with patch("browsercontrol.tools.tabs.browser", mock_browser_manager):
            tool = await mcp_server.get_tool("create_tab")
            with pytest.raises(RuntimeError, match="BROWSER_ALLOW_UNSAFE_SCHEMES"):
                await tool.fn(url="javascript:alert(1)")
            with pytest.raises(RuntimeError, match=r"https://evil\.com/"):
                await tool.fn(url="https://evil.com/")
        mock_browser_manager.create_tab.assert_not_awaited()

    async def test_create_tab_without_url_is_not_restricted(
        self, policy: None, mcp_server: FastMCP, mock_browser_manager: MagicMock
    ) -> None:
        register_tab_tools(mcp_server)
        with (
            patch("browsercontrol.tools.tabs.browser", mock_browser_manager),
            patch(
                "browsercontrol.tools.tabs.get_screenshot_with_summary",
                AsyncMock(return_value=(None, "Summary")),
            ),
        ):
            tool = await mcp_server.get_tool("create_tab")
            await tool.fn()
        mock_browser_manager.create_tab.assert_awaited_once_with(None)

    async def test_create_session_blocked_creates_no_session(
        self, policy: None, mcp_server: FastMCP, mock_browser_manager: MagicMock
    ) -> None:
        register_session_tools(mcp_server)
        mock_browser_manager.create_session = AsyncMock()
        with patch("browsercontrol.tools.sessions.browser", mock_browser_manager):
            tool = await mcp_server.get_tool("create_session")
            with pytest.raises(RuntimeError, match="BROWSER_ALLOWED_DOMAINS"):
                await tool.fn(name="s", url="https://evil.com/")
        mock_browser_manager.create_session.assert_not_awaited()

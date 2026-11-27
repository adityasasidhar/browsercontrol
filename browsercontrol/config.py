import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# A client name from BROWSER_AUTH_TOKENS. Kept short and plain: it shows up in logs.
_CLIENT_NAME = re.compile(r"[A-Za-z0-9_.-]{1,64}")


def parse_auth_tokens(raw: str) -> dict[str, str]:
    """Parse ``BROWSER_AUTH_TOKENS`` (``name:token,name:token``) into ``{name: token}``.

    Malformed entries, repeated names and repeated tokens are skipped with a warning that
    names the entry's position but never the token, so a typo fails closed (that client is
    rejected) instead of leaking a secret into the log.
    """
    tokens: dict[str, str] = {}
    for position, entry in enumerate((e.strip() for e in raw.split(",")), start=1):
        if not entry:
            continue
        name, _, token = entry.partition(":")
        name, token = name.strip(), token.strip()
        if not _CLIENT_NAME.fullmatch(name) or not token:
            problem = "is not name:token with a name of letters, digits, '.', '_' or '-'"
        elif name in tokens:
            problem = f"repeats the client name {name!r}"
        elif token in tokens.values():
            problem = "repeats a token already given to another client"
        else:
            tokens[name] = token
            continue
        logger.warning("Ignoring BROWSER_AUTH_TOKENS entry %d: it %s.", position, problem)
    return tokens


@dataclass
class Config:
    """Browser control configuration."""

    # Browser settings
    headless: bool = False
    viewport_width: int = 1280
    viewport_height: int = 720
    timeout_ms: int = 30000

    # Paths
    user_data_dir: Path = Path.home() / ".browsercontrol" / "user_data"
    extension_path: Path | None = None
    recordings_dir: Path = Path.home() / ".browsercontrol" / "recordings"
    snapshots_dir: Path = Path.home() / ".browsercontrol" / "snapshots"

    downloads_dir: Path = Path.home() / ".browsercontrol" / "downloads"
    generated_tests_dir: Path = Path.home() / ".browsercontrol" / "generated_tests"
    # Saved login state (cookies + storage) from save_auth_state. Holds secrets.
    auth_dir: Path = Path.home() / ".browsercontrol" / "auth"

    # Attach to an already running Chrome (e.g. http://localhost:9222) instead of
    # launching one, so the agent uses that browser's logged-in sessions.
    cdp_url: str | None = None

    # Upper bound for the post-action settle (load, network quiet, DOM quiet).
    settle_timeout_ms: int = 3000

    # Give every MCP client its own isolated browser context automatically.
    isolate_clients: bool = False

    # MCP transport: "stdio" (default), "http" (Streamable HTTP) or "sse".
    transport: str = "stdio"
    host: str = "127.0.0.1"
    port: int = 8000

    # Chromium binary to drive. Left unset, Playwright uses its own bundled
    # build; set it when Playwright ships no build for the host platform.
    executable_path: Path | None = None

    # Bearer token required on the http and sse transports. Unset means no authentication.
    # Env only (never a flag), so it stays out of process lists; hidden from repr.
    auth_token: str | None = field(default=None, repr=False)
    # Named bearer tokens, one per client ({name: token}). The name identifies the client,
    # which is how isolate_clients tells HTTP clients apart on the session-less protocol.
    auth_tokens: dict[str, str] = field(default_factory=dict, repr=False)

    # Navigation policy (see navigation_policy.py). Domains (and their subdomains) that
    # navigation tools may open; empty means no restriction.
    allowed_domains: list[str] = field(default_factory=list)
    # Lift the block on javascript:, file:, data:, chrome: and similar URLs.
    allow_unsafe_schemes: bool = False

    # Logging
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        config = cls()

        # Browser settings
        if os.getenv("BROWSER_HEADLESS"):
            config.headless = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"

        if os.getenv("BROWSER_VIEWPORT_WIDTH"):
            config.viewport_width = int(os.getenv("BROWSER_VIEWPORT_WIDTH", "1280"))

        if os.getenv("BROWSER_VIEWPORT_HEIGHT"):
            config.viewport_height = int(os.getenv("BROWSER_VIEWPORT_HEIGHT", "720"))

        if os.getenv("BROWSER_TIMEOUT"):
            config.timeout_ms = int(os.getenv("BROWSER_TIMEOUT", "30000"))

        # Paths
        user_data_dir = os.getenv("BROWSER_USER_DATA_DIR")
        if user_data_dir:
            config.user_data_dir = Path(user_data_dir)

        extension_path = os.getenv("BROWSER_EXTENSION_PATH")
        if extension_path:
            config.extension_path = Path(extension_path)

        executable_path = os.getenv("BROWSER_EXECUTABLE_PATH")
        if executable_path:
            config.executable_path = Path(executable_path)

        config.cdp_url = os.getenv("BROWSER_CDP_URL") or None

        if os.getenv("BROWSER_SETTLE_TIMEOUT"):
            config.settle_timeout_ms = int(os.getenv("BROWSER_SETTLE_TIMEOUT", "3000"))

        config.isolate_clients = os.getenv("BROWSER_ISOLATE_CLIENTS", "").lower() == "true"
        config.transport = os.getenv("BROWSER_TRANSPORT", config.transport).lower()
        config.host = os.getenv("BROWSER_HOST", config.host)
        if os.getenv("BROWSER_PORT"):
            config.port = int(os.getenv("BROWSER_PORT", "8000"))

        # Recordings and snapshots sit beside the profile unless overridden, so
        # pointing BROWSER_USER_DATA_DIR elsewhere keeps them together.
        recordings_dir = os.getenv("BROWSER_RECORDINGS_DIR")
        config.recordings_dir = (
            Path(recordings_dir) if recordings_dir else config.user_data_dir.parent / "recordings"
        )

        snapshots_dir = os.getenv("BROWSER_SNAPSHOTS_DIR")
        config.snapshots_dir = (
            Path(snapshots_dir) if snapshots_dir else config.user_data_dir.parent / "snapshots"
        )

        downloads_dir = os.getenv("BROWSER_DOWNLOADS_DIR")
        config.downloads_dir = (
            Path(downloads_dir) if downloads_dir else config.user_data_dir.parent / "downloads"
        )

        tests_dir = os.getenv("BROWSER_GENERATED_TESTS_DIR")
        config.generated_tests_dir = (
            Path(tests_dir) if tests_dir else config.user_data_dir.parent / "generated_tests"
        )

        auth_dir = os.getenv("BROWSER_AUTH_DIR")
        config.auth_dir = Path(auth_dir) if auth_dir else config.user_data_dir.parent / "auth"

        config.auth_token = os.getenv("BROWSER_AUTH_TOKEN", "").strip() or None
        config.auth_tokens = parse_auth_tokens(os.getenv("BROWSER_AUTH_TOKENS", ""))
        config.allowed_domains = [
            d.strip().lower()
            for d in os.getenv("BROWSER_ALLOWED_DOMAINS", "").split(",")
            if d.strip()
        ]
        config.allow_unsafe_schemes = (
            os.getenv("BROWSER_ALLOW_UNSAFE_SCHEMES", "").lower() == "true"
        )

        # Logging
        config.log_level = os.getenv("LOG_LEVEL", "INFO")

        return config


# Global configuration instance
config = Config.from_env()

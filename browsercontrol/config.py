import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Browser control configuration."""

    # Browser settings
    headless: bool = True
    viewport_width: int = 1280
    viewport_height: int = 720
    timeout_ms: int = 30000

    # Paths
    user_data_dir: Path = Path.home() / ".browsercontrol" / "user_data"
    extension_path: Path | None = None
    recordings_dir: Path = Path.home() / ".browsercontrol" / "recordings"
    snapshots_dir: Path = Path.home() / ".browsercontrol" / "snapshots"

    # Chromium binary to drive. Left unset, Playwright uses its own bundled
    # build; set it when Playwright ships no build for the host platform.
    executable_path: Path | None = None

    # Logging
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        config = cls()

        # Browser settings
        if os.getenv("BROWSER_HEADLESS"):
            config.headless = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"

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

        # Logging
        config.log_level = os.getenv("LOG_LEVEL", "INFO")

        return config


# Global configuration instance
config = Config.from_env()

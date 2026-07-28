"""Tests for environment-driven configuration."""

from pathlib import Path

import pytest

from browsercontrol.config import Config


class TestPathConfig:
    """Path settings resolved from the environment."""

    def test_recordings_and_snapshots_follow_the_profile_by_default(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Unset, both sit beside the profile dir — not beside the default home dir."""
        monkeypatch.delenv("BROWSER_RECORDINGS_DIR", raising=False)
        monkeypatch.delenv("BROWSER_SNAPSHOTS_DIR", raising=False)
        monkeypatch.setenv("BROWSER_USER_DATA_DIR", "/custom/place/profile")

        config = Config.from_env()

        assert config.recordings_dir == Path("/custom/place/recordings")
        assert config.snapshots_dir == Path("/custom/place/snapshots")

    def test_recordings_and_snapshots_are_overridable(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("BROWSER_RECORDINGS_DIR", "/traces")
        monkeypatch.setenv("BROWSER_SNAPSHOTS_DIR", "/shots")

        config = Config.from_env()

        assert config.recordings_dir == Path("/traces")
        assert config.snapshots_dir == Path("/shots")

    def test_executable_path_defaults_to_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Unset means 'let Playwright pick its bundled build'."""
        monkeypatch.delenv("BROWSER_EXECUTABLE_PATH", raising=False)

        assert Config.from_env().executable_path is None

    def test_executable_path_is_read_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BROWSER_EXECUTABLE_PATH", "/usr/bin/google-chrome")

        assert Config.from_env().executable_path == Path("/usr/bin/google-chrome")

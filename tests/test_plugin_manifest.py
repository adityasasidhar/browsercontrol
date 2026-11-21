"""Keep the plugin manifests in step with the Python package."""

import json
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


def _load(name: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((ROOT / ".claude-plugin" / name).read_text())
    return data


def test_plugin_version_matches_pyproject() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    plugin = _load("plugin.json")
    entry = next(p for p in _load("marketplace.json")["plugins"] if p["name"] == plugin["name"])
    assert plugin["version"] == project["version"]
    assert entry["version"] == project["version"]
    codex = json.loads((ROOT / "plugin.json").read_text())
    assert codex["name"] == entry["name"]
    assert codex["version"] == project["version"]


def test_plugin_runs_bundled_source() -> None:
    server = _load("plugin.json")["mcpServers"]["browsercontrol"]
    assert server["command"] == "uvx"
    assert server["args"] == ["--from", "${CLAUDE_PLUGIN_ROOT}", "browsercontrol"]


def test_plugin_paths_exist() -> None:
    plugin = _load("plugin.json")
    assert (ROOT / plugin["icon"]).is_file()
    assert (ROOT / "skills" / "browsercontrol" / "SKILL.md").is_file()

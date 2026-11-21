"""The package version is declared once in pyproject.toml; everything else must agree."""

import json
import tomllib
from pathlib import Path

import pytest

import browsercontrol

ROOT = Path(__file__).resolve().parent.parent


def _project_version() -> str:
    with open(ROOT / "pyproject.toml", "rb") as f:
        return str(tomllib.load(f)["project"]["version"])


def test_package_version_matches_pyproject() -> None:
    assert browsercontrol.__version__ == _project_version()


@pytest.mark.parametrize("manifest", ["plugin.json", "package.json", ".claude-plugin/plugin.json"])
def test_plugin_manifest_version_matches_pyproject(manifest: str) -> None:
    data = json.loads((ROOT / manifest).read_text(encoding="utf-8"))
    assert data["version"] == _project_version(), f"bump the version in {manifest}"


def test_marketplace_version_matches_pyproject() -> None:
    data = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    versions = {p["name"]: p["version"] for p in data["plugins"]}
    assert versions["browsercontrol"] == _project_version(), (
        "bump the version in .claude-plugin/marketplace.json"
    )


def test_mcp_registry_server_json_matches_pyproject() -> None:
    data = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    assert data["version"] == _project_version(), "bump the version in server.json"
    pypi = [p for p in data["packages"] if p["registryType"] == "pypi"]
    assert [p["version"] for p in pypi] == [_project_version()], (
        "bump the pypi package version in server.json"
    )


def test_readme_carries_mcp_registry_ownership_marker() -> None:
    # The MCP Registry verifies PyPI ownership by finding this line in the package README.
    name = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))["name"]
    assert f"mcp-name: {name}" in (ROOT / "README.md").read_text(encoding="utf-8")

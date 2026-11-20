"""Keep the docs site in sync with the registered tools.

docs/public/tools.json feeds the site's tool explorer and is published for
agents, and docs/reference/*.md is the hand-written reference. Both drift
silently when a tool or parameter changes, so these tests catch it.
"""

import importlib.util
import re
from pathlib import Path
from types import ModuleType

import pytest

from browsercontrol.server import mcp

ROOT = Path(__file__).resolve().parent.parent
REFERENCE = ROOT / "docs" / "reference"


def _load_generator() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "gen_tools_json", ROOT / "scripts" / "gen_tools_json.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_tools_json_is_current() -> None:
    generator = _load_generator()
    assert generator.OUTPUT.read_text(encoding="utf-8") == generator.render(), (
        "docs/public/tools.json is stale; run: uv run python scripts/gen_tools_json.py"
    )


def _section(page: str, tool: str) -> str | None:
    """The reference text for one tool: from its heading to the next H2."""
    text = (REFERENCE / f"{page}.md").read_text(encoding="utf-8")
    match = re.search(rf"^## .*\{{#{tool}\}}\s*$(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else None


@pytest.mark.asyncio
async def test_every_tool_and_parameter_is_documented() -> None:
    generator = _load_generator()
    problems = []
    for tool in await mcp.list_tools():
        module = tool.fn.__module__.rsplit(".", 1)[-1]  # type: ignore[attr-defined]
        page, _ = generator.CATEGORIES[module]
        section = _section(page, tool.name)
        if section is None:
            problems.append(f"docs/reference/{page}.md has no '## `{tool.name}` {{#{tool.name}}}'")
            continue
        for param in tool.parameters.get("properties", {}):
            if f"`{param}`" not in section:
                problems.append(f"docs/reference/{page}.md#{tool.name} does not mention `{param}`")
    assert not problems, "\n".join(problems)

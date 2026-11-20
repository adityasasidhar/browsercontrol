"""Keep the hand-written server `instructions` in sync with the registered tools.

The instructions string is the only tool overview MCP clients receive, so a tool
missing from it is effectively invisible to agents.
"""

import re

import pytest

from browsercontrol.server import mcp

LISTED_TOOL = re.compile(r"^- (\w+)\(([^)]*)\)", re.MULTILINE)


def _listed_tools() -> dict[str, list[str]]:
    assert mcp.instructions is not None
    return {
        name: [arg.strip() for arg in args.split(",") if arg.strip()]
        for name, args in LISTED_TOOL.findall(mcp.instructions)
    }


@pytest.mark.asyncio
async def test_every_registered_tool_is_listed_in_instructions() -> None:
    registered = {tool.name for tool in await mcp.list_tools()}
    listed = set(_listed_tools())

    assert registered - listed == set(), "add these tools to the instructions in server.py"
    assert listed - registered == set(), "remove stale tools from the instructions in server.py"


@pytest.mark.asyncio
async def test_listed_parameters_match_tool_signatures() -> None:
    listed = _listed_tools()
    mismatches = {
        tool.name: (list(tool.parameters.get("properties", {})), listed[tool.name])
        for tool in await mcp.list_tools()
        if tool.name in listed and list(tool.parameters.get("properties", {})) != listed[tool.name]
    }

    assert not mismatches, f"(actual, listed) parameters differ: {mismatches}"

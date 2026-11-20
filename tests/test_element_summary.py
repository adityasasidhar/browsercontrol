"""Tests for the element summary returned alongside every annotated screenshot."""

import ast
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from browsercontrol.tools._summary import (
    MAX_SUMMARY_ELEMENTS,
    format_element_summary,
    get_screenshot_with_summary,
)

ELEMENT_MAP = {
    1: {"tag": "button", "type": "submit", "text": "Click Me"},
    2: {"tag": "input", "type": "text", "text": "plain text input"},
    3: {"tag": "input", "type": "checkbox", "text": ""},
    4: {"tag": "input", "type": "radio", "text": ""},
    5: {"tag": "input", "type": "file", "text": ""},
    6: {"tag": "select", "type": "select-one", "text": "Alpha\nBeta\nGamma"},
    7: {"tag": "a", "type": "a", "text": "Products"},
}

TOOLS_DIR = Path(__file__).resolve().parent.parent / "browsercontrol" / "tools"


def test_input_types_are_distinguishable() -> None:
    """Checkbox, radio and file inputs must not all render as a bare 'input'."""
    summary = format_element_summary(ELEMENT_MAP)

    assert "[3] input[checkbox]" in summary
    assert "[4] input[radio]" in summary
    assert "[5] input[file]" in summary
    assert "[2] input[text] - plain text input" in summary


def test_one_line_per_element() -> None:
    """Multi-line text (e.g. a <select>'s options) must not break the format."""
    summary = format_element_summary(ELEMENT_MAP)

    # 7 elements + the "Found N" header, and nothing wrapping onto extra lines.
    assert len(summary.splitlines()) == len(ELEMENT_MAP) + 1
    assert "[6] select[select-one] - Alpha Beta Gamma" in summary


def test_redundant_type_is_omitted() -> None:
    """When type adds nothing over the tag, don't repeat it."""
    assert "[7] a - Products" in format_element_summary(ELEMENT_MAP)


def test_long_maps_are_truncated() -> None:
    elem_map = {i: {"tag": "button", "text": f"b{i}"} for i in range(1, 46)}
    lines = format_element_summary(elem_map).splitlines()

    assert lines[0] == "Found 45 interactive elements:"
    assert len(lines) == MAX_SUMMARY_ELEMENTS + 2
    assert lines[-1] == "  ... and 15 more"


@pytest.mark.asyncio
async def test_get_screenshot_with_summary_uses_given_manager() -> None:
    manager = MagicMock()
    manager.screenshot_with_som = AsyncMock(return_value=(b"png", ELEMENT_MAP))

    image, summary = await get_screenshot_with_summary(manager)

    manager.screenshot_with_som.assert_awaited_once()
    assert image.data == b"png"
    assert summary == format_element_summary(ELEMENT_MAP)


def test_no_tool_module_redefines_the_helper() -> None:
    """Guard against the summary helper being copy-pasted back into a tool module."""
    offenders = []
    for path in TOOLS_DIR.glob("*.py"):
        if path.name == "_summary.py":
            continue
        for node in ast.parse(path.read_text()).body:
            if isinstance(node, ast.AsyncFunctionDef | ast.FunctionDef) and "summary" in node.name:
                offenders.append(f"{path.name}:{node.name}")

    assert not offenders, f"use browsercontrol.tools._summary instead: {offenders}"

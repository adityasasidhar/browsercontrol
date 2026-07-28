"""Tests for the element summary shared by every tool module.

`_get_screenshot_with_summary` is duplicated across the tool modules, so these
tests pin the format in all of them at once to stop the copies drifting apart.
"""

from unittest.mock import AsyncMock, patch

import pytest

from browsercontrol.tools.content import _get_screenshot_with_summary as content_summary
from browsercontrol.tools.devtools import _get_screenshot_with_summary as devtools_summary
from browsercontrol.tools.forms import _get_screenshot_with_summary as forms_summary
from browsercontrol.tools.interaction import _get_screenshot_with_summary as interaction_summary
from browsercontrol.tools.navigation import _get_screenshot_with_summary as navigation_summary

ALL_SUMMARIES = [
    ("forms", forms_summary),
    ("navigation", navigation_summary),
    ("content", content_summary),
    ("interaction", interaction_summary),
    ("devtools", devtools_summary),
]

ELEMENT_MAP = {
    1: {"tag": "button", "type": "submit", "text": "Click Me"},
    2: {"tag": "input", "type": "text", "text": "plain text input"},
    3: {"tag": "input", "type": "checkbox", "text": ""},
    4: {"tag": "input", "type": "radio", "text": ""},
    5: {"tag": "input", "type": "file", "text": ""},
    6: {"tag": "select", "type": "select-one", "text": "Alpha\nBeta\nGamma"},
    7: {"tag": "a", "type": "a", "text": "Products"},
}


async def _run(module_name, summary_fn):
    with patch(f"browsercontrol.tools.{module_name}.browser") as mock_browser:
        mock_browser.screenshot_with_som = AsyncMock(return_value=(b"png", ELEMENT_MAP))
        _image, summary = await summary_fn()
        return summary


@pytest.mark.parametrize(("module_name", "summary_fn"), ALL_SUMMARIES)
@pytest.mark.asyncio
async def test_input_types_are_distinguishable(module_name, summary_fn):
    """Checkbox, radio and file inputs must not all render as a bare 'input'."""
    summary = await _run(module_name, summary_fn)

    assert "[3] input[checkbox]" in summary
    assert "[4] input[radio]" in summary
    assert "[5] input[file]" in summary
    assert "[2] input[text] - plain text input" in summary


@pytest.mark.parametrize(("module_name", "summary_fn"), ALL_SUMMARIES)
@pytest.mark.asyncio
async def test_one_line_per_element(module_name, summary_fn):
    """Multi-line text (e.g. a <select>'s options) must not break the format."""
    summary = await _run(module_name, summary_fn)

    # 7 elements + the "Found N" header, and nothing wrapping onto extra lines.
    assert len(summary.splitlines()) == len(ELEMENT_MAP) + 1
    assert "[6] select[select-one] - Alpha Beta Gamma" in summary


@pytest.mark.parametrize(("module_name", "summary_fn"), ALL_SUMMARIES)
@pytest.mark.asyncio
async def test_redundant_type_is_omitted(module_name, summary_fn):
    """When type adds nothing over the tag, don't repeat it."""
    summary = await _run(module_name, summary_fn)

    assert "[7] a - Products" in summary


@pytest.mark.asyncio
async def test_all_modules_agree():
    """Every duplicated copy must produce byte-identical output."""
    outputs = {name: await _run(name, fn) for name, fn in ALL_SUMMARIES}

    assert len(set(outputs.values())) == 1, f"summary helpers have drifted: {outputs}"

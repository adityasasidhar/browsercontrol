"""Generate docs/public/tools.json from the registered MCP tools.

The docs site's tool explorer reads this file, and it is published at
``/tools.json`` so agents can fetch a machine-readable catalog of every tool.
``tests/test_docs.py`` fails when it is out of date.

Usage:
    uv run python scripts/gen_tools_json.py          # write the file
    uv run python scripts/gen_tools_json.py --check  # exit 1 if stale
"""

from __future__ import annotations

import argparse
import asyncio
import inspect
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "docs" / "public" / "tools.json"

# Tool module -> (reference page slug, category label). Order sets display order.
CATEGORIES: dict[str, tuple[str, str]] = {
    "navigation": ("navigation", "Navigation"),
    "search": ("navigation", "Navigation"),
    "interaction": ("interaction", "Interaction"),
    "batch": ("interaction", "Interaction"),
    "waiting": ("waiting", "Waiting & dialogs"),
    "forms": ("forms", "Forms"),
    "content": ("content", "Content"),
    "extract": ("extraction", "Extraction"),
    "tabs": ("tabs", "Tabs"),
    "sessions": ("sessions", "Sessions"),
    "devtools": ("devtools", "DevTools"),
    "network": ("network", "Network"),
    "emulate": ("emulation", "Emulation"),
    "recording": ("recording", "Recording"),
}
PAGE_ORDER = list(dict.fromkeys(slug for slug, _ in CATEGORIES.values()))


def _summary(doc: str) -> tuple[str, str]:
    """Split a docstring into its first paragraph and the prose before Args/Returns."""
    text = inspect.cleandoc(doc or "")
    body = re.split(r"\n\s*(Args|Returns|Raises):\s*\n", text)[0].strip()
    paragraphs = [" ".join(p.split()) for p in body.split("\n\n") if p.strip()]
    if not paragraphs:
        return "", ""
    return paragraphs[0], "\n\n".join(paragraphs[1:])


def _type_name(annotation: Any) -> str:
    if annotation is inspect.Parameter.empty:
        return "Any"
    text = annotation if isinstance(annotation, str) else inspect.formatannotation(annotation)
    return text.replace("typing.", "").replace("NoneType", "None")


def _signature(name: str, fn: Any) -> str:
    sig = inspect.signature(fn)
    parts = []
    for p in sig.parameters.values():
        piece = f"{p.name}: {_type_name(p.annotation)}"
        if p.default is not inspect.Parameter.empty:
            piece += f" = {p.default!r}"
        parts.append(piece)
    return f"{name}({', '.join(parts)})"


def _returns(fn: Any) -> str:
    ann = _type_name(inspect.signature(fn).return_annotation)
    return "text + screenshot" if "Image" in ann else "text"


async def build() -> dict[str, Any]:
    from browsercontrol.server import mcp

    tools: list[dict[str, Any]] = []
    for tool in await mcp.list_tools():
        fn = tool.fn  # type: ignore[attr-defined]
        module = fn.__module__.rsplit(".", 1)[-1]
        slug, label = CATEGORIES[module]
        summary, details = _summary(fn.__doc__ or tool.description or "")
        sig = inspect.signature(fn)
        props = tool.parameters.get("properties", {})
        required = set(tool.parameters.get("required", []))
        params = []
        for pname, p in sig.parameters.items():
            default = None if p.default is inspect.Parameter.empty else p.default
            params.append(
                {
                    "name": pname,
                    "type": _type_name(p.annotation),
                    "required": pname in required,
                    "default": default,
                    "description": props.get(pname, {}).get("description", ""),
                }
            )
        tools.append(
            {
                "name": tool.name,
                "category": label,
                "page": slug,
                "url": f"/reference/{slug}#{tool.name}",
                "signature": _signature(tool.name, fn),
                "returns": _returns(fn),
                "summary": summary,
                "details": details,
                "params": params,
            }
        )
    tools.sort(key=lambda t: (PAGE_ORDER.index(t["page"]), t["name"]))
    return {
        "name": "BrowserControl",
        "description": "MCP tools exposed by the BrowserControl server.",
        "count": len(tools),
        "tools": tools,
    }


def render() -> str:
    return json.dumps(asyncio.run(build()), indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit 1 if the file is stale")
    args = parser.parse_args()
    content = render()
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != content:
            print(f"{OUTPUT.relative_to(ROOT)} is stale; run scripts/gen_tools_json.py")
            return 1
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

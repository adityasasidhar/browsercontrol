"""Set of Marks rendering: the numbered boxes drawn over a screenshot.

Pure image work with no browser state, kept out of ``browser.py`` so the manager only decides
*which* elements get a mark and owns the resulting element map.
"""

import logging
from io import BytesIO
from typing import Any

from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont

from browsercontrol.elements import ElementMap

logger = logging.getLogger(__name__)

# Module-level cached font (loaded once, reused across screenshots)
_cached_font: ImageFont.FreeTypeFont | ImageFont.ImageFont | None = None


def _get_label_font() -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load and cache the label font for SoM overlays (loaded once per process)."""
    global _cached_font
    if _cached_font is not None:
        return _cached_font
    font_names = [
        "Arial.ttf",
        "arial.ttf",  # Windows/macOS
        "Helvetica.ttf",
        "helvetica.ttf",  # macOS
        "DejaVuSans-Bold.ttf",  # Linux
        "FreeSansBold.ttf",  # Linux
        "LiberationSans-Bold.ttf",  # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux specific path
        "/System/Library/Fonts/Helvetica.ttc",  # macOS specific path
    ]
    for font_name in font_names:
        try:
            _cached_font = ImageFont.truetype(font_name, 14)
            return _cached_font
        except OSError:
            continue
    _cached_font = ImageFont.load_default()
    return _cached_font


def _draw_mark(
    draw: ImageDraw.ImageDraw,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    element_id: int,
    elem: dict[str, Any],
) -> None:
    """Draw one numbered box. Disabled elements are drawn grey instead of red."""
    x, y = max(0.0, elem["x"]), max(0.0, elem["y"])
    x2, y2 = elem["x"] + elem["width"], elem["y"] + elem["height"]
    color = (128, 128, 128) if elem.get("disabled") else (255, 0, 0)

    draw.rectangle([x, y, x2, y2], outline=color, width=2, fill=(*color, 60))

    label = str(element_id)
    label_bbox = draw.textbbox((0, 0), label, font=font)
    label_w = label_bbox[2] - label_bbox[0] + 6
    label_h = label_bbox[3] - label_bbox[1] + 4
    label_y = max(0.0, y - label_h - 2)

    draw.rectangle([x, label_y, x + label_w, label_y + label_h], fill=color)
    draw.text((x + 3, label_y + 2), label, fill="white", font=font)


def annotate(screenshot: bytes, elements: list[dict[str, Any]]) -> tuple[bytes, ElementMap]:
    """Draw a numbered box for each element on a PNG screenshot.

    Returns the annotated PNG and the element map: 1-indexed IDs in the order given.
    """
    img = PILImage.open(BytesIO(screenshot))
    draw = ImageDraw.Draw(img, "RGBA")
    font = _get_label_font()

    element_map: ElementMap = {}
    for idx, elem in enumerate(elements):
        element_id = idx + 1
        element_map[element_id] = elem
        _draw_mark(draw, font, element_id, elem)

    output = BytesIO()
    img.save(output, format="PNG")
    return output.getvalue(), element_map

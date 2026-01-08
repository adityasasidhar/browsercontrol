"""Browser control tools package."""

from browsercontrol.tools.navigation import register_navigation_tools
from browsercontrol.tools.interaction import register_interaction_tools
from browsercontrol.tools.forms import register_form_tools
from browsercontrol.tools.content import register_content_tools
from browsercontrol.tools.devtools import register_devtools
from browsercontrol.tools.recording import register_recording_tools

__all__ = [
    "register_navigation_tools",
    "register_interaction_tools",
    "register_form_tools",
    "register_content_tools",
    "register_devtools",
    "register_recording_tools",
]

"""Browser control tools package."""

from browsercontrol.tools.assertions import register_assertion_tools
from browsercontrol.tools.batch import register_batch_tools
from browsercontrol.tools.content import register_content_tools
from browsercontrol.tools.devtools import register_devtools
from browsercontrol.tools.emulate import register_emulation_tools
from browsercontrol.tools.extract import register_extract_tools
from browsercontrol.tools.forms import register_form_tools
from browsercontrol.tools.interaction import register_interaction_tools
from browsercontrol.tools.navigation import register_navigation_tools
from browsercontrol.tools.network import register_network_tools
from browsercontrol.tools.recording import register_recording_tools
from browsercontrol.tools.search import register_search_tools
from browsercontrol.tools.sessions import register_session_tools
from browsercontrol.tools.tabs import register_tab_tools
from browsercontrol.tools.waiting import register_waiting_tools

__all__ = [
    "register_assertion_tools",
    "register_batch_tools",
    "register_content_tools",
    "register_devtools",
    "register_emulation_tools",
    "register_extract_tools",
    "register_form_tools",
    "register_interaction_tools",
    "register_navigation_tools",
    "register_network_tools",
    "register_recording_tools",
    "register_search_tools",
    "register_session_tools",
    "register_tab_tools",
    "register_waiting_tools",
]

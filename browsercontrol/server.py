import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastmcp import FastMCP

from browsercontrol.browser import browser
from browsercontrol.config import config
from browsercontrol.resources import SessionBindingMiddleware, register_resources
from browsercontrol.tools import (
    register_batch_tools,
    register_content_tools,
    register_devtools,
    register_emulation_tools,
    register_extract_tools,
    register_form_tools,
    register_interaction_tools,
    register_navigation_tools,
    register_network_tools,
    register_recording_tools,
    register_search_tools,
    register_session_tools,
    register_tab_tools,
    register_waiting_tools,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastMCP) -> AsyncGenerator[None, None]:
    """Manage browser lifecycle with the MCP server."""
    logger.info("Starting Browser Control MCP server")
    try:
        await browser.start()
        yield
    except Exception as e:
        logger.error(f"Failed to start browser: {e}")
        raise
    finally:
        logger.info("Shutting down Browser Control MCP server")
        await browser.stop()


# Create the MCP server
mcp = FastMCP(
    "BrowserControl",
    instructions="""Full-featured browser automation for AI agents.

Features:
- Set of Marks (SoM): Screenshots show numbered interactive elements.
- find(): Search the whole page, off-screen content included, and scroll to it.
- act(): Batch several steps into one call with one screenshot.
- Developer Tools: Console logs, network requests with headers and bodies, errors.
- Network Control: Mock or block requests, wait for responses, export HAR.
- Emulation: Devices, geolocation, timezone, dark mode, network throttling.
- Extraction: Tables, links, and schema-driven JSON.
- Session Recording: Traces, snapshots, and export of the session as a Playwright test.
- Sessions: Persistent logged-in profile, isolated sessions, or your own Chrome over CDP.
- JS dialogs and downloads are handled automatically and reported in the next result.

Element IDs come from the most recent annotated screenshot and are
invalidated by any navigation, click, scroll, or new screenshot. Always act on
the numbers in the latest image. Text after "Notice:" reports dialogs and
downloads that happened during the last action.

Navigation:
- navigate_to(url)
- go_back()
- go_forward()
- refresh_page()
- scroll(direction, amount)
- find(query, role, nth)

Interaction:
- click(element_id)
- double_click(element_id)
- right_click(element_id)
- click_at(x, y)
- type_text(element_id, text)
- press_key(key)
- hover(element_id)
- drag(source_id, target_id)
- scroll_to_element(element_id)
- wait(seconds)
- act(steps, stop_on_error)

Waiting, Dialogs and Downloads:
- wait_for(text, selector, state, network_idle, timeout_seconds)
- handle_dialog(accept, prompt_text)
- list_downloads()

Forms:
- select_option(element_id, option)
- check_checkbox(element_id, check)
- upload_file(element_id, file_path)

Page Content:
- get_page_content()
- get_text(element_id)
- get_page_info()
- run_javascript(script)
- screenshot(annotate, full_page)

Extraction:
- extract_table(element_id, index, output_format)
- extract_links(contains, limit)
- extract(schema)

Tab Management:
- create_tab(url)
- switch_tab(index)
- close_tab(index)
- list_tabs()

Sessions:
- create_session(name, device, url)
- switch_session(name)
- list_sessions()
- close_session(name)
- connect_to_chrome(cdp_url)
- disconnect_chrome()

Developer Tools:
- get_console_logs(clear)
- get_network_requests(num_requests, clear)
- get_request_details(request_id, include_body)
- get_page_errors()
- run_in_console(code)
- inspect_element(element_id)
- get_page_performance()
- get_cookies()
- set_cookie(name, value, domain, path)
- delete_cookie(name)
- clear_cookies()
- set_viewport(width, height)

Network Control:
- mock_route(url_pattern, status, body, content_type, headers, abort)
- clear_mocks(url_pattern)
- wait_for_response(url_pattern, status, timeout_seconds)
- export_har(name, include_bodies)

Emulation:
- list_devices(contains)
- emulate_device(name)
- set_geolocation(latitude, longitude, accuracy)
- set_timezone(timezone_id)
- set_color_scheme(scheme)
- throttle_network(profile)
- reset_emulation()

Session Recording:
- start_recording(name)
- stop_recording()
- take_snapshot(name)
- list_recordings()
- export_test(name, language, clear)

Resources (read without a tool call): browser://console, browser://network,
browser://network/{request_id}, browser://errors, browser://tabs,
browser://downloads, browser://actions, browser://sessions.""",
    lifespan=lifespan,
)

# Each tool call and resource read runs in the calling client's session.
mcp.add_middleware(SessionBindingMiddleware())

# Register all tools
register_navigation_tools(mcp)
register_search_tools(mcp)
register_interaction_tools(mcp)
register_batch_tools(mcp)
register_waiting_tools(mcp)
register_form_tools(mcp)
register_content_tools(mcp)
register_extract_tools(mcp)
register_devtools(mcp)
register_network_tools(mcp)
register_emulation_tools(mcp)
register_recording_tools(mcp)
register_tab_tools(mcp)
register_session_tools(mcp)
register_resources(mcp)

logger.info("Browser Control MCP server initialized with all tools")

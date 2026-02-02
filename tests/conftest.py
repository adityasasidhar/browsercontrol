"""Pytest fixtures for BrowserControl tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import tempfile


@pytest.fixture
def mock_page():
    """Mock Playwright page object."""
    page = AsyncMock()
    page.goto = AsyncMock()
    page.go_back = AsyncMock()
    page.go_forward = AsyncMock()
    page.reload = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.evaluate = AsyncMock()
    page.screenshot = AsyncMock(return_value=b"fake_screenshot_data")
    page.title = AsyncMock(return_value="Test Page")
    page.url = "https://example.com"
    
    # Mouse and keyboard
    page.mouse = AsyncMock()
    page.mouse.click = AsyncMock()
    page.mouse.move = AsyncMock()
    page.keyboard = AsyncMock()
    page.keyboard.type = AsyncMock()
    page.keyboard.press = AsyncMock()
    
    return page


@pytest.fixture
def mock_context():
    """Mock Playwright browser context."""
    context = AsyncMock()
    context.pages = []
    context.new_page = AsyncMock()
    context.cookies = AsyncMock(return_value=[])
    context.add_cookies = AsyncMock()
    context.clear_cookies = AsyncMock()
    return context


@pytest.fixture
def mock_browser():
    """Mock Playwright browser."""
    browser = AsyncMock()
    browser.close = AsyncMock()
    return browser


@pytest.fixture
def mock_playwright():
    """Mock Playwright instance."""
    pw = AsyncMock()
    pw.chromium = AsyncMock()
    pw.chromium.launch_persistent_context = AsyncMock()
    return pw


@pytest.fixture
def sample_element_map():
    """Sample element map for testing SoM functionality."""
    return {
        1: {
            "tag": "button",
            "text": "Sign In",
            "x": 100,
            "y": 200,
            "width": 80,
            "height": 40,
            "centerX": 140,
            "centerY": 220
        },
        2: {
            "tag": "input",
            "text": "",
            "x": 50,
            "y": 100,
            "width": 200,
            "height": 30,
            "centerX": 150,
            "centerY": 115
        },
        3: {
            "tag": "a",
            "text": "Products",
            "x": 300,
            "y": 50,
            "width": 60,
            "height": 20,
            "centerX": 330,
            "centerY": 60
        }
    }


@pytest.fixture
def temp_recordings_dir():
    """Temporary directory for recording tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_browser_manager(mock_page, mock_context, mock_browser):
    """Mock BrowserManager instance."""
    with patch('browsercontrol.browser.browser') as mock_mgr:
        mock_mgr._browser = mock_browser
        mock_mgr._context = mock_context
        mock_mgr._page = mock_page
        mock_mgr.page = mock_page
        mock_mgr.ensure_started = AsyncMock()
        mock_mgr.start = AsyncMock()
        mock_mgr.stop = AsyncMock()
        mock_mgr.screenshot_with_som = AsyncMock(
            return_value=(b"fake_screenshot", {})
        )
        mock_mgr.get_console_logs = MagicMock(return_value=[])
        mock_mgr.get_network_requests = MagicMock(return_value=[])
        mock_mgr.get_page_errors = MagicMock(return_value=[])
        mock_mgr.create_tab = AsyncMock()
        mock_mgr.switch_to_tab = AsyncMock()
        mock_mgr.close_tab = AsyncMock()
        mock_mgr.list_tabs = AsyncMock(return_value=[])
        yield mock_mgr

"""Tests for developer tools."""

import pytest
from unittest.mock import patch, AsyncMock
from fastmcp import FastMCP
from browsercontrol.tools.devtools import register_devtools


@pytest.fixture
def mcp_server():
    """Create a FastMCP server instance for testing."""
    return FastMCP("test")


class TestConsoleLogs:
    """Test console log capture tools."""
    
    @pytest.mark.asyncio
    async def test_get_console_logs(self, mcp_server, mock_browser_manager):
        """Test getting console logs."""
        register_devtools(mcp_server)
        
        mock_browser_manager.get_console_logs.return_value = [
            {"type": "log", "text": "Hello", "timestamp": "2026-01-01T00:00:00"},
            {"type": "error", "text": "Error!", "timestamp": "2026-01-01T00:00:01"}
        ]
        
        with patch('browsercontrol.tools.devtools.browser', mock_browser_manager):
            tool = mcp_server._tool_manager._tools["get_console_logs"]
            result = await tool.fn()
            
            assert "Hello" in result
            assert "Error!" in result


class TestNetworkRequests:
    """Test network request monitoring."""
    
    @pytest.mark.asyncio
    async def test_get_network_requests(self, mcp_server, mock_browser_manager):
        """Test getting network requests."""
        register_devtools(mcp_server)
        
        mock_browser_manager.get_network_requests.return_value = [
            {
                "url": "https://api.example.com/data",
                "method": "GET",
                "status": 200,
                "timestamp": "2026-01-01T00:00:00"
            }
        ]
        
        with patch('browsercontrol.tools.devtools.browser', mock_browser_manager):
            tool = mcp_server._tool_manager._tools["get_network_requests"]
            result = await tool.fn()
            
            assert "api.example.com" in result
            assert "200" in result


class TestCookieManagement:
    """Test cookie get/set/delete/clear tools."""
    
    @pytest.mark.asyncio
    async def test_get_cookies(self, mcp_server, mock_browser_manager, mock_context):
        """Test getting all cookies."""
        register_devtools(mcp_server)
        
        mock_context.cookies.return_value = [
            {"name": "session", "value": "abc123", "domain": "example.com"}
        ]
        
        with patch('browsercontrol.tools.devtools.browser', mock_browser_manager):
            mock_browser_manager._context = mock_context
            
            tool = mcp_server._tool_manager._tools["get_cookies"]
            result = await tool.fn()
            
            assert "session" in result
            assert "abc123" in result
    
    @pytest.mark.asyncio
    async def test_set_cookie(self, mcp_server, mock_browser_manager, mock_context, mock_page):
        """Test setting a cookie."""
        register_devtools(mcp_server)
        
        mock_page.url = "https://example.com"
        
        with patch('browsercontrol.tools.devtools.browser', mock_browser_manager):
            mock_browser_manager._context = mock_context
            mock_browser_manager.page = mock_page
            
            tool = mcp_server._tool_manager._tools["set_cookie"]
            result = await tool.fn(name="test", value="value123")
            
            mock_context.add_cookies.assert_called_once()
            assert "Set cookie 'test'" in result
    
    @pytest.mark.asyncio
    async def test_delete_cookie(self, mcp_server, mock_browser_manager, mock_context):
        """Test deleting a specific cookie."""
        register_devtools(mcp_server)
        
        mock_context.cookies.return_value = [
            {"name": "session", "value": "abc", "domain": "example.com"},
            {"name": "other", "value": "xyz", "domain": "example.com"}
        ]
        
        with patch('browsercontrol.tools.devtools.browser', mock_browser_manager):
            mock_browser_manager._context = mock_context
            
            tool = mcp_server._tool_manager._tools["delete_cookie"]
            result = await tool.fn(name="session")
            
            # Should clear all cookies then re-add the ones we want to keep
            assert "Deleted cookie 'session'" in result
    
    @pytest.mark.asyncio
    async def test_clear_cookies(self, mcp_server, mock_browser_manager, mock_context):
        """Test clearing all cookies."""
        register_devtools(mcp_server)
        
        with patch('browsercontrol.tools.devtools.browser', mock_browser_manager):
            mock_browser_manager._context = mock_context
            
            tool = mcp_server._tool_manager._tools["clear_cookies"]
            result = await tool.fn()
            
            mock_context.clear_cookies.assert_called_once()
            assert "Cleared all cookies" in result


class TestViewport:
    """Test viewport control."""
    
    @pytest.mark.asyncio
    async def test_set_viewport(self, mcp_server, mock_browser_manager, mock_page):
        """Test changing viewport size."""
        register_devtools(mcp_server)
        
        with patch('browsercontrol.tools.devtools.browser', mock_browser_manager):
            mock_browser_manager.page = mock_page
            
            tool = mcp_server._tool_manager._tools["set_viewport"]
            result = await tool.fn(width=1920, height=1080)
            
            mock_page.set_viewport_size.assert_called_once_with({"width": 1920, "height": 1080})
            assert "1920x1080" in result


class TestPageErrors:
    """Test page error capture."""
    
    @pytest.mark.asyncio
    async def test_get_page_errors(self, mcp_server, mock_browser_manager):
        """Test getting page errors."""
        register_devtools(mcp_server)
        
        mock_browser_manager.get_page_errors.return_value = [
            {"message": "TypeError: Cannot read property 'x' of undefined", "timestamp": "2026-01-01T00:00:00"}
        ]
        
        with patch('browsercontrol.tools.devtools.browser', mock_browser_manager):
            tool = mcp_server._tool_manager._tools["get_page_errors"]
            result = await tool.fn()
            
            assert "TypeError" in result


class TestPerformance:
    """Test performance metrics."""
    
    @pytest.mark.asyncio
    async def test_get_page_performance(self, mcp_server, mock_browser_manager, mock_page):
        """Test getting page performance metrics."""
        register_devtools(mcp_server)
        
        mock_page.evaluate.return_value = {
            "loadTime": 1234,
            "domContentLoaded": 500,
            "firstPaint": 300
        }
        
        with patch('browsercontrol.tools.devtools.browser', mock_browser_manager):
            mock_browser_manager.page = mock_page
            
            tool = mcp_server._tool_manager._tools["get_page_performance"]
            result = await tool.fn()
            
            assert "1234" in result or "loadTime" in result

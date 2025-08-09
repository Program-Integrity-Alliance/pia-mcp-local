"""Tests for server module."""

import pytest
from unittest.mock import AsyncMock, patch
import mcp.types as types
from pia_mcp_server.server import list_tools, call_tool


@pytest.mark.asyncio
async def test_list_tools():
    """Test that tools are properly listed."""
    tools = await list_tools()
    
    assert len(tools) == 5
    tool_names = [tool.name for tool in tools]
    
    expected_tools = [
        "pia_search",
        "pia_search_facets", 
        "get_rate_limit_stats",
        "search",
        "fetch"
    ]
    
    for expected_tool in expected_tools:
        assert expected_tool in tool_names


@pytest.mark.asyncio
async def test_call_unknown_tool():
    """Test calling an unknown tool."""
    result = await call_tool("unknown_tool", {})
    
    assert len(result) == 1
    assert result[0].type == "text"
    assert "Error: Unknown tool" in result[0].text


@pytest.mark.asyncio
async def test_call_tool_exception():
    """Test that exceptions in tool calls are handled properly."""
    with patch('pia_mcp_server.tools.handle_pia_search', side_effect=Exception("Test error")):
        result = await call_tool("pia_search", {"query": "test"})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error: Test error" in result[0].text
"""Tests for server module."""

import pytest
from unittest.mock import AsyncMock, patch
import mcp.types as types
from pia_mcp_server.server import server


@pytest.mark.asyncio
async def test_list_tools():
    """Test that tools are properly listed."""
    # Get the list_tools function from the server instance
    tools = await server._handlers.tools_list()

    assert len(tools) == 11  # Updated to match new tool count
    tool_names = [tool.name for tool in tools]

    expected_tools = [
        "pia_search_content",
        "pia_search_content_facets",
        "pia_search_titles",
        "pia_search_titles_facets",
        "pia_search_content_gao",
        "pia_search_content_oig",
        "pia_search_content_crs",
        "pia_search_content_doj",
        "pia_search_content_congress",
        "search",
        "fetch",
    ]

    for expected_tool in expected_tools:
        assert expected_tool in tool_names


@pytest.mark.asyncio
async def test_call_unknown_tool():
    """Test calling an unknown tool."""
    result = await server._handlers.tools_call("unknown_tool", {})

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Error: Unknown tool" in result[0].text


@pytest.mark.asyncio
async def test_call_tool_exception():
    """Test that exceptions in tool calls are handled properly."""
    with patch(
        "pia_mcp_server.config.Settings._get_api_key_from_args", return_value="test_key"
    ):
        with patch("httpx.AsyncClient") as mock_client:
            # Make the client throw an exception when post is called
            mock_client_instance = AsyncMock()
            mock_client_instance.post.side_effect = Exception("Test error")
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await server._handlers.tools_call(
                "pia_search_content", {"query": "test"}
            )

            assert len(result) == 1
            assert result[0].type == "text"
            assert "Error: Test error" in result[0].text

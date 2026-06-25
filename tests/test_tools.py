"""Tests for the tools module (mocked remote forwarding)."""

import json
import os
import httpx
import pytest
from unittest.mock import AsyncMock, patch, Mock

from pia_mcp_server.tools.search_tools import (
    handle_pia_search,
    handle_pia_oversight_recommendations,
)
from pia_mcp_server.config import Settings

settings = Settings()


def build_search_structured_result(
    title: str,
    data_source: str = "GAO",
    url: str = "https://example.com/doc-123",
    doc_id: str = "doc-123",
) -> dict:
    return {
        "output": {
            "total_count": 1,
            "results": [
                {
                    "id": doc_id,
                    "title": title,
                    "data_source": data_source,
                    "url": url,
                }
            ],
        }
    }


def build_tool_result(structured: dict) -> dict:
    return {
        "content": [{"type": "text", "text": json.dumps(structured)}],
        "structuredContent": structured,
        "isError": False,
    }


def _mock_client(mock_client, json_body):
    """Wire a patched httpx.AsyncClient to return ``json_body`` from POST."""
    response = Mock()
    response.json.return_value = json_body
    response.raise_for_status.return_value = None
    instance = AsyncMock()
    instance.post.return_value = response
    mock_client.return_value.__aenter__.return_value = instance
    return instance


# Every tool handler paired with the remote tool name it must forward to,
# and minimal valid arguments.
HANDLERS = [
    (handle_pia_search, "pia_search", {"query": "fraud"}),
    (
        handle_pia_oversight_recommendations,
        "pia_oversight_recommendations",
        {"query": "fraud"},
    ),
]


@pytest.mark.parametrize("handler,tool_name,args", HANDLERS)
async def test_handler_forwards_to_correct_tool(handler, tool_name, args):
    """Each handler forwards the call to its remote tool name with arguments."""
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": build_tool_result(build_search_structured_result("Doc")),
    }
    with patch.object(Settings, "_get_api_key_from_args", return_value="test_key"):
        with patch("httpx.AsyncClient") as mock_client:
            instance = _mock_client(mock_client, body)
            result = await handler(args)

            instance.post.assert_called_once()
            request = instance.post.call_args[1]["json"]
            assert request["method"] == "tools/call"
            assert request["params"]["name"] == tool_name
            assert request["params"]["arguments"] == args
            assert result.structuredContent is not None


async def test_pia_search_success_returns_structured_content():
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": build_tool_result(build_search_structured_result("GAO Fraud Report")),
    }
    with patch.object(Settings, "_get_api_key_from_args", return_value="test_key"):
        with patch("httpx.AsyncClient") as mock_client:
            _mock_client(mock_client, body)
            result = await handle_pia_search({"query": "fraud", "filter": "x eq 'y'"})
            assert (
                result.structuredContent["output"]["results"][0]["title"]
                == "GAO Fraud Report"
            )


@pytest.mark.parametrize("handler,tool_name,args", HANDLERS)
async def test_handler_without_api_key_raises(handler, tool_name, args):
    with patch.object(Settings, "_get_api_key_from_args", return_value=None):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="PIA API key is required"):
                await handler(args)


async def test_api_error_is_raised():
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {"code": -32000, "message": "Invalid API key"},
    }
    with patch.object(Settings, "_get_api_key_from_args", return_value="bad_key"):
        with patch("httpx.AsyncClient") as mock_client:
            _mock_client(mock_client, body)
            with pytest.raises(ValueError, match="API Error: Invalid API key"):
                await handle_pia_search({"query": "fraud"})


@pytest.mark.parametrize("handler,tool_name,args", HANDLERS)
async def test_handler_http_error_is_raised(handler, tool_name, args):
    with patch.object(Settings, "_get_api_key_from_args", return_value="test_key"):
        with patch("httpx.AsyncClient") as mock_client:
            instance = AsyncMock()
            instance.post.side_effect = httpx.HTTPStatusError(
                "Server Error",
                request=Mock(),
                response=Mock(status_code=500, text="Server Error"),
            )
            mock_client.return_value.__aenter__.return_value = instance
            with pytest.raises(ValueError, match="HTTP Error 500"):
                await handler(args)

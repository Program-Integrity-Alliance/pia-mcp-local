"""Tests for tools module."""

import pytest
from unittest.mock import AsyncMock, patch, PropertyMock, Mock
import httpx
from pia_mcp_server.tools.pia_search import handle_pia_search
from pia_mcp_server.tools.pia_search_facets import handle_pia_search_facets
from pia_mcp_server.config import Settings

settings = Settings()


@pytest.mark.asyncio
async def test_pia_search_no_api_key():
    """Test PIA search without API key."""
    with patch.object(Settings, "_get_api_key_from_args", return_value=None):
        result = await handle_pia_search({"query": "test"})

        assert len(result) == 1
        assert "PIA API key is required" in result[0].text


@pytest.mark.asyncio
async def test_pia_search_success():
    """Test successful PIA search."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "documents": [
                {"title": "Test Document", "id": "123", "summary": "Test summary"}
            ],
            "total": 1,
        },
    }

    with patch.object(Settings, "_get_api_key_from_args", return_value="test_key"):
        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response_obj
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await handle_pia_search({"query": "test fraud"})

            assert len(result) == 1
            assert "Test Document" in result[0].text


@pytest.mark.asyncio
async def test_pia_search_api_error():
    """Test PIA search with API error."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {"code": -32000, "message": "Invalid API key"},
    }

    with patch.object(Settings, "_get_api_key_from_args", return_value="invalid_key"):
        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response_obj
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await handle_pia_search({"query": "test"})

            assert len(result) == 1
            assert "API Error: Invalid API key" in result[0].text


@pytest.mark.asyncio
async def test_pia_search_http_error():
    """Test PIA search with HTTP error."""
    with patch.object(Settings, "_get_api_key_from_args", return_value="test_key"):
        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = AsyncMock()
            mock_response_obj.status_code = 500
            mock_response_obj.text = "Internal Server Error"

            http_error = httpx.HTTPStatusError(
                "500 Server Error", request=AsyncMock(), response=mock_response_obj
            )

            mock_client_instance = AsyncMock()
            mock_client_instance.post.side_effect = http_error
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await handle_pia_search({"query": "test"})

            assert len(result) == 1
            assert "HTTP Error 500" in result[0].text


@pytest.mark.asyncio
async def test_pia_search_facets_no_api_key():
    """Test PIA search facets without API key."""
    with patch.object(Settings, "_get_api_key_from_args", return_value=None):
        result = await handle_pia_search_facets({"query": "test"})

        assert len(result) == 1
        assert "PIA API key is required" in result[0].text


@pytest.mark.asyncio
async def test_pia_search_facets_success():
    """Test successful PIA search facets."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "facets": {
                "data_source": ["OIG", "GAO", "CMS"],
                "document_type": ["audit_report", "investigation", "guidance"],
                "agency": ["HHS", "DOD", "VA"],
            }
        },
    }

    with patch.object(Settings, "_get_api_key_from_args", return_value="test_key"):
        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response_obj
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await handle_pia_search_facets({"query": "healthcare"})

            assert len(result) == 1
            assert "data_source" in result[0].text
            assert "OIG" in result[0].text
            assert "document_type" in result[0].text


@pytest.mark.asyncio
async def test_pia_search_facets_api_error():
    """Test PIA search facets with API error."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {"code": -32000, "message": "Invalid query format"},
    }

    with patch.object(Settings, "_get_api_key_from_args", return_value="invalid_key"):
        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response_obj
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await handle_pia_search_facets({"query": "test"})

            assert len(result) == 1
            assert "API Error: Invalid query format" in result[0].text


@pytest.mark.asyncio
async def test_pia_search_facets_http_error():
    """Test PIA search facets with HTTP error."""
    with patch.object(Settings, "_get_api_key_from_args", return_value="test_key"):
        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = AsyncMock()
            mock_response_obj.status_code = 403
            mock_response_obj.text = "Forbidden"

            http_error = httpx.HTTPStatusError(
                "403 Client Error", request=AsyncMock(), response=mock_response_obj
            )

            mock_client_instance = AsyncMock()
            mock_client_instance.post.side_effect = http_error
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await handle_pia_search_facets({"query": "test"})

            assert len(result) == 1
            assert "HTTP Error 403" in result[0].text

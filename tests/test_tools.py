"""Tests for tools module."""

import pytest
from unittest.mock import AsyncMock, patch, Mock
import httpx
from pia_mcp_server.tools.search_tools import (
    handle_pia_search,
    handle_pia_search_facets,
)
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
async def test_pia_search_with_odata_filter():
    """Test PIA search with OData filter parameter."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "documents": [
                {
                    "title": "GAO Fraud Report",
                    "id": "gao_123",
                    "summary": "GAO fraud investigation",
                }
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

            # Test with actual field names from the remote implementation
            result = await handle_pia_search(
                {"query": "fraud", "filter": "SourceDocumentDataSource eq 'GAO'"}
            )

            # Verify the request was made with the filter
            mock_client_instance.post.assert_called_once()
            call_args = mock_client_instance.post.call_args
            request_data = call_args[1]["json"]
            assert (
                request_data["params"]["arguments"]["filter"]
                == "SourceDocumentDataSource eq 'GAO'"
            )

            assert len(result) == 1
            assert "GAO Fraud Report" in result[0].text


@pytest.mark.asyncio
async def test_pia_search_with_complex_odata_filter():
    """Test PIA search with complex OData filter."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "documents": [
                {
                    "title": "High Priority GAO Report",
                    "id": "gao_456",
                    "summary": "High priority integrity violation",
                }
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

            # Test complex boolean logic filter
            complex_filter = "(SourceDocumentDataSource eq 'GAO' or SourceDocumentDataSource eq 'OIG') and RecPriorityFlag in ('High', 'Critical')"
            result = await handle_pia_search(
                {"query": "integrity violations", "filter": complex_filter}
            )

            # Verify the complex filter was passed correctly
            mock_client_instance.post.assert_called_once()
            call_args = mock_client_instance.post.call_args
            request_data = call_args[1]["json"]
            assert request_data["params"]["arguments"]["filter"] == complex_filter

            assert len(result) == 1
            assert "High Priority GAO Report" in result[0].text


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
                "SourceDocumentDataSource": ["OIG", "GAO", "CMS"],
                "RecStatus": ["Open", "Closed", "In Progress"],
                "RecPriorityFlag": ["High", "Medium", "Low", "Critical"],
                "IsIntegrityRelated": ["Yes", "No"],
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
            assert "SourceDocumentDataSource" in result[0].text
            assert "OIG" in result[0].text
            assert "RecStatus" in result[0].text


@pytest.mark.asyncio
async def test_pia_search_facets_with_filter():
    """Test PIA search facets with OData filter parameter."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "facets": {
                "SourceDocumentDataSource": ["GAO"],
                "RecStatus": ["Open", "In Progress"],
                "RecPriorityFlag": ["High", "Critical"],
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

            # Test facets with filter parameter
            result = await handle_pia_search_facets(
                {
                    "query": "fraud",
                    "filter": "SourceDocumentDataSource eq 'GAO' and RecStatus ne 'Closed'",
                }
            )

            # Verify the filter was passed correctly
            mock_client_instance.post.assert_called_once()
            call_args = mock_client_instance.post.call_args
            request_data = call_args[1]["json"]
            assert (
                request_data["params"]["arguments"]["filter"]
                == "SourceDocumentDataSource eq 'GAO' and RecStatus ne 'Closed'"
            )

            assert len(result) == 1
            assert "SourceDocumentDataSource" in result[0].text
            assert "GAO" in result[0].text


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


@pytest.mark.asyncio
async def test_pia_search_empty_filter():
    """Test PIA search with empty filter parameter."""
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

            # Test with empty filter (should work normally)
            result = await handle_pia_search({"query": "test query", "filter": ""})

            assert len(result) == 1
            assert "Test Document" in result[0].text


@pytest.mark.asyncio
async def test_pia_search_with_all_parameters():
    """Test PIA search with all parameters including filter."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "documents": [
                {"title": "Complete Test", "id": "456", "summary": "Full test"}
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

            # Test with all parameters
            result = await handle_pia_search(
                {
                    "query": "comprehensive test",
                    "filter": "SourceDocumentDataSource eq 'GAO' and IsIntegrityRelated eq 'Yes'",
                    "page": 2,
                    "page_size": 5,
                    "search_mode": "titles",
                    "limit": 10,
                    "include_facets": True,
                }
            )

            # Verify all parameters were passed correctly
            mock_client_instance.post.assert_called_once()
            call_args = mock_client_instance.post.call_args
            request_data = call_args[1]["json"]
            arguments = request_data["params"]["arguments"]

            assert arguments["query"] == "comprehensive test"
            assert (
                arguments["filter"]
                == "SourceDocumentDataSource eq 'GAO' and IsIntegrityRelated eq 'Yes'"
            )
            assert arguments["page"] == 2
            assert arguments["page_size"] == 5
            assert arguments["search_mode"] == "titles"
            assert arguments["limit"] == 10
            assert arguments["include_facets"] is True

            assert len(result) == 1
            assert "Complete Test" in result[0].text


@pytest.mark.asyncio
async def test_pia_search_facets_empty_filter():
    """Test PIA search facets with empty filter parameter."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "facets": {
                "SourceDocumentDataSource": ["OIG", "GAO", "CMS"],
                "RecStatus": ["Open", "Closed"],
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

            # Test facets with empty filter
            result = await handle_pia_search_facets({"query": "test", "filter": ""})

            assert len(result) == 1
            assert "SourceDocumentDataSource" in result[0].text

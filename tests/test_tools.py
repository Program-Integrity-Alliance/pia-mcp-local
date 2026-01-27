"""Tests for tools module."""

import json
import os
import pytest
from unittest.mock import AsyncMock, patch, Mock
import httpx
from pia_mcp_server.tools.search_tools import (
    handle_pia_search_content,
    handle_pia_search_content_facets,
    handle_pia_search_titles,
    handle_pia_search_titles_facets,
    handle_pia_search_content_gao,
    handle_pia_search_content_oig,
    handle_pia_search_content_crs,
    handle_pia_search_content_doj,
    handle_pia_search_content_congress,
    handle_pia_search_content_executive_orders,
    handle_search,
    handle_fetch,
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


def build_facets_structured_result(facets: dict[str, list[str]]) -> dict:
    return {
        "output": {
            "facets": {
                key: [{"value": value, "count": 1} for value in values]
                for key, values in facets.items()
            }
        }
    }


def build_fetch_structured_result(
    doc_id: str = "doc-123",
    title: str = "Test Document",
    text: str = "Full document content here",
    url: str = "https://example.com/doc-123",
) -> dict:
    return {"id": doc_id, "title": title, "text": text, "url": url}


def build_tool_result(structured: dict) -> dict:
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(structured),
            }
        ],
        "structuredContent": structured,
        "isError": False,
    }


@pytest.mark.asyncio
async def test_pia_search_content_no_api_key():
    """Test PIA content search without API key."""
    with patch.object(Settings, "_get_api_key_from_args", return_value=None):
        with patch.dict(os.environ, {}, clear=True):  # Clear all environment variables
            with pytest.raises(ValueError, match="PIA API key is required"):
                await handle_pia_search_content({"query": "test"})


@pytest.mark.asyncio
async def test_pia_search_content_success():
    """Test successful PIA content search."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": build_tool_result(build_search_structured_result("Test Document")),
    }

    with patch.object(Settings, "_get_api_key_from_args", return_value="test_key"):
        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response_obj
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await handle_pia_search_content({"query": "test fraud"})

            assert (
                result.structuredContent["output"]["results"][0]["title"]
                == "Test Document"
            )


@pytest.mark.asyncio
async def test_pia_search_content_with_odata_filter():
    """Test PIA search with OData filter parameter."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": build_tool_result(build_search_structured_result("GAO Fraud Report")),
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
            result = await handle_pia_search_content(
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

            assert (
                result.structuredContent["output"]["results"][0]["title"]
                == "GAO Fraud Report"
            )


@pytest.mark.asyncio
async def test_pia_search_content_with_complex_odata_filter():
    """Test PIA search with complex OData filter."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": build_tool_result(
            build_search_structured_result("High Priority GAO Report")
        ),
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
            complex_filter = "(SourceDocumentDataSource eq 'GAO' or SourceDocumentDataSource eq 'Oversight.gov') and RecPriorityFlag in ('High', 'Critical')"
            result = await handle_pia_search_content(
                {"query": "integrity violations", "filter": complex_filter}
            )

            # Verify the complex filter was passed correctly
            mock_client_instance.post.assert_called_once()
            call_args = mock_client_instance.post.call_args
            request_data = call_args[1]["json"]
            assert request_data["params"]["arguments"]["filter"] == complex_filter

            assert (
                result.structuredContent["output"]["results"][0]["title"]
                == "High Priority GAO Report"
            )


@pytest.mark.asyncio
async def test_pia_search_content_api_error():
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

            with pytest.raises(ValueError, match="API Error: Invalid API key"):
                await handle_pia_search_content({"query": "test"})


@pytest.mark.asyncio
async def test_pia_search_content_http_error():
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

            with pytest.raises(ValueError, match="HTTP Error 500"):
                await handle_pia_search_content({"query": "test"})


@pytest.mark.asyncio
async def test_pia_search_content_facets_no_api_key():
    """Test PIA search facets without API key."""
    with patch.object(Settings, "_get_api_key_from_args", return_value=None):
        with patch.dict(os.environ, {}, clear=True):  # Clear all environment variables
            with pytest.raises(ValueError, match="PIA API key is required"):
                await handle_pia_search_content_facets({"query": "test"})


@pytest.mark.asyncio
async def test_pia_search_content_facets_success():
    """Test successful PIA search facets."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": build_tool_result(
            build_facets_structured_result(
                {
                    "SourceDocumentDataSource": ["Oversight.gov", "GAO", "CMS"],
                    "RecStatus": ["Open", "Closed", "In Progress"],
                    "RecPriorityFlag": ["High", "Medium", "Low", "Critical"],
                    "IsIntegrityRelated": ["Yes", "No"],
                }
            )
        ),
    }

    with patch.object(Settings, "_get_api_key_from_args", return_value="test_key"):
        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response_obj
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await handle_pia_search_content_facets({"query": "healthcare"})

            assert (
                result.structuredContent["output"]["facets"][
                    "SourceDocumentDataSource"
                ][0]["value"]
                == "Oversight.gov"
            )
            assert (
                result.structuredContent["output"]["facets"]["RecStatus"][0]["value"]
                == "Open"
            )


@pytest.mark.asyncio
async def test_pia_search_content_facets_with_filter():
    """Test PIA search facets with OData filter parameter."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": build_tool_result(
            build_facets_structured_result(
                {
                    "SourceDocumentDataSource": ["GAO"],
                    "RecStatus": ["Open", "In Progress"],
                    "RecPriorityFlag": ["High", "Critical"],
                }
            )
        ),
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
            result = await handle_pia_search_content_facets(
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

            assert (
                result.structuredContent["output"]["facets"][
                    "SourceDocumentDataSource"
                ][0]["value"]
                == "GAO"
            )


@pytest.mark.asyncio
async def test_pia_search_content_facets_api_error():
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

            with pytest.raises(ValueError, match="API Error: Invalid query format"):
                await handle_pia_search_content_facets({"query": "test"})


@pytest.mark.asyncio
async def test_pia_search_content_facets_http_error():
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

            with pytest.raises(ValueError, match="HTTP Error 403"):
                await handle_pia_search_content_facets({"query": "test"})


@pytest.mark.asyncio
async def test_pia_search_content_empty_filter():
    """Test PIA search with empty filter parameter."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": build_tool_result(build_search_structured_result("Test Document")),
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
            result = await handle_pia_search_content(
                {"query": "test query", "filter": ""}
            )

            assert (
                result.structuredContent["output"]["results"][0]["title"]
                == "Test Document"
            )


@pytest.mark.asyncio
async def test_pia_search_content_with_all_parameters():
    """Test PIA search with all parameters including filter."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": build_tool_result(build_search_structured_result("Complete Test")),
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
            result = await handle_pia_search_content(
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

            assert (
                result.structuredContent["output"]["results"][0]["title"]
                == "Complete Test"
            )


@pytest.mark.asyncio
async def test_pia_search_content_facets_empty_filter():
    """Test PIA search facets with empty filter parameter."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": build_tool_result(
            build_facets_structured_result(
                {
                    "SourceDocumentDataSource": ["Oversight.gov", "GAO", "CMS"],
                    "RecStatus": ["Open", "Closed"],
                }
            )
        ),
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
            result = await handle_pia_search_content_facets(
                {"query": "test", "filter": ""}
            )

            assert (
                result.structuredContent["output"]["facets"][
                    "SourceDocumentDataSource"
                ][0]["value"]
                == "Oversight.gov"
            )


# Agency-specific search tool tests
@pytest.mark.asyncio
async def test_pia_search_content_gao_success():
    """Test successful PIA GAO content search."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": build_tool_result(
            build_search_structured_result(
                "GAO Report", data_source="GAO", doc_id="gao-123"
            )
        ),
    }

    with patch.object(Settings, "_get_api_key_from_args", return_value="test_key"):
        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response_obj
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await handle_pia_search_content_gao({"query": "audit"})

            assert (
                result.structuredContent["output"]["results"][0]["title"]
                == "GAO Report"
            )


@pytest.mark.asyncio
async def test_pia_search_content_oig_success():
    """Test successful PIA OIG content search."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": build_tool_result(
            build_search_structured_result(
                "OIG Investigation",
                data_source="Oversight.gov",
                doc_id="oig-123",
            )
        ),
    }

    with patch.object(Settings, "_get_api_key_from_args", return_value="test_key"):
        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response_obj
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await handle_pia_search_content_oig({"query": "oversight"})

            assert (
                result.structuredContent["output"]["results"][0]["title"]
                == "OIG Investigation"
            )


@pytest.mark.asyncio
async def test_pia_search_content_crs_success():
    """Test successful PIA CRS content search."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": build_tool_result(
            build_search_structured_result(
                "CRS Report", data_source="CRS", doc_id="crs-123"
            )
        ),
    }

    with patch.object(Settings, "_get_api_key_from_args", return_value="test_key"):
        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response_obj
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await handle_pia_search_content_crs({"query": "research"})

            assert (
                result.structuredContent["output"]["results"][0]["title"]
                == "CRS Report"
            )


@pytest.mark.asyncio
async def test_pia_search_content_doj_success():
    """Test successful PIA DOJ content search."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": build_tool_result(
            build_search_structured_result(
                "DOJ Press Release",
                data_source="Department of Justice",
                doc_id="doj-123",
            )
        ),
    }

    with patch.object(Settings, "_get_api_key_from_args", return_value="test_key"):
        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response_obj
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await handle_pia_search_content_doj({"query": "enforcement"})

            assert (
                result.structuredContent["output"]["results"][0]["title"]
                == "DOJ Press Release"
            )


@pytest.mark.asyncio
async def test_pia_search_content_congress_success():
    """Test successful PIA Congress content search."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": build_tool_result(
            build_search_structured_result(
                "Congressional Bill",
                data_source="Congress.gov",
                doc_id="congress-123",
            )
        ),
    }

    with patch.object(Settings, "_get_api_key_from_args", return_value="test_key"):
        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response_obj
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await handle_pia_search_content_congress({"query": "legislation"})

            assert (
                result.structuredContent["output"]["results"][0]["title"]
                == "Congressional Bill"
            )


@pytest.mark.asyncio
async def test_pia_search_content_executive_orders_success():
    """Test successful PIA Executive Orders content search."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": build_tool_result(
            build_search_structured_result(
                "Executive Order 12345",
                data_source="Federal Register",
                doc_id="eo-123",
            )
        ),
    }

    with patch.object(Settings, "_get_api_key_from_args", return_value="test_key"):
        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response_obj
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await handle_pia_search_content_executive_orders(
                {"query": "cybersecurity"}
            )

            assert (
                result.structuredContent["output"]["results"][0]["title"]
                == "Executive Order 12345"
            )


@pytest.mark.asyncio
async def test_fetch_success():
    """Test successful document fetch."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": build_tool_result(build_fetch_structured_result()),
    }

    with patch.object(Settings, "_get_api_key_from_args", return_value="test_key"):
        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response_obj
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await handle_fetch({"id": "doc-123"})

            assert result.structuredContent["title"] == "Test Document"
            assert result.structuredContent["text"] == "Full document content here"


@pytest.mark.asyncio
async def test_agency_tools_no_api_key():
    """Test agency-specific tools without API key."""
    tools_to_test = [
        (handle_pia_search_content_gao, {"query": "test"}),
        (handle_pia_search_content_oig, {"query": "test"}),
        (handle_pia_search_content_crs, {"query": "test"}),
        (handle_pia_search_content_doj, {"query": "test"}),
        (handle_pia_search_content_congress, {"query": "test"}),
        (handle_pia_search_content_executive_orders, {"query": "test"}),
        (handle_fetch, {"id": "test-123"}),
    ]

    for tool_handler, args in tools_to_test:
        with patch.object(Settings, "_get_api_key_from_args", return_value=None):
            with patch.dict(
                os.environ, {}, clear=True
            ):  # Clear all environment variables
                with pytest.raises(ValueError, match="PIA API key is required"):
                    await tool_handler(args)


@pytest.mark.asyncio
async def test_agency_tools_http_error():
    """Test agency-specific tools with HTTP error."""
    tools_to_test = [
        (handle_pia_search_content_gao, {"query": "test"}),
        (handle_pia_search_content_oig, {"query": "test"}),
        (handle_pia_search_content_crs, {"query": "test"}),
        (handle_pia_search_content_doj, {"query": "test"}),
        (handle_pia_search_content_congress, {"query": "test"}),
        (handle_pia_search_content_executive_orders, {"query": "test"}),
        (handle_fetch, {"id": "test-123"}),
    ]

    for tool_handler, args in tools_to_test:
        with patch.object(Settings, "_get_api_key_from_args", return_value="test_key"):
            with patch("httpx.AsyncClient") as mock_client:
                mock_client_instance = AsyncMock()
                mock_client_instance.post.side_effect = httpx.HTTPStatusError(
                    "Server Error",
                    request=Mock(),
                    response=Mock(status_code=500, text="Server Error"),
                )
                mock_client.return_value.__aenter__.return_value = mock_client_instance

                with pytest.raises(ValueError, match="HTTP Error 500"):
                    await tool_handler(args)

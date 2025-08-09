"""Tests for tools module."""

import pytest
from unittest.mock import AsyncMock, patch, PropertyMock
import httpx
from pia_mcp_server.tools.pia_search import handle_pia_search
from pia_mcp_server.tools.search import handle_search
from pia_mcp_server.tools.fetch import handle_fetch
from pia_mcp_server.config import Settings

settings = Settings()


@pytest.mark.asyncio
async def test_pia_search_no_api_key():
    """Test PIA search without API key."""
    with patch('pia_mcp_server.tools.pia_search.settings.API_KEY', side_effect=ValueError("PIA API key is required")):
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
            "total": 1
        }
    }
    
    with patch.object(type(settings), 'API_KEY', new_callable=lambda: PropertyMock(return_value='test_key')):
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response_obj = AsyncMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = AsyncMock()
            mock_post.return_value = mock_response_obj
            
            result = await handle_pia_search({"query": "test fraud"})
            
            assert len(result) == 1
            assert "Test Document" in result[0].text


@pytest.mark.asyncio
async def test_pia_search_api_error():
    """Test PIA search with API error."""
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {
            "code": -32000,
            "message": "Invalid API key"
        }
    }
    
    with patch.object(type(settings), 'API_KEY', new_callable=lambda: PropertyMock(return_value='invalid_key')):
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response_obj = AsyncMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = AsyncMock()
            mock_post.return_value = mock_response_obj
            
            result = await handle_pia_search({"query": "test"})
            
            assert len(result) == 1
            assert "API Error: Invalid API key" in result[0].text


@pytest.mark.asyncio
async def test_pia_search_http_error():
    """Test PIA search with HTTP error."""
    with patch.object(type(settings), 'API_KEY', new_callable=lambda: PropertyMock(return_value='test_key')):
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response_obj = AsyncMock()
            mock_response_obj.status_code = 500
            mock_response_obj.text = "Internal Server Error"
            
            http_error = httpx.HTTPStatusError(
                "500 Server Error", 
                request=AsyncMock(), 
                response=mock_response_obj
            )
            mock_post.side_effect = http_error
            
            result = await handle_pia_search({"query": "test"})
            
            assert len(result) == 1
            assert "HTTP Error 500" in result[0].text


@pytest.mark.asyncio
async def test_search_tool():
    """Test basic search tool."""
    with patch.object(type(settings), 'API_KEY', new_callable=lambda: PropertyMock(return_value='test_key')):
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = {
                "jsonrpc": "2.0", 
                "id": 1,
                "result": {"results": [{"title": "Test Result"}]}
            }
            mock_response_obj = AsyncMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = AsyncMock()
            mock_post.return_value = mock_response_obj
            
            result = await handle_search({"query": "test query"})
            
            assert len(result) == 1
            assert "Test Result" in result[0].text


@pytest.mark.asyncio
async def test_fetch_tool():
    """Test fetch tool."""
    with patch.object(type(settings), 'API_KEY', new_callable=lambda: PropertyMock(return_value='test_key')):
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = {
                "jsonrpc": "2.0",
                "id": 1, 
                "result": {"id": "123", "title": "Test Document", "content": "Document content"}
            }
            mock_response_obj = AsyncMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = AsyncMock()
            mock_post.return_value = mock_response_obj
            
            result = await handle_fetch({"id": "123"})
            
            assert len(result) == 1
            assert "Test Document" in result[0].text
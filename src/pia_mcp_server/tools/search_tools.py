"""PIA Search tools for database searches and facets discovery."""

import httpx
import mcp.types as types
from typing import Dict, Any, List
import json
import logging
from ..config import Settings

logger = logging.getLogger(__name__)
settings = Settings()

# Tool definitions based on the API response
pia_search_tool = types.Tool(
    name="pia_search",
    description="Search the Program Integrity Alliance (PIA) database for documents and recommendations. Returns comprehensive results with full citation information and clickable links for proper attribution. Each result includes corresponding citations with data source attribution (GAO, OIG, etc.). Supports OData filter expressions using operators like eq, ne, gt, ge, lt, le, and, or, etc.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query text"},
            "filter": {
                "type": "string",
                "description": "Optional OData filter expression for narrowing results (e.g., \"data_source eq 'GAO'\")",
            },
            "page": {
                "type": "integer",
                "description": "Page number (default: 1)",
                "default": 1,
            },
            "page_size": {
                "type": "integer",
                "description": "Results per page (default: 10)",
                "default": 10,
            },
            "search_mode": {
                "type": "string",
                "description": "Search mode (default: content)",
                "default": "content",
            },
            "limit": {"type": "integer", "description": "Maximum results limit"},
            "include_facets": {
                "type": "boolean",
                "description": "Include facets in results",
                "default": False,
            },
        },
        "required": ["query"],
    },
)

pia_search_facets_tool = types.Tool(
    name="pia_search_facets",
    description="Get available facets (filter values) for the PIA database. This can help understand what filter values are available before performing searches.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Optional query to get facets for",
                "default": "",
            }
        },
    },
)


async def handle_pia_search(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle PIA search requests."""
    try:
        # Prepare the request payload
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "pia_search", "arguments": arguments},
        }

        try:
            api_key = settings.API_KEY
        except ValueError as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error: {str(e)} Configure API key in MCP server settings.",
                )
            ]

        headers = {"Content-Type": "application/json", "x-api-key": api_key}

        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            response = await client.post(
                settings.PIA_API_URL, json=payload, headers=headers
            )
            response.raise_for_status()

            result = response.json()

            if "error" in result:
                error_msg = result["error"].get("message", "Unknown error")
                return [types.TextContent(type="text", text=f"API Error: {error_msg}")]

            if "result" in result:
                # Format the search results nicely
                search_results = result["result"]
                formatted_result = json.dumps(
                    search_results, indent=2, ensure_ascii=False
                )
                return [types.TextContent(type="text", text=formatted_result)]
            else:
                return [
                    types.TextContent(type="text", text="No results returned from API")
                ]

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during PIA search: {e}")
        return [
            types.TextContent(
                type="text",
                text=f"HTTP Error {e.response.status_code}: {e.response.text}",
            )
        ]
    except Exception as e:
        logger.error(f"Error during PIA search: {e}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_pia_search_facets(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Handle PIA search facets requests."""
    try:
        # Prepare the request payload
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "pia_search_facets", "arguments": arguments},
        }

        try:
            api_key = settings.API_KEY
        except ValueError as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error: {str(e)} Configure API key in MCP server settings.",
                )
            ]

        headers = {"Content-Type": "application/json", "x-api-key": api_key}

        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            response = await client.post(
                settings.PIA_API_URL, json=payload, headers=headers
            )
            response.raise_for_status()

            result = response.json()

            if "error" in result:
                error_msg = result["error"].get("message", "Unknown error")
                return [types.TextContent(type="text", text=f"API Error: {error_msg}")]

            if "result" in result:
                # Format the facets nicely
                facets = result["result"]
                formatted_result = json.dumps(facets, indent=2, ensure_ascii=False)
                return [types.TextContent(type="text", text=formatted_result)]
            else:
                return [
                    types.TextContent(type="text", text="No facets returned from API")
                ]

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during PIA search facets: {e}")
        return [
            types.TextContent(
                type="text",
                text=f"HTTP Error {e.response.status_code}: {e.response.text}",
            )
        ]
    except Exception as e:
        logger.error(f"Error during PIA search facets: {e}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

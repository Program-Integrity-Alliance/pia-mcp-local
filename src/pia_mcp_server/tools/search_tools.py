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
pia_search_content_tool = types.Tool(
    name="pia_search_content",
    description="Search the Program Integrity Alliance (PIA) database for document content and recommendations. Returns comprehensive results with full citation information and clickable links for proper attribution. Each result includes corresponding citations with data source attribution (GAO, OIG, etc.). Supports complex OData filtering with boolean logic, operators, and grouping.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query text"},
            "filter": {
                "type": "string",
                "description": (
                    "OData filter expression supporting complex boolean logic. "
                    "Examples: \"SourceDocumentDataSource eq 'GAO'\", "
                    "\"SourceDocumentDataSource eq 'GAO' or "
                    "SourceDocumentDataSource eq 'OIG'\", "
                    "\"SourceDocumentDataSource eq 'GAO' and RecStatus ne 'Closed'\", "
                    "\"SourceDocumentDataSource ne 'Department of Justice' and not "
                    "(RecStatus eq 'Closed')\", "
                    "\"IsIntegrityRelated eq 'Yes' and RecPriorityFlag in "
                    "('High', 'Critical')\", "
                    "\"SourceDocumentPublishDate ge '2020-01-01' and "
                    "SourceDocumentPublishDate le '2024-12-31'\", "
                    "\"(SourceDocumentDataSource eq 'GAO' or "
                    "SourceDocumentDataSource eq 'OIG') and RecStatus eq 'Open'\""
                ),
            },
            "page": {
                "type": "integer",
                "description": "Page number (1-based)",
                "default": 1,
            },
            "page_size": {
                "type": "integer",
                "description": "Number of results per page (max 50)",
                "default": 10,
            },
            "search_mode": {
                "type": "string",
                "description": 'Search mode - "content" for full-text search or "titles" for title-only search',
                "default": "content",
            },
            "limit": {
                "type": "integer",
                "description": "Alternative name for page_size (for compatibility)",
            },
            "include_facets": {
                "type": "boolean",
                "description": "Whether to include facets in response (default False to reduce token usage)",
                "default": False,
            },
        },
        "required": ["query"],
    },
)

pia_search_content_facets_tool = types.Tool(
    name="pia_search_content_facets",
    description="Get available facets (filter values) for the PIA database content search. This can help understand what filter values are available before performing content searches. Supports complex OData filtering with boolean logic, operators, and grouping.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Optional query to get facets for (if empty, gets all facets)",
                "default": "",
            },
            "filter": {
                "type": "string",
                "description": (
                    "Optional OData filter expression. "
                    "Examples: \"SourceDocumentDataSource eq 'GAO'\", "
                    "\"SourceDocumentDataSource eq 'GAO' and RecStatus ne 'Closed'\", "
                    "\"IsIntegrityRelated eq 'Yes' and RecPriorityFlag in "
                    "('High', 'Critical')\", "
                    "\"SourceDocumentPublishDate ge '2020-01-01' and "
                    "SourceDocumentPublishDate le '2024-12-31'\""
                ),
            },
        },
    },
)

pia_search_titles_tool = types.Tool(
    name="pia_search_titles",
    description="Search the Program Integrity Alliance (PIA) database for document titles only. Returns document titles and metadata without searching the full content. Useful for finding specific documents by title or discovering available documents. Supports complex OData filtering with boolean logic, operators, and grouping.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query text (searches document titles only)",
            },
            "filter": {
                "type": "string",
                "description": (
                    "OData filter expression supporting complex boolean logic. "
                    "Examples: \"SourceDocumentDataSource eq 'GAO'\", "
                    "\"SourceDocumentDataSource eq 'GAO' or "
                    "SourceDocumentDataSource eq 'OIG'\", "
                    "\"SourceDocumentDataSource eq 'GAO' and RecStatus ne 'Closed'\", "
                    "\"SourceDocumentTitle contains 'fraud'\""
                ),
            },
            "page": {
                "type": "integer",
                "description": "Page number (1-based)",
                "default": 1,
            },
            "page_size": {
                "type": "integer",
                "description": "Number of results per page (max 50)",
                "default": 10,
            },
            "limit": {
                "type": "integer",
                "description": "Alternative name for page_size (for compatibility)",
            },
            "include_facets": {
                "type": "boolean",
                "description": "Whether to include facets in response (default False to reduce token usage)",
                "default": False,
            },
        },
        "required": ["query"],
    },
)

pia_search_titles_facets_tool = types.Tool(
    name="pia_search_titles_facets",
    description="Get available facets (filter values) for the PIA database title search. This can help understand what filter values are available before performing title searches. Supports complex OData filtering with boolean logic, operators, and grouping.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Optional query to get facets for (if empty, gets all facets)",
                "default": "",
            },
            "filter": {
                "type": "string",
                "description": (
                    "Optional OData filter expression. "
                    "Examples: \"SourceDocumentDataSource eq 'GAO'\", "
                    "\"SourceDocumentDataSource eq 'GAO' and RecStatus ne 'Closed'\""
                ),
            },
        },
    },
)


async def handle_pia_search_content(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Handle PIA content search requests."""
    try:
        # Prepare the request payload
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "pia_search_content", "arguments": arguments},
        }

        try:
            api_key = settings.API_KEY
            logger.info(
                f"API_KEY retrieved successfully: {api_key[:10]}..."
                if api_key
                else "API_KEY is None or empty"
            )
        except ValueError as e:
            logger.error(f"Failed to retrieve API key: {str(e)}")
            return [
                types.TextContent(
                    type="text",
                    text=f"Error: {str(e)} Configure API key in MCP server settings.",
                )
            ]

        headers = {"Content-Type": "application/json", "x-api-key": api_key}
        logger.info(
            f"Making API call to {settings.PIA_API_URL} with headers: {dict(headers)}"
        )

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


async def handle_pia_search_content_facets(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Handle PIA content search facets requests."""
    try:
        # Prepare the request payload
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "pia_search_content_facets", "arguments": arguments},
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


async def handle_pia_search_titles(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Handle PIA titles search requests."""
    try:
        # Prepare the request payload
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "pia_search_titles", "arguments": arguments},
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
        logger.error(f"HTTP error during PIA titles search: {e}")
        return [
            types.TextContent(
                type="text",
                text=f"HTTP Error {e.response.status_code}: {e.response.text}",
            )
        ]
    except Exception as e:
        logger.error(f"Error during PIA titles search: {e}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_pia_search_titles_facets(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Handle PIA titles search facets requests."""
    try:
        # Prepare the request payload
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "pia_search_titles_facets", "arguments": arguments},
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
        logger.error(f"HTTP error during PIA titles search facets: {e}")
        return [
            types.TextContent(
                type="text",
                text=f"HTTP Error {e.response.status_code}: {e.response.text}",
            )
        ]
    except Exception as e:
        logger.error(f"Error during PIA titles search facets: {e}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

"""Search tool for basic PIA database searches."""

import httpx
import mcp.types as types
from typing import Dict, Any, List
import json
import logging
from ..config import Settings

logger = logging.getLogger(__name__)
settings = Settings()

# Tool definition based on the API response
search_tool = types.Tool(
    name="search",
    description="Search the Program Integrity Alliance (PIA) database and return a list of potentially relevant search results with titles, snippets, and URLs for citation.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "A search query string to find relevant documents in the PIA database"
            }
        },
        "required": ["query"]
    }
)


async def handle_search(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle basic search requests."""
    try:
        # Prepare the request payload
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "search",
                "arguments": arguments
            }
        }
        
        try:
            api_key = settings.API_KEY
        except ValueError as e:
            return [types.TextContent(
                type="text", 
                text=f"Error: {str(e)} Configure API key in MCP server settings."
            )]
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key
        }
        
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            response = await client.post(
                settings.PIA_API_URL,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "error" in result:
                error_msg = result["error"].get("message", "Unknown error")
                return [types.TextContent(type="text", text=f"API Error: {error_msg}")]
            
            if "result" in result:
                # Format the search results nicely
                search_results = result["result"]
                formatted_result = json.dumps(search_results, indent=2, ensure_ascii=False)
                return [types.TextContent(type="text", text=formatted_result)]
            else:
                return [types.TextContent(type="text", text="No results returned from API")]
                
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during search: {e}")
        return [types.TextContent(
            type="text", 
            text=f"HTTP Error {e.response.status_code}: {e.response.text}"
        )]
    except Exception as e:
        logger.error(f"Error during search: {e}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]
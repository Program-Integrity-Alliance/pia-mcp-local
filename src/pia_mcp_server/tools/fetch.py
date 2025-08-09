"""Fetch tool for retrieving specific documents."""

import httpx
import mcp.types as types
from typing import Dict, Any, List
import json
import logging
from ..config import Settings

logger = logging.getLogger(__name__)
settings = Settings()

# Tool definition based on the API response
fetch_tool = types.Tool(
    name="fetch",
    description="Retrieve the full contents of a specific document from the PIA database using its unique identifier.",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "A unique identifier for the document to retrieve"
            }
        },
        "required": ["id"]
    }
)


async def handle_fetch(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle document fetch requests."""
    try:
        # Prepare the request payload
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "fetch",
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
                # Format the document content nicely
                document = result["result"]
                formatted_result = json.dumps(document, indent=2, ensure_ascii=False)
                return [types.TextContent(type="text", text=formatted_result)]
            else:
                return [types.TextContent(type="text", text="No document returned from API")]
                
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during fetch: {e}")
        return [types.TextContent(
            type="text", 
            text=f"HTTP Error {e.response.status_code}: {e.response.text}"
        )]
    except Exception as e:
        logger.error(f"Error during fetch: {e}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]
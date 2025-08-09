"""Rate limiting statistics tool."""

import httpx
import mcp.types as types
from typing import Dict, Any, List
import json
import logging
from ..config import Settings

logger = logging.getLogger(__name__)
settings = Settings()

# Tool definition based on the API response
get_rate_limit_stats_tool = types.Tool(
    name="get_rate_limit_stats",
    description="Get rate limiting statistics and current configuration. Returns JSON structure with rate limiting statistics including request counts, blocked requests, and current limits configuration.",
    inputSchema={
        "type": "object",
        "properties": {}
    }
)


async def handle_get_rate_limit_stats(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle rate limit statistics requests."""
    try:
        # Prepare the request payload
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_rate_limit_stats",
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
                # Format the rate limit stats nicely
                stats = result["result"]
                formatted_result = json.dumps(stats, indent=2, ensure_ascii=False)
                return [types.TextContent(type="text", text=formatted_result)]
            else:
                return [types.TextContent(type="text", text="No rate limit stats returned from API")]
                
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during rate limit stats request: {e}")
        return [types.TextContent(
            type="text", 
            text=f"HTTP Error {e.response.status_code}: {e.response.text}"
        )]
    except Exception as e:
        logger.error(f"Error during rate limit stats request: {e}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]
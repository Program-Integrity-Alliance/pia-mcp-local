"""PIA Search tools for database searches and facets discovery."""

import httpx
import mcp.types as types
from typing import Dict, Any, List
import json
import logging
from importlib.resources import files
from ..config import Settings

logger = logging.getLogger(__name__)
settings = Settings()

# Tool definitions - EXACT copies from remote server
_TOOL_SPECS = json.loads(
    (files("pia_mcp_server.tools") / "tool_specs.json").read_text(encoding="utf-8")
)
_TOOL_SPEC_MAP = {tool["name"]: tool for tool in _TOOL_SPECS["tools"]}


def _build_tool(name: str) -> types.Tool:
    spec = _TOOL_SPEC_MAP[name]
    return types.Tool(
        name=spec["name"],
        description=spec["description"],
        inputSchema=spec["inputSchema"],
        outputSchema=spec.get("outputSchema"),
    )


pia_search_tool = _build_tool("pia_search")
pia_oversight_recommendations_tool = _build_tool("pia_oversight_recommendations")


# Handler functions - thin pass-throughs that forward to the remote server.
async def handle_pia_search(
    arguments: Dict[str, Any],
) -> types.CallToolResult:
    """Handle PIA search requests."""
    return await _forward_to_remote("pia_search", arguments)


async def handle_pia_oversight_recommendations(
    arguments: Dict[str, Any],
) -> types.CallToolResult:
    """Handle PIA oversight recommendations requests."""
    return await _forward_to_remote("pia_oversight_recommendations", arguments)


async def _forward_to_remote(
    tool_name: str, arguments: Dict[str, Any]
) -> types.CallToolResult:
    """Forward tool call to remote MCP server."""
    try:
        # Prepare the request payload
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }

        try:
            api_key = settings.API_KEY
            logger.info(
                "API_KEY retrieved successfully: %s...",
                api_key[:10] if api_key else "API_KEY is None or empty",
            )
        except ValueError as e:
            logger.error("Failed to retrieve API key: %s", str(e))
            raise ValueError(
                f"{str(e)} Configure API key in MCP server settings."
            ) from e

        headers = {"Content-Type": "application/json", "x-api-key": api_key}
        logger.info(
            "Making API call to %s with headers: %s",
            settings.PIA_API_URL,
            dict(headers),
        )

        async with httpx.AsyncClient(
            timeout=settings.REQUEST_TIMEOUT, follow_redirects=True
        ) as client:
            response = await client.post(
                settings.PIA_API_URL, json=payload, headers=headers
            )
            response.raise_for_status()

            result = response.json()

            if "error" in result:
                error_msg = result["error"].get("message", "Unknown error")
                raise ValueError(f"API Error: {error_msg}")

            if "result" in result:
                tool_result = result["result"]
                if not isinstance(tool_result, dict):
                    raise ValueError(
                        "Remote tool call returned unexpected result type."
                    )
                return types.CallToolResult.model_validate(tool_result)
            raise ValueError("No results returned from API")

    except httpx.HTTPStatusError as e:
        logger.error("HTTP error during %s: %s", tool_name, e)
        raise ValueError(
            f"HTTP Error {e.response.status_code}: {e.response.text}"
        ) from e
    except Exception as e:
        logger.error("Error during %s: %s", tool_name, e)
        raise

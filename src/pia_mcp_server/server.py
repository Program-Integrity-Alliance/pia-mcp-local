"""
PIA MCP Server
==============

This module implements an MCP server for interacting with the Program Integrity Alliance API.
"""

import logging
import mcp.types as types
from typing import Dict, Any, List
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions
from mcp.server.stdio import stdio_server
from .config import Settings
from .tools import (
    handle_pia_search_content,
    handle_pia_search_content_facets,
    handle_pia_search_titles,
    handle_pia_search_titles_facets,
    handle_pia_search_content_executive_orders,
)
from .tools import (
    pia_search_content_tool,
    pia_search_content_facets_tool,
    pia_search_titles_tool,
    pia_search_titles_facets_tool,
    pia_search_content_executive_orders_tool,
)
from .prompts.handlers import list_prompts as handler_list_prompts
from .prompts.handlers import get_prompt as handler_get_prompt

settings = Settings()
logger = logging.getLogger("pia-mcp-server")
logger.setLevel(logging.INFO)
server = Server(settings.APP_NAME)


@server.list_prompts()
async def list_prompts() -> List[types.Prompt]:
    """List available prompts."""
    return await handler_list_prompts()


@server.get_prompt()
async def get_prompt(
    name: str, arguments: Dict[str, str] | None = None
) -> types.GetPromptResult:
    """Get a specific prompt with arguments."""
    return await handler_get_prompt(name, arguments)


@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available PIA research tools."""
    return [
        pia_search_content_tool,
        pia_search_content_facets_tool,
        pia_search_titles_tool,
        pia_search_titles_facets_tool,
        pia_search_content_executive_orders_tool,
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls for PIA research functionality."""
    logger.debug(f"Calling tool {name} with arguments {arguments}")
    try:
        if name == "pia_search_content":
            return await handle_pia_search_content(arguments)
        elif name == "pia_search_content_facets":
            return await handle_pia_search_content_facets(arguments)
        elif name == "pia_search_titles":
            return await handle_pia_search_titles(arguments)
        elif name == "pia_search_titles_facets":
            return await handle_pia_search_titles_facets(arguments)
        elif name == "pia_search_content_executive_orders":
            return await handle_pia_search_content_executive_orders(arguments)
        else:
            return [types.TextContent(type="text", text=f"Error: Unknown tool {name}")]
    except Exception as e:
        logger.error(f"Tool error: {str(e)}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the server async context."""
    async with stdio_server() as streams:
        await server.run(
            streams[0],
            streams[1],
            InitializationOptions(
                server_name=settings.APP_NAME,
                server_version=settings.APP_VERSION,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(resources_changed=True),
                    experimental_capabilities={},
                ),
            ),
        )

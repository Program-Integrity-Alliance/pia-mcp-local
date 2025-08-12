"""
PIA MCP Server Tools
===================

This module provides tools for interacting with the Program Integrity Alliance API.
"""

from .search_tools import (
    handle_pia_search_content,
    pia_search_content_tool,
    handle_pia_search_content_facets,
    pia_search_content_facets_tool,
    handle_pia_search_titles,
    pia_search_titles_tool,
    handle_pia_search_titles_facets,
    pia_search_titles_facets_tool,
)

__all__ = [
    "handle_pia_search_content",
    "pia_search_content_tool",
    "handle_pia_search_content_facets",
    "pia_search_content_facets_tool",
    "handle_pia_search_titles",
    "pia_search_titles_tool",
    "handle_pia_search_titles_facets",
    "pia_search_titles_facets_tool",
]

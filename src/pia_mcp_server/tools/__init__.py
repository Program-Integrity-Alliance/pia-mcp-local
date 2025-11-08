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
    handle_pia_search_content_gao,
    pia_search_content_gao_tool,
    handle_pia_search_content_oig,
    pia_search_content_oig_tool,
    handle_pia_search_content_crs,
    pia_search_content_crs_tool,
    handle_pia_search_content_doj,
    pia_search_content_doj_tool,
    handle_pia_search_content_congress,
    pia_search_content_congress_tool,
    handle_pia_search_content_executive_orders,
    pia_search_content_executive_orders_tool,
    handle_search,
    search_tool,
    handle_fetch,
    fetch_tool,
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
    "handle_pia_search_content_gao",
    "pia_search_content_gao_tool",
    "handle_pia_search_content_oig",
    "pia_search_content_oig_tool",
    "handle_pia_search_content_crs",
    "pia_search_content_crs_tool",
    "handle_pia_search_content_doj",
    "pia_search_content_doj_tool",
    "handle_pia_search_content_congress",
    "pia_search_content_congress_tool",
    "handle_pia_search_content_executive_orders",
    "pia_search_content_executive_orders_tool",
    "handle_search",
    "search_tool",
    "handle_fetch",
    "fetch_tool",
]

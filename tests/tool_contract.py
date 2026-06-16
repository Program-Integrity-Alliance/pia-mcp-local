"""Shared tool-contract constants used by both unit and integration tests.

This is the single source of truth for which tools the server exposes and
which of them return structured JSON output, so the unit schema tests and the
live integration tests stay in sync.
"""

# Every tool the local proxy advertises (mirrors the remote server).
EXPECTED_TOOL_NAMES = {
    "pia_search_content",
    "pia_oversight_recommendations",
    "pia_search_content_wide",
    "pia_search_content_facets",
    "pia_search_titles",
    "pia_search_titles_facets",
    "pia_search_content_gao",
    "pia_search_content_oig",
    "pia_search_content_crs",
    "pia_search_content_doj",
    "pia_search_content_congress",
    "pia_search_content_executive_orders",
    "search",
    "fetch",
    "pia_filter_snippets",
}

# Tools that intentionally do NOT declare an outputSchema. pia_filter_snippets
# returns plain text content (it has no structured output), so it is the only
# tool exempt from the outputSchema contract.
TOOLS_WITHOUT_OUTPUT_SCHEMA = {"pia_filter_snippets"}

# Content/search tools whose structuredContent is {"output": {"results": [...]}}.
# Mapped to a broad query that reliably returns results from the live index.
CONTENT_RESULT_TOOLS = {
    "pia_search_content": "improper payments",
    "pia_search_content_wide": "fraud",
    "pia_search_titles": "fraud",
    "pia_search_content_gao": "audit",
    "pia_search_content_oig": "oversight",
    "pia_search_content_crs": "policy",
    "pia_search_content_doj": "fraud",
    "pia_search_content_congress": "appropriations",
    "pia_search_content_executive_orders": "executive order",
    "pia_oversight_recommendations": "fraud",
}

# Facet-discovery tools whose structuredContent is {"output": {"facets": {...}}}.
FACET_TOOLS = {
    "pia_search_content_facets": "fraud",
    "pia_search_titles_facets": "fraud",
}

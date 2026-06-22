"""Shared tool-contract constants used by both unit and integration tests.

Single source of truth for which tools the server exposes and which return
structured results, so the unit schema tests and the live integration tests
stay in sync.
"""

# Every tool the local proxy advertises (mirrors the remote server).
EXPECTED_TOOL_NAMES = {
    "pia_search",
    "pia_oversight_recommendations",
    "search",
    "fetch",
}

# Tools that intentionally do NOT declare an outputSchema. Every current tool
# declares one, so this set is empty; it stays here so the schema tests keep
# tolerating a future schema-less tool without code changes.
TOOLS_WITHOUT_OUTPUT_SCHEMA: set[str] = set()

# Content/search tools whose structuredContent is {"output": {"results": [...]}}.
# Mapped to a broad query that reliably returns results from the live index.
CONTENT_RESULT_TOOLS = {
    "pia_search": "improper payments",
    "pia_oversight_recommendations": "fraud",
}

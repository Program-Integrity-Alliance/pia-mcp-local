"""Live integration tests against the remote PIA MCP server.

These tests make real network calls through the same forwarding code path the
server uses in production, exercising the configured ``PIA_API_URL`` and
``X-API-KEY`` authentication.

They require a valid key in the ``PIA_API_KEY`` environment variable (supplied
in CI via the ``PIA_API_KEY`` GitHub Actions secret) and are skipped
automatically when no key is configured.

What they assert:
  * the remote ``tools/list`` matches the local snapshot and every structured
    tool advertises an outputSchema;
  * each search/content tool returns real, non-empty results;
  * the facet tools return facets;
  * ``fetch`` returns document text for a real result id.
"""

import os

import httpx
import pytest

from pia_mcp_server.config import Settings
from pia_mcp_server.server import list_tools
from pia_mcp_server.tools import search_tools as st
from tests.tool_contract import (
    CONTENT_RESULT_TOOLS,
    EXPECTED_TOOL_NAMES,
    FACET_TOOLS,
    TOOLS_WITHOUT_OUTPUT_SCHEMA,
)

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.getenv("PIA_API_KEY"),
        reason="PIA_API_KEY not set; skipping live integration tests",
    ),
]

settings = Settings()


async def _remote_tools_list() -> list[dict]:
    """Fetch the tool list directly from the remote server (JSON-RPC)."""
    payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    headers = {"Content-Type": "application/json", "x-api-key": settings.API_KEY}
    async with httpx.AsyncClient(
        timeout=settings.REQUEST_TIMEOUT, follow_redirects=True
    ) as client:
        response = await client.post(
            settings.PIA_API_URL, json=payload, headers=headers
        )
        response.raise_for_status()
        return response.json()["result"]["tools"]


async def test_remote_tools_list_matches_local_snapshot():
    """Remote tool list, local snapshot, and expected set all agree."""
    remote = await _remote_tools_list()
    remote_names = {tool["name"] for tool in remote}
    local_names = {tool.name for tool in await list_tools()}

    assert remote_names == EXPECTED_TOOL_NAMES
    assert local_names == EXPECTED_TOOL_NAMES


async def test_remote_structured_tools_advertise_output_schema():
    """Every structured tool on the remote advertises an object outputSchema."""
    for tool in await _remote_tools_list():
        if tool["name"] in TOOLS_WITHOUT_OUTPUT_SCHEMA:
            continue
        output_schema = tool.get("outputSchema")
        assert output_schema, f"remote {tool['name']} is missing an outputSchema"
        assert output_schema.get("type") == "object"


@pytest.mark.parametrize("tool_name,query", sorted(CONTENT_RESULT_TOOLS.items()))
async def test_content_tool_returns_live_results(tool_name, query):
    """Each content/search tool returns real, non-empty results."""
    handler = getattr(st, f"handle_{tool_name}")
    result = await handler({"query": query})

    assert result.isError is not True
    assert result.structuredContent is not None
    output = result.structuredContent["output"]
    results = output["results"]
    assert isinstance(results, list)
    assert len(results) > 0, f"{tool_name} returned no results for {query!r}"
    first = results[0]
    assert first.get("title"), f"{tool_name} result missing title"
    assert first.get("url"), f"{tool_name} result missing url"


async def test_search_tool_returns_live_results():
    """The simple ``search`` tool returns top-level results."""
    result = await st.handle_search({"query": "medicaid fraud"})

    assert result.isError is not True
    results = result.structuredContent["results"]
    assert isinstance(results, list)
    assert len(results) > 0
    assert results[0].get("title")


@pytest.mark.parametrize("tool_name,query", sorted(FACET_TOOLS.items()))
async def test_facet_tool_returns_live_facets(tool_name, query):
    """Each facet tool returns a non-empty facets mapping."""
    handler = getattr(st, f"handle_{tool_name}")
    result = await handler({"query": query})

    assert result.isError is not True
    facets = result.structuredContent["output"]["facets"]
    assert isinstance(facets, dict)
    assert len(facets) > 0, f"{tool_name} returned no facets"


async def test_fetch_returns_document_text():
    """``fetch`` returns document content for a real result id."""
    search = await st.handle_pia_search_content({"query": "improper payments"})
    doc_id = search.structuredContent["output"]["results"][0]["id"]

    fetched = await st.handle_fetch({"id": doc_id})

    assert fetched.isError is not True
    document = fetched.structuredContent
    assert document.get("id")
    assert document.get("text"), "fetch returned no document text"

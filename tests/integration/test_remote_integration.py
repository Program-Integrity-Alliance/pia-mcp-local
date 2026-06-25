"""Live integration tests against the remote PIA MCP server.

These tests make real network calls through the same forwarding code path the
server uses in production, exercising the configured ``PIA_API_URL`` and
``X-API-KEY`` authentication.

They require a valid key in the ``PIA_API_KEY`` environment variable (supplied
in CI via the ``PIA_API_KEY`` GitHub Actions secret) and are skipped
automatically when no key is configured.

What they assert:
  * every tool the proxy advertises exists on the remote and advertises an
    outputSchema;
  * each search/content tool returns real, non-empty results.
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


async def test_local_snapshot_matches_expected_and_exists_on_remote():
    """The proxy advertises exactly EXPECTED_TOOL_NAMES, and every advertised
    tool exists on the configured remote.

    The snapshot intentionally tracks the upstream build being released next, so
    it may *lead* the currently-deployed remote (which can still expose tools the
    snapshot has dropped). The contract that matters is that everything the proxy
    advertises is actually callable on the remote — i.e. advertised ⊆ remote.
    """
    remote_names = {tool["name"] for tool in await _remote_tools_list()}
    local_names = {tool.name for tool in await list_tools()}

    assert local_names == EXPECTED_TOOL_NAMES
    missing = EXPECTED_TOOL_NAMES - remote_names
    assert not missing, f"advertised tools not present on remote: {sorted(missing)}"


async def test_advertised_structured_tools_advertise_output_schema():
    """Every structured tool the proxy advertises has an object outputSchema on
    the remote. Remote-only tools the proxy does not expose are ignored."""
    for tool in await _remote_tools_list():
        if tool["name"] not in EXPECTED_TOOL_NAMES:
            continue
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

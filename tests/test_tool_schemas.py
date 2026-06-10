"""Unit tests asserting the tool definitions advertise valid JSON schemas.

These do not touch the network: they validate the local tool snapshot that the
server serves from ``tool_specs.json``. They guarantee every tool exposes a
valid inputSchema and that every structured tool exposes a valid outputSchema.
"""

import pytest
from jsonschema import Draft202012Validator

from pia_mcp_server.server import list_tools
from tests.tool_contract import EXPECTED_TOOL_NAMES, TOOLS_WITHOUT_OUTPUT_SCHEMA


async def test_expected_tools_are_registered():
    """The server advertises exactly the expected set of tools."""
    tools = await list_tools()
    assert {tool.name for tool in tools} == EXPECTED_TOOL_NAMES


async def test_every_tool_has_a_valid_input_schema():
    """Every tool declares an object inputSchema that is a valid JSON Schema."""
    for tool in await list_tools():
        assert tool.inputSchema, f"{tool.name} is missing an inputSchema"
        assert (
            tool.inputSchema.get("type") == "object"
        ), f"{tool.name} inputSchema is not an object"
        # Raises SchemaError if the schema itself is malformed.
        Draft202012Validator.check_schema(tool.inputSchema)


async def test_structured_tools_have_a_valid_output_schema():
    """Every structured tool declares a valid object outputSchema.

    pia_filter_snippets returns plain text content and is the only tool
    exempt from the outputSchema contract.
    """
    for tool in await list_tools():
        if tool.name in TOOLS_WITHOUT_OUTPUT_SCHEMA:
            assert (
                tool.outputSchema is None
            ), f"{tool.name} unexpectedly declares an outputSchema"
            continue

        assert tool.outputSchema, f"{tool.name} is missing an outputSchema"
        assert (
            tool.outputSchema.get("type") == "object"
        ), f"{tool.name} outputSchema is not an object"
        Draft202012Validator.check_schema(tool.outputSchema)


@pytest.mark.parametrize("tool_name", sorted(TOOLS_WITHOUT_OUTPUT_SCHEMA))
async def test_unstructured_tools_are_documented(tool_name):
    """Tools exempt from the outputSchema contract are actually registered."""
    assert tool_name in EXPECTED_TOOL_NAMES

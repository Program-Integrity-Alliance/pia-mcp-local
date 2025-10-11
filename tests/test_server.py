"""Tests for server module."""

import pytest


@pytest.mark.asyncio
async def test_server_can_be_imported():
    """Test that server module can be imported successfully."""
    try:
        from pia_mcp_server import server

        assert server is not None
        # Basic smoke test that the server object exists
        assert hasattr(server, "server")
    except ImportError as e:
        pytest.fail(f"Failed to import server module: {e}")


@pytest.mark.asyncio
async def test_basic_functionality():
    """Test basic server functionality."""
    # This is a placeholder test that ensures the module structure is correct
    # More detailed tests should be added as the codebase stabilizes
    assert True

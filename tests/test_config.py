"""Tests for configuration module."""

import pytest
from pia_mcp_server.config import Settings


def test_default_settings():
    """Test default configuration values."""
    settings = Settings()
    
    assert settings.APP_NAME == "pia-mcp-server"
    assert settings.APP_VERSION == "0.1.0"
    assert settings.PIA_API_URL == "https://mcp.programintegrity.org/"
    assert settings.MAX_RESULTS == 50
    assert settings.REQUEST_TIMEOUT == 60


def test_api_key_property_no_args():
    """Test API key property without arguments raises error."""
    settings = Settings()
    
    # With no API key argument should raise ValueError
    with pytest.raises(ValueError, match="PIA API key is required"):
        api_key = settings.API_KEY


def test_api_key_from_args(monkeypatch):
    """Test API key loaded from command line arguments."""
    import sys
    monkeypatch.setattr(sys, 'argv', ['pia-mcp-server', '--api-key', 'test_key_123'])
    
    settings = Settings()
    
    assert settings.API_KEY == "test_key_123"
"""Configuration settings for the PIA MCP server."""

import sys
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Server configuration settings."""

    APP_NAME: str = "pia-mcp-server"
    APP_VERSION: str = "0.1.0"
    MAX_RESULTS: int = 50
    BATCH_SIZE: int = 20
    REQUEST_TIMEOUT: int = 60
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # PIA Server Configuration
    PIA_API_URL: str = "https://mcp.programintegrity.org/"
    
    model_config = SettingsConfigDict(extra="allow")

    def _get_api_key_from_args(self) -> str | None:
        """Extract API key from command line arguments.

        Returns:
            str | None: The API key if specified in arguments, None otherwise.
        """
        args = sys.argv[1:]

        # If not enough arguments
        if len(args) < 2:
            return None

        # Look for the --api-key option
        try:
            api_key_index = args.index("--api-key")
        except ValueError:
            return None

        # Early return if --api-key is the last argument
        if api_key_index + 1 >= len(args):
            return None

        try:
            return args[api_key_index + 1]
        except (TypeError, ValueError) as e:
            logger.warning(f"Invalid API key format: {e}")

        return None

    @property
    def API_KEY(self) -> str:
        """Get the API key from command line arguments."""
        api_key = self._get_api_key_from_args()
        if not api_key:
            raise ValueError("PIA API key is required. Please provide --api-key argument.")
        return api_key
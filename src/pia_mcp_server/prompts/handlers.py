"""Prompt handlers for the PIA MCP server.

Prompts are served from a local snapshot (``prompt_specs.json``) refreshed from
the remote MCP server, mirroring how tools are served from ``tool_specs.json``.
"""

import json
import logging
from importlib.resources import files
from typing import Dict, List

import mcp.types as types

logger = logging.getLogger(__name__)

# Prompt definitions - snapshot of the remote server's prompts/list + content.
_PROMPT_SPECS = json.loads(
    (files("pia_mcp_server.prompts") / "prompt_specs.json").read_text(encoding="utf-8")
)
_PROMPT_MAP = {prompt["name"]: prompt for prompt in _PROMPT_SPECS["prompts"]}


async def list_prompts() -> List[types.Prompt]:
    """List available prompts from the local snapshot."""
    prompts = []
    for spec in _PROMPT_SPECS["prompts"]:
        arguments = [
            types.PromptArgument(
                name=arg["name"],
                description=arg.get("description"),
                required=arg.get("required", False),
            )
            for arg in spec.get("arguments", [])
        ]
        prompts.append(
            types.Prompt(
                name=spec["name"],
                description=spec.get("description", ""),
                arguments=arguments,
            )
        )
    return prompts


async def get_prompt(
    name: str, arguments: Dict[str, str] | None = None
) -> types.GetPromptResult:
    """Return a prompt's messages from the local snapshot."""
    spec = _PROMPT_MAP.get(name)
    if spec is None:
        raise ValueError(f"Prompt '{name}' not found")

    messages = [
        types.PromptMessage.model_validate(message) for message in spec["messages"]
    ]
    return types.GetPromptResult(
        description=spec.get("description", ""),
        messages=messages,
    )

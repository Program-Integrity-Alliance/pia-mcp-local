#!/usr/bin/env python3
"""
Refresh the local tool specs snapshot from the remote MCP server.

Usage:
    python utils/refresh_tools.py [--output PATH]

Environment Variables:
    PIA_API_KEY: API key for accessing the remote server (required)
"""

import argparse
import json
import os
from pathlib import Path

import httpx

REMOTE_URL = "https://www.programintegrity.org/mcp"

# Tools intentionally NOT exposed by this local server. ``search`` and ``fetch``
# exist on the remote only to satisfy OpenAI's ChatGPT MCP search/fetch spec;
# this proxy exposes the richer ``pia_*`` tools instead, so they are excluded
# from the snapshot (and must stay excluded on every refresh).
EXCLUDED_TOOLS = {"search", "fetch"}


def fetch_tools(api_key: str) -> dict:
    payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    headers = {"Content-Type": "application/json", "x-api-key": api_key}

    response = httpx.post(
        REMOTE_URL,
        json=payload,
        headers=headers,
        timeout=60,
        follow_redirects=True,
    )
    response.raise_for_status()
    result = response.json()

    if "error" in result:
        message = result["error"].get("message", "Unknown error")
        raise RuntimeError(f"API Error: {message}")

    if "result" not in result:
        raise RuntimeError("No tools returned from server.")

    return result["result"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh local tool specs snapshot")
    parser.add_argument(
        "--output",
        default="src/pia_mcp_server/tools/tool_specs.json",
        help="Output path for tool specs (default: src/pia_mcp_server/tools/tool_specs.json)",
    )
    args = parser.parse_args()

    api_key = os.getenv("PIA_API_KEY")
    if not api_key:
        raise RuntimeError("PIA_API_KEY environment variable is required.")

    tools = fetch_tools(api_key)

    excluded = [t for t in tools.get("tools", []) if t["name"] in EXCLUDED_TOOLS]
    tools["tools"] = [
        t for t in tools.get("tools", []) if t["name"] not in EXCLUDED_TOOLS
    ]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(tools, indent=2), encoding="utf-8")

    print(f"Saved {len(tools['tools'])} tools to {output_path}")
    if excluded:
        print(f"Excluded {len(excluded)} tools: {[t['name'] for t in excluded]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

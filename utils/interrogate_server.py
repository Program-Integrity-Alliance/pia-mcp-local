#!/usr/bin/env python3
"""
Script to interrogate the remote MCP server and discover available tools and prompts.

This utility helps developers understand what tools and prompts are available on the
remote PIA MCP server, making it easier to implement matching functionality in the
local server.

Usage:
    python utils/interrogate_server.py [--output-dir OUTPUT_DIR]

Environment Variables:
    PIA_API_KEY: API key for accessing the remote server (required)

The script will:
1. Query the remote server for available tools and prompts
2. Save the results to JSON files for analysis
3. Display a summary of what was found
"""

import asyncio
import httpx
import json
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


async def list_remote_tools(api_key: str):
    """List all available tools from the remote MCP server."""

    # Prepare the JSON-RPC request to list tools
    payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}

    headers = {"Content-Type": "application/json", "x-api-key": api_key}

    url = "https://mcp.programintegrity.org/"

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            print(f"Making request to {url}")
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()

            if "error" in result:
                print(f"API Error: {result['error']}")
                return None

            if "result" in result:
                tools = result["result"]
                print("Available tools from remote server:")
                print(json.dumps(tools, indent=2))
                return tools
            else:
                print("No tools returned from server")
                return None

    except Exception as e:
        print(f"Error querying remote server: {e}")
        return None


async def list_remote_prompts(api_key: str):
    """List all available prompts from the remote MCP server."""

    payload = {"jsonrpc": "2.0", "id": 1, "method": "prompts/list", "params": {}}

    headers = {"Content-Type": "application/json", "x-api-key": api_key}

    url = "https://mcp.programintegrity.org/"

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()

            if "error" in result:
                print(f"API Error: {result['error']}")
                return None

            if "result" in result:
                prompts = result["result"]
                print("Available prompts from remote server:")
                print(json.dumps(prompts, indent=2))
                return prompts
            else:
                print("No prompts returned from server")
                return None

    except Exception as e:
        print(f"Error querying remote server prompts: {e}")
        return None


async def get_prompt_content(api_key: str, prompt_name: str):
    """Get the content of a specific prompt from the remote server."""

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "prompts/get",
        "params": {"name": prompt_name, "arguments": {}},
    }

    headers = {"Content-Type": "application/json", "x-api-key": api_key}

    url = "https://mcp.programintegrity.org/"

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()
            return result

    except Exception as e:
        print(f"Error getting prompt {prompt_name}: {e}")
        return None


async def main():
    """Main function to interrogate the server."""
    parser = argparse.ArgumentParser(
        description="Interrogate the remote PIA MCP server to discover tools and prompts"
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to save output files (default: current directory)",
    )

    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    # Get API key from environment
    api_key = os.getenv("PIA_API_KEY")
    if not api_key:
        print("Error: Please set PIA_API_KEY environment variable")
        print("You can also create a .env file with: PIA_API_KEY=your_key_here")
        return 1

    print("Interrogating remote PIA MCP server...")

    # Get tools
    tools = await list_remote_tools(api_key)
    if tools and "tools" in tools:
        tools_file = output_dir / "remote_tools.json"
        with open(tools_file, "w") as f:
            json.dump(tools, f, indent=2)
        print(f"\nTools saved to {tools_file}")

        print(f"\nFound {len(tools['tools'])} tools:")
        for tool in tools["tools"]:
            print(
                f"- {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}"
            )

    # Get prompts
    prompts = await list_remote_prompts(api_key)
    if prompts and "prompts" in prompts:
        prompts_file = output_dir / "remote_prompts.json"
        with open(prompts_file, "w") as f:
            json.dump(prompts, f, indent=2)
        print(f"\nPrompts saved to {prompts_file}")

        print(f"\nFound {len(prompts['prompts'])} prompts:")
        for prompt in prompts["prompts"]:
            print(
                f"- {prompt.get('name', 'Unknown')}: {prompt.get('description', 'No description')}"
            )

        # Get detailed content for each prompt
        prompt_details = {}
        for prompt in prompts["prompts"]:
            prompt_name = prompt.get("name")
            if prompt_name:
                print(f"\nGetting content for prompt: {prompt_name}")
                content = await get_prompt_content(api_key, prompt_name)
                if content:
                    prompt_details[prompt_name] = content

        if prompt_details:
            prompt_details_file = output_dir / "remote_prompt_details.json"
            with open(prompt_details_file, "w") as f:
                json.dump(prompt_details, f, indent=2)
            print(f"\nPrompt details saved to {prompt_details_file}")

    print(f"\nInterrogation complete! Check the output files in {output_dir}")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

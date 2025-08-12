"""Prompt handlers for the PIA MCP server."""

import mcp.types as types
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

# Available prompts for PIA MCP server
AVAILABLE_PROMPTS = [
    {
        "name": "summarization_guidance",
        "description": "Provides guidance on how to summarize information from PIA search results with proper citations",
        "arguments": [],
    },
    {
        "name": "search_guidance",
        "description": "Provides guidance on how to perform PIA searches with or without filters",
        "arguments": [],
    },
]


async def list_prompts() -> List[types.Prompt]:
    """List all available prompts."""
    prompts = []

    for prompt_data in AVAILABLE_PROMPTS:
        # Convert arguments to proper format
        arguments = []
        for arg in prompt_data["arguments"]:
            arguments.append(
                types.PromptArgument(
                    name=arg["name"],
                    description=arg["description"],
                    required=arg["required"],
                )
            )

        prompt = types.Prompt(
            name=prompt_data["name"],
            description=prompt_data["description"],
            arguments=arguments,
        )
        prompts.append(prompt)

    return prompts


async def get_prompt(
    name: str, arguments: Dict[str, str] | None = None
) -> types.GetPromptResult:
    """Get a specific prompt with its content."""
    # Find the prompt
    prompt_data = None
    for p in AVAILABLE_PROMPTS:
        if p["name"] == name:
            prompt_data = p
            break

    if not prompt_data:
        raise ValueError(f"Prompt '{name}' not found")

    arguments = arguments or {}

    # Generate prompt content based on the type
    if name == "summarization_guidance":
        content = _generate_summarization_guidance()
    elif name == "search_guidance":
        content = _generate_search_guidance()
    else:
        content = f"Prompt template for {name} - implement specific logic based on arguments: {arguments}"

    return types.GetPromptResult(
        description=prompt_data["description"],
        messages=[
            types.PromptMessage(
                role="user", content=types.TextContent(type="text", text=content)
            )
        ],
    )


def _generate_summarization_guidance() -> str:
    """Generate summarization guidance prompt."""
    return """You are an assistant that summarizes information **only** from the provided search results.

Your task:
1. **Only include facts that appear in the provided search results.**
   - Do NOT use prior knowledge or make assumptions.
   - If a fact is not in the search results, exclude it entirely.

2. **Every factual statement must have at least one inline citation in the format**: [n]
   - Where n matches the numbered source in the References section.
   - Multiple citations are allowed, e.g., [1][3].

3. **References section format:**
   - Numbered list matching the inline citations.
   - **Each reference on a separate line**.
   - Each reference must include:
     - **Document title**
     - **Page number** (or "n/a" if page not given in source)
     - **Source name** (publisher, organization, or site)
     - **URL** — exactly the URL given in the search results.

4. **Output format:**
   - A concise **Summary** section with inline citations [n].
   - A **References** section in the required format.

5. **Style guidelines:**
   - Be objective and factual.
   - No speculation, filler, or unrelated information.
   - Use clear, precise language.
   - Organize logically (group related facts together).
   - Ensure all facts have at least one supporting citation.

Input to use:
<SEARCH_RESULTS>

Output template:
---
Summary:
<Your fact-based summary here with inline [n] citations>

References:
[1] Document Title — Page X — Source Name — URL
[2] Document Title — Page X — Source Name — URL
[3] Document Title — Page X — Source Name — URL
...
---

Remember:
- Do not invent URLs — copy exactly from the provided search results.
- Do not merge facts without maintaining accurate citations.
- If you can't find enough information for a point, omit it entirely."""


def _generate_search_guidance() -> str:
    """Generate search guidance prompt."""
    return """You can perform searches using the PIA Search tools with or without filters.

General rules:
- Run an **unfiltered search** by default if no filter criteria are mentioned in the user's request.
- If the user's request includes any specific filter criteria (e.g., agency name, year, category):
  1. Call `pia_search_content_facets` or `pia_search_titles_facets` once to discover the filterable field names and allowed values.
  2. Use these to build a valid OData filter expression.
  3. Call the search tool with the filter applied.

Available search tools:
- `pia_search_content`: Search within document content and recommendations
- `pia_search_content_facets`: Get available filter values for content search
- `pia_search_titles`: Search document titles only (faster, good for discovery)
- `pia_search_titles_facets`: Get available filter values for title search

Process for applying filters:

1. **Detect filter intent**:
   - Examine the user's query for references to agencies, dates, categories, or other filterable attributes.
   - If such references are present, treat the search as **filtered**.

2. **Discover filterable fields and values** (only if filtering):
   - Call the appropriate facets tool (one time per session unless filters change).
   - Review the output to see:
     - Field names that support filtering.
     - Possible values for each field.

3. **Build the filter expression**:
   - Use **only field names and values** returned by the facets tools.
   - Construct the filter in **OData syntax**:
     - `SourceDocumentDataSource eq 'GAO'`
     - `(SourceDocumentDataSource eq 'GAO' or SourceDocumentDataSource eq 'OIG') and SourceDocumentPublishDate ge '2020-01-01'`
   - Use correct operators: `eq`, `ne`, `gt`, `ge`, `lt`, `le`, `and`, `or`.
   - Wrap string values in single quotes `'value'`.

4. **Execute the filtered search**:
   - Pass the OData filter string to the search tool's `filter` parameter.
   - Example:
     ```
     {{
       "query": "fraud detection",
       "filter": "SourceDocumentDataSource eq 'GAO' and SourceDocumentPublishDate ge '2021-01-01'"
     }}
     ```

5. **Fallback to unfiltered search**:
   - If the filtered search returns no results **and** you haven't yet run an unfiltered search for this query:
     - Run the same query without the filter.
     - Inform the user you are showing unfiltered results because no matches were found with the filter.

6. **Validation**:
   - Never use a field or value not provided by the facets tools.
   - If the user requests a filter that doesn't exist in facets, explain it's not available and offer an unfiltered search instead.

Goal:
- Default to unfiltered search unless filter criteria are clearly present in the query.
- Always validate filter fields/values before applying them.
- Fall back to unfiltered if filtering produces zero results and it hasn't already been run.

"""

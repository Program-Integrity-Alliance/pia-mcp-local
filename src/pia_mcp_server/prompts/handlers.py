"""Prompt handlers for the PIA MCP server."""

import mcp.types as types
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

# Available prompts for PIA MCP server - EXACT copies from remote server
AVAILABLE_PROMPTS = [
    {
        "name": "summarization_guidance",
        "description": "Provides guidance on how to summarize information from PIA search results with proper citations",
        "arguments": [],
    },
    {
        "name": "content_search_guidance",
        "description": "Provides guidance on how to perform PIA content searches with or without filters",
        "arguments": [],
    },
    {
        "name": "titles_search_guidance",
        "description": "Provides guidance on how to search PIA document titles to discover available documents",
        "arguments": [],
    },
    {
        "name": "recommendations_guidance",
        "description": "Provides guidance for questions about oversight recommendations data and how to search for recommendation information",
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
    # Find the prompt
    prompt_data = None
    for p in AVAILABLE_PROMPTS:
        if p["name"] == name:
            prompt_data = p
            break

    if not prompt_data:
        raise ValueError(f"Prompt '{name}' not found")

    arguments = arguments or {}

    # Generate prompt content based on the type - EXACT content from remote server
    if name == "summarization_guidance":
        content = _generate_summarization_guidance()
    elif name == "content_search_guidance":
        content = _generate_content_search_guidance()
    elif name == "titles_search_guidance":
        content = _generate_titles_search_guidance()
    elif name == "recommendations_guidance":
        content = _generate_recommendations_guidance()
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
    """Generate summarization guidance prompt - EXACT content from remote server."""
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
   - **Each reference on a separate line** in the format: [n] Document Title — Page X — Source Name — URL
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
...
---

Remember:
- Do not invent URLs — copy exactly from the provided search results.
- Do not merge facts without maintaining accurate citations.
- If you can't find enough information for a point, omit it entirely."""


def _generate_content_search_guidance() -> str:
    """Generate content search guidance prompt - EXACT content from remote server."""
    return """You can perform searches using the PIA Search tools with or without filters.

**Search Tool Selection**:
- Use `pia_search_content` and `pia_search_content_facets` for searching document content and recommendations
- Use `pia_search_titles` and `pia_search_titles_facets` to find document titles and discover available documents
- To find what document titles are available, you can call the pia_search_titles tool and its pia_search_titles_facets to see what fields you can filter with. If the user is obviously referencing a specific document, you can filter this tool using SourceDocumentTitle

**General rules**:
- Run an **unfiltered search** by default if no filter criteria are mentioned in the user's request.
- If the user's request includes any specific filter criteria (e.g., agency name, year, category):
  1. Call `pia_search_content_facets` or `pia_search_titles_facets` once to discover the filterable field names and allowed values.
  2. Use these to build a valid OData filter expression.
  3. Call the appropriate search tool with the filter applied.

**Process for applying filters**:

1. **Detect filter intent**:
   - Examine the user's query for references to agencies, dates, categories, or other filterable attributes.
   - If such references are present, treat the search as **filtered**.

2. **Discover filterable fields and values** (only if filtering):
   - Call the `pia_search_content_facets` or `pia_search_titles_facets` tool (one time per session unless filters change).
   - Review the output to see:
     - Field names that support filtering.
     - Possible values for each field.

3. **Build the filter expression**:
   - Use **only field names and values** returned by the facets tools.
   - Construct the filter in **OData syntax**:
     - `data_source eq 'GAO'`
     - `(data_source eq 'GAO' or data_source eq 'CIGIE') and year ge 2020`
   - Use correct operators: `eq`, `ne`, `gt`, `ge`, `lt`, `le`, `and`, `or`.
   - Wrap string values in single quotes `'value'`.

4. **Execute the filtered search**:
   - Pass the OData filter string to the search tool's `filter` parameter.
   - Example:
     ```
     {
       "query": "fraud detection",
       "filter": "data_source eq 'GAO' and year ge 2021"
     }
     ```

5. **Fallback to unfiltered search**:
   - If the filtered search returns no results **and** you haven't yet run an unfiltered search for this query:
     - Run the same query without the filter.
     - Inform the user you are showing unfiltered results because no matches were found with the filter.

6. **Validation**:
   - Never use a field or value not provided by the facets tools.
   - If the user requests a filter that doesn't exist in the facets, explain it's not available and offer an unfiltered search instead.

**Goal**:
- Default to unfiltered search unless filter criteria are clearly present in the query.
- Always validate filter fields/values before applying them.
- Fall back to unfiltered if filtering produces zero results and it hasn't already been run."""


def _generate_titles_search_guidance() -> str:
    """Generate titles search guidance prompt - EXACT content from remote server."""
    return """You can search document titles using the PIA title search tools to discover what documents are available.

**Title Search Tool Selection**:
- Use `pia_search_titles` to search for document titles only (not content)
- Use `pia_search_titles_facets` to see what fields you can filter with for title searches
- This is ideal for finding specific documents or discovering available documents

**When to use title search**:
- User asks "What documents are available?" or "Show me all documents"
- User references a specific document title or wants to find documents by title
- User wants to browse or discover available documents

**General rules**:
- Run an **unfiltered title search** by default if no filter criteria are mentioned
- If the user's request includes any specific filter criteria (e.g., agency name, document type):
  1. Call `pia_search_titles_facets` once to discover the filterable field names and allowed values
  2. Use these to build a valid OData filter expression
  3. Call `pia_search_titles` with the filter applied

**Process for applying filters**:

1. **Detect filter intent**:
   - Examine the user's query for references to agencies, document types, dates, or other filterable attributes
   - If such references are present, treat the search as **filtered**

2. **Discover filterable fields and values** (only if filtering):
   - Call the `pia_search_titles_facets` tool (one time per session unless filters change)
   - Review the output to see:
     - Field names that support filtering
     - Possible values for each field

3. **Build the filter expression**:
   - Use **only field names and values** returned by `pia_search_titles_facets`
   - Construct the filter in **OData syntax**:
     - `SourceDocumentDataSource eq 'GAO'`
     - `SourceDocumentTitle contains 'fraud'`
     - `(SourceDocumentDataSource eq 'GAO' or SourceDocumentDataSource eq 'Oversight.gov') and SourceDocumentIsRecDoc eq 'Yes'`
   - Use correct operators: `eq`, `ne`, `gt`, `ge`, `lt`, `le`, `and`, `or`, `contains`
   - Wrap string values in single quotes `'value'`

4. **Execute the filtered title search**:
   - Pass the OData filter string to `pia_search_titles` tool's `filter` parameter
   - Example:
     ```
     {
       "query": "audit report",
       "filter": "SourceDocumentDataSource eq 'GAO' and SourceDocumentTitle contains 'fraud'"
     }
     ```

5. **Fallback to unfiltered search**:
   - If the filtered search returns no results and you haven't yet run an unfiltered search:
     - Run the same query without the filter
     - Inform the user you are showing unfiltered results

6. **Validation**:
   - Never use a field or value not provided by `pia_search_titles_facets`
   - If the user requests a filter that doesn't exist, explain it's not available and offer an unfiltered search

**Goal**:
- Use title search to discover what documents are available
- Help users find specific documents by title or browse available documents
- Always validate filter fields/values before applying them"""


def _generate_recommendations_guidance() -> str:
    """Generate recommendations guidance prompt - EXACT content from remote server."""
    return """You can search and analyze oversight recommendations data using the PIA Search tools.

**Understanding Recommendations Data**:
- Recommendations are identified as records where `SourceDocumentDataSet eq 'Open Recommendations'`
- Some recommendations are closed, as indicated by `RecStatus eq 'Closed'`
- Users might refer to these as "Recommendations" or "Recs"

**Search Strategy for Recommendations**:

1. **For numerical questions about recommendations** (e.g., "How many recommendations are there?", "Show me stats by agency"):
   - Use `pia_search_content_facets` with **no query string** (empty query)
   - Apply filter: `SourceDocumentDataSet eq 'Open Recommendations'`
   - This gives you recommendations broken down by various dimensions you can analyze

2. **For specific recommendation information**:
   - Use `pia_search_content` with appropriate filters to find specific recommendations
   - Always include: `SourceDocumentDataSet eq 'Open Recommendations'`
   - Add additional filters as needed (agency, status, etc.)
   - Results should provide links to the full recommendation details

3. **Example filter patterns**:
   - All open recommendations: `SourceDocumentDataSet eq 'Open Recommendations'`
   - Only closed recommendations: `SourceDocumentDataSet eq 'Open Recommendations' and RecStatus eq 'Closed'`
   - Recommendations from specific agency: `SourceDocumentDataSet eq 'Open Recommendations' and [AgencyField] eq 'AgencyName'`

**Additional Resources**:
- For overall questions about how PIA ingests recommendations, refer users to the FAQ: https://programintegrity.org/spotlight-faq/
- You can also refer users to PIA's [Recommendations Spotlight](https://programintegrity.org/rec-spotlight/) for more ways to access recommendations data

**Process**:
1. Determine if the question is numerical/statistical or about specific recommendations
2. Use `pia_search_content_facets` for stats, `pia_search_content` for specific information
3. Always filter by `SourceDocumentDataSet eq 'Open Recommendations'`
4. Consider whether to include/exclude closed recommendations based on the question
5. Provide links from search results when available
6. Direct users to additional resources when appropriate"""

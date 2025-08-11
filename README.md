[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/Program-Integrity-Alliance/pia-mcp-local/actions/workflows/tests.yml/badge.svg)](https://github.com/Program-Integrity-Alliance/pia-mcp-local/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<div align="center">
  <a href="https://programintegrity.org/">
    <img src="https://programintegrity.org/wp-content/uploads/2024/07/PIA-Logo.svg" alt="Program Integrity Alliance" width="400"/>
  </a>

# MCP Server
</div>

<br/>

[The Program Integrity Alliance (PIA)](https://programintegrity.org/) aims to make working with U.S. Government datasets easier and AI-friendly. We have ingested hundreds of thousands of documents and articles across a range of sources, and this list is growing. This MCP server enables AIs to search this data at a more detailed level than on most source websites, for example, searching within PDF reports to find the exact pages where text and images appear.

Full attribution is given to the amazing open federal data sources, and all links in the data provided by PIA will always direct back to the original source.

Currently, the list of datasets includes:

1. [U.S. Government Accountability Office (GAO)](https://www.gao.gov/) - 10k Federal Reports since 2010 and 5.5k Open Oversight Recommendations
2. [Oversight.gov](https://www.oversight.gov/) - 28k OIG Federal Reports since 2010, and 29k Open Oversight Recommendations
3. [U.S. Congress](https://www.congress.gov/) - Bill texts for sessions 118 and 119
4. [Department of Justice (DOJ)](https://www.justice.gov/) - 195k Press Releases since 2000
5. Federal Agency annual reports - Congressional Justification, Financial Report, Performance Report - 139 reports across 10 priority agencies, with best coverage in 2024.

This data is updated weekly, and we will be adding more datasets and tools soon.

If you have any questions, we look forward to hearing from you by raising a question [here](https://github.com/Program-Integrity-Alliance/pia-mcp-local/issues)

<div align="center">

🤝 **[Contribute](CONTRIBUTING.md)** •
📝 **[Report Bugs or Questions](https://github.com/Program-Integrity-Alliance/pia-mcp-local/issues)**

</div>

## ✨ Core Features

- 🔎 **Document Search**: Query PIA database with comprehensive OData filtering options
- 📊 **Faceted Search**: Discover available filter fields and values
- 📝 **AI Instruction Prompts**: Prompts that instruct LLMs on how to summarize search results and use search tools

## 🚀 Quick Start

### Installing via Smithery

To install PIA Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/pia-mcp-server):

```bash
npx -y @smithery/cli install pia-mcp-server --client claude
```

### Installing Manually
Install using uv:

```bash
uv tool install pia-mcp-server
```

For development:

```bash
# Clone and set up development environment
git clone https://github.com/Program-Integrity-Alliance/pia-mcp-local.git
cd pia-mcp-local

# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install with test dependencies
uv pip install -e ".[test]"
```

For Docker:

```bash
# Build the Docker image if you want to use a local image
git clone https://github.com/Program-Integrity-Alliance/pia-mcp-local.git
cd pia-mcp-local
docker build -t pia-mcp-server:latest .
```

### 🔌 MCP Integration

Add this configuration to your MCP client config file:

```json
{
    "mcpServers": {
        "pia-mcp-server": {
            "command": "uv",
            "args": [
                "tool",
                "run",
                "pia-mcp-server",
                "--api-key", "YOUR_API_KEY"
            ]
        }
    }
}
```

For Docker:

```json
{
    "mcpServers": {
        "pia-mcp-server": {
            "command": "docker",
            "args": [
                "run",
                "--rm",
                "-i",
                "pia-mcp-server:latest",
                "--api-key", "YOUR_API_KEY"
            ]
        }
    }
}
```

## 💡 Available Tools

The server provides two main tools:

### 1. PIA Search
Comprehensive search with OData filtering and faceting. The `filter` parameter uses standard [OData query syntax](https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part2-url-conventions.html).

**Tool Name:** `pia_search`

**Parameters:**
- `query` (required): Search query text
- `filter` (optional): OData filter expression
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Results per page (default: 10)
- `search_mode` (optional): Search mode (default: "content")
- `limit` (optional): Maximum results limit
- `include_facets` (optional): Include facets in results (default: false)

**Example Filter Expressions:**
- Basic filter: `"data_source eq 'OIG'"`
- Multiple conditions: `"data_source in ('OIG', 'GAO') and published_date ge '2023-01-01'"`
- Complex grouping: `"(agency ne 'Department of Defense') and (severity in ('High', 'Critical'))"`
- Date ranges: `"published_date ge '2023-01-01' and published_date le '2023-12-31'"`
- String functions: `"contains(title, 'Medicare') and startswith(agency, 'Department')"`

**OData Filter Operators:**
- `eq` - equals: `field eq 'value'`
- `ne` - not equals: `field ne 'value'`
- `gt` - greater than: `amount gt 1000`
- `ge` - greater than or equal: `date ge '2023-01-01'`
- `lt` - less than: `amount lt 5000`
- `le` - less than or equal: `date le '2023-12-31'`
- `in` - value in list: `status in ('Active', 'Pending')`

**OData Logical Operators:**
- `and` - logical AND: `field1 eq 'value' and field2 gt 100`
- `or` - logical OR: `status eq 'Active' or status eq 'Pending'`
- `not` - logical NOT: `not (status eq 'Inactive')`
- `()` - grouping: `(field1 eq 'A' or field1 eq 'B') and field2 gt 0`

**OData String Functions:**
- `contains(field, 'text')` - field contains text
- `startswith(field, 'prefix')` - field starts with prefix
- `endswith(field, 'suffix')` - field ends with suffix



### 2. PIA Search Facets
Discover available field names and values for filtering.

**Tool Name:** `pia_search_facets`

**Parameters:**
- `query` (optional): Optional query to get facets for (default: "")

**Purpose:**
- Discover available field names (e.g., `data_source`, `document_type`, `agency`)
- Find possible field values (e.g., "OIG", "GAO", "audit_report")
- Understand data types for each field (string, date, number)

This information helps you construct proper `filter` expressions for the `pia_search` tool.

## 🔍 Filter Discovery Workflow

To effectively use OData filters, follow this workflow:

### Step 1: Discover Available Fields
Use the `pia_search_facets` tool to explore what fields are available for filtering. You can provide a query to get facets relevant to your search topic, or omit the query to see all available fields.

### Step 2: Examine Field Values
The facets response will show available fields and their possible values:
```json
{
  "data_source": ["OIG", "GAO", "CMS", "FBI"],
  "document_type": ["audit_report", "investigation", "enforcement_action"],
  "agency": ["Department of Health", "Department of Defense"],
  "published_date": "2020-01-01 to 2024-12-31"
}
```

### Step 3: Build Targeted Search
Use the `pia_search` tool with discovered fields to create precise OData filters:

**Basic Example:**
```
Query: "Medicare fraud"
Filter: "data_source in ('OIG', 'CMS') and published_date ge '2023-01-01' and document_type eq 'audit_report'"
```

**Complex Example:**
```
Query: "healthcare violations"
Filter: "(data_source eq 'OIG' or data_source eq 'CMS') and (severity eq 'High' or amount gt 1000000) and published_date ge '2023-01-01'"
```

## 📝 AI Instruction Prompts

The server provides prompts that instruct the calling LLM on how to effectively use PIA tools and format responses:

### Summary Prompt
Instructions for LLM to summarize information only from provided search results with proper citations.

**Prompt Name:** `summary_prompt`

**Purpose:** Ensures LLM creates fact-based summaries with inline citations and proper reference formatting

**Arguments:**
- `search_results` (required): The search results to summarize (inserted into &lt;SEARCH_RESULTS&gt; tags)

**Returns:** Instructions that guide the LLM to:
- Only include facts from search results (no prior knowledge)
- Use inline citations [n] for every factual statement
- Format references with document title, page, source, and URL
- Follow strict citation and formatting guidelines

### Search Prompt
Instructions for LLM on how to effectively use PIA search tools with proper filtering.

**Prompt Name:** `search_prompt`

**Purpose:** Guides LLM through proper search workflow including filter discovery and OData syntax

**Arguments:**
- `user_query` (required): The user's search query to analyze for filter criteria

**Returns:** Instructions that guide the LLM to:
- Detect when filters should be applied based on query content
- Use `pia_search_facets` to discover available filter fields and values
- Build valid OData filter expressions with correct syntax
- Fall back to unfiltered search when filtered search returns no results
- Validate all filter fields against available facets

## ⚙️ Configuration

The API key is always provided via the MCP server configuration. Additional settings can be configured through environment variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `PIA_API_URL` | PIA API endpoint | https://mcp.programintegrity.org/ |
| `REQUEST_TIMEOUT` | API request timeout (seconds) | 60 |
| `MAX_RESULTS` | Maximum results per query | 50 |

### MCP Configuration

The API key must be provided in your MCP client configuration using the `--api-key` argument. Contact the Program Integrity Alliance to obtain your API key.

```json
{
    "mcpServers": {
        "pia-mcp-server": {
            "command": "pia-mcp-server",
            "args": ["--api-key", "YOUR_API_KEY"]
        }
    }
}
```

Replace `YOUR_API_KEY` with your actual PIA API key.


## 🧪 Testing

Run the test suite:

```bash
python -m pytest
```

Run with coverage:

```bash
python -m pytest --cov=pia_mcp_server
```

## 📄 License

Released under the MIT License. See the LICENSE file for details.

---

<div align="center">

Made with ❤️ for Government Transparency and Accountability

</div>

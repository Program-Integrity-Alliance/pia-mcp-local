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

If you have any questions, or requests for other datasets, we look forward to hearing from you by raising an issue [here](https://github.com/Program-Integrity-Alliance/pia-mcp-local/issues).

<div align="center">

🤝 **[Contribute](CONTRIBUTING.md)** •
📝 **[Report Bugs or Questions](https://github.com/Program-Integrity-Alliance/pia-mcp-local/issues)**

</div>

## ✨ Core Features

- 🔎 **Document Search**: Query PIA database with comprehensive OData filtering options
- 📊 **Faceted Search**: Discover available filter fields and values
- 📝 **AI Instruction Prompts**: Prompts that instruct LLMs on how to summarize search results and use search tools

## 🚀 Quick Start

### Getting a PIA API Key

1. Go to [https://mcp.programintegrity.org/get-api-key](https://mcp.programintegrity.org/get-api-key)
2. If you don't have a **free** PIA account, click the 'No account? Create one' link, otherwise log in
3. Once logged in, you should automatically receive your key

### Installing using Docker MCP Toolkit (Recommended)

*Note: This is pending PR review to be accepted to catalog*

1. Download and run the latest version of [Docker Desktop](https://docs.docker.com/desktop/)
2. Navigate to 'MCP Toolkit'
3. Search for 'Program Integrity Alliance'
4. Add as a server by clicking '+'
5. Under 'Configuration' enter your key
6. In 'MCP Toolkit' navigate to 'Clients'
7. Choose one, eg 'Claude Desktop'
8. Start your Client
9. You should now see 'pia_search_content' and other tools

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

The server provides four main tools for searching the Program Integrity Alliance (PIA) database:

### 1. `pia_search_content`

**Purpose:** Comprehensive search tool for querying document content and recommendations in the PIA database.

**Description:** Returns comprehensive results with full citation information and clickable links for proper attribution. Each result includes corresponding citations with data source attribution (GAO, OIG, etc.). Supports complex OData filtering with boolean logic, operators, and grouping.

**Parameters:**
- `query` (required): Search query text
- `filter` (optional): OData filter expression supporting complex boolean logic
- `page` (optional): Page number (1-based, default: 1)
- `page_size` (optional): Number of results per page (max 50, default: 10)
- `search_mode` (optional): Search mode - "content" for full-text search or "titles" for title-only search (default: "content")
- `limit` (optional): Alternative name for page_size (for compatibility)
- `include_facets` (optional): Whether to include facets in response (default: false to reduce token usage)

### 2. `pia_search_content_facets`

**Purpose:** Get available facets (filter values) for the PIA database content search.

**Description:** This can help understand what filter values are available before performing content searches. Supports complex OData filtering with boolean logic, operators, and grouping.

**Parameters:**
- `query` (optional): Optional query to get facets for (if empty, gets all facets, default: "")
- `filter` (optional): Optional OData filter expression

### 3. `pia_search_titles`

**Purpose:** Search the Program Integrity Alliance (PIA) database for document titles only.

**Description:** Returns document titles and metadata without searching the full content. Useful for finding specific documents by title or discovering available documents. Supports complex OData filtering with boolean logic, operators, and grouping.

**Parameters:**
- `query` (required): Search query text (searches document titles only)
- `filter` (optional): OData filter expression supporting complex boolean logic
- `page` (optional): Page number (1-based, default: 1)
- `page_size` (optional): Number of results per page (max 50, default: 10)
- `limit` (optional): Alternative name for page_size (for compatibility)
- `include_facets` (optional): Whether to include facets in response (default: false to reduce token usage)

### 4. `pia_search_titles_facets`

**Purpose:** Get available facets (filter values) for the PIA database title search.

**Description:** This can help understand what filter values are available before performing title searches. Supports complex OData filtering with boolean logic, operators, and grouping.

**Parameters:**
- `query` (optional): Optional query to get facets for (if empty, gets all facets, default: "")
- `filter` (optional): Optional OData filter expression

## Search Modes

Comprehensive search with OData filtering and faceting. The `filter` parameter uses standard [OData query syntax](https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part2-url-conventions.html).

- **Content Search** (`pia_search_content`): Searches within document content and recommendations for comprehensive results
- **Title Search** (`pia_search_titles`): Searches document titles only - faster and useful for document discovery

**Example Filter Expressions:**
- Basic filter: `"SourceDocumentDataSource eq 'GAO'"`
- Multiple conditions: `"SourceDocumentDataSource eq 'GAO' or SourceDocumentDataSource eq 'OIG'"`
- Complex grouping: `"SourceDocumentDataSource eq 'GAO' and RecStatus ne 'Closed'"`
- Negation: `"SourceDocumentDataSource ne 'Department of Justice' and not (RecStatus eq 'Closed')"`
- List membership: `"IsIntegrityRelated eq 'Yes' and RecPriorityFlag in ('High', 'Critical')"`
- Date ranges: `"SourceDocumentPublishDate ge '2020-01-01' and SourceDocumentPublishDate le '2024-12-31'"`
- Boolean grouping: `"(SourceDocumentDataSource eq 'GAO' or SourceDocumentDataSource eq 'OIG') and RecStatus eq 'Open'"`

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

This information helps you construct proper `filter` expressions for the search tools.

## 🔍 Filter Discovery Workflow

To effectively use OData filters, follow this workflow:

### Step 1: Discover Available Fields
Use the `pia_search_facets` tool to explore what fields are available for filtering. You can provide a query to get facets relevant to your search topic, or omit the query to see all available fields.

### Step 2: Examine Field Values
The facets response will show available fields and their possible values:
```json
{
  "SourceDocumentDataSource": ["OIG", "GAO", "CMS", "FBI"],
  "RecStatus": ["Open", "Closed", "In Progress"],
  "RecPriorityFlag": ["High", "Medium", "Low", "Critical"],
  "IsIntegrityRelated": ["Yes", "No"],
  "SourceDocumentPublishDate": "2020-01-01 to 2024-12-31"
}
```

### Step 3: Build Targeted Search
Use the `pia_search` tool with discovered fields to create precise OData filters:

**Basic Example:**
```
Query: "Medicare fraud"
Filter: "SourceDocumentDataSource eq 'GAO' and SourceDocumentPublishDate ge '2023-01-01' and IsIntegrityRelated eq 'Yes'"
```

**Complex Example:**
```
Query: "healthcare violations"
Filter: "(SourceDocumentDataSource eq 'OIG' or SourceDocumentDataSource eq 'CMS') and RecPriorityFlag in ('High', 'Critical') and SourceDocumentPublishDate ge '2023-01-01'"
```

## 📝 AI Instruction Prompts

The server provides prompts that instruct the calling LLM on how to effectively use PIA tools and format responses:

### 1. Summarization Guidance
Provides guidance on how to summarize information from PIA search results with proper citations.

**Prompt Name:** `summarization_guidance`

**Purpose:** Ensures LLM creates fact-based summaries with inline citations and proper reference formatting

**Arguments:** None (reusable guidance)

**Returns:** Comprehensive instructions that guide the LLM to:
- Only include facts that appear in the provided search results (no prior knowledge)
- Use proper inline citation format [n] for every factual statement
- Create a References section with format: [n] Document Title — Page X — Source Name — URL
- Follow objective, factual style guidelines without speculation or filler
- Include all necessary attribution elements exactly as provided in search results
- Organize information logically and ensure every fact has supporting citations

### 2. Search Guidance
Provides guidance on how to perform PIA searches with or without filters.

**Prompt Name:** `search_guidance`

**Purpose:** Guides LLM through proper search workflow including filter discovery and OData syntax for all four search tools

**Arguments:** None (reusable guidance)

**Returns:** Comprehensive instructions that guide the LLM to:
- Run unfiltered searches by default unless filter criteria are mentioned
- Choose between content search (comprehensive) and title search (fast discovery)
- Use `pia_search_content_facets` or `pia_search_titles_facets` to discover available filter fields and values
- Build valid OData filter expressions with correct syntax and actual field names
- Apply proper OData operators: `eq`, `ne`, `gt`, `ge`, `lt`, `le`, `and`, `or`
- Fall back to unfiltered search when filtered search returns no results
- Validate all filter fields against available facets before use

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

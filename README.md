[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/Program-Integrity-Alliance/pia-mcp-local/actions/workflows/tests.yml/badge.svg)](https://github.com/Program-Integrity-Alliance/pia-mcp-local/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<div align="center">
  <a href="https://programintegrity.org/">
    <img src="https://www.programintegrity.org/api/assets/site-images/brand/docker-mcp-pia-icon-512.png" alt="Program Integrity Alliance" width="400"/>
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
6. All Congression Research Service reports - 22k reports provided by [EveryCRSReport.com](https://www.everycrsreport.com/)
7. U.S. Presidential Executive Orders - Order for the last 7 presidencies as provided by the [Federal Register](https://www.federalregister.gov/presidential-documents/executive-orders).

This data is updated weekly, and we will be adding more datasets and tools soon.

If you have any questions, or requests for other datasets, we look forward to hearing from you by raising an issue [here](https://github.com/Program-Integrity-Alliance/pia-mcp-local/issues).

For more information on how to use PIA's MCP resources in platforms like Claude and ChatGPT, see [PIA Connect](https://programintegrity.org/connect/).

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

1. Go to [https://programintegrity.org/](https://programintegrity.org/) and register for a **free** PIA account (or log in if you already have one)
2. Once logged in, click the user icon (top right) and choose **API/MCP key** (this opens the **API / MCP Keys** page at `/account/api-keys`)
3. Generate a new key, then copy it — you'll provide it to the MCP server via the `X-API-KEY` header / `--api-key` argument

### Installing using Docker MCP Toolkit (Recommended)

1. Download and run the latest version of [Docker Desktop](https://docs.docker.com/desktop/)
2. Navigate to 'MCP Toolkit'
3. Search for 'Program Integrity Alliance'
4. Add as a server by clicking '+'
5. Under 'Configuration' enter your key
6. In 'MCP Toolkit' navigate to 'Clients'
7. Choose one, eg 'Claude Desktop'
8. Start your Client
9. You should now see 'pia_search' and other tools

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

### Refreshing Tool Specs (No API Key Needed for Listing)

Tool listing in this local server is served from a local snapshot, so tools are
discoverable even without an API key. To refresh the snapshot from the remote
server, run:

```bash
PIA_API_KEY=your_key python utils/refresh_tools.py
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
            ],
            "cwd": "/path/to/your/pia-mcp-local"
        }
    }
}
```

For Docker:

You must build the Docker image ...

`docker build -t pia-mcp-server:latest .`

Then add this to your Client, eg Claude ...

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

The server provides 4 tools, forwarded verbatim to the Program Integrity Alliance (PIA) MCP server:

### 1. `pia_search`

**Purpose:** Primary search over the PIA database of government oversight reports, recommendations, and related documents.

**Description:** Returns ranked results with snippets, citations, embedded facets, and a `govquery_url`, with full OData filtering. Consolidates the former per-dataset and agency-specific search tools into one.

**Parameters:**
- `query` (required): Search query text
- `filter` (optional): OData filter expression supporting complex boolean logic
- Additional optional paging / facet / mode parameters — see the tool's `inputSchema`

### 2. `pia_oversight_recommendations`

**Purpose:** Search the Open Recommendations dataset (GAO + Oversight.gov) with facets enabled by default.

**Parameters:**
- `query` (required): Search query text
- `filter` (optional): OData filter expression

### 3. `search`

**Purpose:** Simple search interface for ChatGPT connectors (OpenAI MCP spec).

**Parameters:**
- `query` (required): A search query string

### 4. `fetch`

**Purpose:** Retrieve the full contents of a document by its unique id (ChatGPT connectors / OpenAI MCP spec).

**Parameters:**
- `id` (required): A unique identifier for the document to retrieve

## Search Modes

`pia_search` supports OData filtering and faceting. The `filter` parameter uses standard [OData query syntax](https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part2-url-conventions.html).

**Example Filter Expressions:**
- Basic filter: `"SourceDocumentDataSource eq 'GAO'"`
- Multiple conditions: `"SourceDocumentDataSource eq 'GAO' or SourceDocumentDataSource eq 'Oversight.gov'"`
- Complex grouping: `"SourceDocumentDataSource eq 'GAO' and RecStatus ne 'Closed'"`
- Negation: `"SourceDocumentDataSource ne 'Department of Justice' and not (RecStatus eq 'Closed')"`
- List membership: `"IsIntegrityRelated eq 'Yes' and RecPriorityFlag in ('High', 'Critical')"`
- Date ranges: `"SourceDocumentPublishDate ge '2020-01-01' and SourceDocumentPublishDate le '2024-12-31'"`
- Boolean grouping: `"(SourceDocumentDataSource eq 'GAO' or SourceDocumentDataSource eq 'Oversight.gov') and RecStatus eq 'Open'"`

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
  "SourceDocumentDataSource": ["Oversight.gov", "GAO", "CMS", "FBI"],
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
Filter: "(SourceDocumentDataSource eq 'Oversight.gov' or SourceDocumentDataSource eq 'CMS') and RecPriorityFlag in ('High', 'Critical') and SourceDocumentPublishDate ge '2023-01-01'"
```

## 📝 AI Instruction Prompts

The server exposes one prompt that instructs the calling LLM how to use the PIA tools and format responses:

### `pia_assistant_guidance`

Comprehensive guidance for an LLM using the PIA (GovQuery) tools: search strategy, citation format, and response structure.

**Arguments:** None (reusable guidance)

## ⚙️ Configuration

The API key is always provided via the MCP server configuration. Additional settings can be configured through environment variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `PIA_API_URL` | PIA API endpoint | https://www.programintegrity.org/mcp |
| `REQUEST_TIMEOUT` | API request timeout (seconds) | 60 |
| `MAX_RESULTS` | Maximum results per query | 50 |

### MCP Configuration

The API key must be provided in your MCP client configuration using the `--api-key` argument. See [Getting a PIA API Key](#getting-a-pia-api-key) above to create one.

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

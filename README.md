[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/YOUR-ORG/pia-mcp-server/actions/workflows/tests.yml/badge.svg)](https://github.com/YOUR-ORG/pia-mcp-server/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# PIA MCP Server

> 🔍 Enable AI assistants to search and access Program Integrity Alliance documents through a simple MCP interface.

This MCP Server provides tools for working with Government Open Data which has been processed by the [The Program Integrity Alliance (PIA)](https://programintegrity.org/). Currently this includes:

1. [U.S. Government Accountability Office (GAO)](https://www.gao.gov/) - 10k Federal Reports since 2010 and 5.5k Open Oversight Recommendations
2. [Oversight.gov](https://www.oversight.gov/) - 28k OIG Federal Reports since 2010, and 29k Open Oversight Recommendations
3. [U.S. Congress](https://www.congress.gov/) - Bill texts for sessions 118 and 119
4. [Department of Justice (DOJ)](https://www.justice.gov/) - 195k Press Releases since 2000

This data is updated weekly, and we will be adding more datasets and tools soon.

<div align="center">
  
🤝 **[Contribute](CONTRIBUTING.md)** • 
📝 **[Report Bug](https://github.com/Program-Integrity-Alliance/pia-mcp-local/issues)**

</div>

## ✨ Core Features

- 🔎 **Document Search**: Query PIA database with comprehensive filtering options
- 📄 **Document Access**: Retrieve full contents of specific documents
- 📊 **Faceted Search**: Explore available filter values and categories
- 📈 **Rate Limiting**: Monitor API usage and limits
- 📝 **Research Prompts**: Specialized prompts for fraud investigation, compliance, and risk analysis

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
git clone https://github.com/YOUR-ORG/pia-mcp-server.git
cd pia-mcp-server

# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install with test dependencies
uv pip install -e ".[test]"
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

For Development:

```json
{
    "mcpServers": {
        "pia-mcp-server": {
            "command": "uv",
            "args": [
                "--directory",
                "path/to/cloned/pia-mcp-server",
                "run",
                "pia-mcp-server",
                "--api-key", "YOUR_API_KEY"
            ]
        }
    }
}
```

## 💡 Available Tools

The server provides five main tools:

### 1. PIA Search
Comprehensive search with OData filtering and faceting. The `filters` parameter uses standard [OData query syntax](https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part2-url-conventions.html).

**Tool Name:** `pia_search`

**Parameters:**
- `query` (required): Search query text
- `filters` (optional): OData filter expression
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

This information helps you construct proper `filters` for the `pia_search` tool.

### 3. Basic Search
Simple search for quick results.

**Tool Name:** `search`

**Parameters:**
- `query` (required): A search query string to find relevant documents

### 4. Fetch Document
Retrieve full document content.

**Tool Name:** `fetch`

**Parameters:**
- `id` (required): A unique identifier for the document to retrieve

### 5. Rate Limit Stats
Monitor API usage and current configuration.

**Tool Name:** `get_rate_limit_stats`

**Parameters:** None

**Returns:** JSON structure with rate limiting statistics including request counts, blocked requests, and current limits configuration.

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
Filters: "data_source in ('OIG', 'CMS') and published_date ge '2023-01-01' and document_type eq 'audit_report'"
```

**Complex Example:**
```
Query: "healthcare violations"  
Filters: "(data_source eq 'OIG' or data_source eq 'CMS') and (severity eq 'High' or amount gt 1000000) and published_date ge '2023-01-01'"
```

## 📝 Research Prompts

The server offers specialized prompts for different research workflows:

### Fraud Investigation Search
Systematically search for fraud investigations and related findings.

**Prompt Name:** `fraud_investigation_search`

**Arguments:**
- `topic` (required): The fraud topic or area to investigate
- `time_period` (optional): Time period for the search (e.g., 'last 5 years')

### Compliance Recommendations
Find compliance recommendations and regulatory guidance.

**Prompt Name:** `compliance_recommendations`

**Arguments:**
- `area` (required): The compliance area or domain to search
- `data_source` (optional): Specific data source (GAO, OIG, etc.)

### Risk Analysis
Analyze risk factors and vulnerabilities in specific domains.

**Prompt Name:** `risk_analysis`

**Arguments:**
- `domain` (required): The domain or sector to analyze for risks
- `risk_type` (optional): Type of risk to focus on (financial, operational, etc.)

### Findings Summary
Generate comprehensive summaries of findings about a specific subject.

**Prompt Name:** `findings_summary`

**Arguments:**
- `subject` (required): The subject or entity to summarize findings about
- `max_results` (optional): Maximum number of results to include in summary

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
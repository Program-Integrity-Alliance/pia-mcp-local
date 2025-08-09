"""Prompt handlers for the PIA MCP server."""

import mcp.types as types
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

# Available prompts based on the PIA API response
AVAILABLE_PROMPTS = [
    {
        "name": "fraud_investigation_search",
        "description": "Search for fraud investigations and related findings in the PIA database",
        "arguments": [
            {
                "name": "topic",
                "description": "The fraud topic or area to investigate",
                "required": True,
            },
            {
                "name": "time_period",
                "description": "Time period for the search (e.g., 'last 5 years')",
                "required": False,
            },
        ],
    },
    {
        "name": "compliance_recommendations",
        "description": "Find compliance recommendations and regulatory guidance",
        "arguments": [
            {
                "name": "area",
                "description": "The compliance area or domain to search",
                "required": True,
            },
            {
                "name": "data_source",
                "description": "Specific data source (GAO, OIG, etc.)",
                "required": False,
            },
        ],
    },
    {
        "name": "risk_analysis",
        "description": "Analyze risk factors and vulnerabilities in specific domains",
        "arguments": [
            {
                "name": "domain",
                "description": "The domain or sector to analyze for risks",
                "required": True,
            },
            {
                "name": "risk_type",
                "description": "Type of risk to focus on (financial, operational, etc.)",
                "required": False,
            },
        ],
    },
    {
        "name": "findings_summary",
        "description": "Generate a comprehensive summary of findings about a specific subject",
        "arguments": [
            {
                "name": "subject",
                "description": "The subject or entity to summarize findings about",
                "required": True,
            },
            {
                "name": "max_results",
                "description": "Maximum number of results to include in summary",
                "required": False,
            },
        ],
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
    if name == "fraud_investigation_search":
        content = _generate_fraud_investigation_prompt(arguments)
    elif name == "compliance_recommendations":
        content = _generate_compliance_recommendations_prompt(arguments)
    elif name == "risk_analysis":
        content = _generate_risk_analysis_prompt(arguments)
    elif name == "findings_summary":
        content = _generate_findings_summary_prompt(arguments)
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


def _generate_fraud_investigation_prompt(arguments: Dict[str, str]) -> str:
    """Generate fraud investigation search prompt."""
    topic = arguments.get("topic", "")
    time_period = arguments.get("time_period", "all available years")

    return f"""You are a fraud investigation analyst using the Program Integrity Alliance (PIA) database.

Your task is to search for fraud investigations and related findings on the topic: "{topic}"

Time period: {time_period}

Please use the available PIA search tools to:

1. Start with a broad search using the "pia_search" tool with the topic as your query
2. If needed, use "pia_search_facets" to understand available filters for narrowing your search
3. Use the "search" tool for quick overviews if needed
4. Use the "fetch" tool to retrieve full document contents for the most relevant findings

Focus on finding:
- Investigation reports
- Audit findings
- Compliance violations
- Recommended corrective actions
- Follow-up enforcement actions

Provide a comprehensive summary of your findings with proper citations and links."""


def _generate_compliance_recommendations_prompt(arguments: Dict[str, str]) -> str:
    """Generate compliance recommendations prompt."""
    area = arguments.get("area", "")
    data_source = arguments.get("data_source", "all sources")

    return f"""You are a compliance analyst using the Program Integrity Alliance (PIA) database.

Your task is to find compliance recommendations and regulatory guidance for: "{area}"

Data source preference: {data_source}

Please use the available PIA search tools to:

1. Search for compliance recommendations using the "pia_search" tool
2. If targeting specific sources, use filters to focus on {data_source}
3. Use "pia_search_facets" to explore available data sources and compliance domains
4. Retrieve full documents with "fetch" for detailed recommendations

Focus on finding:
- Regulatory guidance documents
- Best practice recommendations
- Compliance frameworks
- Implementation guidance
- Monitoring and oversight recommendations

Organize your findings by:
- Type of recommendation
- Source agency (GAO, OIG, etc.)
- Implementation priority
- Monitoring requirements"""


def _generate_risk_analysis_prompt(arguments: Dict[str, str]) -> str:
    """Generate risk analysis prompt."""
    domain = arguments.get("domain", "")
    risk_type = arguments.get("risk_type", "all risk types")

    return f"""You are a risk analyst using the Program Integrity Alliance (PIA) database.

Your task is to analyze risk factors and vulnerabilities in: "{domain}"

Risk focus: {risk_type}

Please use the available PIA search tools to:

1. Search for risk assessments and vulnerability reports using "pia_search"
2. Use filters to focus on {risk_type} if specific risk types are specified
3. Use "pia_search_facets" to understand risk categories and domains
4. Retrieve detailed risk analyses with "fetch"

Focus on identifying:
- Known vulnerabilities and weaknesses
- Risk factors and threat vectors
- Historical incidents and patterns
- Mitigation strategies and controls
- Monitoring and detection mechanisms

Provide a risk analysis summary including:
- Risk severity and likelihood
- Potential impact areas
- Recommended mitigation strategies
- Monitoring and oversight needs"""


def _generate_findings_summary_prompt(arguments: Dict[str, str]) -> str:
    """Generate findings summary prompt."""
    subject = arguments.get("subject", "")
    max_results = arguments.get("max_results", "20")

    return f"""You are a research analyst using the Program Integrity Alliance (PIA) database.

Your task is to generate a comprehensive summary of findings about: "{subject}"

Maximum results to review: {max_results}

Please use the available PIA search tools to:

1. Conduct a comprehensive search using "pia_search" with relevant keywords
2. Use "pia_search_facets" to explore all relevant categories and sources
3. Retrieve full document contents using "fetch" for the most significant findings
4. Use the "search" tool for additional quick searches if needed

Create a comprehensive summary including:

## Executive Summary
- Key findings overview
- Major themes and patterns

## Detailed Findings by Category
- Audit findings
- Investigation results
- Compliance issues
- Recommendations

## Data Sources and Citations
- List all sources consulted
- Provide proper attribution and links

## Timeline of Significant Events
- Chronological overview of major findings

## Recommendations and Next Steps
- Synthesized recommendations from multiple sources
- Priority actions identified

Ensure all findings are properly cited with links to source documents."""

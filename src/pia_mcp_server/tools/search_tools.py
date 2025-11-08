"""PIA Search tools for database searches and facets discovery."""

import httpx
import mcp.types as types
from typing import Dict, Any, List
import json
import logging
from ..config import Settings

logger = logging.getLogger(__name__)
settings = Settings()

# Tool definitions - EXACT copies from remote server
pia_search_content_tool = types.Tool(
    name="pia_search_content",
    description="Search the Program Integrity Alliance (PIA) database for document content and recommendations. Returns comprehensive results with full citation information and clickable links for proper attribution. Each result includes corresponding citations with data source attribution. Major data sources include: Department of Justice (198k+ docs), Congress.gov (29k+ docs), Oversight.gov (22k+ docs), CRS (22k+ docs), GAO (10k+ docs), Federal Register (1k+ executive orders). Use pia_search_content_executive_orders to search only executive orders. Supports complex OData filtering with boolean logic, operators, and grouping.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query text"},
            "filter": {
                "type": "string",
                "description": "Optional OData filter expression supporting complex boolean logic.\n\n    AVAILABLE FIELDS:\n    • SourceDocumentDataSource: Data source/agency that published the document. Major sources (>1k documents): 'Department of Justice', 'Congress.gov', 'Oversight.gov', 'CRS', 'GAO', 'Federal Register'\n• SourceDocumentDataSet: Dataset or collection the document belongs to. Values: 'press-releases', 'reports', 'bills-and-laws', 'federal-reports', 'executive orders', 'state-and-local-reports', 'federal reports'\n• SourceDocumentTitle: Document title - use contains, eq for text matching\n• SourceDocumentPublishDate: Publication date - ISO 8601 format YYYY-MM-DD (e.g., '2023-01-01'). Use ge/le for ranges\n• RecStatus: Recommendation status\n• RecPriorityFlag: Priority flag for recommendations\n• SourceDocumentIsRecDoc: Whether the document contains recommendations. Values: 'No', 'Yes'\n• RecFraudRiskManagementThemePIA: Fraud risk management theme classification\n• RecMatterForCongressPIA: Whether the matter is for Congressional attention\n• RecRecommendation: Recommendation text - use contains, eq for text matching\n• RecAgencyComments: Agency comments on recommendations - use contains, eq for text matching\n• referenced_agencies: Agencies referenced by documents (collection field). Example: (referenced_agencies/any(a: a eq 'Department of Defense (DOD)') or referenced_agencies/any(a: a eq 'Department of Justice (DOJ)')) - for single agency omit outer parentheses and 'or'. Get all values via pia_search_content_facets. Note: Many data sources such as CRS and Congress do not tag documents with agency. In these cases PIA infers agencies through AI tagging and in some cases the agency may be incorrect. This tagging only tags documents where the agency is explicitly mentioned.\n\n    OPERATORS:\n    • Text: contains, eq, ne, startswith, endswith\n    • Exact: eq (equals), ne (not equals), in (in list)\n    • Date: ge (greater/equal), le (less/equal), eq (equals)\n    • Logic: and, or, not, parentheses for grouping\n\n    EXAMPLES:\n    • \"SourceDocumentDataSource eq 'GAO'\"\n    • \"SourceDocumentDataSource eq 'GAO' and RecStatus ne 'Closed'\"\n    • \"(SourceDocumentDataSource eq 'GAO' or SourceDocumentDataSource eq 'OIG') and RecStatus eq 'Open'\"\n    • \"SourceDocumentPublishDate ge '2020-01-01' and SourceDocumentPublishDate le '2024-12-31'\"\n\n    TIP: Use pia_search_content_facets tool to get the most current available values.",
            },
            "page": {
                "type": "integer",
                "description": "Page number (default: 1)",
                "default": 1,
            },
            "page_size": {
                "type": "integer",
                "description": "Results per page (default: 10)",
                "default": 10,
            },
            "search_mode": {
                "type": "string",
                "description": "Search mode (default: content)",
                "default": "content",
            },
            "limit": {"type": "integer", "description": "Maximum results limit"},
            "include_facets": {
                "type": "boolean",
                "description": "Include facets in results",
                "default": False,
            },
        },
        "required": ["query"],
    },
    outputSchema={
        "type": "object",
        "properties": {
            "output": {
                "type": "object",
                "properties": {
                    "total_count": {"type": "integer"},
                    "query": {"type": "string"},
                    "summary": {"type": "string"},
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "title": {"type": "string"},
                                "snippet": {"type": "string"},
                                "score": {"type": "number"},
                                "data_source": {"type": "string"},
                                "url": {"type": "string", "format": "uri"},
                                "publication_date": {
                                    "type": "string",
                                    "format": "date-time",
                                },
                            },
                            "required": ["id", "title", "data_source", "url"],
                            "additionalProperties": False,
                        },
                    },
                    "citations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "label": {"type": "string"},
                                "url": {"type": "string", "format": "uri"},
                                "title": {"type": "string"},
                                "data_source": {"type": "string"},
                                "publication_date": {
                                    "type": "string",
                                    "format": "date-time",
                                },
                            },
                            "required": ["id", "label", "url"],
                            "additionalProperties": False,
                        },
                    },
                    "references": {"type": "array", "items": {"type": "string"}},
                    "citation_guidance": {"type": "string"},
                },
                "required": ["total_count", "results"],
                "additionalProperties": False,
            }
        },
        "required": ["output"],
        "additionalProperties": False,
    },
)

pia_search_content_facets_tool = types.Tool(
    name="pia_search_content_facets",
    description="Get available facets (filter values) for the PIA database content search. This can help understand what filter values are available before performing content searches. Major data sources include: Department of Justice (198k+ docs), Congress.gov (29k+ docs), Oversight.gov (22k+ docs), CRS (22k+ docs), GAO (10k+ docs), Federal Register (1k+ executive orders). Use pia_search_content_executive_orders to search only executive orders.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Optional query to get facets for",
                "default": "",
            },
            "filter": {
                "type": "string",
                "description": "Optional OData filter expression supporting complex boolean logic.\n\nAVAILABLE FIELDS:\n• SourceDocumentDataSource: Data source/agency that published the document. Major sources (>1k documents): 'Department of Justice', 'Congress.gov', 'Oversight.gov', 'CRS', 'GAO', 'Federal Register'\n• SourceDocumentDataSet: Dataset or collection the document belongs to. Values: 'press-releases', 'reports', 'bills-and-laws', 'federal-reports', 'executive orders', 'state-and-local-reports', 'federal reports'\n• SourceDocumentOrg: Organization associated with the document. There are many values, use pia_search_content_facets tool to see available options\n• SourceDocumentTitle: Document title - use contains, eq for text matching\n• SourceDocumentPublishDate: Publication date - ISO 8601 format YYYY-MM-DD (e.g., '2023-01-01'). Use ge/le for ranges\n• RecStatus: Recommendation status\n• RecPriorityFlag: Priority flag for recommendations\n• IsIntegrityRelated: Whether the content is integrity-related\n• SourceDocumentIsRecDoc: Whether the document contains recommendations. Values: 'No', 'Yes'\n• RecFraudRiskManagementThemePIA: Fraud risk management theme classification\n• RecMatterForCongressPIA: Whether the matter is for Congressional attention\n• RecRecommendation: Recommendation text - use contains, eq for text matching\n• RecAgencyComments: Agency comments on recommendations - use contains, eq for text matching\n\nOPERATORS:\n• Text: contains, eq, ne, startswith, endswith\n• Exact: eq (equals), ne (not equals), in (in list)\n• Date: ge (greater/equal), le (less/equal), eq (equals)\n• Logic: and, or, not, parentheses for grouping\n\nEXAMPLES:\n• \"SourceDocumentDataSource eq 'GAO'\"\n• \"SourceDocumentDataSource eq 'GAO' and RecStatus ne 'Closed'\"\n• \"IsIntegrityRelated eq 'True' and RecPriorityFlag eq 'Yes'\"\n• \"(SourceDocumentDataSource eq 'GAO' or SourceDocumentDataSource eq 'OIG') and RecStatus eq 'Open'\"\n• \"SourceDocumentPublishDate ge '2020-01-01' and SourceDocumentPublishDate le '2024-12-31'\"\n\nTIP: Use pia_search_content_facets tool to get the most current available values.",
            },
        },
    },
)

pia_search_titles_tool = types.Tool(
    name="pia_search_titles",
    description="Search the Program Integrity Alliance (PIA) database for document titles only. Returns document titles and metadata without searching the full content. Useful for finding specific documents by title or discovering available documents. Major data sources include: Department of Justice (198k+ docs), Congress.gov (29k+ docs), Oversight.gov (22k+ docs), CRS (22k+ docs), GAO (10k+ docs), Federal Register (1k+ executive orders). Use pia_search_content_executive_orders to search only executive orders.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query text (searches document titles only)",
            },
            "filter": {
                "type": "string",
                "description": "Optional OData filter expression supporting complex boolean logic.\n\nAVAILABLE FIELDS:\n• SourceDocumentDataSource: Data source/agency that published the document. Major sources (>1k documents): 'Department of Justice', 'Congress.gov', 'Oversight.gov', 'CRS', 'GAO', 'Federal Register'\n• SourceDocumentDataSet: Dataset or collection the document belongs to. Values: 'press-releases', 'reports', 'bills-and-laws', 'federal-reports', 'executive orders', 'state-and-local-reports', 'federal reports'\n• SourceDocumentOrg: Organization associated with the document. There are many values, use pia_search_content_facets tool to see available options\n• SourceDocumentTitle: Document title - use contains, eq for text matching\n• SourceDocumentPublishDate: Publication date - ISO 8601 format YYYY-MM-DD (e.g., '2023-01-01'). Use ge/le for ranges\n• RecStatus: Recommendation status\n• RecPriorityFlag: Priority flag for recommendations\n• IsIntegrityRelated: Whether the content is integrity-related\n• SourceDocumentIsRecDoc: Whether the document contains recommendations. Values: 'No', 'Yes'\n• RecFraudRiskManagementThemePIA: Fraud risk management theme classification\n• RecMatterForCongressPIA: Whether the matter is for Congressional attention\n• RecRecommendation: Recommendation text - use contains, eq for text matching\n• RecAgencyComments: Agency comments on recommendations - use contains, eq for text matching\n\nOPERATORS:\n• Text: contains, eq, ne, startswith, endswith\n• Exact: eq (equals), ne (not equals), in (in list)\n• Date: ge (greater/equal), le (less/equal), eq (equals)\n• Logic: and, or, not, parentheses for grouping\n\nEXAMPLES:\n• \"SourceDocumentDataSource eq 'GAO'\"\n• \"SourceDocumentDataSource eq 'GAO' and RecStatus ne 'Closed'\"\n• \"IsIntegrityRelated eq 'True' and RecPriorityFlag eq 'Yes'\"\n• \"(SourceDocumentDataSource eq 'GAO' or SourceDocumentDataSource eq 'OIG') and RecStatus eq 'Open'\"\n• \"SourceDocumentPublishDate ge '2020-01-01' and SourceDocumentPublishDate le '2024-12-31'\"\n\nTIP: Use pia_search_content_facets tool to get the most current available values.",
            },
            "page": {
                "type": "integer",
                "description": "Page number (default: 1)",
                "default": 1,
            },
            "page_size": {
                "type": "integer",
                "description": "Results per page (default: 10)",
                "default": 10,
            },
            "limit": {"type": "integer", "description": "Maximum results limit"},
            "include_facets": {
                "type": "boolean",
                "description": "Include facets in results",
                "default": False,
            },
        },
        "required": ["query"],
    },
)

pia_search_titles_facets_tool = types.Tool(
    name="pia_search_titles_facets",
    description="Get available facets (filter values) for the PIA database title search. This can help understand what filter values are available before performing title searches. Major data sources include: Department of Justice (198k+ docs), Congress.gov (29k+ docs), Oversight.gov (22k+ docs), CRS (22k+ docs), GAO (10k+ docs), Federal Register (1k+ executive orders). Use pia_search_content_executive_orders to search only executive orders.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Optional query to get facets for",
                "default": "",
            },
            "filter": {
                "type": "string",
                "description": "Optional OData filter expression supporting complex boolean logic.\n\nAVAILABLE FIELDS:\n• SourceDocumentDataSource: Data source/agency that published the document. Major sources (>1k documents): 'Department of Justice', 'Congress.gov', 'Oversight.gov', 'CRS', 'GAO', 'Federal Register'\n• SourceDocumentDataSet: Dataset or collection the document belongs to. Values: 'press-releases', 'reports', 'bills-and-laws', 'federal-reports', 'executive orders', 'state-and-local-reports', 'federal reports'\n• SourceDocumentOrg: Organization associated with the document. There are many values, use pia_search_content_facets tool to see available options\n• SourceDocumentTitle: Document title - use contains, eq for text matching\n• SourceDocumentPublishDate: Publication date - ISO 8601 format YYYY-MM-DD (e.g., '2023-01-01'). Use ge/le for ranges\n• RecStatus: Recommendation status\n• RecPriorityFlag: Priority flag for recommendations\n• IsIntegrityRelated: Whether the content is integrity-related\n• SourceDocumentIsRecDoc: Whether the document contains recommendations. Values: 'No', 'Yes'\n• RecFraudRiskManagementThemePIA: Fraud risk management theme classification\n• RecMatterForCongressPIA: Whether the matter is for Congressional attention\n• RecRecommendation: Recommendation text - use contains, eq for text matching\n• RecAgencyComments: Agency comments on recommendations - use contains, eq for text matching\n\nOPERATORS:\n• Text: contains, eq, ne, startswith, endswith\n• Exact: eq (equals), ne (not equals), in (in list)\n• Date: ge (greater/equal), le (less/equal), eq (equals)\n• Logic: and, or, not, parentheses for grouping\n\nEXAMPLES:\n• \"SourceDocumentDataSource eq 'GAO'\"\n• \"SourceDocumentDataSource eq 'GAO' and RecStatus ne 'Closed'\"\n• \"IsIntegrityRelated eq 'True' and RecPriorityFlag eq 'Yes'\"\n• \"(SourceDocumentDataSource eq 'GAO' or SourceDocumentDataSource eq 'OIG') and RecStatus eq 'Open'\"\n• \"SourceDocumentPublishDate ge '2020-01-01' and SourceDocumentPublishDate le '2024-12-31'\"\n\nTIP: Use pia_search_content_facets tool to get the most current available values.",
            },
        },
    },
)

# NEW TOOLS from remote server
pia_search_content_gao_tool = types.Tool(
    name="pia_search_content_gao",
    description="Search the Program Integrity Alliance (PIA) database for GAO document content and recommendations. This tool automatically filters results to only include documents from the Government Accountability Office (GAO). Returns comprehensive results with full citation information and clickable links for proper attribution. Each result includes corresponding citations with data source attribution. Supports complex OData filtering with boolean logic, operators, and grouping.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query text"},
            "filter": {
                "type": "string",
                "description": "Optional OData filter expression supporting complex boolean logic.\n\nAVAILABLE FIELDS:\n• Note: SourceDocumentDataSource is automatically set to 'GAO' for this tool. Major sources (>1k documents): 'Department of Justice', 'Congress.gov', 'Oversight.gov', 'CRS', 'GAO', 'Federal Register'\n• SourceDocumentDataSet: Dataset or collection the document belongs to. Values: 'press-releases', 'reports', 'bills-and-laws', 'federal-reports', 'executive orders', 'state-and-local-reports', 'federal reports'\n• SourceDocumentOrg: Organization associated with the document. There are many values, use pia_search_content_facets tool to see available options\n• SourceDocumentTitle: Document title - use contains, eq for text matching\n• SourceDocumentPublishDate: Publication date - ISO 8601 format YYYY-MM-DD (e.g., '2023-01-01'). Use ge/le for ranges\n• RecStatus: Recommendation status\n• RecPriorityFlag: Priority flag for recommendations\n• IsIntegrityRelated: Whether the content is integrity-related\n• SourceDocumentIsRecDoc: Whether the document contains recommendations. Values: 'No', 'Yes'\n• RecFraudRiskManagementThemePIA: Fraud risk management theme classification\n• RecMatterForCongressPIA: Whether the matter is for Congressional attention\n• RecRecommendation: Recommendation text - use contains, eq for text matching\n• RecAgencyComments: Agency comments on recommendations - use contains, eq for text matching\n\nOPERATORS:\n• Text: contains, eq, ne, startswith, endswith\n• Exact: eq (equals), ne (not equals), in (in list)\n• Date: ge (greater/equal), le (less/equal), eq (equals)\n• Logic: and, or, not, parentheses for grouping\n\nEXAMPLES:\n• \"RecStatus eq 'Open'\"\n• \"RecStatus ne 'Closed' and RecPriorityFlag eq 'Yes'\"\n• \"IsIntegrityRelated eq 'True' and RecPriorityFlag eq 'Yes'\"\n• \"(RecStatus eq 'Open' and RecPriorityFlag eq 'Yes')\"\n• \"SourceDocumentPublishDate ge '2020-01-01' and SourceDocumentPublishDate le '2024-12-31'\"\n\nTIP: Use pia_search_content_facets tool to get the most current available values.",
            },
            "page": {
                "type": "integer",
                "description": "Page number (default: 1)",
                "default": 1,
            },
            "page_size": {
                "type": "integer",
                "description": "Results per page (default: 10)",
                "default": 10,
            },
            "search_mode": {
                "type": "string",
                "description": "Search mode (default: content)",
                "default": "content",
            },
            "limit": {"type": "integer", "description": "Maximum results limit"},
            "include_facets": {
                "type": "boolean",
                "description": "Include facets in results",
                "default": False,
            },
        },
        "required": ["query"],
    },
)

pia_search_content_oig_tool = types.Tool(
    name="pia_search_content_oig",
    description="Search the Program Integrity Alliance (PIA) database for OIG document content and recommendations. This tool automatically filters results to only include documents from Office of Inspector General (OIG) sources. Returns comprehensive results with full citation information and clickable links for proper attribution. Each result includes corresponding citations with data source attribution. Supports complex OData filtering with boolean logic, operators, and grouping.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query text"},
            "filter": {
                "type": "string",
                "description": "Optional OData filter expression supporting complex boolean logic.\n\nAVAILABLE FIELDS:\n• Note: SourceDocumentDataSource is automatically set to 'Oversight.gov' for this tool. Major sources (>1k documents): 'Department of Justice', 'Congress.gov', 'Oversight.gov', 'CRS', 'GAO', 'Federal Register'\n• SourceDocumentDataSet: Dataset or collection the document belongs to. Values: 'press-releases', 'reports', 'bills-and-laws', 'federal-reports', 'executive orders', 'state-and-local-reports', 'federal reports'\n• SourceDocumentOrg: Organization associated with the document. There are many values, use pia_search_content_facets tool to see available options\n• SourceDocumentTitle: Document title - use contains, eq for text matching\n• SourceDocumentPublishDate: Publication date - ISO 8601 format YYYY-MM-DD (e.g., '2023-01-01'). Use ge/le for ranges\n• RecStatus: Recommendation status\n• RecPriorityFlag: Priority flag for recommendations\n• IsIntegrityRelated: Whether the content is integrity-related\n• SourceDocumentIsRecDoc: Whether the document contains recommendations. Values: 'No', 'Yes'\n• RecFraudRiskManagementThemePIA: Fraud risk management theme classification\n• RecMatterForCongressPIA: Whether the matter is for Congressional attention\n• RecRecommendation: Recommendation text - use contains, eq for text matching\n• RecAgencyComments: Agency comments on recommendations - use contains, eq for text matching\n\nOPERATORS:\n• Text: contains, eq, ne, startswith, endswith\n• Exact: eq (equals), ne (not equals), in (in list)\n• Date: ge (greater/equal), le (less/equal), eq (equals)\n• Logic: and, or, not, parentheses for grouping\n\nEXAMPLES:\n• \"RecStatus eq 'Open'\"\n• \"RecStatus ne 'Closed' and RecPriorityFlag eq 'Yes'\"\n• \"IsIntegrityRelated eq 'True' and RecPriorityFlag eq 'Yes'\"\n• \"(RecStatus eq 'Open' and RecPriorityFlag eq 'Yes')\"\n• \"SourceDocumentPublishDate ge '2020-01-01' and SourceDocumentPublishDate le '2024-12-31'\"\n\nTIP: Use pia_search_content_facets tool to get the most current available values.",
            },
            "page": {
                "type": "integer",
                "description": "Page number (default: 1)",
                "default": 1,
            },
            "page_size": {
                "type": "integer",
                "description": "Results per page (default: 10)",
                "default": 10,
            },
            "search_mode": {
                "type": "string",
                "description": "Search mode (default: content)",
                "default": "content",
            },
            "limit": {"type": "integer", "description": "Maximum results limit"},
            "include_facets": {
                "type": "boolean",
                "description": "Include facets in results",
                "default": False,
            },
        },
        "required": ["query"],
    },
)

pia_search_content_crs_tool = types.Tool(
    name="pia_search_content_crs",
    description="Search the Program Integrity Alliance (PIA) database for CRS document content and recommendations. This tool automatically filters results to only include documents from Congressional Research Service (CRS). Returns comprehensive results with full citation information and clickable links for proper attribution. Each result includes corresponding citations with data source attribution. Supports complex OData filtering with boolean logic, operators, and grouping.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query text"},
            "filter": {
                "type": "string",
                "description": "Optional OData filter expression supporting complex boolean logic.\n\nAVAILABLE FIELDS:\n• Note: SourceDocumentDataSource is automatically set to 'CRS' for this tool. Major sources (>1k documents): 'Department of Justice', 'Congress.gov', 'Oversight.gov', 'CRS', 'GAO', 'Federal Register'\n• SourceDocumentDataSet: Dataset or collection the document belongs to. Values: 'press-releases', 'reports', 'bills-and-laws', 'federal-reports', 'executive orders', 'state-and-local-reports', 'federal reports'\n• SourceDocumentOrg: Organization associated with the document. There are many values, use pia_search_content_facets tool to see available options\n• SourceDocumentTitle: Document title - use contains, eq for text matching\n• SourceDocumentPublishDate: Publication date - ISO 8601 format YYYY-MM-DD (e.g., '2023-01-01'). Use ge/le for ranges\n• RecStatus: Recommendation status\n• RecPriorityFlag: Priority flag for recommendations\n• IsIntegrityRelated: Whether the content is integrity-related\n• SourceDocumentIsRecDoc: Whether the document contains recommendations. Values: 'No', 'Yes'\n• RecFraudRiskManagementThemePIA: Fraud risk management theme classification\n• RecMatterForCongressPIA: Whether the matter is for Congressional attention\n• RecRecommendation: Recommendation text - use contains, eq for text matching\n• RecAgencyComments: Agency comments on recommendations - use contains, eq for text matching\n\nOPERATORS:\n• Text: contains, eq, ne, startswith, endswith\n• Exact: eq (equals), ne (not equals), in (in list)\n• Date: ge (greater/equal), le (less/equal), eq (equals)\n• Logic: and, or, not, parentheses for grouping\n\nEXAMPLES:\n• \"RecStatus eq 'Open'\"\n• \"RecStatus ne 'Closed' and RecPriorityFlag eq 'Yes'\"\n• \"IsIntegrityRelated eq 'True' and RecPriorityFlag eq 'Yes'\"\n• \"(RecStatus eq 'Open' and RecPriorityFlag eq 'Yes')\"\n• \"SourceDocumentPublishDate ge '2020-01-01' and SourceDocumentPublishDate le '2024-12-31'\"\n\nTIP: Use pia_search_content_facets tool to get the most current available values.",
            },
            "page": {
                "type": "integer",
                "description": "Page number (default: 1)",
                "default": 1,
            },
            "page_size": {
                "type": "integer",
                "description": "Results per page (default: 10)",
                "default": 10,
            },
            "search_mode": {
                "type": "string",
                "description": "Search mode (default: content)",
                "default": "content",
            },
            "limit": {"type": "integer", "description": "Maximum results limit"},
            "include_facets": {
                "type": "boolean",
                "description": "Include facets in results",
                "default": False,
            },
        },
        "required": ["query"],
    },
)

pia_search_content_doj_tool = types.Tool(
    name="pia_search_content_doj",
    description="Search the Program Integrity Alliance (PIA) database for Department of Justice document content and recommendations. This tool automatically filters results to only include documents from the Department of Justice. Returns comprehensive results with full citation information and clickable links for proper attribution. Each result includes corresponding citations with data source attribution. Supports complex OData filtering with boolean logic, operators, and grouping.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query text"},
            "filter": {
                "type": "string",
                "description": "Optional OData filter expression supporting complex boolean logic.\n\nAVAILABLE FIELDS:\n• Note: SourceDocumentDataSource is automatically set to 'Department of Justice' for this tool. Major sources (>1k documents): 'Department of Justice', 'Congress.gov', 'Oversight.gov', 'CRS', 'GAO', 'Federal Register'\n• SourceDocumentDataSet: Dataset or collection the document belongs to. Values: 'press-releases', 'reports', 'bills-and-laws', 'federal-reports', 'executive orders', 'state-and-local-reports', 'federal reports'\n• SourceDocumentOrg: Organization associated with the document. There are many values, use pia_search_content_facets tool to see available options\n• SourceDocumentTitle: Document title - use contains, eq for text matching\n• SourceDocumentPublishDate: Publication date - ISO 8601 format YYYY-MM-DD (e.g., '2023-01-01'). Use ge/le for ranges\n• RecStatus: Recommendation status\n• RecPriorityFlag: Priority flag for recommendations\n• IsIntegrityRelated: Whether the content is integrity-related\n• SourceDocumentIsRecDoc: Whether the document contains recommendations. Values: 'No', 'Yes'\n• RecFraudRiskManagementThemePIA: Fraud risk management theme classification\n• RecMatterForCongressPIA: Whether the matter is for Congressional attention\n• RecRecommendation: Recommendation text - use contains, eq for text matching\n• RecAgencyComments: Agency comments on recommendations - use contains, eq for text matching\n\nOPERATORS:\n• Text: contains, eq, ne, startswith, endswith\n• Exact: eq (equals), ne (not equals), in (in list)\n• Date: ge (greater/equal), le (less/equal), eq (equals)\n• Logic: and, or, not, parentheses for grouping\n\nEXAMPLES:\n• \"RecStatus eq 'Open'\"\n• \"RecStatus ne 'Closed' and RecPriorityFlag eq 'Yes'\"\n• \"IsIntegrityRelated eq 'True' and RecPriorityFlag eq 'Yes'\"\n• \"(RecStatus eq 'Open' and RecPriorityFlag eq 'Yes')\"\n• \"SourceDocumentPublishDate ge '2020-01-01' and SourceDocumentPublishDate le '2024-12-31'\"\n\nTIP: Use pia_search_content_facets tool to get the most current available values.",
            },
            "page": {
                "type": "integer",
                "description": "Page number (default: 1)",
                "default": 1,
            },
            "page_size": {
                "type": "integer",
                "description": "Results per page (default: 10)",
                "default": 10,
            },
            "search_mode": {
                "type": "string",
                "description": "Search mode (default: content)",
                "default": "content",
            },
            "limit": {"type": "integer", "description": "Maximum results limit"},
            "include_facets": {
                "type": "boolean",
                "description": "Include facets in results",
                "default": False,
            },
        },
        "required": ["query"],
    },
)

pia_search_content_congress_tool = types.Tool(
    name="pia_search_content_congress",
    description="Search the Program Integrity Alliance (PIA) database for Congress.gov document content and recommendations. This tool automatically filters results to only include documents from Congress.gov. Returns comprehensive results with full citation information and clickable links for proper attribution. Each result includes corresponding citations with data source attribution. Supports complex OData filtering with boolean logic, operators, and grouping.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query text"},
            "filter": {
                "type": "string",
                "description": "Optional OData filter expression supporting complex boolean logic.\n\nAVAILABLE FIELDS:\n• Note: SourceDocumentDataSource is automatically set to 'Congress.gov' for this tool. Major sources (>1k documents): 'Department of Justice', 'Congress.gov', 'Oversight.gov', 'CRS', 'GAO', 'Federal Register'\n• SourceDocumentDataSet: Dataset or collection the document belongs to. Values: 'press-releases', 'reports', 'bills-and-laws', 'federal-reports', 'executive orders', 'state-and-local-reports', 'federal reports'\n• SourceDocumentOrg: Organization associated with the document. There are many values, use pia_search_content_facets tool to see available options\n• SourceDocumentTitle: Document title - use contains, eq for text matching\n• SourceDocumentPublishDate: Publication date - ISO 8601 format YYYY-MM-DD (e.g., '2023-01-01'). Use ge/le for ranges\n• RecStatus: Recommendation status\n• RecPriorityFlag: Priority flag for recommendations\n• IsIntegrityRelated: Whether the content is integrity-related\n• SourceDocumentIsRecDoc: Whether the document contains recommendations. Values: 'No', 'Yes'\n• RecFraudRiskManagementThemePIA: Fraud risk management theme classification\n• RecMatterForCongressPIA: Whether the matter is for Congressional attention\n• RecRecommendation: Recommendation text - use contains, eq for text matching\n• RecAgencyComments: Agency comments on recommendations - use contains, eq for text matching\n\nOPERATORS:\n• Text: contains, eq, ne, startswith, endswith\n• Exact: eq (equals), ne (not equals), in (in list)\n• Date: ge (greater/equal), le (less/equal), eq (equals)\n• Logic: and, or, not, parentheses for grouping\n\nEXAMPLES:\n• \"RecStatus eq 'Open'\"\n• \"RecStatus ne 'Closed' and RecPriorityFlag eq 'Yes'\"\n• \"IsIntegrityRelated eq 'True' and RecPriorityFlag eq 'Yes'\"\n• \"(RecStatus eq 'Open' and RecPriorityFlag eq 'Yes')\"\n• \"SourceDocumentPublishDate ge '2020-01-01' and SourceDocumentPublishDate le '2024-12-31'\"\n\nTIP: Use pia_search_content_facets tool to get the most current available values.",
            },
            "page": {
                "type": "integer",
                "description": "Page number (default: 1)",
                "default": 1,
            },
            "page_size": {
                "type": "integer",
                "description": "Results per page (default: 10)",
                "default": 10,
            },
            "search_mode": {
                "type": "string",
                "description": "Search mode (default: content)",
                "default": "content",
            },
            "limit": {"type": "integer", "description": "Maximum results limit"},
            "include_facets": {
                "type": "boolean",
                "description": "Include facets in results",
                "default": False,
            },
        },
        "required": ["query"],
    },
)

pia_search_content_executive_orders_tool = types.Tool(
    name="pia_search_content_executive_orders",
    description="Search the Program Integrity Alliance (PIA) database for Executive Orders document content from the Federal Register. This tool automatically filters results to only include Executive Orders from the Federal Register (https://www.federalregister.gov/). Returns comprehensive results with full citation information and clickable links for proper attribution. Each result includes corresponding citations with data source attribution. Supports complex OData filtering with boolean logic, operators, and grouping.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query text"},
            "filter": {
                "type": "string",
                "description": "Optional OData filter expression supporting complex boolean logic.\n\nAVAILABLE FIELDS:\n• Note: SourceDocumentDataSource is automatically set to 'Federal Register' and SourceDocumentDataSet is set to 'executive orders' for this tool. Major sources (>1k documents): 'Department of Justice', 'Congress.gov', 'Oversight.gov', 'CRS', 'GAO', 'Federal Register'\n• SourceDocumentDataSet: Dataset or collection the document belongs to. Values: 'press-releases', 'reports', 'bills-and-laws', 'federal-reports', 'executive orders', 'state-and-local-reports', 'federal reports'\n• SourceDocumentOrg: Organization associated with the document. There are many values, use pia_search_content_facets tool to see available options\n• SourceDocumentTitle: Document title - use contains, eq for text matching\n• SourceDocumentPublishDate: Publication date - ISO 8601 format YYYY-MM-DD (e.g., '2023-01-01'). Use ge/le for ranges\n• RecStatus: Recommendation status\n• RecPriorityFlag: Priority flag for recommendations\n• IsIntegrityRelated: Whether the content is integrity-related\n• SourceDocumentIsRecDoc: Whether the document contains recommendations. Values: 'No', 'Yes'\n• RecFraudRiskManagementThemePIA: Fraud risk management theme classification\n• RecMatterForCongressPIA: Whether the matter is for Congressional attention\n• RecRecommendation: Recommendation text - use contains, eq for text matching\n• RecAgencyComments: Agency comments on recommendations - use contains, eq for text matching\n\nOPERATORS:\n• Text: contains, eq, ne, startswith, endswith\n• Exact: eq (equals), ne (not equals), in (in list)\n• Date: ge (greater/equal), le (less/equal), eq (equals)\n• Logic: and, or, not, parentheses for grouping\n\nEXAMPLES:\n• \"SourceDocumentPublishDate ge '2020-01-01'\"\n• \"SourceDocumentPublishDate ge '2020-01-01' and SourceDocumentPublishDate le '2024-12-31'\"\n• \"IsIntegrityRelated eq 'True' and RecPriorityFlag eq 'Yes'\"\n• \"IsIntegrityRelated eq 'True'\"\n• \"SourceDocumentPublishDate ge '2020-01-01' and SourceDocumentPublishDate le '2024-12-31'\"\n\nTIP: Use pia_search_content_facets tool to get the most current available values.",
            },
            "page": {
                "type": "integer",
                "description": "Page number (default: 1)",
                "default": 1,
            },
            "page_size": {
                "type": "integer",
                "description": "Results per page (default: 10)",
                "default": 10,
            },
            "search_mode": {
                "type": "string",
                "description": "Search mode (default: content)",
                "default": "content",
            },
            "limit": {"type": "integer", "description": "Maximum results limit"},
            "include_facets": {
                "type": "boolean",
                "description": "Include facets in results",
                "default": False,
            },
        },
        "required": ["query"],
    },
)

search_tool = types.Tool(
    name="search",
    description="Search the Program Integrity Alliance (PIA) database and return a list of potentially relevant search results with titles, snippets, and URLs for citation. This endpoint is one of the supported for OpenAI's MCP spec when integrating ChatGPT Connectors.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "A search query string to find relevant documents in the PIA database",
            }
        },
        "required": ["query"],
    },
)

fetch_tool = types.Tool(
    name="fetch",
    description="Retrieve the full contents of a specific document from the PIA database using its unique identifier. This endpoint is one of the supported for OpenAI's MCP spec when integrating ChatGPT Connectors.",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "A unique identifier for the document to retrieve",
            }
        },
        "required": ["id"],
    },
)


# Handler functions - using generic handler that forwards to remote server
async def handle_pia_search_content(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Handle PIA content search requests."""
    return await _forward_to_remote("pia_search_content", arguments)


async def handle_pia_search_content_facets(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Handle PIA content search facets requests."""
    return await _forward_to_remote("pia_search_content_facets", arguments)


async def handle_pia_search_titles(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Handle PIA titles search requests."""
    return await _forward_to_remote("pia_search_titles", arguments)


async def handle_pia_search_titles_facets(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Handle PIA titles search facets requests."""
    return await _forward_to_remote("pia_search_titles_facets", arguments)


async def handle_pia_search_content_gao(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Handle PIA GAO content search requests."""
    return await _forward_to_remote("pia_search_content_gao", arguments)


async def handle_pia_search_content_oig(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Handle PIA OIG content search requests."""
    return await _forward_to_remote("pia_search_content_oig", arguments)


async def handle_pia_search_content_crs(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Handle PIA CRS content search requests."""
    return await _forward_to_remote("pia_search_content_crs", arguments)


async def handle_pia_search_content_doj(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Handle PIA DOJ content search requests."""
    return await _forward_to_remote("pia_search_content_doj", arguments)


async def handle_pia_search_content_congress(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Handle PIA Congress content search requests."""
    return await _forward_to_remote("pia_search_content_congress", arguments)


async def handle_pia_search_content_executive_orders(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Handle PIA Executive Orders content search requests."""
    return await _forward_to_remote("pia_search_content_executive_orders", arguments)


async def handle_search(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Handle simple search requests."""
    return await _forward_to_remote("search", arguments)


async def handle_fetch(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Handle fetch document requests."""
    return await _forward_to_remote("fetch", arguments)


async def _forward_to_remote(
    tool_name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Forward tool call to remote MCP server."""
    try:
        # Prepare the request payload
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }

        try:
            api_key = settings.API_KEY
            logger.info(
                "API_KEY retrieved successfully: %s...",
                api_key[:10] if api_key else "API_KEY is None or empty",
            )
        except ValueError as e:
            logger.error("Failed to retrieve API key: %s", str(e))
            return [
                types.TextContent(
                    type="text",
                    text=f"Error: {str(e)} Configure API key in MCP server settings.",
                )
            ]

        headers = {"Content-Type": "application/json", "x-api-key": api_key}
        logger.info(
            "Making API call to %s with headers: %s",
            settings.PIA_API_URL,
            dict(headers),
        )

        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            response = await client.post(
                settings.PIA_API_URL, json=payload, headers=headers
            )
            response.raise_for_status()

            result = response.json()

            if "error" in result:
                error_msg = result["error"].get("message", "Unknown error")
                return [types.TextContent(type="text", text=f"API Error: {error_msg}")]

            if "result" in result:
                # Format the search results nicely
                search_results = result["result"]
                formatted_result = json.dumps(
                    search_results, indent=2, ensure_ascii=False
                )
                return [types.TextContent(type="text", text=formatted_result)]
            else:
                return [
                    types.TextContent(type="text", text="No results returned from API")
                ]

    except httpx.HTTPStatusError as e:
        logger.error("HTTP error during %s: %s", tool_name, e)
        return [
            types.TextContent(
                type="text",
                text=f"HTTP Error {e.response.status_code}: {e.response.text}",
            )
        ]
    except Exception as e:
        logger.error("Error during %s: %s", tool_name, e)
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

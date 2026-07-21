#!/usr/bin/env python3
# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)

"""
MCP Server for IBM MDM
This server exposes tools to interact with IBM MDM services via REST API calls.
"""

import os
import logging
from dotenv import load_dotenv
import argparse
from fastmcp import FastMCP
from fastapi.middleware.cors import CORSMiddleware
from fastmcp.tools.tool import Tool

# Import configuration
from config import Config

# Import identity propagation middleware
from common.auth.token_middleware import UserTokenMiddleware

# Import your tools
from data_ms.search.tools import search_master_data, SEARCH_TOOL_DESCRIPTION
from data_ms.federated_search.tools import search_potential_match_issues, FEDERATED_SEARCH_TOOL_DESCRIPTION
from matching_ms.data_quality.tools import get_data_quality_issues, DATA_QUALITY_ISSUES_TOOL_DESCRIPTION
from data_ms.records.tools import get_record_by_id, get_records_entities_by_record_id
from data_ms.entities.tools import get_entity, get_entities_by_ids, GET_ENTITIES_BY_IDS_TOOL_DESCRIPTION
from matching_ms.compare.tools import compare_records
from matching_ms.linkage_rules.tools import preview_linkage_rules
from matching_ms.algorithm.tools import get_matching_algorithm
from model_ms.model.tools import get_data_model
from matching_ms.linkage.tools import apply_linkage_rules

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize MCP with identity-propagation middleware
mcp = FastMCP("mdm-mcp-server", middleware=[UserTokenMiddleware()])

# Get tools mode from configuration
TOOLS_MODE = Config.MCP_TOOLS_MODE.lower()

logger.info(f"Registering tools in '{TOOLS_MODE}' mode")

# Register core tools (always available)
mcp.add_tool(Tool.from_function(search_master_data, name="search_master_data", description=SEARCH_TOOL_DESCRIPTION))
mcp.add_tool(Tool.from_function(search_potential_match_issues, name="search_potential_match_issues", description=FEDERATED_SEARCH_TOOL_DESCRIPTION))
mcp.add_tool(Tool.from_function(get_data_quality_issues, name="get_data_quality_issues", description=DATA_QUALITY_ISSUES_TOOL_DESCRIPTION))
mcp.add_tool(Tool.from_function(get_data_model, name="get_data_model"))

# Register additional tools only in full mode
if TOOLS_MODE == "full":
    logger.info("Registering additional tools: get_record, get_entity, get_entities_by_ids, get_records_entities_by_record_id, compare_records, preview_linkage_rules, get_matching_algorithm, apply_linkage_rules")
    mcp.add_tool(Tool.from_function(get_record_by_id, name="get_record"))
    mcp.add_tool(Tool.from_function(get_entity, name="get_entity"))
    mcp.add_tool(Tool.from_function(get_entities_by_ids, name="get_entities_by_ids", description=GET_ENTITIES_BY_IDS_TOOL_DESCRIPTION))
    mcp.add_tool(Tool.from_function(get_records_entities_by_record_id, name="get_records_entities_by_record_id"))
    mcp.add_tool(Tool.from_function(compare_records, name="compare_records"))
    mcp.add_tool(Tool.from_function(preview_linkage_rules, name="preview_linkage_rules"))
    mcp.add_tool(Tool.from_function(get_matching_algorithm, name="get_matching_algorithm"))
    mcp.add_tool(Tool.from_function(apply_linkage_rules, name="apply_linkage_rules"))

@mcp.prompt()
def match360_mdm_assistant() -> str:
    """
    Initializes the AI as an IBM MDM Specialist with strict protocol enforcement.
    """
    return """You are the **IBM Master Data Management (MDM) Specialist**. Your purpose is to assist users in searching, resolving, and managing master data using IBM MDM via the mdm-mcp-server tools.

**CRITICAL PROTOCOL (3-STEP PROCESS):**

1. **STEP 1: Fetch Data Model (if needed)**
   - Call `get_data_model(format="enhanced_compact")` if:
     * This is the first search in the current session
     * You're unsure about field names or data structure
     * Previous searches failed due to invalid field names
   - Skip if you already have the schema from earlier in this session
   - The data model reveals valid search fields, entity types, and record types

2. **STEP 2: Execute Search**
   - Use `search_master_data` with COMPLETE property paths from the data model
   - **CRITICAL**: Use full nested paths like "legal_name.last_name", NOT just "legal_name"
   - **CRITICAL**: NEVER use property="*" as your first attempt - only as fallback
   - Choose search_type based on user intent:
     * "entity" (golden records) - DEFAULT for most queries about entities/people/organizations
     * "record" (source records) - ONLY when user explicitly asks for source records
   - Validation will reject invalid property paths - use exact paths from data model
   
3. **STEP 3: Fallback Strategy (ONLY if Step 2 fails)**
   - If specific field search returns 0 results OR validation error, try full-text search
   - Full-text syntax: {"property": "*", "condition": "contains", "value": "searchterm"}
   - This searches across ALL fields but is slower

**Property Path Rules (CRITICAL):**
- ✅ CORRECT: "legal_name.last_name", "address.city", "contact.email"
- ❌ WRONG: "legal_name", "address", "contact" (incomplete paths)
- ✅ Use "*" ONLY as fallback after specific search fails
- ❌ NEVER use "*" as first attempt

**Example Workflows:**

First search in session:
User: "Find people named Smith"
1. Call get_data_model() → Learn that "legal_name.last_name" exists (NOT just "legal_name")
2. Call search_master_data(search_type="entity", property="legal_name.last_name", value="Smith")
3. If 0 results → Try search_master_data(search_type="entity", property="*", value="Smith")

Subsequent search in same session:
User: "Now find people in Boston"
1. Skip get_data_model (already have schema)
2. Call search_master_data(search_type="entity", property="address.city", value="Boston")
3. If 0 results → Try full-text search

Entity counting/dashboard:
User: "Count entities by type"
1. Call get_data_model() → Learn entity types
2. For each type: search_master_data(search_type="entity", filters=[{"type":"entity","values":["person"]}], limit=1, include_total_count=true)
3. Use total_count from response for statistics

**Tool Selection — search_master_data vs search_potential_match_issues:**

| User Intent | Tool to Use |
|---|---|
| Find people, organizations, records, entities | `search_master_data` |
| Potential matches / potential duplicates / data quality issues | `search_potential_match_issues` |

`search_potential_match_issues` wraps the `/federated_search` endpoint and returns `potential_match_issues` (not `results`).
- To list all issues: query={"expressions": [{"property": "*", "condition": "equal", "value": "*"}]}
- To count only: add limit=0, include_total_count=True
- Does NOT require fetching the data model first

**Common Mistakes to Avoid:**
- ❌ Calling search_master_data without ever fetching the data model in the session
- ❌ Fetching data model repeatedly when you already have it
- ❌ Using incomplete property paths (e.g., "legal_name" instead of "legal_name.last_name")
- ❌ Using property="*" as first attempt (only use as fallback)
- ❌ Using search_type="record" when user asks about entities (default to "entity")
- ❌ Giving up after 0 results or validation error (try full-text search with property="*")
- ❌ Using search_master_data for potential match / duplicate queries (use search_potential_match_issues instead)

**Current Task:**
Await user query and begin Step 1 immediately.
"""

def main():
    parser = argparse.ArgumentParser(description="MCP Server arguments to control the mode and port")
    parser.add_argument("--mode", "-m", help="Mode of operation of the server", choices=["http", "stdio"], default="http")
    parser.add_argument(
        "--port", "-p",
        help="Port on which the server should listen for requests if running on http",
        type=int,
        default=8000,
    )
    parser.add_argument(
        "--host",
        help="Host interface to bind to in HTTP mode (default: 127.0.0.1)",
        default="127.0.0.1",
    )
    args = parser.parse_args()
    mode = args.mode
    logger.info(f"Starting MCP server in mode {mode}")
    
    if mode == "stdio":
        mcp.run(transport="stdio")
    else:
        port_arg = args.port
        port = int(os.getenv("PORT", str(port_arg)))
        host = os.getenv("HOST", args.host)
        logger.info(f"Starting MCP server on {host}:{port}")
        mcp.run(transport="streamable-http", host=host, port=port)

if __name__ == "__main__":
    main()


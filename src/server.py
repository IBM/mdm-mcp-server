#!/usr/bin/env python3
# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

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

# Import your tools
from data_ms.search.tools import search_records
from data_ms.records.tools import get_record_by_id, get_records_entities_by_record_id
from data_ms.entities.tools import get_entity
from model_ms.model.tools import get_data_model

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize MCP
mcp = FastMCP("mdm-mcp-server")

# Get tools mode from configuration
TOOLS_MODE = Config.MCP_TOOLS_MODE.lower()

logger.info(f"Registering tools in '{TOOLS_MODE}' mode")

# Register core tools (always available)
mcp.add_tool(Tool.from_function(search_records, name="search_records"))
mcp.add_tool(Tool.from_function(get_data_model, name="get_data_model"))

# Register additional tools only in full mode
if TOOLS_MODE == "full":
    logger.info("Registering additional tools: get_record, get_entity, get_records_entities_by_record_id")
    mcp.add_tool(Tool.from_function(get_record_by_id, name="get_record"))
    mcp.add_tool(Tool.from_function(get_entity, name="get_entity"))
    mcp.add_tool(Tool.from_function(get_records_entities_by_record_id, name="get_records_entities_by_record_id"))

@mcp.prompt()
def match360_mdm_assistant() -> str:
    """
    Initializes the AI as an IBM MDM Specialist with strict protocol enforcement.
    """
    return """You are the **IBM Master Data Management (MDM) Specialist**. Your only purpose is to assist users in resolving, searching, and managing master data using the underlying IBM MDM system via proper mdm-mcp-server tools.
    
    **CRITICAL PROTOCOL (STRICT ORDERING REQUIRED):**
    You must strictly adhere to the following 2-step process for every user query:
    
    1. **STEP 1: Fetch Schema**
       Call `get_data_model(format=enhanced_compact)` FIRST. 
       *Reason:* You do not know the valid search fields until you see the schema.
       
    2. **STEP 2: Grounded Search of master data**
       Only AFTER receiving the schema, formulate a search using `search_record`.
       *Constraint:* Your search query must ONLY use fields confirmed in Step 1.
    
    **Example of Failure:** Calling `search_record` immediately without checking the model first.
    
    **Current Task:**
    The user is asking for data assistance. Await their query and begin Step 1 immediately.
    """

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCP Server arguments to control the mode and port")
    parser.add_argument("--mode", "-m", help="Mode of operation of the server", choices=["http", "stdio"], default="http")
    parser.add_argument(
        "--port", "-p",
        help="Port on which the server should listen for requests if running on http",
        type=int,
        default=8000,
    )
    args = parser.parse_args()
    mode = args.mode
    logger.info(f"Starting MCP server in mode {mode}")
    
    if mode == "stdio":
        mcp.run(transport="stdio")
    else:
        port_arg = args.port
        port = int(os.getenv("PORT", str(port_arg)))
        logger.info(f"Starting MCP server on port {port}")
        mcp.run(transport="streamable-http")

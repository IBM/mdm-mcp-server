# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    
    API_CPD_BASE_URL = os.getenv("API_CPD_BASE_URL", "")
    API_CPD_AUTH_URL = os.getenv("API_CPD_AUTH_URL", "")
    
    API_CLOUD_BASE_URL = os.getenv("API_CLOUD_BASE_URL", "")
    API_CLOUD_AUTH_URL = os.getenv("API_CLOUD_AUTH_URL", "")
    API_CLOUD_API_KEY = os.getenv("API_CLOUD_API_KEY", "")
    API_CLOUD_CRN = os.getenv("API_CLOUD_CRN", "")
    
    M360_TARGET_PLATFORM = os.getenv("M360_TARGET_PLATFORM", "cloud")
    
    # Tools mode configuration
    # Options: "minimal" (default) or "full"
    # minimal: Only search_master_data and get_data_model
    # full: All available tools
    MCP_TOOLS_MODE = os.getenv("MCP_TOOLS_MODE", "minimal")
    
    API_USERNAME = os.getenv("API_USERNAME", "")
    API_PASSWORD = os.getenv("API_PASSWORD", "")

    # Determine API_BASE_URL based on platform
    if M360_TARGET_PLATFORM == "cloud":
        API_BASE_URL = API_CLOUD_BASE_URL
    elif M360_TARGET_PLATFORM == "cpd":
        API_BASE_URL = API_CPD_BASE_URL
    else:
        raise ValueError("Invalid platform specified")

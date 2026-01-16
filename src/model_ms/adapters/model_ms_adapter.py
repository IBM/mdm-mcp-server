# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Model Microservice adapter for IBM MDM MCP server.

This module provides an adapter for communicating with the Model Microservice,
handling data model operations.
"""

import logging
from typing import Dict, Any

from common.core.base_adapter import BaseMDMAdapter

logger = logging.getLogger(__name__)


class ModelMSAdapter(BaseMDMAdapter):
    """
    Adapter for Model Microservice endpoints.
    
    This adapter provides methods for interacting with the Model Microservice:
    - Data model retrieval (get_data_model)
    
    All methods use the base adapter's HTTP execution methods and handle
    Model MS-specific endpoint construction and parameter formatting.
    
    Note: Only includes currently exposed APIs. Additional methods can be added
    as new endpoints are exposed by the Model Microservice.
    """
    
    def get_data_model(
        self,
        crn: str,
        version: str = "current"
    ) -> Dict[str, Any]:
        """
        Get the data model from the Model Microservice.
        
        This is currently the only exposed API endpoint for the Model Microservice.
        
        Args:
            crn: Cloud Resource Name identifying the tenant
            version: Version of the data model to retrieve (default: "current")
            
        Returns:
            Data model dictionary
            
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        endpoint = "data_model"
        params = {
            "crn": crn,
            "version": version
        }
        
        self.logger.info(f"Fetching data model version '{version}' for CRN: {crn}")
        return self.execute_get(endpoint, params)
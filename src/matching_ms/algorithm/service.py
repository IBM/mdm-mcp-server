# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Algorithm service for IBM MDM MCP server.

This module provides a service class that encapsulates matching algorithm business logic,
separating concerns from the tool interface layer and following Hexagonal Architecture.
"""

import logging
import requests
from typing import Dict, Any, Optional, Literal

from fastmcp import Context

from common.core.base_service import BaseService
from common.domain.crn_validator import CRNValidationError
from matching_ms.adapters.matching_ms_adapter import MatchingMSAdapter
from matching_ms.algorithm.formatters import apply_format_transformation

logger = logging.getLogger(__name__)


class AlgorithmService(BaseService):
    """
    Service class for handling matching algorithm operations.
    
    This class extends BaseService and provides algorithm-specific functionality:
    - Retrieve matching algorithm via MatchingMSAdapter
    - Algorithm-specific error handling
    - Validation of algorithm parameters
    
    Inherits from BaseService:
    - Session and CRN validation
    - Common error handling patterns
    
    Uses MatchingMSAdapter for:
    - HTTP communication with Matching Microservice
    - Algorithm endpoint operations
    
    The algorithm functions in tools.py use these methods to retrieve matching algorithms.
    """
    
    def __init__(self, adapter: Optional[MatchingMSAdapter] = None):
        """
        Initialize the algorithm service with a Matching MS adapter.
        
        Args:
            adapter: Optional MatchingMSAdapter instance (creates default if None)
        """
        super().__init__(adapter or MatchingMSAdapter())
        # Store typed adapter reference for type checking
        self.adapter: MatchingMSAdapter = self.adapter  # type: ignore
    
    def fetch_algorithm_from_api(
        self,
        record_type: str,
        validated_crn: str,
        template: bool = False,
        format: Literal["full", "compact"] = "compact"
    ) -> Dict[str, Any]:
        """
        Fetch matching algorithm from the IBM MDM API via adapter.
        
        Args:
            record_type: The data type identifier of source records
            validated_crn: Validated Cloud Resource Name
            template: Response will return the default template algorithm when set to true
            format: Format of the response - "full" or "compact" (default: "compact")
            
        Returns:
            Algorithm dictionary from the API, optionally transformed
            
        Raises:
            requests.exceptions.RequestException: If API request fails
            ValueError: If format is invalid
        """
        algorithm = self.adapter.get_matching_algorithm(
            record_type=record_type,
            crn=validated_crn,
            template=template
        )
        
        # Apply format transformation
        return apply_format_transformation(algorithm, format)
    
    def get_matching_algorithm(
        self,
        ctx: Context,
        record_type: str,
        crn: Optional[str] = None,
        template: bool = False,
        format: Literal["full", "compact"] = "compact"
    ) -> Dict[str, Any]:
        """
        Retrieve the matching algorithm for a given record type with declarative validation.
        
        This method orchestrates the retrieval process:
        1. Validates session and CRN
        2. Validates record_type parameter
        3. Fetches algorithm from API
        4. Applies format transformation
        5. Handles errors with standardized responses
        
        A matching algorithm contains the matching metadata for a given record type
        and is comprised of standardization, bucket generation and comparison sections.
        
        Args:
            ctx: MCP Context object with session information
            record_type: The data type identifier of source records (e.g., 'person', 'organization', 'contract')
            crn: Cloud Resource Name identifying the tenant (optional)
            template: Response will return the default template algorithm when set to true (default: False)
            format: Format of the response - "full" or "compact" (default: "compact")
            
        Returns:
            Algorithm from IBM MDM or error response
        """
        try:
            # Validate session and CRN
            session_id, validated_crn, tenant_id = self.validate_session_and_crn(ctx, crn)
            
            # Validate record_type
            if not record_type or not record_type.strip():
                return {
                    "error": "record_type is required and cannot be empty",
                    "status_code": 400
                }
            
            self.logger.info(
                f"Fetching matching algorithm for record_type: {record_type}, "
                f"template: {template}, format: {format} "
                f"for tenant: {tenant_id} (CRN: {validated_crn}), session: {session_id}"
            )
            
            # Fetch algorithm from API with format transformation
            return self.fetch_algorithm_from_api(
                record_type=record_type,
                validated_crn=validated_crn,
                template=template,
                format=format
            )
            
        except CRNValidationError as e:
            # CRN validation errors already formatted
            return e.args[0] if e.args else {"error": str(e), "status_code": 400}
        
        except ValueError as e:
            # Format validation errors
            return {
                "error": str(e),
                "status_code": 400
            }
        
        except requests.exceptions.RequestException as e:
            return self.handle_api_error(
                e,
                "get matching algorithm",
                {
                    "record_type": record_type,
                    "template": template,
                    "format": format
                }
            )
        
        except Exception as e:
            return self.handle_unexpected_error(e, "get matching algorithm")


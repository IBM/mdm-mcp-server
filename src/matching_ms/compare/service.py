# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Compare service for IBM MDM MCP server.

This module provides a service class that encapsulates compare-related business logic,
separating concerns from the tool interface layer and following Hexagonal Architecture.
"""

import logging
import requests
from typing import Dict, Any, Optional, List

from fastmcp import Context

from common.core.base_service import BaseService
from common.domain.crn_validator import CRNValidationError
from matching_ms.adapters.matching_ms_adapter import MatchingMSAdapter

logger = logging.getLogger(__name__)


class CompareService(BaseService):
    """
    Service class for handling record comparison operations.
    
    This class extends BaseService and provides compare-specific functionality:
    - Record comparison via MatchingMSAdapter (by record numbers or record data)
    - Compare-specific error handling
    - Validation of comparison parameters
    
    Inherits from BaseService:
    - Session and CRN validation
    - Common error handling patterns
    
    Uses MatchingMSAdapter for:
    - HTTP communication with Matching Microservice
    - Compare endpoint operations
    
    The compare functions in tools.py use these methods to compare records.
    """
    
    def __init__(self, adapter: Optional[MatchingMSAdapter] = None):
        """
        Initialize the compare service with a Matching MS adapter.
        
        Args:
            adapter: Optional MatchingMSAdapter instance (creates default if None)
        """
        super().__init__(adapter or MatchingMSAdapter())
        # Store typed adapter reference for type checking
        self.adapter: MatchingMSAdapter = self.adapter  # type: ignore
    
    def fetch_comparison_from_api(
        self,
        entity_type: str,
        record_type: str,
        validated_crn: str,
        details: str = "low",
        record_number1: Optional[str] = None,
        record_number2: Optional[str] = None,
        records: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Fetch comparison results from the IBM MDM API via adapter.
        
        Args:
            entity_type: The entity type for the records
            record_type: The record type
            validated_crn: Validated Cloud Resource Name
            details: Level of detail in response
            record_number1: First record number (for record number comparison)
            record_number2: Second record number (for record number comparison)
            records: Array of record objects (for record data comparison)
            
        Returns:
            Comparison results dictionary from the API
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        return self.adapter.compare_records(
            entity_type=entity_type,
            record_type=record_type,
            crn=validated_crn,
            details=details,
            record_number1=record_number1,
            record_number2=record_number2,
            records=records
        )
    
    def compare_records(
        self,
        ctx: Context,
        entity_type: str,
        record_type: str = "person",
        record_number1: Optional[str] = None,
        record_number2: Optional[str] = None,
        records: Optional[List[Dict[str, Any]]] = None,
        crn: Optional[str] = None,
        details: str = "low"
    ) -> Dict[str, Any]:
        """
        Compare two records with declarative validation and error handling.
        
        This method orchestrates the comparison process:
        1. Validates session and CRN
        2. Validates comparison parameters (supports two modes)
        3. Fetches comparison results from API
        4. Handles errors with standardized responses
        
        Supports two comparison modes:
        - By record numbers: Provide record_number1 and record_number2
        - By record data: Provide records array with full record attributes
        
        Args:
            ctx: MCP Context object with session information
            entity_type: The entity type for the records
            record_type: The record type
            record_number1: First record number (for record number comparison)
            record_number2: Second record number (for record number comparison)
            records: Array of record objects (for record data comparison)
            crn: Cloud Resource Name identifying the tenant (optional)
            details: Level of detail in response
            
        Returns:
            Comparison results from IBM MDM or error response
        """
        try:
            # Validate session and CRN
            session_id, validated_crn, tenant_id = self.validate_session_and_crn(ctx, crn)
            
            # Validate entity_type
            if not entity_type or not entity_type.strip():
                return {
                    "error": "entity_type is required and cannot be empty",
                    "status_code": 400
                }
            
            # Validate record_type
            if not record_type or not record_type.strip():
                return {
                    "error": "record_type is required and cannot be empty",
                    "status_code": 400
                }
            
            # Determine comparison mode and validate accordingly
            if records is not None and len(records) > 0:
                # Mode 1: Compare by record data
                if len(records) < 1 or len(records) > 2:
                    return {
                        "error": "records array must contain 1 or 2 record objects",
                        "status_code": 400
                    }
                
                # Validate each record has required structure
                for idx, record in enumerate(records):
                    if not isinstance(record, dict):
                        return {
                            "error": f"Record at index {idx} must be a dictionary",
                            "status_code": 400
                        }
                    if "record_type" not in record:
                        return {
                            "error": f"Record at index {idx} missing required field 'record_type'",
                            "status_code": 400
                        }
                    if "attributes" not in record:
                        return {
                            "error": f"Record at index {idx} missing required field 'attributes'",
                            "status_code": 400
                        }
                
                self.logger.info(
                    f"Comparing {len(records)} record(s) by data "
                    f"(entity_type: {entity_type}, record_type: {record_type}) "
                    f"for tenant: {tenant_id} (CRN: {validated_crn}), session: {session_id}"
                )
                
            elif record_number1 is not None and record_number2 is not None:
                # Mode 2: Compare by record numbers
                if not record_number1.strip():
                    return {
                        "error": "record_number1 cannot be empty",
                        "status_code": 400
                    }
                
                if not record_number2.strip():
                    return {
                        "error": "record_number2 cannot be empty",
                        "status_code": 400
                    }
                
                if record_number1 == record_number2:
                    return {
                        "error": "record_number1 and record_number2 must be different",
                        "status_code": 400
                    }
                
                self.logger.info(
                    f"Comparing records {record_number1} and {record_number2} "
                    f"(entity_type: {entity_type}, record_type: {record_type}) "
                    f"for tenant: {tenant_id} (CRN: {validated_crn}), session: {session_id}"
                )
                
            else:
                return {
                    "error": "Must provide either (record_number1 and record_number2) or (records array)",
                    "status_code": 400
                }
            
            # Fetch comparison from API
            return self.fetch_comparison_from_api(
                entity_type=entity_type,
                record_type=record_type,
                validated_crn=validated_crn,
                details=details,
                record_number1=record_number1,
                record_number2=record_number2,
                records=records
            )
            
        except CRNValidationError as e:
            # CRN validation errors already formatted
            return e.args[0] if e.args else {"error": str(e), "status_code": 400}
        
        except requests.exceptions.RequestException as e:
            return self.handle_api_error(
                e, 
                "compare records", 
                {
                    "entity_type": entity_type,
                    "record_type": record_type,
                    "record_number1": record_number1,
                    "record_number2": record_number2,
                    "has_records_data": records is not None
                }
            )
        
        except Exception as e:
            return self.handle_unexpected_error(e, "compare records")

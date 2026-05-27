# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Linkage rules service for IBM MDM MCP server.

This module provides a service class that encapsulates linkage rules preview business logic,
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


class LinkageRulesService(BaseService):
    """
    Service class for handling linkage rules preview operations.
    
    This class extends BaseService and provides linkage rules-specific functionality:
    - Preview entity composition via MatchingMSAdapter
    - Linkage rules-specific error handling
    - Validation of linkage rules parameters
    
    Inherits from BaseService:
    - Session and CRN validation
    - Common error handling patterns
    
    Uses MatchingMSAdapter for:
    - HTTP communication with Matching Microservice
    - Linkage rules preview endpoint operations
    
    The linkage rules functions in tools.py use these methods to preview entity composition.
    """
    
    def __init__(self, adapter: Optional[MatchingMSAdapter] = None):
        """
        Initialize the linkage rules service with a Matching MS adapter.
        
        Args:
            adapter: Optional MatchingMSAdapter instance (creates default if None)
        """
        super().__init__(adapter or MatchingMSAdapter())
        # Store typed adapter reference for type checking
        self.adapter: MatchingMSAdapter = self.adapter  # type: ignore
    
    def fetch_linkage_rules_preview_from_api(
        self,
        entity_type: str,
        rules: List[Dict[str, Any]],
        validated_crn: str,
        create_rule_for_non_existent_derived_data: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Fetch linkage rules preview from the IBM MDM API via adapter.
        
        Args:
            entity_type: The data type identifier of entity
            rules: Collection of linkage rules
            validated_crn: Validated Cloud Resource Name
            create_rule_for_non_existent_derived_data: Creates a rule when derived data is not present
            
        Returns:
            Preview results dictionary from the API
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        return self.adapter.preview_linkage_rules(
            entity_type=entity_type,
            rules=rules,
            crn=validated_crn,
            create_rule_for_non_existent_derived_data=create_rule_for_non_existent_derived_data
        )
    
    def preview_linkage_rules(
        self,
        ctx: Context,
        entity_type: str,
        rules: List[Dict[str, Any]],
        crn: Optional[str] = None,
        create_rule_for_non_existent_derived_data: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Preview entity composition by hypothesizing linkage rules with declarative validation.
        
        This method orchestrates the preview process:
        1. Validates session and CRN
        2. Validates linkage rules parameters
        3. Fetches preview results from API
        4. Handles errors with standardized responses
        
        Args:
            ctx: MCP Context object with session information
            entity_type: The data type identifier of entity (e.g., person_entity, organization_entity)
            rules: Collection of linkage rules, each containing:
                - record_numbers: List of record numbers to link/unlink
                - rule_type: Type of rule - 'link' or 'unlink'
                - description: Optional description of the rule
            crn: Cloud Resource Name identifying the tenant (optional)
            create_rule_for_non_existent_derived_data: Creates a rule when derived data is not present
            
        Returns:
            Preview results from IBM MDM or error response
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
            
            # Validate rules
            if not rules or len(rules) == 0:
                return {
                    "error": "rules array is required and must contain at least one rule",
                    "status_code": 400
                }
            
            # Validate each rule
            for idx, rule in enumerate(rules):
                if not isinstance(rule, dict):
                    return {
                        "error": f"Rule at index {idx} must be a dictionary",
                        "status_code": 400
                    }
                
                # Validate required fields
                if "record_numbers" not in rule:
                    return {
                        "error": f"Rule at index {idx} missing required field 'record_numbers'",
                        "status_code": 400
                    }
                
                if "rule_type" not in rule:
                    return {
                        "error": f"Rule at index {idx} missing required field 'rule_type'",
                        "status_code": 400
                    }
                
                # Validate record_numbers is a list
                if not isinstance(rule["record_numbers"], list):
                    return {
                        "error": f"Rule at index {idx}: 'record_numbers' must be a list",
                        "status_code": 400
                    }
                
                if len(rule["record_numbers"]) == 0:
                    return {
                        "error": f"Rule at index {idx}: 'record_numbers' must contain at least one record number",
                        "status_code": 400
                    }
                
                # Validate rule_type
                if rule["rule_type"] not in ["link", "unlink"]:
                    return {
                        "error": f"Rule at index {idx}: 'rule_type' must be either 'link' or 'unlink'",
                        "status_code": 400
                    }
            
            self.logger.info(
                f"Previewing {len(rules)} linkage rule(s) "
                f"(entity_type: {entity_type}) "
                f"for tenant: {tenant_id} (CRN: {validated_crn}), session: {session_id}"
            )
            
            # Fetch preview from API
            return self.fetch_linkage_rules_preview_from_api(
                entity_type=entity_type,
                rules=rules,
                validated_crn=validated_crn,
                create_rule_for_non_existent_derived_data=create_rule_for_non_existent_derived_data
            )
            
        except CRNValidationError as e:
            # CRN validation errors already formatted
            return e.args[0] if e.args else {"error": str(e), "status_code": 400}
        
        except requests.exceptions.RequestException as e:
            return self.handle_api_error(
                e, 
                "preview linkage rules", 
                {
                    "entity_type": entity_type,
                    "rules_count": len(rules) if rules else 0
                }
            )
        
        except Exception as e:
            return self.handle_unexpected_error(e, "preview linkage rules")

# Made with Bob

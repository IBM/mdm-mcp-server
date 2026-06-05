# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Linkage rule service for IBM MDM MCP server.

This module provides a service class that encapsulates linkage rule business logic,
including entity resolution operations.
"""

import logging
import requests
from typing import Dict, Any, Optional, List

from fastmcp import Context

from common.core.base_service import BaseService
from common.domain.crn_validator import CRNValidationError
from matching_ms.adapters.matching_ms_adapter import MatchingMSAdapter

logger = logging.getLogger(__name__)


class LinkageRuleService(BaseService):
    """
    Service class for handling linkage rule operations.
    
    This class extends BaseService and provides linkage rule-specific functionality:
    - Linkage rule application via MatchingMSAdapter
    - Entity resolution-specific error handling
    
    Inherits from BaseService:
    - Session and CRN validation
    - Common error handling patterns
    
    Uses MatchingMSAdapter for:
    - HTTP communication with Matching Microservice
    - Linkage rule endpoint operations
    
    The apply_linkage_rules function in tools.py uses these methods to apply
    entity resolution decisions.
    """
    
    def __init__(self, adapter: Optional[MatchingMSAdapter] = None):
        """
        Initialize the linkage rule service with a Matching MS adapter.
        
        Args:
            adapter: Optional MatchingMSAdapter instance (creates default if None)
        """
        super().__init__(adapter or MatchingMSAdapter())
        # Store typed adapter reference for type checking
        self.adapter: MatchingMSAdapter = self.adapter  # type: ignore
    
    def apply_linkage_rules_from_api(
        self,
        entity_type: str,
        rule_type: str,
        record_numbers: List[str],
        validated_crn: str,
        description: str,
        create_rule_for_non_existent_derived_data: bool = False
    ) -> Dict[str, Any]:
        """
        Apply linkage rule via the Matching MS API.
        
        Args:
            entity_type: The entity type (e.g., "us_bank_entity")
            rule_type: Type of rule to apply (link, unlink, merge, unmerge)
            record_numbers: List of record numbers to apply the rule to
            validated_crn: Validated Cloud Resource Name
            description: Description of the rule (required)
            create_rule_for_non_existent_derived_data: Whether to create rule for non-existent derived data
            
        Returns:
            Response dictionary from the API
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        return self.adapter.apply_linkage_rules(
            entity_type=entity_type,
            rule_type=rule_type,
            record_numbers=record_numbers,
            crn=validated_crn,
            description=description,
            create_rule_for_non_existent_derived_data=create_rule_for_non_existent_derived_data
        )
    
    def apply_linkage_rules(
        self,
        ctx: Context,
        entity_type: str,
        rule_type: str,
        record_numbers: List[str],
        description: str,
        crn: Optional[str] = None,
        create_rule_for_non_existent_derived_data: bool = False
    ) -> Dict[str, Any]:
        """
        Apply a linkage rule to resolve entity relationships.
        
        This method orchestrates the linkage rule application process:
        1. Validates session and CRN
        2. Applies linkage rule via API
        3. Returns standardized response
        
        Args:
            ctx: MCP Context object with session information
            entity_type: The entity type (e.g., "us_bank_entity")
            rule_type: Type of rule to apply (link, unlink, merge, unmerge)
            record_numbers: List of record numbers to apply the rule to
            description: Description of the rule (required)
            crn: Cloud Resource Name identifying the tenant (optional)
            create_rule_for_non_existent_derived_data: Whether to create rule for non-existent derived data
            
        Returns:
            Dictionary containing:
                - success: Boolean indicating operation success
                - action: The action that was performed
                - entity_state: Current state of the entities after the operation
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
            
            # Validate rule_type
            if not rule_type or not rule_type.strip():
                return {
                    "error": "rule_type is required and cannot be empty",
                    "status_code": 400
                }
            
            # Validate record_numbers
            if not record_numbers or len(record_numbers) < 2:
                return {
                    "error": "record_numbers must contain at least 2 record numbers",
                    "status_code": 400
                }
            
            # Validate each record number is not empty
            for idx, record_num in enumerate(record_numbers):
                if not record_num or not record_num.strip():
                    return {
                        "error": f"Record number at index {idx} cannot be empty",
                        "status_code": 400
                    }
            
            # Check for duplicate record numbers
            if len(record_numbers) != len(set(record_numbers)):
                return {
                    "error": "record_numbers must not contain duplicates",
                    "status_code": 400
                }
            
            # Validate description
            if not description or not description.strip():
                return {
                    "error": "description is required and cannot be empty",
                    "status_code": 400
                }
            
            self.logger.info(
                f"Applying linkage rule: rule_type={rule_type}, "
                f"entity_type={entity_type}, record_numbers={record_numbers}, "
                f"tenant: {tenant_id}, session: {session_id}"
            )
            
            # Apply linkage rule via API
            response = self.apply_linkage_rules_from_api(
                entity_type=entity_type,
                rule_type=rule_type,
                record_numbers=record_numbers,
                validated_crn=validated_crn,
                description=description,
                create_rule_for_non_existent_derived_data=create_rule_for_non_existent_derived_data
            )
            
            self.logger.info(
                f"Linkage rule applied successfully: rule_type={rule_type}, "
                f"success={response.get('success', False)}"
            )
            
            return response
            
        except CRNValidationError as e:
            # CRN validation errors already formatted
            return e.args[0] if e.args else {"error": str(e), "status_code": 400}
        
        except requests.exceptions.RequestException as e:
            # Log the full error details for debugging
            self.logger.error(
                f"API error applying linkage rule: {str(e)}",
                extra={
                    "rule_type": rule_type,
                    "entity_type": entity_type,
                    "record_numbers": record_numbers,
                    "status_code": getattr(getattr(e, 'response', None), 'status_code', None),
                    "response_text": getattr(getattr(e, 'response', None), 'text', None)
                }
            )
            return self.handle_api_error(
                e,
                "apply linkage rule",
                {
                    "rule_type": rule_type,
                    "entity_type": entity_type,
                    "record_numbers": record_numbers
                }
            )
        
        except Exception as e:
            return self.handle_unexpected_error(e, "apply linkage rule")
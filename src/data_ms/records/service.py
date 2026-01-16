# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Record service for IBM MDM MCP server.

This module provides a service class that encapsulates record-related business logic,
separating concerns from the tool interface layer and following Hexagonal Architecture.
"""

import logging
import requests
from typing import Dict, Any, Optional

from fastmcp import Context

from common.core.base_service import BaseService
from common.domain.crn_validator import CRNValidationError
from data_ms.adapters.data_ms_adapter import DataMSAdapter

logger = logging.getLogger(__name__)


class RecordService(BaseService):
    """
    Service class for handling record operations.
    
    This class extends BaseService and provides record-specific functionality:
    - Record retrieval via DataMSAdapter
    - Entity retrieval for records via DataMSAdapter
    - Record-specific error handling
    
    Inherits from BaseService:
    - Session and CRN validation
    - Common error handling patterns
    
    Uses DataMSAdapter for:
    - HTTP communication with Data Microservice
    - Record and entity endpoint operations
    
    The record functions in tools.py use these methods to retrieve records and entities.
    """
    
    def __init__(self, adapter: Optional[DataMSAdapter] = None):
        """
        Initialize the record service with a Data MS adapter.
        
        Args:
            adapter: Optional DataMSAdapter instance (creates default if None)
        """
        super().__init__(adapter or DataMSAdapter())
        # Store typed adapter reference for type checking
        self.adapter: DataMSAdapter = self.adapter  # type: ignore
    
    def fetch_record_from_api(
        self,
        record_id: str,
        validated_crn: str
    ) -> Dict[str, Any]:
        """
        Fetch record from the IBM MDM API via adapter.
        
        Args:
            record_id: The ID of the record to retrieve
            validated_crn: Validated Cloud Resource Name
            
        Returns:
            Record data dictionary from the API
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        return self.adapter.get_record(record_id, validated_crn)
    
    def fetch_record_entities_from_api(
        self,
        record_id: str,
        validated_crn: str
    ) -> Dict[str, Any]:
        """
        Fetch entities for a record from the IBM MDM API via adapter.
        
        Args:
            record_id: The ID of the record to retrieve entities for
            validated_crn: Validated Cloud Resource Name
            
        Returns:
            Entities data dictionary from the API
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        return self.adapter.get_record_entities(record_id, validated_crn)
    
    def get_record_by_id(
        self,
        ctx: Context,
        record_id: str,
        crn: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a record by ID with declarative validation and error handling.
        
        This method orchestrates the record retrieval process:
        1. Validates session and CRN
        2. Fetches record from API
        3. Handles errors with standardized responses
        
        Args:
            ctx: MCP Context object with session information
            record_id: The ID of the record to retrieve
            crn: Cloud Resource Name identifying the tenant (optional)
            
        Returns:
            Record data from IBM MDM or error response
        """
        try:
            # Validate session and CRN
            session_id, validated_crn, tenant_id = self.validate_session_and_crn(ctx, crn)
            
            self.logger.info(
                f"Getting record with ID {record_id} for tenant: {tenant_id} "
                f"(CRN: {validated_crn}), session: {session_id}"
            )
            
            # Fetch record from API
            return self.fetch_record_from_api(record_id, validated_crn)
            
        except CRNValidationError as e:
            # CRN validation errors already formatted
            return e.args[0] if e.args else {"error": str(e), "status_code": 400}
        
        except requests.exceptions.RequestException as e:
            return self.handle_api_error(e, "retrieve record", {"record_id": record_id})
        
        except Exception as e:
            return self.handle_unexpected_error(e, "retrieve record")
    
    def get_records_entities_by_record_id(
        self,
        ctx: Context,
        record_id: str,
        crn: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all entities for a record with declarative validation and error handling.
        
        This method orchestrates the entity retrieval process:
        1. Validates session and CRN
        2. Fetches entities from API
        3. Handles errors with standardized responses
        
        Args:
            ctx: MCP Context object with session information
            record_id: The ID of the record to retrieve entities for
            crn: Cloud Resource Name identifying the tenant (optional)
            
        Returns:
            Entities data from IBM MDM or error response
        """
        try:
            # Validate session and CRN
            session_id, validated_crn, tenant_id = self.validate_session_and_crn(ctx, crn)
            
            self.logger.info(
                f"Getting entities for record ID {record_id} for tenant: {tenant_id} "
                f"(CRN: {validated_crn}), session: {session_id}"
            )
            
            # Fetch entities from API
            return self.fetch_record_entities_from_api(record_id, validated_crn)
            
        except CRNValidationError as e:
            # CRN validation errors already formatted
            return e.args[0] if e.args else {"error": str(e), "status_code": 400}
        
        except requests.exceptions.RequestException as e:
            return self.handle_api_error(e, "retrieve entities for record", {"record_id": record_id})
        
        except Exception as e:
            return self.handle_unexpected_error(e, "retrieve entities for record")
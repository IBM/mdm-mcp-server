# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Data export service for IBM MDM MCP server.

This module provides a service class that encapsulates data export business logic,
separating concerns from the tool interface layer and following Hexagonal Architecture.
"""

import logging
import requests
from typing import Dict, Any, Optional, Literal

from fastmcp import Context
from pydantic import ValidationError

from common.core.base_service import BaseService
from common.domain.crn_validator import CRNValidationError
from common.models.error_models import (
    create_validation_error,
    create_api_error
)
from data_ms.adapters.data_ms_adapter import DataMSAdapter

logger = logging.getLogger(__name__)


class DataExportService(BaseService):
    """
    Service class for handling data export operations.
    
    This class extends BaseService and provides export-specific functionality:
    - Creating export jobs
    - Downloading export files
    
    Inherits from BaseService:
    - Session and CRN validation
    - Common error handling patterns
    
    Uses DataMSAdapter for:
    - HTTP communication with Data Microservice
    - Export endpoint operations
    """
    
    def __init__(self, adapter: Optional[DataMSAdapter] = None):
        """
        Initialize the data export service with a Data MS adapter.
        
        Args:
            adapter: Optional DataMSAdapter instance (creates default if None)
        """
        super().__init__(adapter or DataMSAdapter())
        self.adapter: DataMSAdapter = self.adapter  # type: ignore
    
    def _build_export_request_body(
        self,
        export_name: str,
        export_type: Literal["record", "entity"],
        record_type: str,
        file_format: Literal["csv", "tsv", "psv"],
        compression_type: Literal["tar", "tgz", "zip", "none"],
        search_criteria: Optional[Dict[str, Any]] = None,
        include_only_updated_after: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build the request body for creating an export job.
        
        Args:
            export_name: Name for the export job
            export_type: Type of data to export (record or entity)
            record_type: Record type to export
            file_format: Format of the export file
            compression_type: Compression type for the export
            search_criteria: Optional search criteria for filtering
            include_only_updated_after: Optional timestamp for incremental export
            
        Returns:
            Request body dictionary for the API
        """
        # Build search criteria - required by API
        # If not provided, default to export all records
        if search_criteria:
            criteria: Dict[str, Any] = {
                "search_type": export_type
            }
            if "query" in search_criteria:
                criteria["query"] = search_criteria["query"]
            if "filters" in search_criteria:
                criteria["filters"] = search_criteria["filters"]
        else:
            # Default: export all data (wildcard search)
            criteria = {
                "search_type": export_type,
                "query": {
                    "expressions": [
                        {"property": "*", "condition": "contains", "value": "*"}
                    ]
                }
            }
        
        request_body: Dict[str, Any] = {
            "job_name": export_name,
            "export_type": export_type,
            "record_type": record_type,
            "format": file_format,  # API uses 'format' not 'file_format'
            "compression_type": compression_type,
            "search_criteria": criteria  # Required by API
        }
        
        # Add incremental export timestamp if provided
        if include_only_updated_after:
            request_body["include_only_updated_after"] = include_only_updated_after
        
        return request_body
    
    def create_export(
        self,
        ctx: Context,
        export_name: str,
        export_type: Literal["record", "entity"],
        record_type: str,
        file_format: Literal["csv", "tsv", "psv"],
        compression_type: Literal["tar", "tgz", "zip", "none"],
        search_criteria: Optional[Dict[str, Any]] = None,
        include_only_updated_after: Optional[str] = None,
        crn: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new data export job.
        
        Args:
            ctx: MCP Context object for session tracking
            export_name: Name for the export job
            export_type: Type of data to export (record or entity)
            record_type: Record type to export
            file_format: Format of the export file
            compression_type: Compression type for the export
            search_criteria: Optional search criteria for filtering
            include_only_updated_after: Optional timestamp for incremental export
            crn: Optional CRN (uses default if None)
            
        Returns:
            Export job response or formatted error response
        """
        try:
            # Validate session and CRN
            session_id, validated_crn, tenant_id = self.validate_session_and_crn(
                ctx, crn, check_preconditions=False
            )
            
            self.logger.info(
                f"Creating export job '{export_name}' for {export_type} type '{record_type}', "
                f"tenant: {tenant_id}, session: {session_id}"
            )
            
            # Build request body
            request_body = self._build_export_request_body(
                export_name=export_name,
                export_type=export_type,
                record_type=record_type,
                file_format=file_format,
                compression_type=compression_type,
                search_criteria=search_criteria,
                include_only_updated_after=include_only_updated_after
            )
            
            # Execute export creation request via adapter
            return self.adapter.create_data_export(
                export_request=request_body,
                crn=validated_crn
            )
            
        except CRNValidationError as e:
            return e.args[0] if e.args else {"error": str(e), "status_code": 400}
        
        except ValidationError as e:
            self.logger.error(f"Validation error: {str(e)}")
            return create_validation_error(
                message=f"Invalid export request: {str(e)}",
                field="export_request"
            )
        
        except requests.exceptions.RequestException as e:
            return self.handle_api_error(e, "create export job")
        
        except Exception as e:
            return self.handle_unexpected_error(e, "create export job")
    
    def download_export(
        self,
        ctx: Context,
        export_id: str,
        crn: Optional[str] = None,
        save_to_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Download an export file.
        
        This method downloads the actual export file content. The file can either
        be saved to disk or returned in memory.
        
        Args:
            ctx: MCP Context object for session tracking
            export_id: The unique identifier of the export job
            crn: Optional CRN (uses default if None)
            save_to_path: Optional directory path to save the file.
                          If None, file content is returned in memory.
            
        Returns:
            Download result including file info and optionally file path
            or formatted error response
        """
        try:
            # Validate session and CRN
            session_id, validated_crn, tenant_id = self.validate_session_and_crn(
                ctx, crn, check_preconditions=False
            )
            
            self.logger.info(
                f"Downloading export '{export_id}', "
                f"tenant: {tenant_id}, session: {session_id}"
            )
            
            # Download file via adapter
            result = self.adapter.download_data_export(
                export_id=export_id,
                crn=validated_crn,
                save_to_path=save_to_path
            )
            
            # Remove file_content from response (too large for JSON)
            # Keep only metadata
            if "file_content" in result:
                del result["file_content"]
            
            return result
            
        except CRNValidationError as e:
            return e.args[0] if e.args else {"error": str(e), "status_code": 400}
        
        except requests.exceptions.RequestException as e:
            return self.handle_api_error(e, f"download export {export_id}")
        
        except Exception as e:
            return self.handle_unexpected_error(e, f"download export {export_id}")
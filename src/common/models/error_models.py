# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Pydantic models and exceptions for standardized error responses.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CRNValidationErrorDetails(BaseModel):
    """Details for CRN validation errors."""
    provided_crn: str = Field(..., description="The CRN that was provided")
    default_crn: str = Field(..., description="The default CRN that can be used")
    valid_formats: List[str] = Field(..., description="List of valid CRN format examples")


class ErrorResponse(BaseModel):
    """Base error response model."""
    error: str = Field(..., description="Error type identifier")
    status_code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class CRNValidationErrorResponse(BaseModel):
    """Error response for CRN validation failures."""
    error: str = Field(default="CRNValidationFailed", description="Error type")
    status_code: int = Field(default=400, description="HTTP status code")
    message: str = Field(..., description="Human-readable error message")
    details: Dict[str, Any] = Field(..., description="CRN validation error details")


class PreconditionFailedErrorResponse(BaseModel):
    """Error response for precondition failures."""
    error: str = Field(default="PreconditionFailed", description="Error type")
    status_code: int = Field(default=428, description="HTTP status code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class ValidationErrorResponse(BaseModel):
    """Error response for input validation failures."""
    error: str = Field(default="ValidationError", description="Error type")
    status_code: int = Field(default=400, description="HTTP status code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Validation error details")


class APIErrorResponse(BaseModel):
    """Error response for API request failures."""
    error: str = Field(default="APIError", description="Error type")
    status_code: int = Field(..., description="HTTP status code from API")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="API error details")


def create_crn_validation_error(
    provided_crn: str,
    message: str,
    default_crn: str,
    valid_formats: List[str]
) -> Dict[str, Any]:
    """
    Create a CRN validation error response.
    
    Args:
        provided_crn: The CRN that was provided
        message: Error message
        default_crn: The default CRN
        valid_formats: List of valid format examples
        
    Returns:
        Dictionary representation of the error
    """
    details_obj = CRNValidationErrorDetails(
        provided_crn=provided_crn,
        default_crn=default_crn,
        valid_formats=valid_formats
    )
    error = CRNValidationErrorResponse(
        message=message,
        details=details_obj.model_dump()
    )
    return error.model_dump()


def create_data_model_precondition_error(
    session_id: str,
    crn: str
) -> Dict[str, Any]:
    """
    Create a precondition failed error for missing data model fetch.
    
    Args:
        session_id: The session ID
        crn: The CRN being used
        
    Returns:
        Dictionary representation of the error
    """
    instructions = f"""
    PRECONDITION FAILED: Data model must be fetched before searching.

    To fix this error:
    
    1. First call get_data_model() with the same session:
    get_data_model(
        crn="{crn}", format='enhanced_compact'
    )

    2. Review the data model to understand:
    - Available entity types (e.g., 'person_entity', 'organization_entity', etc.)
    - Searchable attributes and their property paths (e.g., 'legal_name.last_name', etc.)
    - Attribute data types and valid search conditions

    3. Then call search_master_data() with the same session and properly created search request:

    The data model is essential for constructing valid search queries with correct
    property paths and understanding which fields are searchable.
    """
    
    error = PreconditionFailedErrorResponse(
        message="Data model must be fetched before searching.",
        details={
            "session_id": session_id,
            "required_action": "Call get_data_model(format='enhanced_compact') in the same session",
            "instructions": instructions
        }
    )
    return error.model_dump()


def create_precondition_error(
    session_id: str,
    message: str,
    required_action: str
) -> Dict[str, Any]:
    """
    Create a generic precondition failed error response.
    
    Args:
        session_id: The session ID
        message: Error message
        required_action: Description of required action
        
    Returns:
        Dictionary representation of the error
    """
    error = PreconditionFailedErrorResponse(
        message=message,
        details={
            "session_id": session_id,
            "required_action": required_action
        }
    )
    return error.model_dump()


def create_validation_error(
    message: str,
    field: Optional[str] = None,
    constraint: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a validation error response.
    
    Args:
        message: Error message
        field: Field that failed validation
        constraint: Constraint that was violated
        
    Returns:
        Dictionary representation of the error
    """
    details = {}
    if field:
        details["field"] = field
    if constraint:
        details["constraint"] = constraint
    
    error = ValidationErrorResponse(
        message=message,
        details=details if details else None
    )
    return error.model_dump()


def create_api_error(
    message: str,
    status_code: int,
    api_details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create an API error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        api_details: Additional API error details
        
    Returns:
        Dictionary representation of the error
    """
    error = APIErrorResponse(
        message=message,
        status_code=status_code,
        details=api_details
    )
    return error.model_dump()


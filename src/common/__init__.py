# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Common utilities and shared components for the IBM MDM MCP server.

This package contains:
- auth: Authentication and token management
- core: Base classes and architectural components
- domain: Domain-specific logic (CRN validation, session management)
- models: Shared data models and error responses

Note: Authentication is now handled by AuthenticationManager via dependency injection
in adapters. Use get_shared_auth_manager() to get a shared instance for cache efficiency.
"""

import logging
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = Config.API_BASE_URL
M360_TARGET_PLATFORM = Config.M360_TARGET_PLATFORM


# Export authentication manager functions
from .auth.authentication_manager import (
    AuthenticationManager,
    get_shared_auth_manager,
    invalidate_shared_auth_manager
)

# Export session store functions for convenience
from .domain.session_store import (
    register_data_model_fetch,
    has_fetched_data_model,
    clear_session,
    get_active_sessions,
    clear_all_sessions
)

# Export CRN validation functions
from .domain.crn_validator import (
    validate_crn,
    get_tenant_id_from_crn,
    validate_and_get_crn,
    get_crn_with_precedence,
    format_crn_error_response,
    CRNValidationError,
    DEFAULT_CRN,
    CLOUD_CRN
)

# Export error models
from .models.error_models import (
    create_crn_validation_error,
    create_data_model_precondition_error,
    create_precondition_error,
    create_validation_error,
    create_api_error,
    ErrorResponse,
    CRNValidationErrorResponse,
    PreconditionFailedErrorResponse,
    ValidationErrorResponse,
    APIErrorResponse
)

__all__ = [
    'API_BASE_URL',
    'M360_TARGET_PLATFORM',
    'AuthenticationManager',
    'get_shared_auth_manager',
    'invalidate_shared_auth_manager',
    'register_data_model_fetch',
    'has_fetched_data_model',
    'clear_session',
    'get_active_sessions',
    'clear_all_sessions',
    'validate_crn',
    'get_tenant_id_from_crn',
    'validate_and_get_crn',
    'get_crn_with_precedence',
    'format_crn_error_response',
    'CRNValidationError',
    'DEFAULT_CRN',
    'CLOUD_CRN',
    'create_crn_validation_error',
    'create_data_model_precondition_error',
    'create_precondition_error',
    'create_validation_error',
    'create_api_error',
    'ErrorResponse',
    'CRNValidationErrorResponse',
    'PreconditionFailedErrorResponse',
    'ValidationErrorResponse',
    'APIErrorResponse'
]

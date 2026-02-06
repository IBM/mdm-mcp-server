# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
CRN (Cloud Resource Name) validation utility for IBM MDM MCP server.

CRN Format:
- Full format: "crn:v1:staging:public:mdm-oc:us-south:a/account123:instance456::"
- On-Prem format: ":::::::1::"

The tenant ID is the instance field (index 7).
"""

import logging
import re
from typing import Tuple, Optional
from config import Config

logger = logging.getLogger(__name__)

# Default CRN for On-Prem deployments
DEFAULT_CRN = ":::::::1::"

# Get cloud CRN from config
CLOUD_CRN = Config.API_CLOUD_CRN

# Tenant ID is always at index 7 (the instance field)
TENANT_ID_INDEX = 7

# CRN validation patterns
CRN_PATTERN = re.compile(r'^[^:]*:[^:]*:[^:]*:[^:]*:[^:]*:[^:]*:[^:]*:[^:]+:[^:]*:[^:]*$')
ONPREM_CRN_PATTERN = re.compile(r'^:::::::[\w\-]+::$')


class CRNValidationError(Exception):
    """Raised when CRN validation fails."""
    pass


def validate_crn(crn: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """Validate CRN and extract tenant ID (instance field at index 7)."""
    if not crn or not isinstance(crn, str):
        return False, None, "CRN must be a non-empty string"
    
    parts = crn.split(':')
    
    # Check for On-Prem format (:::::::tenant_id::)
    if ONPREM_CRN_PATTERN.match(crn):
        tenant_id = parts[TENANT_ID_INDEX] if len(parts) > TENANT_ID_INDEX else None
        if tenant_id:
            logger.debug(f"Valid On-Prem CRN format, tenant_id: {tenant_id}")
            return True, tenant_id, None
        else:
            return False, None, f"On-Prem CRN format is missing tenant ID at index {TENANT_ID_INDEX}"
    
    # Check for full CRN format
    if CRN_PATTERN.match(crn):
        if len(parts) > TENANT_ID_INDEX:
            tenant_id = parts[TENANT_ID_INDEX]
            if tenant_id:
                logger.debug(f"Valid full CRN format, tenant_id: {tenant_id}")
                return True, tenant_id, None
            else:
                return False, None, f"CRN is missing tenant ID at index {TENANT_ID_INDEX}"
        else:
            return False, None, f"CRN has insufficient parts: expected at least {TENANT_ID_INDEX + 1}, got {len(parts)}"
    
    return False, None, (
        "CRN format is invalid. Expected formats:\n"
        "  - On-Prem: ':::::::tenant_id::' (e.g., ':::::::1::')\n"
        "  - Full: 'crn:version:env:visibility:service:region:account:instance::' "
        "(e.g., 'crn:v1:staging:public:mdm-oc:us-south:a/account123:instance456::')"
    )


def get_tenant_id_from_crn(crn: str) -> str:
    """Extract tenant ID from CRN or raise CRNValidationError if invalid."""
    is_valid, tenant_id, error_msg = validate_crn(crn)
    
    if not is_valid:
        raise CRNValidationError(f"Invalid CRN: {error_msg}")
    
    if tenant_id is None:
        raise CRNValidationError("Failed to extract tenant ID from CRN")
    
    return tenant_id


def validate_and_get_crn(crn: Optional[str] = None) -> Tuple[str, str]:
    """Validate CRN and return (crn, tenant_id). Uses default if crn is None/empty."""
    # Use default if not provided
    if not crn:
        logger.info(f"No CRN provided, using default: {DEFAULT_CRN}")
        return DEFAULT_CRN, get_tenant_id_from_crn(DEFAULT_CRN)
    
    # Validate provided CRN
    is_valid, tenant_id, error_msg = validate_crn(crn)
    
    if not is_valid:
        logger.error(f"CRN validation failed: {error_msg}")
        raise CRNValidationError(
            f"Invalid CRN format: {error_msg}\n\n"
            f"Provided CRN: {crn}\n"
            f"Default CRN: {DEFAULT_CRN}"
        )
    
    if tenant_id is None:
        raise CRNValidationError("Failed to extract tenant ID from validated CRN")
    
    logger.info(f"CRN validated successfully, tenant_id: {tenant_id}")
    return crn, tenant_id


def get_crn_with_precedence(crn: Optional[str] = None) -> Tuple[str, str]:
    """Get CRN with precedence: 1) provided crn, 2) cloud env CRN, 3) default on-prem CRN."""
    platform = Config.M360_TARGET_PLATFORM
    
    # Priority 1: Explicitly provided CRN
    if crn:
        logger.info(f"Using explicitly provided CRN: {crn}")
        return validate_and_get_crn(crn)
    
    # Priority 2: Platform-specific logic
    if platform == "cloud":
        # For cloud platform, use API_CLOUD_CRN from environment
        if CLOUD_CRN:
            logger.info(f"Using cloud CRN from environment: {CLOUD_CRN}")
            return validate_and_get_crn(CLOUD_CRN)
        else:
            # No CRN configured for cloud platform
            error_msg = (
                "No CRN information found for cloud platform. "
                "Please provide a CRN explicitly or set API_CLOUD_CRN in environment variables."
            )
            logger.error(error_msg)
            raise CRNValidationError(error_msg)
    
    elif platform in ["cpd", "local"]:
        # For CPD/Local platforms, use default on-prem CRN
        logger.info(f"Using default on-prem CRN for {platform} platform: {DEFAULT_CRN}")
        return validate_and_get_crn(DEFAULT_CRN)
    
    else:
        error_msg = f"Unknown platform: {platform}. Expected 'cloud', 'cpd', or 'local'."
        logger.error(error_msg)
        raise CRNValidationError(error_msg)


def format_crn_error_response(crn: str, error_msg: str) -> dict:
    """Format standardized error response for CRN validation failures."""
    from common.models.error_models import create_crn_validation_error
    
    return create_crn_validation_error(
        provided_crn=crn,
        message=error_msg,
        default_crn=DEFAULT_CRN,
        valid_formats=[
            "On-Prem: ':::::::tenant_id::' (e.g., ':::::::1::')",
            "Full: 'crn:version:env:visibility:service:region:account:instance::'"
        ]
    )



# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Algorithm tools for IBM MDM MCP server.
"""

import logging
from typing import Dict, Any, Optional

from fastmcp import Context
from .service import AlgorithmService

logger = logging.getLogger(__name__)

_algorithm_service = AlgorithmService()

def get_matching_algorithm(
    ctx: Context,
    record_type: str,
    crn: Optional[str] = None,
    template: bool = False
) -> Dict[str, Any]:
    """
    Retrieve the matching algorithm for a given record type.
    
    A matching algorithm contains the matching metadata for a given record type and is comprised of:
    - Standardization: Rules for normalizing and standardizing data
    - Bucket generation: Configuration for grouping similar records
    - Comparison: Methods and weights for comparing record attributes
    
    This tool is useful for:
    - Understanding how records are matched in IBM MDM
    - Reviewing matching configuration for a specific record type
    - Getting the default template algorithm for configuration
    - Analyzing standardizers, entity types, and comparison methods
    
    Args:
        ctx: MCP Context object (automatically injected) - provides session information
        record_type: The data type identifier of source records (e.g., 'person', 'organization', 'contract')
        crn: Cloud Resource Name identifying the tenant (optional, defaults to On-Prem tenant)
        template: When set to true, returns the default template algorithm instead of the configured one (default: False)
        
    Returns:
        Algorithm dictionary from IBM MDM containing:
        - locale: The request language and location (e.g., 'en_us')
        - encryption: Asymmetric encryption configuration
        - standardizers: Collection of standardizer definitions for data normalization
        - entity_types: Collection of entity type definitions and their matching rules
        - bucket_group_bit_length: Bit length for bucket group (optional)
        
    Examples:
        # Get the matching algorithm for person records
        result = get_matching_algorithm(
            record_type="person"
        )
        
        # Get the matching algorithm for organization records
        result = get_matching_algorithm(
            record_type="organization"
        )
        
        # Get the default template algorithm for person records
        result = get_matching_algorithm(
            record_type="person",
            template=True
        )
        
        # Get algorithm with full CRN
        result = get_matching_algorithm(
            record_type="person",
            crn="crn:v1:staging:public:mdm-oc:us-south:a/account123:instance456::"
        )
        
    Response Format:
        {
            "locale": "en_us",
            "encryption": {},
            "standardizers": {
                "standardizer_name": {
                    "type": "standardizer_type",
                    "config": {}
                }
            },
            "entity_types": {
                "person_entity": {
                    "matching_rules": [],
                    "comparison_methods": []
                }
            },
            "bucket_group_bit_length": 4
        }
        
    Use Cases:
        1. Configuration Review: Understand current matching configuration
        2. Template Generation: Get default template for new configurations
        3. Troubleshooting: Analyze why records are/aren't matching
        4. Documentation: Document matching rules for a record type
    """
    return _algorithm_service.get_matching_algorithm(
        ctx,
        record_type,
        crn,
        template
    )

# Made with Bob

# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Models for matching algorithm in IBM MDM MCP server.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class AlgorithmEncryption(BaseModel):
    """
    Model for asymmetric encryption configuration in algorithm.
    """
    # The encryption configuration structure can be extended based on actual API response
    pass


class Algorithm(BaseModel):
    """
    Model for matching algorithm response.
    
    The matching algorithm contains the matching metadata for a given record type
    and is comprised of standardization, bucket generation and comparison sections.
    
    Attributes:
        locale: The request language and location (e.g., 'en_us')
        encryption: Asymmetric encryption configuration
        standardizers: Collection of standardizer definitions
        entity_types: Collection of entity type definitions
        bucket_group_bit_length: Bit length for bucket group (default is 4)
    """
    locale: str = Field(
        ...,
        description="The request language and location (e.g., 'en_us')"
    )
    encryption: Dict[str, Any] = Field(
        ...,
        description="Asymmetric encryption configuration"
    )
    standardizers: Dict[str, Any] = Field(
        ...,
        description="Collection of standardizer definitions"
    )
    entity_types: Dict[str, Any] = Field(
        ...,
        description="Collection of entity type definitions"
    )
    bucket_group_bit_length: Optional[int] = Field(
        None,
        description="Bit length for bucket group. The default length is 4"
    )

# Made with Bob

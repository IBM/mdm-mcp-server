# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Adapters package for Matching Microservice.

This package contains adapters for communicating with the Matching Microservice endpoints.
"""

from .matching_ms_adapter import MatchingMSAdapter

__all__ = ['MatchingMSAdapter']

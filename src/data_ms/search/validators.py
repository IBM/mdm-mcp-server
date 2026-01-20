# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Search query validation utilities for the search microservice.

This module helps reduce LLM hallucinations by ensuring that search queries
only reference valid attributes and fields from the actual data model.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from common.domain.session_store import get_cached_data_model

logger = logging.getLogger(__name__)


class SearchQueryValidationError(Exception):
    """
    Raised when a search query contains invalid property paths or attributes.
    """
    def __init__(self, message: str, invalid_properties: List[str], suggestions: Optional[List[str]] = None):
        self.message = message
        self.invalid_properties = invalid_properties
        self.suggestions = suggestions or []
        super().__init__(message)


class DataModelValidator:
    """
    Validates search query property paths against the data model.
    
    This validator ensures that:
    1. Property paths reference valid attributes
    2. Nested property paths (e.g., "legal_name.last_name") are valid
    3. Attributes are searchable (indexed)
    """
    
    def __init__(self, data_model: Dict[str, Any]):
        """
        Initialize the validator with a data model.
        
        Args:
            data_model: The raw data model from IBM MDM API
        """
        self.data_model = data_model
        self.valid_properties = self._build_valid_properties_map()
        self.searchable_properties = self._build_searchable_properties_set()
        
    def _build_valid_properties_map(self) -> Dict[str, Dict[str, Any]]:
        """
        Build a map of all valid property paths from the data model.
        
        Returns:
            Dictionary mapping property paths to their metadata
        """
        properties_map = {}
        
        # Process record types
        if "record_types" in self.data_model:
            for record_type_name, record_type_info in self.data_model["record_types"].items():
                if "attributes" not in record_type_info:
                    continue
                    
                for attr_name, attr_info in record_type_info["attributes"].items():
                    attr_type = attr_info.get("attribute_type", "string")
                    is_indexed = attr_info.get("indexed", False)
                    
                    # Add the top-level attribute
                    properties_map[attr_name] = {
                        "type": attr_type,
                        "indexed": is_indexed,
                        "record_type": record_type_name,
                        "label": attr_info.get("label", attr_name)
                    }
                    
                    # Check if this attribute type has fields (complex type)
                    if "attribute_types" in self.data_model:
                        attr_type_def = self.data_model["attribute_types"].get(attr_type, {})
                        if "fields" in attr_type_def:
                            # Add nested property paths
                            for field_name, field_info in attr_type_def["fields"].items():
                                nested_path = f"{attr_name}.{field_name}"
                                field_indexed = field_info.get("indexed", False)
                                
                                properties_map[nested_path] = {
                                    "type": attr_type,
                                    "field": field_name,
                                    "indexed": field_indexed,
                                    "record_type": record_type_name,
                                    "label": field_info.get("label", field_name),
                                    "parent_attribute": attr_name
                                }
        
        return properties_map
    
    def _build_searchable_properties_set(self) -> Set[str]:
        """
        Build a set of all searchable (indexed) property paths.
        
        Returns:
            Set of searchable property paths
        """
        return {
            prop_path 
            for prop_path, metadata in self.valid_properties.items() 
            if metadata.get("indexed", False)
        }
    
    def validate_property_path(self, property_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a single property path.
        
        Args:
            property_path: The property path to validate (e.g., "legal_name.last_name")
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Special case: "*" is allowed for full-text search
        if property_path == "*":
            return True, None
        
        # FIRST: Check if this is an incomplete path (e.g., "legal_name" when "legal_name.last_name" exists)
        # This must be checked BEFORE checking if property exists, because the parent attribute
        # might exist in valid_properties but we want to reject it if nested paths exist
        nested_paths = [p for p in self.valid_properties.keys() if p.startswith(f"{property_path}.")]
        if nested_paths:
            return False, (
                f"Invalid property path '{property_path}'. This appears to be an incomplete path. "
                f"You must use the complete nested path. "
                f"Did you mean one of: {', '.join(nested_paths[:3])}?"
            )
        
        # Check if property exists
        if property_path not in self.valid_properties:
            # Try to provide helpful suggestions
            suggestions = self._find_similar_properties(property_path)
            suggestion_text = ""
            if suggestions:
                suggestion_text = f" Did you mean: {', '.join(suggestions[:3])}?"
            
            return False, f"Invalid property path '{property_path}'. This property does not exist in the data model.{suggestion_text}"
        
        # Check if property is searchable
        if property_path not in self.searchable_properties:
            metadata = self.valid_properties[property_path]
            return False, (
                f"Property '{property_path}' exists but is not searchable (not indexed). "
                f"Only indexed attributes can be used in search queries. "
                f"Label: {metadata.get('label', 'N/A')}"
            )
        
        return True, None
    
    def _find_similar_properties(self, property_path: str, max_suggestions: int = 5) -> List[str]:
        """
        Find similar property paths to suggest as alternatives using similarity scoring.
        
        Uses sequence matching to find the most similar valid properties,
        prioritizing searchable properties.
        
        Args:
            property_path: The invalid property path
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of similar valid property paths, sorted by similarity
        """
        suggestions_with_scores = []
        
        # Split the property path
        parts = property_path.split(".")
        
        if len(parts) == 1:
            # Single-level property - find similar top-level attributes
            for valid_prop in self.valid_properties.keys():
                if "." not in valid_prop:
                    similarity = self._calculate_similarity(parts[0], valid_prop)
                    if similarity >= 0.4:  # Lower threshold for suggestions
                        suggestions_with_scores.append((valid_prop, similarity))
        else:
            # Multi-level property - check if parent exists
            parent = parts[0]
            if parent in self.valid_properties:
                # Parent exists, suggest valid fields under this parent
                for valid_prop in self.valid_properties.keys():
                    if valid_prop.startswith(f"{parent}."):
                        # Calculate similarity for the field part
                        field_part = valid_prop.split(".", 1)[1] if "." in valid_prop else ""
                        query_field = parts[1] if len(parts) > 1 else ""
                        similarity = self._calculate_similarity(query_field, field_part)
                        # Boost score since parent matches exactly
                        suggestions_with_scores.append((valid_prop, similarity + 0.3))
            else:
                # Parent doesn't exist, find similar complete paths
                for valid_prop in self.valid_properties.keys():
                    similarity = self._calculate_similarity(property_path, valid_prop)
                    if similarity >= 0.4:
                        suggestions_with_scores.append((valid_prop, similarity))
        
        # Sort by similarity score (descending)
        suggestions_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Prioritize searchable properties at the same similarity level
        searchable_suggestions = [
            (prop, score) for prop, score in suggestions_with_scores
            if prop in self.searchable_properties
        ]
        non_searchable_suggestions = [
            (prop, score) for prop, score in suggestions_with_scores
            if prop not in self.searchable_properties
        ]
        
        # Combine and return top suggestions
        all_suggestions = searchable_suggestions + non_searchable_suggestions
        return [prop for prop, _ in all_suggestions[:max_suggestions]]
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity score between two strings using sequence matching.
        
        Uses Python's difflib.SequenceMatcher for accurate similarity scoring.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        from difflib import SequenceMatcher
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def _is_similar(self, str1: str, str2: str, threshold: float = 0.6) -> bool:
        """
        Check if two strings are similar using similarity scoring.
        
        Args:
            str1: First string
            str2: Second string
            threshold: Minimum similarity score (0.0-1.0) to consider strings similar
            
        Returns:
            True if strings are similar enough
        """
        return self._calculate_similarity(str1, str2) >= threshold
    
    def validate_expression(self, expression: Dict[str, Any]) -> List[str]:
        """
        Validate a single expression from a search query.
        
        Args:
            expression: The expression dictionary to validate
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Check if this is a nested expression with sub-expressions
        if "expressions" in expression and expression.get("expressions"):
            # Recursively validate nested expressions
            for nested_expr in expression["expressions"]:
                errors.extend(self.validate_expression(nested_expr))
        
        # Validate property path if present
        if "property" in expression:
            property_path = expression["property"]
            is_valid, error_msg = self.validate_property_path(property_path)
            if not is_valid:
                errors.append(error_msg)
        
        return errors
    
    def validate_query(self, query: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Validate an entire search query.
        
        Args:
            query: The search query dictionary containing expressions
            
        Returns:
            Tuple of (is_valid, error_messages, invalid_properties)
        """
        errors = []
        invalid_properties = []
        
        if "expressions" not in query:
            return True, [], []
        
        for expression in query["expressions"]:
            expr_errors = self.validate_expression(expression)
            errors.extend(expr_errors)
            
            # Extract invalid property names from error messages
            for error in expr_errors:
                if "Invalid property path" in error:
                    # Extract property name from error message
                    start = error.find("'") + 1
                    end = error.find("'", start)
                    if start > 0 and end > start:
                        invalid_properties.append(error[start:end])
        
        is_valid = len(errors) == 0
        return is_valid, errors, invalid_properties
    
    def validate_query_complexity(
        self,
        query: Dict[str, Any],
        max_depth: int = 5,
        max_expressions: int = 50
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate query complexity to prevent performance issues.
        
        Checks:
        1. Maximum nesting depth (default: 5 levels)
        2. Maximum total expression count (default: 50 expressions)
        
        Args:
            query: The search query dictionary
            max_depth: Maximum allowed nesting depth
            max_expressions: Maximum total number of expressions
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        def count_depth(expr: Dict[str, Any], current_depth: int = 0) -> int:
            """Recursively count the maximum depth of nested expressions."""
            if "expressions" not in expr or not expr["expressions"]:
                return current_depth
            
            max_child_depth = current_depth
            for child in expr["expressions"]:
                child_depth = count_depth(child, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)
            
            return max_child_depth
        
        def count_expressions(expr: Dict[str, Any]) -> int:
            """Recursively count total number of expressions."""
            count = 1
            if "expressions" in expr and expr["expressions"]:
                for child in expr["expressions"]:
                    count += count_expressions(child)
            return count
        
        # Count depth starting from the query level
        depth = 0
        if "expressions" in query:
            for expr in query["expressions"]:
                expr_depth = count_depth(expr, 1)
                depth = max(depth, expr_depth)
        
        # Count total expressions
        expr_count = 0
        if "expressions" in query:
            for expr in query["expressions"]:
                expr_count += count_expressions(expr)
        
        # Validate depth
        if depth > max_depth:
            return False, (
                f"Query nesting too deep ({depth} levels). "
                f"Maximum allowed: {max_depth} levels. "
                f"Consider simplifying your query or breaking it into multiple searches."
            )
        
        # Validate expression count
        if expr_count > max_expressions:
            return False, (
                f"Too many expressions ({expr_count} total). "
                f"Maximum allowed: {max_expressions} expressions. "
                f"Consider simplifying your query or using broader search criteria."
            )
        
        return True, None
    
    def get_all_searchable_properties(self) -> List[Dict[str, Any]]:
        """
        Get a list of all searchable properties with their metadata.
        
        Returns:
            List of dictionaries containing property information
        """
        searchable = []
        for prop_path in sorted(self.searchable_properties):
            metadata = self.valid_properties[prop_path]
            searchable.append({
                "property_path": prop_path,
                "type": metadata.get("type"),
                "label": metadata.get("label"),
                "record_type": metadata.get("record_type")
            })
        return searchable


def validate_search_query(
    session_id: str,
    query: Dict[str, Any],
    search_type: str
) -> Tuple[bool, Optional[str], Optional[List[str]]]:
    """
    Validate a search query against the cached data model for the session.
    
    Performs multiple validation checks:
    1. Query complexity (depth and expression count)
    2. Property path validation against data model
    3. Searchability validation (indexed attributes)
    
    Args:
        session_id: The session ID to get the cached data model
        query: The search query to validate
        search_type: The type of search (record, entity, etc.)
        
    Returns:
        Tuple of (is_valid, error_message, suggestions)
        
    Raises:
        ValueError: If no data model is cached for the session
    """
    # Get cached data model
    data_model = get_cached_data_model(session_id)
    
    if not data_model:
        raise ValueError(
            f"No data model cached for session {session_id}. "
            "You must call get_data_model() before using search_master_data()."
        )
    
    # Create validator
    validator = DataModelValidator(data_model)
    
    # First, validate query complexity
    complexity_valid, complexity_error = validator.validate_query_complexity(query)
    if not complexity_valid:
        return False, complexity_error, None
    
    # Then validate the query against data model
    is_valid, errors, invalid_properties = validator.validate_query(query)
    
    if not is_valid:
        # Build comprehensive error message
        error_parts = [
            "❌ SEARCH QUERY VALIDATION FAILED",
            "",
            "The search query contains invalid property paths that do not exist in the data model.",
            "",
            "Errors found:"
        ]
        
        for i, error in enumerate(errors, 1):
            error_parts.append(f"  {i}. {error}")
        
        error_parts.extend([
            "",
            "⚠️ REQUIRED ACTION:",
            "1. Call get_data_model() with format='enhanced_compact' to retrieve the current data model",
            "2. Review the available searchable attributes in the data model",
            "3. Reconstruct your search query using ONLY valid property paths from the data model",
            "",
            "Example of valid property paths format:",
            "  - Single-level: 'attribute_name' (e.g., 'age', 'status')",
            "  - Nested: 'attribute_name.field_name' (e.g., 'legal_name.last_name', 'address.city')",
            "",
            "All property paths must:",
            "  ✓ Exist in the data model",
            "  ✓ Be marked as searchable (indexed=true)",
            ""
        ])
        
        # Add searchable properties hint
        searchable_props = validator.get_all_searchable_properties()
        if searchable_props:
            error_parts.append(f"Available searchable properties ({len(searchable_props)} total):")
            # Show first 10 as examples
            for prop in searchable_props[:10]:
                error_parts.append(f"  - {prop['property_path']} ({prop['label']})")
            if len(searchable_props) > 10:
                error_parts.append(f"  ... and {len(searchable_props) - 10} more")
        
        error_message = "\n".join(error_parts)
        
        # Extract suggestions from errors
        suggestions = []
        for error in errors:
            if "Did you mean:" in error:
                suggestion_part = error.split("Did you mean:")[1].strip().rstrip("?")
                suggestions.extend([s.strip() for s in suggestion_part.split(",")])
        
        return False, error_message, suggestions if suggestions else None
    
    return True, None, None



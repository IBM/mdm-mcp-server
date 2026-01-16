# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Pydantic models for search requests and responses.
"""

from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, model_validator


class Expression(BaseModel):
    """
    An expression used to describe what to search for.
    
    Supports nested expressions with AND/OR operations for complex queries.
    
    Examples:
        Simple expression:
            {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"}
        
        Expression with record type:
            {"property": "legal_name.last_name", "condition": "equal", "value": "Smith", "record_type": "person"}
        
        Nested expressions with OR:
            {
                "operation": "or",
                "expressions": [
                    {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"},
                    {"property": "legal_name.last_name", "condition": "equal", "value": "Jones"}
                ]
            }
        
        Complex nested query (last_name is Smith OR Jones) AND (city is Boston):
            {
                "operation": "and",
                "expressions": [
                    {
                        "operation": "or",
                        "expressions": [
                            {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"},
                            {"property": "legal_name.last_name", "condition": "equal", "value": "Jones"}
                        ]
                    },
                    {"property": "address.city", "condition": "equal", "value": "Boston"}
                ]
            }
    """
    property: Optional[str] = Field(
        None,
        description="The property path to search on (e.g., 'legal_name.last_name', 'address.city', 'age')"
    )
    condition: Optional[Literal[
        "equal", "not_equal", "greater_than", "greater_than_equal",
        "less_than", "less_than_equal", "starts_with", "ends_with",
        "contains", "not_contains", "fuzzy", "has_value", "has_no_value"
    ]] = Field(
        None,
        description="The condition to apply on the property or value"
    )
    value: Optional[Union[str, int, float, bool]] = Field(
        None,
        description="The value to search for"
    )
    record_type: Optional[str] = Field(
        None,
        description="The record type to search on (e.g., 'person', 'organization')"
    )
    entity_type: Optional[str] = Field(
        None,
        description="The entity type to search on"
    )
    operation: Optional[Literal["and", "or"]] = Field(
        None,
        description="The operation to use to join multiple expressions if additional expressions are defined"
    )
    expressions: Optional[List['Expression']] = Field(
        None,
        description="An optional list of additional expressions to apply (for nested queries)"
    )
    
    @model_validator(mode='after')
    def validate_expression_structure(self) -> 'Expression':
        """
        Validate that expression has valid structure.
        
        An expression must be either:
        1. A leaf expression: has property and condition (and optionally value)
        2. A nested expression: has operation and expressions list
        
        It cannot be both or neither.
        """
        has_property = self.property is not None
        has_operation = self.operation is not None
        has_expressions = self.expressions is not None and len(self.expressions) > 0
        
        # Check if this is a nested expression
        if has_operation and has_expressions:
            # Nested expression - should not have property/condition/value
            if has_property:
                raise ValueError(
                    "Nested expressions with 'operation' and 'expressions' "
                    "should not have 'property', 'condition', or 'value'. "
                    "Use nested expressions for grouping, leaf expressions for actual searches."
                )
            return self
        
        # Check if this is a leaf expression
        if has_property:
            # Leaf expression - must have condition
            if not self.condition:
                raise ValueError(
                    f"Leaf expression with property '{self.property}' must have a 'condition'. "
                    f"Valid conditions: equal, not_equal, greater_than, less_than, contains, etc."
                )
            
            # Check if condition requires a value
            if self.condition not in ["has_value", "has_no_value"] and self.value is None:
                raise ValueError(
                    f"Condition '{self.condition}' requires a 'value'. "
                    f"Only 'has_value' and 'has_no_value' conditions can omit the value."
                )
            
            return self
        
        # Neither leaf nor nested - invalid
        raise ValueError(
            "Expression must be either a leaf expression (with 'property' and 'condition') "
            "or a nested expression (with 'operation' and 'expressions'). "
            "Current expression has neither valid structure."
        )


# Enable forward references for recursive model
Expression.model_rebuild()


class SearchQuery(BaseModel):
    """
    A search query to run.
    
    Contains a list of expressions and an operation to combine them.
    The expressions list supports nested Expression objects for complex AND/OR logic.
    
    Examples:
        Simple query (single condition):
            {
                "expressions": [
                    {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"}
                ]
            }
        
        Multiple conditions with AND (default):
            {
                "expressions": [
                    {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"},
                    {"property": "address.city", "condition": "equal", "value": "Boston"}
                ],
                "operation": "and"
            }
        
        Multiple conditions with OR:
            {
                "expressions": [
                    {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"},
                    {"property": "legal_name.last_name", "condition": "equal", "value": "Jones"}
                ],
                "operation": "or"
            }
        
        Complex nested query:
            {
                "expressions": [
                    {
                        "operation": "or",
                        "expressions": [
                            {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"},
                            {"property": "legal_name.last_name", "condition": "equal", "value": "Jones"}
                        ]
                    },
                    {"property": "address.city", "condition": "equal", "value": "Boston"}
                ],
                "operation": "and"
            }
    """
    expressions: List[Expression] = Field(
        default_factory=list,
        description="The list of expressions to search with"
    )
    operation: Optional[Literal["and", "or"]] = Field(
        "and",
        description="The operation to apply to the expressions (default: 'and')"
    )


class SearchFilter(BaseModel):
    """
    A filter to apply to a search to narrow down results.
    
    Examples:
        Filter by record type:
            {"type": "record", "values": ["person", "organization"]}
        
        Filter by source:
            {"type": "source", "values": ["CRM", "ERP"]}
        
        Filter by data quality issues:
            {"type": "data_quality", "data_quality_issues": ["potential_match", "potential_duplicate"]}
    """
    type: Literal[
        "record", "entity", "source", "relationship", 
        "data_quality", "hierarchy_type", "hierarchy_number", "group"
    ] = Field(
        ...,
        description="The filter type"
    )
    values: Optional[List[str]] = Field(
        None,
        description="The values to filter upon (either values or data_quality_issues is required)"
    )
    data_quality_issues: Optional[List[Literal[
        "potential_match", "potential_overlay", "user_tasks_only", 
        "same_source_only", "potential_duplicate"
    ]]] = Field(
        None,
        description="The data quality issues to filter by (either data_quality_issues or values is required)"
    )


class SearchCriteria(BaseModel):
    """
    A set of criteria for a search operation.
    
    Examples:
        Simple record search:
            {
                "search_type": "record",
                "query": {
                    "expressions": [
                        {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"}
                    ]
                }
            }
        
        Entity search with filters:
            {
                "search_type": "entity",
                "query": {
                    "expressions": [
                        {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"}
                    ]
                },
                "filters": [
                    {"type": "entity", "values": ["person"]}
                ]
            }
        
        Complex search with nested conditions:
            {
                "search_type": "record",
                "query": {
                    "expressions": [
                        {
                            "operation": "or",
                            "expressions": [
                                {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"},
                                {"property": "legal_name.last_name", "condition": "equal", "value": "Jones"}
                            ]
                        },
                        {"property": "address.city", "condition": "equal", "value": "Boston"}
                    ],
                    "operation": "and"
                },
                "filters": [
                    {"type": "record", "values": ["person"]}
                ]
            }
    """
    search_type: Literal["record", "relationship", "entity", "hierarchy_node"] = Field(
        "record",
        description="The type of data to search against"
    )
    query: SearchQuery = Field(
        ...,
        description="The search query containing expressions"
    )
    filters: Optional[List[SearchFilter]] = Field(
        None,
        description="The search filters to apply to narrow down results"
    )


# Using Dict for attributes as they are Map<String, Object> in Java
# where Object can be another Map<String, Object> or List<Map<String, Object>>

class SearchResult(BaseModel):
    """
    A single search result item.
    """
    attributes: Dict[str, Any] = Field(..., description="Attributes of the search result as a dictionary")
    id: str = Field(..., description="ID of the result")
    type: str = Field(..., description="Type of the result (e.g., 'record', 'entity')")
    record_number: Optional[int] = Field(None, description="Record number")
    type_name: Optional[str] = Field(None, description="Type name (e.g., 'person', 'entity')")
    entity_id: Optional[str] = Field(None, description="Entity ID if available")


class PaginationLink(BaseModel):
    """
    A pagination link in the search response.
    """
    href: str = Field(..., description="URL for the pagination link")


class SearchResponse(BaseModel):
    """
    Response model for search results.
    """
    first: Optional[PaginationLink] = Field(None, description="Link to the first page of results")
    last: Optional[PaginationLink] = Field(None, description="Link to the last page of results")
    limit: int = Field(..., description="Maximum number of results per page")
    offset: int = Field(..., description="Number of results skipped")
    is_exact_count: bool = Field(..., description="Whether the total count is exact")
    results: List[SearchResult] = Field(default_factory=list, description="List of search results")
    total_count: int = Field(..., description="Total number of results")
    
    # Error fields
    error: Optional[str] = Field(None, description="Error message if an error occurred")
    status_code: Optional[int] = Field(None, description="HTTP status code if an error occurred")
    details: Optional[str] = Field(None, description="Additional error details")



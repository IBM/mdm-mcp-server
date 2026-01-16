# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Data model formatting utilities for the model microservice.

This module provides functions for transforming data models into various formats
suitable for different use cases, such as simplified entity-attribute formats,
enhanced formats with complex type definitions, and prompt-friendly representations.
"""

import json
from typing import Dict, Any, List, Optional

def transform_to_entity_attribute_format(data_model: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Transform the data model into a simplified entity-attribute format.
    
    This format focuses on entity types and their attributes, with each attribute having
    a name, type, description, and is_searchable flag.
    
    Args:
        data_model: The full data model from IBM MDM
        
    Returns:
        A list of entity types with their attributes in the simplified format
    """
    result = []
    
    # Process record types and their associated entity types
    if "record_types" in data_model:
        for record_type_name, record_type_info in data_model["record_types"].items():
            # Check if this record type has associated entity types
            if "entity_types" in record_type_info:
                for entity_type_name, entity_type_info in record_type_info["entity_types"].items():
                    entity_entry = {
                        "entity_type": entity_type_name,
                        "description": entity_type_info.get("description", f"Entity type for {record_type_name}"),
                        "attributes": []
                    }
                    
                    # Add record-level attributes (composite view attributes)
                    if "attributes" in record_type_info:
                        for attr_name, attr_info in record_type_info["attributes"].items():
                            # Get attribute type information
                            attr_type = attr_info.get("attribute_type", "string")
                            attr_type_info = data_model.get("attribute_types", {}).get(attr_type, {})
                            
                            # Determine if attribute is searchable (indexed)
                            is_searchable = attr_info.get("indexed", False)
                            
                            # Create attribute entry
                            attribute_entry = {
                                "name": attr_name,
                                "type": attr_type,
                                "description": attr_info.get("label", attr_name),
                                "is_searchable": is_searchable
                            }
                            
                            entity_entry["attributes"].append(attribute_entry)
                    
                    # Add the entity to the result if it has attributes
                    if entity_entry["attributes"]:
                        result.append(entity_entry)
    
    # If no entities were found, create a generic example
    if not result:
        result = [
            {
                "entity_type": "GenericEntity",
                "description": "A generic entity type created as an example.",
                "attributes": [
                    {
                        "name": "ID",
                        "type": "string",
                        "description": "The unique identifier for the entity.",
                        "is_searchable": True
                    },
                    {
                        "name": "Name",
                        "type": "string",
                        "description": "The name of the entity.",
                        "is_searchable": True
                    }
                ]
            }
        ]
    
    return result

def transform_to_enhanced_entity_attribute_format(data_model: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform the data model into an enhanced entity-attribute format.
    
    This format includes:
    1. Entity types with their attributes
    2. Complex attribute type definitions with their fields
    3. Relationship types
    
    Args:
        data_model: The full data model from IBM MDM
        
    Returns:
        A dictionary containing the enhanced entity-attribute format
    """
    result = {
        "entity_types": [],
        "attribute_type_definitions": {},
        "relationship_types": []
    }
    
    # Process attribute types to get their field definitions
    if "attribute_types" in data_model:
        for attr_type_name, attr_type_info in data_model["attribute_types"].items():
            # Skip simple attribute types without fields
            if "fields" not in attr_type_info:
                continue
                
            fields = []
            for field_name, field_info in attr_type_info["fields"].items():
                is_indexed = field_info.get("indexed", False)
                fields.append({
                    "name": field_name,
                    "description": field_info.get("label", field_name),
                    "is_searchable": is_indexed
                })
            
            # Add the attribute type definition
            result["attribute_type_definitions"][attr_type_name] = {
                "description": attr_type_info.get("description", ""),
                "label": attr_type_info.get("label", attr_type_name),
                "fields": fields,
                "matching_types": attr_type_info.get("matching_types", [])
            }
    
    # Process record types and their associated entity types
    if "record_types" in data_model:
        for record_type_name, record_type_info in data_model["record_types"].items():
            # Check if this record type has associated entity types
            if "entity_types" in record_type_info:
                for entity_type_name, entity_type_info in record_type_info["entity_types"].items():
                    entity_entry = {
                        "entity_type": entity_type_name,
                        "record_type": record_type_name,
                        "description": entity_type_info.get("description", f"Entity type for {record_type_name}"),
                        "attributes": []
                    }
                    
                    # Add record-level attributes
                    if "attributes" in record_type_info:
                        for attr_name, attr_info in record_type_info["attributes"].items():
                            # Get attribute type information
                            attr_type = attr_info.get("attribute_type", "string")
                            
                            # Determine if attribute is searchable (indexed)
                            is_searchable = attr_info.get("indexed", False)
                            
                            # Create attribute entry
                            attribute_entry = {
                                "name": attr_name,
                                "type": attr_type,
                                "description": attr_info.get("label", attr_name),
                                "is_searchable": is_searchable,
                                "cardinality": attr_info.get("cardinality", "SINGLE")
                            }
                            
                            # Add matching type if available
                            if "matching_type" in attr_info:
                                attribute_entry["matching_type"] = attr_info["matching_type"]
                            
                            entity_entry["attributes"].append(attribute_entry)
                    
                    # Add the entity to the result if it has attributes
                    if entity_entry["attributes"]:
                        result["entity_types"].append(entity_entry)
    
    # Process relationship types
    if "relationship_types" in data_model:
        for rel_type_name, rel_type_info in data_model["relationship_types"].items():
            relationship_entry = {
                "name": rel_type_name,
                "label": rel_type_info.get("label", rel_type_name),
                "description": rel_type_info.get("description", ""),
                "directional": rel_type_info.get("directional", False),
                "cardinality": rel_type_info.get("cardinality", "ONE2ONE"),
                "rules": []
            }
            
            # Add rules if available
            if "rules" in rel_type_info:
                for rule in rel_type_info["rules"]:
                    source = rule.get("source", {})
                    target = rule.get("target", {})
                    
                    rule_entry = {
                        "source_record_types": source.get("record_types", []),
                        "source_entity_types": source.get("entity_types", []),
                        "target_record_types": target.get("record_types", []),
                        "target_entity_types": target.get("entity_types", [])
                    }
                    
                    relationship_entry["rules"].append(rule_entry)
            
            # Add attributes if available
            if "attributes" in rel_type_info:
                relationship_entry["attributes"] = []
                for attr_name, attr_info in rel_type_info["attributes"].items():
                    attribute_entry = {
                        "name": attr_name,
                        "type": attr_info.get("attribute_type", "string"),
                        "description": attr_info.get("label", attr_name),
                        "is_searchable": attr_info.get("indexed", False),
                        "cardinality": attr_info.get("cardinality", "SINGLE")
                    }
                    relationship_entry["attributes"].append(attribute_entry)
            
            result["relationship_types"].append(relationship_entry)
    
    return result

def transform_to_enhanced_compact_format(data_model: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform the data model into an enhanced compact format that excludes relationship types.
    
    This format includes only:
    1. Entity types with their attributes
    2. Complex attribute type definitions with their fields
    
    Args:
        data_model: The full data model from IBM MDM
        
    Returns:
        A dictionary containing the enhanced compact format
    """
    # Create a copy of the result from the enhanced format
    result = transform_to_enhanced_entity_attribute_format(data_model)
    
    # Remove the relationship_types key
    if "relationship_types" in result:
        del result["relationship_types"]
    
    return result

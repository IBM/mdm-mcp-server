# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Matching algorithm formatting utilities.

This module provides functions for transforming matching algorithms into various formats
suitable for different use cases, such as compact formats for agent consumption.
"""

from typing import Dict, Any, List


def _flatten_compare_method(method: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten a compare method by removing nested wrapper structures.
    
    The API returns compare methods with nested structures like:
    - methods[0].compare_recipe[0] wrappers
    - inputs: [1] index pointers
    
    This function collapses these into a simpler structure.
    
    Args:
        method: The compare method from the API
        
    Returns:
        Flattened compare method dictionary
    """
    flattened = {}
    
    # Extract from methods[0] wrapper if present
    if "methods" in method and isinstance(method["methods"], list) and len(method["methods"]) > 0:
        inner_method = method["methods"][0]
        
        # Extract from compare_recipe[0] wrapper if present
        if "compare_recipe" in inner_method and isinstance(inner_method["compare_recipe"], list) and len(inner_method["compare_recipe"]) > 0:
            recipe = inner_method["compare_recipe"][0]
            
            # Copy relevant fields
            if "compare_function" in recipe:
                flattened["compare_function"] = recipe["compare_function"]
            if "label" in recipe:
                flattened["label"] = recipe["label"]
            if "inputs" in recipe:
                # Resolve input indices to actual attribute names if possible
                flattened["inputs"] = recipe["inputs"]
            if "weight" in recipe:
                flattened["weight"] = recipe["weight"]
        else:
            # No compare_recipe wrapper, copy directly
            for key in ["compare_function", "label", "inputs", "weight"]:
                if key in inner_method:
                    flattened[key] = inner_method[key]
    else:
        # No methods wrapper, copy directly
        for key in ["compare_function", "label", "inputs", "weight"]:
            if key in method:
                flattened[key] = method[key]
    
    return flattened if flattened else method


def transform_to_compact_algorithm(algorithm: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a matching algorithm into a compact format for agent consumption.
    
    The compact format:
    - Keeps only matching-decision essentials per entity type
    - Removes locale, encryption, standardizers, and bucket_generators (~80% of payload)
    - Retains clerical_review_threshold, auto_link_threshold, and compare_methods
    - Flattens compare_methods to remove nested wrapper structures
    - Keeps the full weights array (agreement/disagreement weight curve)
    
    Args:
        algorithm: The full algorithm from IBM MDM API
        
    Returns:
        Compact algorithm dictionary with only essential matching information
    """
    compact = {}
    
    # Process entity_types - this is the core matching configuration
    if "entity_types" in algorithm:
        compact["entity_types"] = {}
        
        for entity_type_name, entity_type_config in algorithm["entity_types"].items():
            compact_entity = {}
            
            # Keep thresholds - these are critical for match decisions
            if "clerical_review_threshold" in entity_type_config:
                compact_entity["clerical_review_threshold"] = entity_type_config["clerical_review_threshold"]
            
            if "auto_link_threshold" in entity_type_config:
                compact_entity["auto_link_threshold"] = entity_type_config["auto_link_threshold"]
            
            # Process compare_methods - it's a dictionary where keys are method names
            if "compare_methods" in entity_type_config:
                compact_entity["compare_methods"] = {}
                
                for method_name, method_config in entity_type_config["compare_methods"].items():
                    compact_method = {}
                    
                    # Keep label if present
                    if "label" in method_config:
                        compact_method["label"] = method_config["label"]
                    
                    # Keep weights array - needed for match explanation
                    if "weights" in method_config:
                        compact_method["weights"] = method_config["weights"]
                    
                    # Flatten methods array - extract compare_recipe from each method
                    if "methods" in method_config and isinstance(method_config["methods"], list):
                        compact_method["methods"] = []
                        
                        for method_item in method_config["methods"]:
                            flattened_item = {}
                            
                            # Keep inputs if present
                            if "inputs" in method_item:
                                flattened_item["inputs"] = method_item["inputs"]
                            
                            # Flatten compare_recipe array
                            if "compare_recipe" in method_item and isinstance(method_item["compare_recipe"], list):
                                flattened_item["compare_recipe"] = []
                                
                                for recipe in method_item["compare_recipe"]:
                                    # Keep essential recipe fields
                                    flattened_recipe = {}
                                    for key in ["fields", "method", "label", "comparison_resource", "inputs"]:
                                        if key in recipe:
                                            flattened_recipe[key] = recipe[key]
                                    
                                    if flattened_recipe:
                                        flattened_item["compare_recipe"].append(flattened_recipe)
                            
                            if flattened_item:
                                compact_method["methods"].append(flattened_item)
                    
                    compact_entity["compare_methods"][method_name] = compact_method
            
            compact["entity_types"][entity_type_name] = compact_entity
    
    return compact


# Format transformer strategy map
FORMAT_TRANSFORMERS = {
    "full": lambda a: a,  # Return algorithm unchanged
    "compact": transform_to_compact_algorithm
}


def apply_format_transformation(algorithm: Dict[str, Any], format_type: str) -> Dict[str, Any]:
    """
    Apply a format transformation to an algorithm.
    
    Args:
        algorithm: The algorithm to transform
        format_type: The format to transform to ("full" or "compact")
        
    Returns:
        Transformed algorithm
        
    Raises:
        ValueError: If format_type is not recognized
    """
    if format_type not in FORMAT_TRANSFORMERS:
        raise ValueError(
            f"Invalid format type: {format_type}. "
            f"Valid options are: {', '.join(FORMAT_TRANSFORMERS.keys())}"
        )
    
    transformer = FORMAT_TRANSFORMERS[format_type]
    return transformer(algorithm)

# Made with Bob

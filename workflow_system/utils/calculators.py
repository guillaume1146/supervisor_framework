"""
Shared calculation utilities
"""

from typing import Dict, Any


def calculate_data_quality_score(data: Dict[str, Any], core_fields: list = None) -> int:
    """Calculate data quality score out of 100"""
    total_fields = len(data)
    completed_fields = len([v for v in data.values() if v and v != "Not specified" and v != "None"])
    
    if core_fields:
        # Core fields have higher weight
        core_completed = sum(1 for field in core_fields if data.get(field))
        
        # Calculate weighted score (core fields = 70%, optional = 30%)
        core_score = (core_completed / len(core_fields)) * 70
        optional_score = (completed_fields / total_fields) * 30
        
        return round(core_score + optional_score)
    else:
        # Simple percentage if no core fields specified
        return round((completed_fields / total_fields) * 100)


def calculate_completion_percentage(data: Dict[str, Any]) -> float:
    """Calculate completion percentage"""
    total_fields = len(data)
    completed_fields = len([v for v in data.values() if v and v != "Not specified" and v != "None"])
    return round((completed_fields / total_fields) * 100, 1)
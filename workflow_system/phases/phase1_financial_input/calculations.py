"""
Calculations specific to Phase 1: Financial Input Validation
"""

from typing import Dict, Any
from workflow_system.utils.calculators import calculate_data_quality_score

def calculate_phase1_completion_score(processed_data: Dict[str, Any]) -> int:
    """Calculate completion score specific to Phase 1 requirements"""
    core_fields = [
        'valuation_date', 
        'current_fund_value', 
        'annual_contribution', 
        'product_type', 
        'provider_name'
    ]
    
    return calculate_data_quality_score(processed_data, core_fields)

def assess_data_readiness(processed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Assess if data is ready for next phase"""
    core_fields = [
        'valuation_date', 
        'current_fund_value', 
        'annual_contribution', 
        'product_type', 
        'provider_name'
    ]
    
    core_complete = all(processed_data.get(field) for field in core_fields)
    completion_score = calculate_phase1_completion_score(processed_data)
    
    return {
        "core_fields_complete": core_complete,
        "completion_score": completion_score,
        "ready_for_next_phase": core_complete,
        "missing_core_fields": [
            field for field in core_fields 
            if not processed_data.get(field)
        ]
    }
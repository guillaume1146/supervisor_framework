"""
Enhanced shared utilities for all workflows
File: workflow_system/utils/__init__.py (UPDATED)
"""

# Import all validation functions
from .validators import (
    validate_date_format,
    validate_currency_amount, 
    validate_age,
    validate_percentage,
    validate_product_type,
    validate_investment_term_type,
    validate_tax_band,
    validate_currency_range,
    validate_age_range,
    validate_term_years_range,
    validate_field_completeness,
    validate_date_range,
    validate_surrender_vs_fund_value,
    validate_multiple_fields
)

# Import all normalization functions
from .normalizers import (
    normalize_date,
    normalize_currency,
    normalize_product_type,
    normalize_provider_name,
    normalize_investment_term_type,
    normalize_tax_band,
    normalize_years,
    normalize_age,
    normalize_boolean_input,
    normalize_all_fields,
    normalize_field_names
)

# Import all calculation functions
from .calculators import (
    calculate_data_quality_score,
    calculate_completion_percentage,
    calculate_term_years_from_dates,
    calculate_term_years_from_years_months,
    calculate_term_years_from_ages,
    calculate_compound_growth,
    calculate_annuity_future_value,
    calculate_total_future_value,
    calculate_tax_impact,
    calculate_inflation_adjustment,
    calculate_retirement_income,
    calculate_cost_analysis,
    calculate_surrender_penalty,
    calculate_switching_analysis,
    calculate_risk_metrics,
    calculate_comprehensive_projection
)

# Import all formatting functions
from .formatters import (
    format_currency,
    format_percentage,
    format_date,
    format_enum_value,
    format_product_type,
    format_investment_term_type,
    format_tax_band,
    format_analysis_mode,
    format_boolean,
    format_integer,
    format_age,
    format_term_years,
    format_data_quality_score,
    format_completion_percentage,
    format_validation_status,
    format_list_items,
    format_field_for_display,
    format_all_fields,
    format_summary_table,
    format_for_user_display,
    format_for_report,
    format_for_api_response
)

# Import converter classes
from .converters import (
    DataTypeConverter,
    DisplayFormatter,
    Phase1DataConverter,
    ValidationHelper
)

__all__ = [
    # Validators
    "validate_date_format",
    "validate_currency_amount", 
    "validate_age",
    "validate_percentage",
    "validate_product_type",
    "validate_investment_term_type",
    "validate_tax_band",
    "validate_currency_range",
    "validate_age_range",
    "validate_term_years_range",
    "validate_field_completeness",
    "validate_date_range",
    "validate_surrender_vs_fund_value",
    "validate_multiple_fields",
    
    # Normalizers
    "normalize_date",
    "normalize_currency",
    "normalize_product_type",
    "normalize_provider_name",
    "normalize_investment_term_type",
    "normalize_tax_band",
    "normalize_years",
    "normalize_age",
    "normalize_boolean_input",
    "normalize_all_fields",
    "normalize_field_names",
    
    # Calculators
    "calculate_data_quality_score",
    "calculate_completion_percentage",
    "calculate_term_years_from_dates",
    "calculate_term_years_from_years_months",
    "calculate_term_years_from_ages",
    "calculate_compound_growth",
    "calculate_annuity_future_value",
    "calculate_total_future_value",
    "calculate_tax_impact",
    "calculate_inflation_adjustment",
    "calculate_retirement_income",
    "calculate_cost_analysis",
    "calculate_surrender_penalty",
    "calculate_switching_analysis",
    "calculate_risk_metrics",
    "calculate_comprehensive_projection",
    
    # Formatters
    "format_currency",
    "format_percentage",
    "format_date",
    "format_enum_value",
    "format_product_type",
    "format_investment_term_type",
    "format_tax_band",
    "format_analysis_mode",
    "format_boolean",
    "format_integer",
    "format_age",
    "format_term_years",
    "format_data_quality_score",
    "format_completion_percentage",
    "format_validation_status",
    "format_list_items",
    "format_field_for_display",
    "format_all_fields",
    "format_summary_table",
    "format_for_user_display",
    "format_for_report",
    "format_for_api_response",
    
    # Converter classes
    "DataTypeConverter",
    "DisplayFormatter", 
    "Phase1DataConverter",
    "ValidationHelper"
]

# Convenience functions for common operations
def validate_and_normalize_field(field_name: str, value: any, field_type: str = None) -> dict:
    """
    Convenience function to validate and normalize a single field
    
    Args:
        field_name: Name of the field
        value: Raw field value
        field_type: Optional type hint (currency, date, age, etc.)
        
    Returns:
        Dictionary with validation result, normalized value, and formatted value
    """
    result = {
        'field_name': field_name,
        'original_value': value,
        'is_valid': False,
        'normalized_value': None,
        'formatted_value': None,
        'errors': [],
        'warnings': []
    }
    
    try:
        # Auto-detect field type if not provided
        if not field_type:
            if 'date' in field_name.lower():
                field_type = 'date'
            elif any(keyword in field_name.lower() for keyword in ['value', 'amount', 'fund']):
                field_type = 'currency'
            elif 'age' in field_name.lower():
                field_type = 'age'
            elif field_name == 'product_type':
                field_type = 'product_type'
            elif field_name == 'tax_band':
                field_type = 'tax_band'
            else:
                field_type = 'string'
        
        # Validate based on type
        if field_type == 'date':
            result['is_valid'] = validate_date_format(value)
            result['normalized_value'] = normalize_date(value)
            result['formatted_value'] = format_date(result['normalized_value'])
            
        elif field_type == 'currency':
            validation_result = validate_currency_range(value)
            result['is_valid'] = validation_result['is_valid']
            result['errors'] = validation_result['errors']
            result['warnings'] = validation_result['warnings']
            result['normalized_value'] = normalize_currency(value)
            result['formatted_value'] = format_currency(result['normalized_value'])
            
        elif field_type == 'age':
            validation_result = validate_age_range(value)
            result['is_valid'] = validation_result['is_valid']
            result['errors'] = validation_result['errors']
            result['warnings'] = validation_result['warnings']
            result['normalized_value'] = normalize_age(value)
            result['formatted_value'] = format_age(result['normalized_value'])
            
        elif field_type == 'product_type':
            result['is_valid'] = validate_product_type(value)
            result['normalized_value'] = normalize_product_type(value)
            result['formatted_value'] = format_product_type(result['normalized_value'])
            
        elif field_type == 'tax_band':
            result['is_valid'] = validate_tax_band(value)
            result['normalized_value'] = normalize_tax_band(value)
            result['formatted_value'] = format_tax_band(result['normalized_value'])
            
        else:  # string or unknown type
            result['is_valid'] = value is not None and str(value).strip() != ''
            result['normalized_value'] = str(value).strip() if value else None
            result['formatted_value'] = result['normalized_value'] or "Not specified"
        
        if not result['is_valid'] and not result['errors']:
            result['errors'] = [f"Invalid {field_type} format"]
            
    except Exception as e:
        result['errors'] = [f"Validation error: {str(e)}"]
        result['is_valid'] = False
    
    return result


def process_all_fields(data: dict, field_types: dict = None) -> dict:
    """
    Process all fields in a data dictionary with validation, normalization, and formatting
    
    Args:
        data: Dictionary of field values
        field_types: Optional dictionary mapping field names to types
        
    Returns:
        Comprehensive processing result
    """
    field_types = field_types or {}
    
    result = {
        'is_valid': True,
        'processed_fields': {},
        'summary': {
            'total_fields': len(data),
            'valid_fields': 0,
            'invalid_fields': 0,
            'fields_with_warnings': 0
        },
        'normalized_data': {},
        'formatted_data': {},
        'all_errors': [],
        'all_warnings': []
    }
    
    for field_name, value in data.items():
        field_type = field_types.get(field_name)
        field_result = validate_and_normalize_field(field_name, value, field_type)
        
        result['processed_fields'][field_name] = field_result
        result['normalized_data'][field_name] = field_result['normalized_value']
        result['formatted_data'][field_name] = field_result['formatted_value']
        
        if field_result['is_valid']:
            result['summary']['valid_fields'] += 1
        else:
            result['summary']['invalid_fields'] += 1
            result['is_valid'] = False
        
        if field_result['errors']:
            result['all_errors'].extend(field_result['errors'])
        
        if field_result['warnings']:
            result['all_warnings'].extend(field_result['warnings'])
            result['summary']['fields_with_warnings'] += 1
    
    return result


# Version information
__version__ = "2.0.0"
__description__ = "Enhanced utilities for financial workflow processing with database integration"
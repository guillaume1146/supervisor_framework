"""
Enhanced data validation utilities shared across all workflows
File: workflow_system/utils/validators.py (UPDATED)
"""

import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Any, Optional, List, Dict

# Import Phase 1 specific validators for enhanced validation
from workflow_system.phases.phase1_financial_input.constants import (
    ProductType, InvestmentTermType, TaxBand, SystemLimits
)


def validate_date_format(date_str: Optional[str]) -> bool:
    """Validate if a date string is in acceptable format"""
    if not date_str:
        return False
    
    if date_str.lower() == 'today':
        return True
    
    date_patterns = [
        r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})',
        r'(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})',
        r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2})',
    ]
    
    return any(re.match(pattern, date_str) for pattern in date_patterns)


def validate_currency_amount(amount_str: Optional[str]) -> bool:
    """Validate if a string represents a valid currency amount"""
    if not amount_str:
        return False
    if amount_str.lower() in ['none', 'not applicable', 'n/a']:
        return True
    
    # Remove currency symbols and clean up
    cleaned = amount_str.replace('£', '').replace(',', '').replace(' ', '').strip()
    
    # Handle K and M notation
    if cleaned.lower().endswith('k') or cleaned.lower().endswith('m'):
        cleaned = cleaned[:-1]
    
    # Check if we can extract a valid number
    numbers = re.findall(r'\d+\.?\d*', cleaned)
    return len(numbers) > 0


def validate_age(age_str: Optional[str]) -> bool:
    """Validate if a string represents a valid age"""
    if not age_str:
        return False
    if age_str.lower() in ['not specified', 'none']:
        return True
    
    numbers = re.findall(r'\d+', age_str)
    if numbers:
        age = int(numbers[0])
        return 0 <= age <= 120  # CHANGED: More lenient range
    return False


def validate_percentage(percent_str: Optional[str]) -> bool:
    """Validate if a string represents a valid percentage"""
    if not percent_str:
        return False
    numbers = re.findall(r'\d+\.?\d*', percent_str.replace('%', ''))
    if numbers:
        value = float(numbers[0])
        return 0 <= value <= 100
    return False


def validate_product_type(product_str: Optional[str]) -> bool:
    """Enhanced validation for product type against enum values"""
    if not product_str:
        return False
    
    # Normalize input
    normalized = product_str.lower().strip().replace(' ', '_').replace('-', '_').replace('&', '_')
    
    # Check against ProductType enum values
    valid_types = [pt.value for pt in ProductType]
    if normalized in valid_types:
        return True
    
    # Check common aliases
    aliases = {
        'stocks_and_shares_isa': 'stocks_shares_isa',
        'personal_pension': 'pension',
        'workplace_pension': 'pension',
        'stakeholder_pension': 'pension',
        'self_invested_personal_pension': 'sipp',
        'open_ended_investment_company': 'oeic'
    }
    
    return aliases.get(normalized) in valid_types


def validate_investment_term_type(term_type_str: Optional[str]) -> bool:
    """Validate investment term type"""
    if not term_type_str:
        return False
    
    normalized = term_type_str.lower().strip()
    valid_types = [itt.value for itt in InvestmentTermType]
    return normalized in valid_types


def validate_tax_band(tax_band_str: Optional[str]) -> bool:
    """Validate tax band"""
    if not tax_band_str:
        return False
    
    # Handle percentage formats
    if '%' in str(tax_band_str):
        percentage = str(tax_band_str).replace('%', '').strip()
        if percentage in ['20', '40', '45']:
            return True
    
    # Handle enum values
    normalized = str(tax_band_str).lower().strip().replace(' ', '_')
    valid_bands = [tb.value for tb in TaxBand]
    return normalized in valid_bands


def validate_currency_range(amount_str: Optional[str]) -> Dict[str, Any]:
    """
    Enhanced currency validation with range checking
    Returns validation result with details
    """
    result = {
        'is_valid': False,
        'value': None,
        'errors': [],
        'warnings': []
    }
    
    if not amount_str:
        result['errors'].append("Amount is required")
        return result
    
    try:
        from workflow_system.utils.converters import DataTypeConverter
        converter = DataTypeConverter()
        decimal_value = converter.to_database_decimal(amount_str)
        
        if decimal_value is None:
            result['errors'].append("Invalid amount format")
            return result
        
        result['value'] = decimal_value
        
        # Range validation
        if decimal_value <= 0:
            result['errors'].append("Amount must be greater than £0")
        elif decimal_value > SystemLimits.MAX_FUND_VALUE:
            result['errors'].append(f"Amount cannot exceed £{SystemLimits.MAX_FUND_VALUE:,}")
        elif decimal_value < SystemLimits.MIN_FUND_VALUE:
            result['warnings'].append(f"Amount is below typical minimum of £{SystemLimits.MIN_FUND_VALUE:,}")
        
        # Set validity
        result['is_valid'] = len(result['errors']) == 0
        
    except Exception as e:
        result['errors'].append(f"Validation error: {str(e)}")
    
    return result


def validate_age_range(age_str: Optional[str]) -> Dict[str, Any]:
    """
    Enhanced age validation with range checking
    Returns validation result with details
    """
    result = {
        'is_valid': False,
        'value': None,
        'errors': [],
        'warnings': []
    }
    
    if not age_str:
        result['errors'].append("Age is required")
        return result
    
    try:
        from workflow_system.utils.converters import DataTypeConverter
        converter = DataTypeConverter()
        age_value = converter.to_database_integer(age_str)
        
        if age_value is None:
            result['errors'].append("Invalid age format")
            return result
        
        result['value'] = age_value
        
        # Range validation
        if age_value < SystemLimits.MIN_AGE:
            result['errors'].append(f"Age must be at least {SystemLimits.MIN_AGE}")
        elif age_value > SystemLimits.MAX_AGE:
            result['errors'].append(f"Age cannot exceed {SystemLimits.MAX_AGE}")
        elif age_value < 18:
            result['warnings'].append("Client is under 18 - special rules may apply")
        elif age_value >= SystemLimits.STATE_PENSION_AGE:
            result['warnings'].append("Client is at/past state pension age")
        
        result['is_valid'] = len(result['errors']) == 0
        
    except Exception as e:
        result['errors'].append(f"Age validation error: {str(e)}")
    
    return result


def validate_term_years_range(years_str: Optional[str]) -> Dict[str, Any]:
    """
    Validate investment term years with range checking
    Returns validation result with details
    """
    result = {
        'is_valid': False,
        'value': None,
        'errors': [],
        'warnings': []
    }
    
    if not years_str:
        result['errors'].append("Term years is required")
        return result
    
    try:
        from workflow_system.utils.converters import DataTypeConverter
        converter = DataTypeConverter()
        
        # Handle both integer and decimal inputs
        if '.' in str(years_str):
            years_value = converter.to_database_decimal(years_str)
        else:
            years_value = Decimal(converter.to_database_integer(years_str) or 0)
        
        if years_value is None or years_value == 0:
            result['errors'].append("Invalid term years format")
            return result
        
        result['value'] = years_value
        
        # Range validation
        if years_value < SystemLimits.MIN_TERM_YEARS:
            result['errors'].append(f"Term must be at least {SystemLimits.MIN_TERM_YEARS} years")
        elif years_value > SystemLimits.MAX_TERM_YEARS:
            result['errors'].append(f"Term cannot exceed {SystemLimits.MAX_TERM_YEARS} years")
        elif years_value > 40:
            result['warnings'].append("Very long investment term - please verify")
        elif years_value < 1:
            result['warnings'].append("Very short investment term")
        
        result['is_valid'] = len(result['errors']) == 0
        
    except Exception as e:
        result['errors'].append(f"Term validation error: {str(e)}")
    
    return result


def validate_field_completeness(fields: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """
    Validate completeness of required fields
    Returns validation summary
    """
    result = {
        'is_complete': False,
        'missing_fields': [],
        'present_fields': [],
        'completion_percentage': 0.0
    }
    
    for field in required_fields:
        value = fields.get(field)
        is_present = (
            value is not None and 
            str(value).strip().lower() not in ['', 'none', 'not specified', 'null']
        )
        
        if is_present:
            result['present_fields'].append(field)
        else:
            result['missing_fields'].append(field)
    
    # Calculate completion percentage
    if required_fields:
        result['completion_percentage'] = (len(result['present_fields']) / len(required_fields)) * 100
    
    result['is_complete'] = len(result['missing_fields']) == 0
    
    return result


def validate_date_range(start_date_str: Optional[str], end_date_str: Optional[str]) -> Dict[str, Any]:
    """
    Validate date range (start date must be before end date)
    Returns validation result
    """
    result = {
        'is_valid': False,
        'start_date': None,
        'end_date': None,
        'errors': [],
        'warnings': []
    }
    
    try:
        from workflow_system.utils.converters import DataTypeConverter
        converter = DataTypeConverter()
        
        if start_date_str:
            result['start_date'] = converter.to_database_date(start_date_str)
        
        if end_date_str:
            result['end_date'] = converter.to_database_date(end_date_str)
        
        # Validate range
        if result['start_date'] and result['end_date']:
            if result['end_date'] <= result['start_date']:
                result['errors'].append("End date must be after start date")
            else:
                # Check if range is reasonable
                days_diff = (result['end_date'] - result['start_date']).days
                if days_diff > (SystemLimits.MAX_TERM_YEARS * 365):
                    result['warnings'].append("Very long date range - please verify")
                elif days_diff < 90:  # Less than 3 months
                    result['warnings'].append("Very short date range")
        
        result['is_valid'] = len(result['errors']) == 0
        
    except Exception as e:
        result['errors'].append(f"Date range validation error: {str(e)}")
    
    return result


def validate_surrender_vs_fund_value(fund_value_str: Optional[str], 
                                    surrender_value_str: Optional[str]) -> Dict[str, Any]:
    """
    Validate surrender value against fund value
    Returns validation result with ratio analysis
    """
    result = {
        'is_valid': False,
        'fund_value': None,
        'surrender_value': None,
        'ratio': None,
        'errors': [],
        'warnings': []
    }
    
    try:
        from workflow_system.utils.converters import DataTypeConverter
        converter = DataTypeConverter()
        
        if fund_value_str:
            result['fund_value'] = converter.to_database_decimal(fund_value_str)
        
        if surrender_value_str:
            result['surrender_value'] = converter.to_database_decimal(surrender_value_str)
        
        # Validate relationship
        if result['fund_value'] and result['surrender_value']:
            result['ratio'] = result['surrender_value'] / result['fund_value']
            
            if result['ratio'] > Decimal('1.2'):
                result['warnings'].append("Surrender value is unusually high compared to fund value")
            elif result['ratio'] < Decimal('0.5'):
                result['warnings'].append("Surrender value is very low - high exit penalties may apply")
            elif result['ratio'] > Decimal('1.0'):
                result['warnings'].append("Surrender value exceeds fund value - please verify")
        
        result['is_valid'] = len(result['errors']) == 0
        
    except Exception as e:
        result['errors'].append(f"Value comparison error: {str(e)}")
    
    return result


# Batch validation function
def validate_multiple_fields(fields: Dict[str, Any], validation_rules: Dict[str, str]) -> Dict[str, Any]:
    """
    Validate multiple fields at once based on validation rules
    
    Args:
        fields: Dictionary of field values
        validation_rules: Dictionary mapping field names to validation types
                         e.g., {'fund_value': 'currency', 'current_age': 'age'}
    
    Returns:
        Comprehensive validation result
    """
    result = {
        'is_valid': True,
        'field_results': {},
        'total_errors': 0,
        'total_warnings': 0,
        'summary': ''
    }
    
    validators = {
        'currency': validate_currency_range,
        'age': validate_age_range,
        'term_years': validate_term_years_range,
        'date': lambda x: {'is_valid': validate_date_format(x), 'errors': [] if validate_date_format(x) else ['Invalid date format']},
        'product_type': lambda x: {'is_valid': validate_product_type(x), 'errors': [] if validate_product_type(x) else ['Invalid product type']},
        'tax_band': lambda x: {'is_valid': validate_tax_band(x), 'errors': [] if validate_tax_band(x) else ['Invalid tax band']}
    }
    
    for field_name, validation_type in validation_rules.items():
        field_value = fields.get(field_name)
        
        if validation_type in validators:
            field_result = validators[validation_type](field_value)
            result['field_results'][field_name] = field_result
            
            if not field_result.get('is_valid', False):
                result['is_valid'] = False
            
            result['total_errors'] += len(field_result.get('errors', []))
            result['total_warnings'] += len(field_result.get('warnings', []))
    
    # Create summary
    if result['is_valid']:
        if result['total_warnings'] > 0:
            result['summary'] = f"Validation passed with {result['total_warnings']} warning(s)"
        else:
            result['summary'] = "All validations passed"
    else:
        result['summary'] = f"Validation failed with {result['total_errors']} error(s)"
    
    return result
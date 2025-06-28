"""
Data validation utilities shared across all workflows
"""

import re
from datetime import datetime
from typing import Any, Optional

def validate_date_format(date_str: Optional[str]) -> bool:
    """Validate if a date string is in acceptable format"""
    if not date_str:
        return False
    
    if date_str.lower() == 'today':
        return True
    
    date_patterns = [
        r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})',
        r'(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})',
    ]
    
    return any(re.match(pattern, date_str) for pattern in date_patterns)


def validate_currency_amount(amount_str: Optional[str]) -> bool:
    """Validate if a string represents a valid currency amount"""
    if not amount_str:
        return False
    if amount_str.lower() in ['none', 'not applicable', 'n/a']:
        return True
    numbers = re.findall(r'[\d,]+', amount_str.replace('£', '').replace(',', ''))
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
        return 16 <= age <= 100
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
    """Validate if product type is recognized"""
    if not product_str:
        return False
    
    valid_types = [ 'pension', 'sipp', 'isa', 'stocks and shares isa', 'investment bond', 'unit trust', 'oeic', 'investment trust' , 'life insurance', 'endowment', 'whole of life', 'term assurance', 'critical illness cover', 'income protection', 'health insurance' ]
    
    return product_str.lower() in valid_types
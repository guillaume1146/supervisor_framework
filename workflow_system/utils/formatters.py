"""
Data formatting utilities
"""

import re
from typing import Any, Optional


def format_currency(amount: Any) -> str:
    """Format currency amount consistently"""
    if not amount:
        return "Not specified"
    
    if isinstance(amount, str):
        numbers = re.findall(r'[\d,]+', amount.replace('£', '').replace(',', ''))
        if numbers:
            try:
                amount = int(''.join(numbers))
            except ValueError:
                return amount
    
    if isinstance(amount, (int, float)):
        return f"£{amount:,}"
    
    return str(amount)


def format_percentage(value: Any) -> str:
    """Format percentage consistently"""
    if not value:
        return "Not specified"
    
    if isinstance(value, str):
        numbers = re.findall(r'\d+\.?\d*', value.replace('%', ''))
        if numbers:
            try:
                value = float(numbers[0])
            except ValueError:
                return value
    
    if isinstance(value, (int, float)):
        return f"{value}%"
    
    return str(value)


def format_date(date_str: Optional[str]) -> str:
    """Format date consistently"""
    if not date_str:
        return "Not specified"
    
    return date_str
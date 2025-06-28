"""
Data normalization utilities shared across all workflows
"""

import re
from datetime import datetime
from typing import Optional


def normalize_date(date_str: Optional[str]) -> Optional[str]:
    """Normalize date string to dd/mm/yyyy format"""
    if not date_str:
        return None
    
    if date_str.lower() == 'today':
        return datetime.now().strftime("%d/%m/%Y")
    
    date_patterns = [
        (r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})', r'\1/\2/\3'),  # dd/mm/yyyy
        (r'(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})', r'\3/\2/\1'),  # yyyy/mm/dd to dd/mm/yyyy
    ]
    
    for pattern, replacement in date_patterns:
        if re.match(pattern, date_str):
            return re.sub(pattern, replacement, date_str)
    
    return date_str


def normalize_currency(amount_str: Optional[str]) -> Optional[str]:
    """Normalize currency amounts to £X,XXX format"""
    if not amount_str or amount_str.lower() in ['none', 'not applicable', 'n/a']:
        return None
    
    numbers = re.findall(r'[\d,]+', amount_str.replace('£', '').replace(',', ''))
    if numbers:
        try:
            amount = int(''.join(numbers))
            if 'k' in amount_str.lower():
                amount *= 1000
            return f"£{amount:,}"
        except ValueError:
            pass
    return amount_str


def normalize_product_type(product_str: Optional[str]) -> Optional[str]:
    """Normalize product type names"""
    if not product_str:
        return None
    
    product_mappings = {
        'sipp': 'SIPP',
        'isa': 'ISA',
        'stocks and shares isa': 'Stocks & Shares ISA',
        'pension': 'Pension',
        'investment bond': 'Investment Bond',
        'unit trust': 'Unit Trust',
        'oeic': 'OEIC',
        'investment trust': 'Investment Trust'
    }
    
    product_lower = product_str.lower()
    return product_mappings.get(product_lower, product_str.title())

def normalize_provider_name(provider_str: Optional[str]) -> Optional[str]:
    """Normalize provider names"""
    if not provider_str:
        return None
    
    provider_mappings = {
        'standard life': 'Standard Life',
        'aviva': 'Aviva',
        'vanguard': 'Vanguard',
        'aj bell': 'AJ Bell',
        'hargreaves lansdown': 'Hargreaves Lansdown',
        'ii': 'Interactive Investor',
        'interactive investor': 'Interactive Investor',
        'fidelity': 'Fidelity',
        'aegon': 'Aegon',
        'prudential': 'Prudential'
    }
    
    provider_lower = provider_str.lower()
    return provider_mappings.get(provider_lower, provider_str.title())


def normalize_years(years_str: Optional[str]) -> Optional[str]:
    """Normalize year specifications"""
    if not years_str or years_str.lower() in ['not specified', 'none']:
        return "Not specified"
    
    numbers = re.findall(r'\d+', years_str)
    if numbers:
        return f"{numbers[0]} years"
    
    if 'retirement' in years_str.lower():
        return "Until retirement"
    
    return years_str


def normalize_age(age_str: Optional[str]) -> Optional[str]:
    """Normalize age specifications"""
    if not age_str or age_str.lower() in ['not specified', 'none']:
        return "Not specified"
    
    numbers = re.findall(r'\d+', age_str)
    if numbers:
        return f"{numbers[0]} years old"
    return age_str
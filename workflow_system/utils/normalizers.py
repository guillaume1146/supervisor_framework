"""
Enhanced data normalization utilities shared across all workflows
File: workflow_system/utils/normalizers.py (UPDATED)
"""

import re
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, Any

from workflow_system.phases.phase1_financial_input.constants import (
    ProductType, InvestmentTermType, TaxBand
)


def normalize_date(date_str: Optional[str]) -> Optional[str]:
    """Enhanced date normalization with better format handling"""
    if not date_str:
        return None
    
    date_str = str(date_str).strip()
    
    if date_str.lower() == 'today':
        return datetime.now().strftime("%d/%m/%Y")
    
    # Handle various date formats
    date_patterns = [
        # dd/mm/yyyy or dd-mm-yyyy
        (r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})', r'\1/\2/\3'),
        # yyyy/mm/dd or yyyy-mm-dd to dd/mm/yyyy
        (r'(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})', r'\3/\2/\1'),
        # dd/mm/yy to dd/mm/20yy
        (r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2})$', lambda m: f"{m.group(1)}/{m.group(2)}/20{m.group(3)}"),
    ]
    
    for pattern, replacement in date_patterns:
        if callable(replacement):
            match = re.match(pattern, date_str)
            if match:
                return replacement(match)
        else:
            if re.match(pattern, date_str):
                return re.sub(pattern, replacement, date_str)
    
    # Handle text dates like "March 2024", "Mar 2024"
    month_patterns = [
        (r'(january|jan)\s+(\d{4})', r'01/01/\2'),
        (r'(february|feb)\s+(\d{4})', r'01/02/\2'),
        (r'(march|mar)\s+(\d{4})', r'01/03/\2'),
        (r'(april|apr)\s+(\d{4})', r'01/04/\2'),
        (r'(may)\s+(\d{4})', r'01/05/\2'),
        (r'(june|jun)\s+(\d{4})', r'01/06/\2'),
        (r'(july|jul)\s+(\d{4})', r'01/07/\2'),
        (r'(august|aug)\s+(\d{4})', r'01/08/\2'),
        (r'(september|sep)\s+(\d{4})', r'01/09/\2'),
        (r'(october|oct)\s+(\d{4})', r'01/10/\2'),
        (r'(november|nov)\s+(\d{4})', r'01/11/\2'),
        (r'(december|dec)\s+(\d{4})', r'01/12/\2'),
    ]
    
    date_lower = date_str.lower()
    for pattern, replacement in month_patterns:
        if re.search(pattern, date_lower):
            return re.sub(pattern, replacement, date_lower)
    
    return date_str


def normalize_currency(amount_str: Optional[str]) -> Optional[str]:
    """Enhanced currency normalization with better format handling"""
    if not amount_str or str(amount_str).lower() in ['none', 'not applicable', 'n/a', 'null', '']:
        return None
    
    amount_str = str(amount_str).strip()
    
    # Remove currency symbols and clean up
    cleaned = amount_str.replace('£', '').replace('$', '').replace(',', '').replace(' ', '')
    
    # Handle written numbers
    number_words = {
        'thousand': '000',
        'k': '000',
        'million': '000000',
        'm': '000000',
        'billion': '000000000',
        'b': '000000000'
    }
    
    # Extract base number and multiplier
    for word, zeros in number_words.items():
        if word in cleaned.lower():
            base_number = re.findall(r'\d+\.?\d*', cleaned.lower().replace(word, ''))
            if base_number:
                try:
                    value = float(base_number[0]) * (10 ** len(zeros))
                    return f"£{int(value):,}"
                except (ValueError, IndexError):
                    continue
    
    # Handle regular numbers
    numbers = re.findall(r'\d+\.?\d*', cleaned)
    if numbers:
        try:
            amount = float(numbers[0])
            
            # Handle K/M suffixes in original string
            if 'k' in amount_str.lower() or 'thousand' in amount_str.lower():
                amount *= 1000
            elif 'm' in amount_str.lower() or 'million' in amount_str.lower():
                amount *= 1000000
            
            return f"£{int(amount):,}"
        except ValueError:
            pass
    
    return amount_str


def normalize_product_type(product_str: Optional[str]) -> Optional[str]:
    """Enhanced product type normalization using enum mapping"""
    if not product_str:
        return None
    
    # Normalize input
    normalized = product_str.lower().strip().replace(' ', '_').replace('-', '_').replace('&', '_')
    
    # Direct enum mapping
    for product_type in ProductType:
        if product_type.value == normalized:
            return product_type.value
    
    # Common aliases mapping
    aliases = {
        'stocks_and_shares_isa': ProductType.STOCKS_SHARES_ISA.value,
        'stocks_shares_isa': ProductType.STOCKS_SHARES_ISA.value,
        'personal_pension': ProductType.PENSION.value,
        'workplace_pension': ProductType.PENSION.value,
        'stakeholder_pension': ProductType.PENSION.value,
        'self_invested_personal_pension': ProductType.SIPP.value,
        'self_invested_pension': ProductType.SIPP.value,
        'open_ended_investment_company': ProductType.OEIC.value,
        'life_insurance': ProductType.LIFE_INSURANCE.value,
        'life_cover': ProductType.LIFE_INSURANCE.value,
        'term_life': ProductType.TERM_ASSURANCE.value,
        'term_insurance': ProductType.TERM_ASSURANCE.value,
        'critical_illness': ProductType.CRITICAL_ILLNESS_COVER.value,
        'ci_cover': ProductType.CRITICAL_ILLNESS_COVER.value,
        'income_protection_insurance': ProductType.INCOME_PROTECTION.value,
        'ip_insurance': ProductType.INCOME_PROTECTION.value,
        'health_insurance': ProductType.HEALTH_INSURANCE.value,
        'private_medical': ProductType.HEALTH_INSURANCE.value
    }
    
    return aliases.get(normalized, product_str.title())


def normalize_provider_name(provider_str: Optional[str]) -> Optional[str]:
    """Enhanced provider name normalization with comprehensive mapping"""
    if not provider_str:
        return None
    
    provider_lower = provider_str.lower().strip()
    
    # Comprehensive provider mappings
    provider_mappings = {
        # Major insurers
        'aviva': 'Aviva',
        'legal & general': 'Legal & General',
        'legal and general': 'Legal & General',
        'l&g': 'Legal & General',
        'standard life': 'Standard Life',
        'standard life aberdeen': 'Standard Life Aberdeen',
        'abrdn': 'abrdn',
        'prudential': 'Prudential',
        'aegon': 'Aegon',
        'scottish widows': 'Scottish Widows',
        'royal london': 'Royal London',
        'zurich': 'Zurich',
        
        # Investment platforms
        'hargreaves lansdown': 'Hargreaves Lansdown',
        'hl': 'Hargreaves Lansdown',
        'aj bell': 'AJ Bell',
        'ajbell': 'AJ Bell',
        'interactive investor': 'Interactive Investor',
        'ii': 'Interactive Investor',
        'charles stanley': 'Charles Stanley',
        'vanguard': 'Vanguard',
        'fidelity': 'Fidelity',
        'blackrock': 'BlackRock',
        'ishares': 'iShares',
        
        # Banks and building societies
        'lloyds': 'Lloyds Bank',
        'lloyds bank': 'Lloyds Bank',
        'halifax': 'Halifax',
        'bank of scotland': 'Bank of Scotland',
        'santander': 'Santander',
        'barclays': 'Barclays',
        'hsbc': 'HSBC',
        'natwest': 'NatWest',
        'rbs': 'Royal Bank of Scotland',
        'nationwide': 'Nationwide Building Society',
        
        # Specialist providers
        'pensionbee': 'PensionBee',
        'nutmeg': 'Nutmeg',
        'moneybox': 'Moneybox',
        'freetrade': 'Freetrade',
        'trading212': 'Trading 212',
        'etoro': 'eToro',
        
        # Older/legacy providers
        'friends provident': 'Friends Provident',
        'friends life': 'Friends Life',
        'phoenix': 'Phoenix Group',
        'reassure': 'ReAssure',
        'clerical medical': 'Clerical Medical',
        'scottish equitable': 'Scottish Equitable',
        'cornhill': 'Cornhill',
        'pearl': 'Pearl'
    }
    
    # Try exact match first
    if provider_lower in provider_mappings:
        return provider_mappings[provider_lower]
    
    # Try partial matches
    for key, value in provider_mappings.items():
        if key in provider_lower or provider_lower in key:
            return value
    
    # Default to title case
    return provider_str.title()


def normalize_investment_term_type(term_str: Optional[str]) -> Optional[str]:
    """Normalize investment term type using enum values"""
    if not term_str:
        return None
    
    term_lower = term_str.lower().strip()
    
    # Direct enum matching
    for term_type in InvestmentTermType:
        if term_type.value == term_lower:
            return term_type.value
    
    # Alias matching
    aliases = {
        'until_date': InvestmentTermType.UNTIL.value,
        'to_date': InvestmentTermType.UNTIL.value,
        'end_date': InvestmentTermType.UNTIL.value,
        'for_years': InvestmentTermType.YEARS.value,
        'number_of_years': InvestmentTermType.YEARS.value,
        'years_term': InvestmentTermType.YEARS.value,
        'until_age': InvestmentTermType.AGE.value,
        'to_age': InvestmentTermType.AGE.value,
        'target_age': InvestmentTermType.AGE.value
    }
    
    return aliases.get(term_lower, term_str)


def normalize_tax_band(tax_str: Optional[str]) -> Optional[str]:
    """Normalize tax band using enum values"""
    if not tax_str:
        return None
    
    tax_str = str(tax_str).strip()
    
    # Handle percentage formats
    if '%' in tax_str:
        percentage = tax_str.replace('%', '').strip()
        if percentage == '20':
            return TaxBand.BASIC_RATE.value
        elif percentage == '40':
            return TaxBand.HIGHER_RATE.value
        elif percentage == '45':
            return TaxBand.ADDITIONAL_RATE.value
    
    # Handle decimal formats
    try:
        decimal_value = float(tax_str)
        if decimal_value == 0.2 or decimal_value == 20:
            return TaxBand.BASIC_RATE.value
        elif decimal_value == 0.4 or decimal_value == 40:
            return TaxBand.HIGHER_RATE.value
        elif decimal_value == 0.45 or decimal_value == 45:
            return TaxBand.ADDITIONAL_RATE.value
    except ValueError:
        pass
    
    # Normalize to enum format
    normalized = tax_str.lower().replace(' ', '_').replace('%', '')
    
    # Direct enum matching
    for tax_band in TaxBand:
        if tax_band.value == normalized:
            return tax_band.value
    
    # Alias matching
    aliases = {
        'basic': TaxBand.BASIC_RATE.value,
        'basic_rate': TaxBand.BASIC_RATE.value,
        'standard': TaxBand.BASIC_RATE.value,
        'standard_rate': TaxBand.BASIC_RATE.value,
        'higher': TaxBand.HIGHER_RATE.value,
        'higher_rate': TaxBand.HIGHER_RATE.value,
        'additional': TaxBand.ADDITIONAL_RATE.value,
        'additional_rate': TaxBand.ADDITIONAL_RATE.value,
        'top': TaxBand.ADDITIONAL_RATE.value,
        'top_rate': TaxBand.ADDITIONAL_RATE.value
    }
    
    return aliases.get(normalized, tax_str)


def normalize_years(years_str: Optional[str]) -> Optional[str]:
    """Enhanced years normalization with text-to-number conversion"""
    if not years_str or str(years_str).lower() in ['not specified', 'none', 'null', '']:
        return "Not specified"
    
    years_str = str(years_str).strip()
    
    # Handle retirement keyword
    if 'retirement' in years_str.lower():
        return "Until retirement"
    
    # Handle text numbers
    text_numbers = {
        'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
        'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
        'eleven': '11', 'twelve': '12', 'thirteen': '13', 'fourteen': '14', 'fifteen': '15',
        'sixteen': '16', 'seventeen': '17', 'eighteen': '18', 'nineteen': '19', 'twenty': '20',
        'twenty-five': '25', 'thirty': '30', 'thirty-five': '35', 'forty': '40', 'forty-five': '45', 'fifty': '50'
    }
    
    years_lower = years_str.lower()
    for text, number in text_numbers.items():
        if text in years_lower:
            return f"{number} years"
    
    # Extract numbers
    numbers = re.findall(r'\d+', years_str)
    if numbers:
        return f"{numbers[0]} years"
    
    return years_str


def normalize_age(age_str: Optional[str]) -> Optional[str]:
    """Enhanced age normalization with text-to-number conversion"""
    if not age_str or str(age_str).lower() in ['not specified', 'none', 'null', '']:
        return "Not specified"
    
    age_str = str(age_str).strip()
    
    # Handle text numbers (similar to years but more comprehensive)
    text_numbers = {
        'sixteen': '16', 'seventeen': '17', 'eighteen': '18', 'nineteen': '19',
        'twenty': '20', 'twenty-one': '21', 'twenty-five': '25',
        'thirty': '30', 'thirty-five': '35', 'forty': '40', 'forty-five': '45',
        'fifty': '50', 'fifty-five': '55', 'sixty': '60', 'sixty-five': '65',
        'seventy': '70', 'seventy-five': '75', 'eighty': '80'
    }
    
    age_lower = age_str.lower()
    for text, number in text_numbers.items():
        if text in age_lower:
            return f"{number} years old"
    
    # Extract numbers
    numbers = re.findall(r'\d+', age_str)
    if numbers:
        return f"{numbers[0]} years old"
    
    return age_str


def normalize_boolean_input(input_str: Optional[str]) -> Optional[bool]:
    """Normalize various boolean input formats"""
    if not input_str:
        return None
    
    input_lower = str(input_str).lower().strip()
    
    true_values = ['true', 'yes', 'y', '1', 'on', 'include', 'enable', 'enabled', 'active']
    false_values = ['false', 'no', 'n', '0', 'off', 'exclude', 'disable', 'disabled', 'inactive']
    
    if input_lower in true_values:
        return True
    elif input_lower in false_values:
        return False
    
    return None


def normalize_all_fields(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize all fields in a data dictionary
    Returns normalized dictionary
    """
    normalized = {}
    
    for field_name, raw_value in raw_data.items():
        if raw_value is None:
            normalized[field_name] = None
            continue
        
        # Date fields
        if field_name in ['valuation_date', 'end_date']:
            normalized[field_name] = normalize_date(raw_value)
        
        # Currency fields
        elif field_name in ['fund_value', 'surrender_value', 'initial_investment_value']:
            normalized[field_name] = normalize_currency(raw_value)
        
        # Product type
        elif field_name == 'product_type':
            normalized[field_name] = normalize_product_type(raw_value)
        
        # Provider name
        elif field_name == 'provider_name':
            normalized[field_name] = normalize_provider_name(raw_value)
        
        # Investment term type
        elif field_name == 'investment_term_type':
            normalized[field_name] = normalize_investment_term_type(raw_value)
        
        # Tax band
        elif field_name == 'tax_band':
            normalized[field_name] = normalize_tax_band(raw_value)
        
        # Years
        elif field_name in ['user_input_years', 'term_years']:
            normalized[field_name] = normalize_years(raw_value)
        
        # Age
        elif field_name in ['current_age', 'target_age']:
            normalized[field_name] = normalize_age(raw_value)
        
        # Boolean fields
        elif field_name in ['include_taxation', 'performing_switch_analysis']:
            bool_result = normalize_boolean_input(raw_value)
            normalized[field_name] = bool_result if bool_result is not None else raw_value
        
        # Default: keep as string, but clean up
        else:
            normalized[field_name] = str(raw_value).strip() if raw_value else None
    
    return normalized


def normalize_field_names(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize field names to standard format (snake_case)
    """
    normalized = {}
    
    for field_name, value in data.items():
        # Convert to snake_case
        snake_case_name = re.sub(r'[^\w\s]', '', field_name)  # Remove special chars
        snake_case_name = re.sub(r'\s+', '_', snake_case_name)  # Replace spaces with underscores
        snake_case_name = snake_case_name.lower()  # Convert to lowercase
        
        normalized[snake_case_name] = value
    
    return normalized
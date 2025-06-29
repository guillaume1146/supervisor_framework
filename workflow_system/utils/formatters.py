"""
Enhanced data formatting utilities for display purposes
File: workflow_system/utils/formatters.py (UPDATED)
"""

import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional, Dict, List

from workflow_system.phases.phase1_financial_input.constants import (
    ProductType, InvestmentTermType, TaxBand, AnalysisMode
)


def format_currency(amount: Any) -> str:
    """Enhanced currency formatting with better handling of different input types"""
    if not amount:
        return "Not specified"
    
    try:
        # Convert to Decimal for consistent handling
        if isinstance(amount, str):
            # Remove existing formatting
            cleaned = amount.replace('£', '').replace(',', '').replace(' ', '')
            if 'k' in cleaned.lower():
                cleaned = cleaned.lower().replace('k', '')
                decimal_amount = Decimal(cleaned) * 1000
            elif 'm' in cleaned.lower():
                cleaned = cleaned.lower().replace('m', '')
                decimal_amount = Decimal(cleaned) * 1000000
            else:
                decimal_amount = Decimal(cleaned)
        elif isinstance(amount, (int, float)):
            decimal_amount = Decimal(str(amount))
        elif isinstance(amount, Decimal):
            decimal_amount = amount
        else:
            return str(amount)
        
        # Format based on magnitude
        if decimal_amount >= 1000000:
            return f"£{decimal_amount/1000000:.1f}M"
        elif decimal_amount >= 1000:
            return f"£{decimal_amount/1000:.0f}K"
        else:
            return f"£{decimal_amount:,.2f}"
            
    except (ValueError, TypeError, ArithmeticError):
        return str(amount) if amount else "Not specified"


def format_percentage(value: Any, decimal_places: int = 2) -> str:
    """Enhanced percentage formatting with configurable decimal places"""
    if not value:
        return "Not specified"
    
    try:
        if isinstance(value, str):
            # Remove existing % and convert
            cleaned = value.replace('%', '').strip()
            decimal_value = Decimal(cleaned)
            # If the input was already a percentage (e.g., "20%"), don't multiply by 100
            if '%' in value:
                return f"{decimal_value:.{decimal_places}f}%"
            else:
                return f"{decimal_value * 100:.{decimal_places}f}%"
        elif isinstance(value, (int, float, Decimal)):
            decimal_value = Decimal(str(value))
            # Assume input is a decimal (0.2 = 20%)
            return f"{decimal_value * 100:.{decimal_places}f}%"
        else:
            return str(value)
            
    except (ValueError, TypeError, ArithmeticError):
        return str(value) if value else "Not specified"


def format_date(date_value: Optional[Any], format_string: str = "%d/%m/%Y") -> str:
    """Enhanced date formatting with multiple input type support"""
    if not date_value:
        return "Not specified"
    
    try:
        if isinstance(date_value, date):
            return date_value.strftime(format_string)
        elif isinstance(date_value, datetime):
            return date_value.strftime(format_string)
        elif isinstance(date_value, str):
            # Try to parse the string
            date_patterns = [
                "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d",
                "%d/%m/%y", "%d-%m-%y"
            ]
            
            for pattern in date_patterns:
                try:
                    parsed_date = datetime.strptime(date_value, pattern)
                    return parsed_date.strftime(format_string)
                except ValueError:
                    continue
            
            # If no pattern matches, return as-is
            return date_value
        else:
            return str(date_value)
            
    except (ValueError, TypeError):
        return str(date_value) if date_value else "Not specified"


def format_enum_value(value: Optional[str], enum_class, friendly_format: bool = True) -> str:
    """Format enum values for display with optional friendly formatting"""
    if not value:
        return "Not specified"
    
    try:
        # Find the enum item
        enum_item = None
        for item in enum_class:
            if item.value == value:
                enum_item = item
                break
        
        if enum_item:
            if friendly_format:
                # Convert to friendly format: "basic_rate_20" -> "Basic Rate 20%"
                friendly_name = enum_item.name.replace('_', ' ').title()
                
                # Special handling for tax bands
                if enum_class == TaxBand:
                    if "20" in friendly_name:
                        return "Basic Rate (20%)"
                    elif "40" in friendly_name:
                        return "Higher Rate (40%)"
                    elif "45" in friendly_name:
                        return "Additional Rate (45%)"
                
                return friendly_name
            else:
                return enum_item.value
        else:
            # If not found in enum, format the raw value
            return value.replace('_', ' ').title()
            
    except Exception:
        return str(value) if value else "Not specified"


def format_product_type(product_type: Optional[str]) -> str:
    """Specialized formatting for product types"""
    return format_enum_value(product_type, ProductType, friendly_format=True)


def format_investment_term_type(term_type: Optional[str]) -> str:
    """Specialized formatting for investment term types"""
    return format_enum_value(term_type, InvestmentTermType, friendly_format=True)


def format_tax_band(tax_band: Optional[str]) -> str:
    """Specialized formatting for tax bands"""
    return format_enum_value(tax_band, TaxBand, friendly_format=True)


def format_analysis_mode(analysis_mode: Optional[str]) -> str:
    """Specialized formatting for analysis modes"""
    return format_enum_value(analysis_mode, AnalysisMode, friendly_format=True)


def format_boolean(value: Optional[Any], true_text: str = "Yes", false_text: str = "No") -> str:
    """Enhanced boolean formatting with customizable text"""
    if value is None:
        return "Not specified"
    
    if isinstance(value, bool):
        return true_text if value else false_text
    elif isinstance(value, str):
        value_lower = value.lower().strip()
        if value_lower in ['true', 'yes', 'y', '1', 'on', 'include', 'enable']:
            return true_text
        elif value_lower in ['false', 'no', 'n', '0', 'off', 'exclude', 'disable']:
            return false_text
        else:
            return value
    else:
        return str(value)


def format_integer(value: Optional[Any], suffix: str = "") -> str:
    """Enhanced integer formatting with optional suffix"""
    if value is None:
        return "Not specified"
    
    try:
        if isinstance(value, str):
            # Extract number from string
            numbers = re.findall(r'\d+', value)
            if numbers:
                int_value = int(numbers[0])
                return f"{int_value}{suffix}"
            else:
                return value
        elif isinstance(value, (int, float, Decimal)):
            int_value = int(value)
            return f"{int_value}{suffix}"
        else:
            return str(value)
            
    except (ValueError, TypeError):
        return str(value) if value else "Not specified"


def format_age(age_value: Optional[Any]) -> str:
    """Specialized formatting for age values"""
    if not age_value:
        return "Not specified"
    
    try:
        if isinstance(age_value, str):
            # Extract number from string like "45 years old"
            numbers = re.findall(r'\d+', age_value)
            if numbers:
                age = int(numbers[0])
                return f"{age} years old"
            else:
                return age_value
        elif isinstance(age_value, (int, float)):
            age = int(age_value)
            return f"{age} years old"
        else:
            return str(age_value)
            
    except (ValueError, TypeError):
        return str(age_value) if age_value else "Not specified"


def format_term_years(term_value: Optional[Any]) -> str:
    """Specialized formatting for term years"""
    if not term_value:
        return "Not specified"
    
    try:
        if isinstance(term_value, str):
            if "retirement" in term_value.lower():
                return "Until retirement"
            # Extract number
            numbers = re.findall(r'\d+\.?\d*', term_value)
            if numbers:
                years = float(numbers[0])
                if years == int(years):
                    return f"{int(years)} years"
                else:
                    return f"{years:.1f} years"
            else:
                return term_value
        elif isinstance(term_value, (int, float, Decimal)):
            years = float(term_value)
            if years == int(years):
                return f"{int(years)} years"
            else:
                return f"{years:.1f} years"
        else:
            return str(term_value)
            
    except (ValueError, TypeError):
        return str(term_value) if term_value else "Not specified"


def format_data_quality_score(score: Optional[Any]) -> str:
    """Format data quality score with visual indicators"""
    if score is None:
        return "Not calculated"
    
    try:
        score_int = int(score)
        
        if score_int >= 90:
            return f"{score_int}/100 ✅ Excellent"
        elif score_int >= 80:
            return f"{score_int}/100 ✅ Very Good"
        elif score_int >= 70:
            return f"{score_int}/100 ⚠️ Good"
        elif score_int >= 60:
            return f"{score_int}/100 ⚠️ Fair"
        else:
            return f"{score_int}/100 ❌ Poor"
            
    except (ValueError, TypeError):
        return str(score) if score else "Not calculated"


def format_completion_percentage(percentage: Optional[Any]) -> str:
    """Format completion percentage with visual indicators"""
    if percentage is None:
        return "Not calculated"
    
    try:
        percent_float = float(percentage)
        
        if percent_float >= 100:
            return f"{percent_float:.1f}% ✅ Complete"
        elif percent_float >= 80:
            return f"{percent_float:.1f}% ⚠️ Nearly Complete"
        elif percent_float >= 50:
            return f"{percent_float:.1f}% 📝 In Progress"
        else:
            return f"{percent_float:.1f}% 🔄 Just Started"
            
    except (ValueError, TypeError):
        return str(percentage) if percentage else "Not calculated"


def format_validation_status(status: Optional[str]) -> str:
    """Format validation status with visual indicators"""
    if not status:
        return "Unknown"
    
    status_lower = status.lower().strip()
    
    status_mapping = {
        'validated': '✅ Validated',
        'pending': '⚠️ Pending',
        'failed': '❌ Failed',
        'error': '❌ Error',
        'incomplete': '📝 Incomplete',
        'complete': '✅ Complete'
    }
    
    return status_mapping.get(status_lower, status.title())


def format_list_items(items: Optional[List[str]], separator: str = ", ", 
                     max_items: int = 5, truncate_text: str = "and {count} more") -> str:
    """Format list of items with optional truncation"""
    if not items:
        return "None"
    
    if len(items) <= max_items:
        return separator.join(items)
    else:
        visible_items = items[:max_items]
        remaining_count = len(items) - max_items
        truncate = truncate_text.format(count=remaining_count)
        return f"{separator.join(visible_items)}{separator}{truncate}"


def format_field_for_display(field_name: str, value: Any) -> str:
    """
    Auto-format any field value based on field name conventions
    This is the main dispatcher function for formatting
    """
    if value is None:
        return "Not specified"
    
    # Currency fields
    if 'value' in field_name.lower() or 'amount' in field_name.lower() or 'fund' in field_name.lower():
        return format_currency(value)
    
    # Date fields
    elif 'date' in field_name.lower():
        return format_date(value)
    
    # Percentage fields
    elif 'percentage' in field_name.lower() or 'rate' in field_name.lower() or 'score' in field_name.lower():
        if 'score' in field_name.lower():
            return format_data_quality_score(value)
        else:
            return format_percentage(value)
    
    # Age fields
    elif 'age' in field_name.lower():
        return format_age(value)
    
    # Term fields
    elif 'term' in field_name.lower() and 'year' in field_name.lower():
        return format_term_years(value)
    
    # Boolean fields
    elif field_name.lower() in ['include_taxation', 'performing_switch_analysis']:
        return format_boolean(value)
    
    # Enum fields
    elif field_name == 'product_type':
        return format_product_type(value)
    elif field_name == 'investment_term_type':
        return format_investment_term_type(value)
    elif field_name == 'tax_band':
        return format_tax_band(value)
    elif field_name == 'analysis_mode':
        return format_analysis_mode(value)
    elif field_name == 'validation_status':
        return format_validation_status(value)
    
    # List fields
    elif isinstance(value, list):
        return format_list_items(value)
    
    # Default formatting
    else:
        return str(value) if value else "Not specified"


def format_all_fields(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Format all fields in a dictionary for display
    Returns dictionary with formatted string values
    """
    formatted = {}
    
    for field_name, value in data.items():
        formatted[field_name] = format_field_for_display(field_name, value)
    
    return formatted


def format_summary_table(data: Dict[str, Any], title: str = "Summary") -> str:
    """
    Format data as a readable summary table
    """
    if not data:
        return f"**{title}**\nNo data available"
    
    # Format each field
    formatted_data = format_all_fields(data)
    
    # Create table
    lines = [f"**{title}**", ""]
    
    for field_name, formatted_value in formatted_data.items():
        # Convert field name to readable format
        readable_name = field_name.replace('_', ' ').title()
        lines.append(f"• **{readable_name}:** {formatted_value}")
    
    return "\n".join(lines)


# Specialized formatting for different contexts
def format_for_user_display(data: Dict[str, Any]) -> Dict[str, str]:
    """Format data specifically for user-facing display"""
    return format_all_fields(data)


def format_for_report(data: Dict[str, Any]) -> Dict[str, str]:
    """Format data specifically for report generation"""
    # Similar to user display but may have different formatting rules
    return format_all_fields(data)


def format_for_api_response(data: Dict[str, Any]) -> Dict[str, str]:
    """Format data specifically for API responses"""
    # Ensure all values are strings for consistent API responses
    formatted = format_all_fields(data)
    return {k: str(v) for k, v in formatted.items()}
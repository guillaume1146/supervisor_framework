"""
Data type converters for handling conversion between display formats and database formats
File: workflow_system/utils/converters.py
"""

import re
import json
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Any, Optional, Dict, List, Union
from workflow_system.phases.phase1_financial_input.constants import (
    ProductType, InvestmentTermType, TaxBand, AnalysisMode,
    TAX_RATES, SystemLimits
)


class DataTypeConverter:
    """Main converter class for handling data type conversions"""
    
    @staticmethod
    def to_database_date(date_input: Union[str, date, None]) -> Optional[date]:
        """Convert various date formats to database date"""
        if not date_input:
            return None
            
        if isinstance(date_input, date):
            return date_input
            
        if isinstance(date_input, str):
            # Handle 'today' keyword
            if date_input.lower() == 'today':
                return date.today()
                
            # Try different date formats
            date_patterns = [
                (r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})', '%d/%m/%Y'),  # dd/mm/yyyy
                (r'(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})', '%Y/%m/%d'),  # yyyy/mm/dd
                (r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2})', '%d/%m/%y'),  # dd/mm/yy
            ]
            
            for pattern, date_format in date_patterns:
                if re.match(pattern, date_input.strip()):
                    try:
                        return datetime.strptime(date_input.strip(), date_format).date()
                    except ValueError:
                        continue
                        
        raise ValueError(f"Cannot convert '{date_input}' to date")
    
    @staticmethod
    def to_database_decimal(amount_input: Union[str, float, int, Decimal, None]) -> Optional[Decimal]:
        """Convert various amount formats to database decimal"""
        if not amount_input:
            return None
            
        if isinstance(amount_input, Decimal):
            return amount_input
            
        if isinstance(amount_input, (int, float)):
            return Decimal(str(amount_input))
            
        if isinstance(amount_input, str):
            # Clean the input
            cleaned = amount_input.strip().replace('£', '').replace(',', '').replace(' ', '')
            
            if not cleaned or cleaned.lower() in ['none', 'null', 'n/a']:
                return None
                
            # Handle K and M notation
            multiplier = 1
            if cleaned.lower().endswith('k'):
                multiplier = 1000
                cleaned = cleaned[:-1]
            elif cleaned.lower().endswith('m'):
                multiplier = 1000000
                cleaned = cleaned[:-1]
                
            try:
                value = Decimal(cleaned) * multiplier
                return value.quantize(Decimal('0.01'))  # Round to 2 decimal places
            except InvalidOperation:
                raise ValueError(f"Cannot convert '{amount_input}' to decimal")
                
        raise ValueError(f"Cannot convert '{amount_input}' to decimal")
    
    @staticmethod
    def to_database_enum(enum_input: Union[str, None], enum_class) -> Optional[str]:
        """Convert string to enum value for database storage"""
        if not enum_input:
            return None
            
        if isinstance(enum_input, str):
            # Try exact match first
            cleaned_input = enum_input.lower().strip().replace(' ', '_').replace('-', '_')
            
            for enum_item in enum_class:
                if enum_item.value == cleaned_input:
                    return enum_item.value
                if enum_item.name.lower() == cleaned_input:
                    return enum_item.value
                    
            # Try partial matches for user-friendly input
            for enum_item in enum_class:
                if cleaned_input in enum_item.value or enum_item.value in cleaned_input:
                    return enum_item.value
                    
        raise ValueError(f"Cannot convert '{enum_input}' to {enum_class.__name__}")
    
    @staticmethod
    def to_database_boolean(bool_input: Union[str, bool, None]) -> Optional[bool]:
        """Convert various boolean formats to database boolean"""
        if bool_input is None:
            return None
            
        if isinstance(bool_input, bool):
            return bool_input
            
        if isinstance(bool_input, str):
            cleaned = bool_input.lower().strip()
            if cleaned in ['true', 'yes', 'y', '1', 'on', 'include', 'enable']:
                return True
            elif cleaned in ['false', 'no', 'n', '0', 'off', 'exclude', 'disable']:
                return False
                
        raise ValueError(f"Cannot convert '{bool_input}' to boolean")
    
    @staticmethod
    def to_database_integer(int_input: Union[str, int, None]) -> Optional[int]:
        """Convert various integer formats to database integer"""
        if not int_input:
            return None
            
        if isinstance(int_input, int):
            return int_input
            
        if isinstance(int_input, str):
            # Extract numbers from string
            numbers = re.findall(r'\d+', int_input.strip())
            if numbers:
                return int(numbers[0])
                
        raise ValueError(f"Cannot convert '{int_input}' to integer")


class DisplayFormatter:
    """Formatter for creating user-friendly display values"""
    
    @staticmethod
    def format_currency(value: Optional[Decimal]) -> str:
        """Format currency for display"""
        if not value:
            return "Not specified"
            
        if value >= 1000000:
            return f"£{value/1000000:.1f}M"
        elif value >= 1000:
            return f"£{value/1000:.0f}K"
        else:
            return f"£{value:,.2f}"
    
    @staticmethod
    def format_percentage(value: Optional[Decimal]) -> str:
        """Format percentage for display"""
        if not value:
            return "Not specified"
        return f"{value * 100:.2f}%"
    
    @staticmethod
    def format_date(value: Optional[date]) -> str:
        """Format date for display"""
        if not value:
            return "Not specified"
        return value.strftime("%d/%m/%Y")
    
    @staticmethod
    def format_enum(value: Optional[str], enum_class) -> str:
        """Format enum value for display"""
        if not value:
            return "Not specified"
            
        for enum_item in enum_class:
            if enum_item.value == value:
                return enum_item.name.replace('_', ' ').title()
                
        return value.replace('_', ' ').title()
    
    @staticmethod
    def format_boolean(value: Optional[bool]) -> str:
        """Format boolean for display"""
        if value is None:
            return "Not specified"
        return "Yes" if value else "No"
    
    @staticmethod
    def format_integer(value: Optional[int]) -> str:
        """Format integer for display"""
        if value is None:
            return "Not specified"
        return str(value)


class Phase1DataConverter:
    """Specialized converter for Phase 1 financial input validation"""
    
    def __init__(self):
        self.type_converter = DataTypeConverter()
        self.formatter = DisplayFormatter()
    
    def convert_and_format(self, field_name: str, raw_value: Any) -> tuple[Any, str]:
        """
        Convert raw value to database format and create display format
        Returns: (database_value, formatted_display_value)
        """
        
        # Date fields
        if field_name in ['valuation_date', 'end_date']:
            db_value = self.type_converter.to_database_date(raw_value)
            display_value = self.formatter.format_date(db_value)
            return db_value, display_value
        
        # Currency fields
        elif field_name in ['fund_value', 'surrender_value', 'initial_investment_value']:
            db_value = self.type_converter.to_database_decimal(raw_value)
            display_value = self.formatter.format_currency(db_value)
            return db_value, display_value
        
        # Decimal fields
        elif field_name in ['term_years', 'client_tax_rate', 'completion_percentage']:
            db_value = self.type_converter.to_database_decimal(raw_value)
            if field_name == 'client_tax_rate':
                display_value = self.formatter.format_percentage(db_value)
            else:
                display_value = str(db_value) if db_value else "Not specified"
            return db_value, display_value
        
        # Integer fields
        elif field_name in ['user_input_years', 'user_input_months', 'current_age', 'target_age', 'data_quality_score']:
            db_value = self.type_converter.to_database_integer(raw_value)
            display_value = self.formatter.format_integer(db_value)
            return db_value, display_value
        
        # Boolean fields
        elif field_name in ['include_taxation', 'performing_switch_analysis']:
            db_value = self.type_converter.to_database_boolean(raw_value)
            display_value = self.formatter.format_boolean(db_value)
            return db_value, display_value
        
        # Enum fields
        elif field_name == 'product_type':
            db_value = self.type_converter.to_database_enum(raw_value, ProductType)
            display_value = self.formatter.format_enum(db_value, ProductType)
            return db_value, display_value
        
        elif field_name == 'investment_term_type':
            db_value = self.type_converter.to_database_enum(raw_value, InvestmentTermType)
            display_value = self.formatter.format_enum(db_value, InvestmentTermType)
            return db_value, display_value
        
        elif field_name == 'tax_band':
            db_value = self.type_converter.to_database_enum(raw_value, TaxBand)
            display_value = self.formatter.format_enum(db_value, TaxBand)
            return db_value, display_value
        
        elif field_name == 'analysis_mode':
            db_value = self.type_converter.to_database_enum(raw_value, AnalysisMode)
            display_value = self.formatter.format_enum(db_value, AnalysisMode)
            return db_value, display_value
        
        # String fields
        elif field_name in ['provider_name', 'product_name', 'session_id', 'validation_status']:
            db_value = str(raw_value).strip() if raw_value else None
            display_value = db_value if db_value else "Not specified"
            return db_value, display_value
        
        # JSON fields
        elif field_name in ['missing_fields', 'validation_errors']:
            if isinstance(raw_value, (list, dict)):
                db_value = json.dumps(raw_value)
                display_value = json.dumps(raw_value, indent=2)
            else:
                db_value = str(raw_value) if raw_value else None
                display_value = db_value if db_value else "None"
            return db_value, display_value
        
        # Default handling
        else:
            db_value = raw_value
            display_value = str(raw_value) if raw_value is not None else "Not specified"
            return db_value, display_value
    
    def convert_all_fields(self, raw_data: Dict[str, Any]) -> Dict[str, tuple]:
        """
        Convert all fields in a dictionary
        Returns: Dict[field_name, (database_value, display_value)]
        """
        converted = {}
        for field_name, raw_value in raw_data.items():
            try:
                converted[field_name] = self.convert_and_format(field_name, raw_value)
            except (ValueError, TypeError) as e:
                # Log the error but continue with other fields
                converted[field_name] = (None, f"Error: {str(e)}")
                
        return converted
    
    def get_database_values(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get only database values"""
        converted = self.convert_all_fields(raw_data)
        return {field: db_value for field, (db_value, _) in converted.items()}
    
    def get_display_values(self, raw_data: Dict[str, Any]) -> Dict[str, str]:
        """Get only display values"""
        converted = self.convert_all_fields(raw_data)
        return {field: display_value for field, (_, display_value) in converted.items()}


# Validation helpers
class ValidationHelper:
    """Helper functions for validation during conversion"""
    
    @staticmethod
    def validate_currency_range(value: Optional[Decimal], field_name: str) -> List[str]:
        """Validate currency value is within acceptable range"""
        errors = []
        if value is None:
            return errors
            
        if value <= 0:
            errors.append(f"{field_name} must be greater than £0")
        elif value > SystemLimits.MAX_FUND_VALUE:
            errors.append(f"{field_name} cannot exceed £{SystemLimits.MAX_FUND_VALUE:,}")
        elif value < SystemLimits.MIN_FUND_VALUE:
            errors.append(f"{field_name} must be at least £{SystemLimits.MIN_FUND_VALUE:,}")
            
        return errors
    
    @staticmethod
    def validate_age_range(value: Optional[int], field_name: str) -> List[str]:
        """Validate age value is within acceptable range"""
        errors = []
        if value is None:
            return errors
            
        if value < SystemLimits.MIN_AGE:
            errors.append(f"{field_name} must be at least {SystemLimits.MIN_AGE}")
        elif value > SystemLimits.MAX_AGE:
            errors.append(f"{field_name} cannot exceed {SystemLimits.MAX_AGE}")
            
        return errors
    
    @staticmethod
    def validate_term_range(value: Optional[Decimal], field_name: str) -> List[str]:
        """Validate term value is within acceptable range"""
        errors = []
        if value is None:
            return errors
            
        if value < SystemLimits.MIN_TERM_YEARS:
            errors.append(f"{field_name} must be at least {SystemLimits.MIN_TERM_YEARS} years")
        elif value > SystemLimits.MAX_TERM_YEARS:
            errors.append(f"{field_name} cannot exceed {SystemLimits.MAX_TERM_YEARS} years")
            
        return errors
"""
Enhanced validation rules for Phase 1 financial input validation
File: workflow_system/phases/phase1_financial_input/validation_rules.py
"""

from typing import Dict, Any, List, Optional
from datetime import date, datetime
from decimal import Decimal
import re

from workflow_system.phases.phase1_financial_input.constants import (
    ProductType, InvestmentTermType, TaxBand, SystemLimits,
    PENSION_PRODUCTS, ISA_PRODUCTS, INVESTMENT_PRODUCTS, 
    TAX_EXEMPT_PRODUCTS, AGE_SENSITIVE_PRODUCTS,
    REQUIRED_FIELDS_BY_PRODUCT, VALIDATION_MESSAGES
)


class Phase1ValidationRules:
    """Comprehensive validation rules for Phase 1 financial input"""
    
    def __init__(self):
        self.validation_errors = []
        self.validation_warnings = []
    
    def clear_errors(self):
        """Clear validation errors and warnings"""
        self.validation_errors.clear()
        self.validation_warnings.clear()
    
    def get_errors(self) -> List[str]:
        """Get validation errors"""
        return self.validation_errors.copy()
    
    def get_warnings(self) -> List[str]:
        """Get validation warnings"""
        return self.validation_warnings.copy()
    
    def validate_required_fields(self, params: Dict[str, Any], 
                                product_type: Optional[str] = None) -> bool:
        """
        Validate all required fields based on product type
        Returns: True if all required fields present
        """
        is_valid = True
        
        # Common required fields
        common_fields = REQUIRED_FIELDS_BY_PRODUCT.get('common', [])
        for field in common_fields:
            if not self._is_field_present(params, field):
                self.validation_errors.append(
                    VALIDATION_MESSAGES.get(f"{field}_required", f"{field} is required")
                )
                is_valid = False
        
        # Product-specific required fields
        if product_type:
            if product_type in PENSION_PRODUCTS:
                pension_fields = REQUIRED_FIELDS_BY_PRODUCT.get('pension', [])
                for field in pension_fields:
                    if not self._is_field_present(params, field):
                        self.validation_errors.append(
                            VALIDATION_MESSAGES.get(f"{field}_required", f"{field} is required for pension products")
                        )
                        is_valid = False
            
            elif product_type in ISA_PRODUCTS:
                isa_fields = REQUIRED_FIELDS_BY_PRODUCT.get('isa', [])
                for field in isa_fields:
                    if not self._is_field_present(params, field):
                        self.validation_errors.append(
                            VALIDATION_MESSAGES.get(f"{field}_required", f"{field} is required for ISA products")
                        )
                        is_valid = False
            
            elif product_type in INVESTMENT_PRODUCTS:
                investment_fields = REQUIRED_FIELDS_BY_PRODUCT.get('investment', [])
                for field in investment_fields:
                    if not self._is_field_present(params, field):
                        self.validation_errors.append(
                            VALIDATION_MESSAGES.get(f"{field}_required", f"{field} is required for investment products")
                        )
                        is_valid = False
        
        return is_valid
    
    def validate_date_fields(self, params: Dict[str, Any]) -> bool:
        """Validate all date fields"""
        is_valid = True
        
        # Validate valuation_date
        valuation_date = params.get('valuation_date')
        if valuation_date:
            parsed_valuation = self._validate_date_format(valuation_date, 'valuation_date')
            if parsed_valuation is None:
                is_valid = False
        else:
            parsed_valuation = None
        
        # Validate end_date
        end_date = params.get('end_date')
        if end_date:
            parsed_end = self._validate_date_format(end_date, 'end_date')
            if parsed_end is None:
                is_valid = False
            elif parsed_valuation and parsed_end <= parsed_valuation:
                self.validation_errors.append(VALIDATION_MESSAGES.get('end_date_future'))
                is_valid = False
        
        return is_valid
    
    def validate_currency_fields(self, params: Dict[str, Any]) -> bool:
        """Validate all currency/monetary fields"""
        is_valid = True
        
        currency_fields = ['fund_value', 'surrender_value']
        
        for field in currency_fields:
            value_str = params.get(field)
            if value_str:
                decimal_value = self._validate_currency_amount(value_str, field)
                if decimal_value is None:
                    is_valid = False
                else:
                    # Range validation
                    if decimal_value <= 0:
                        self.validation_errors.append(VALIDATION_MESSAGES.get(f"{field}_positive"))
                        is_valid = False
                    elif decimal_value > SystemLimits.MAX_FUND_VALUE:
                        self.validation_errors.append(VALIDATION_MESSAGES.get(f"{field}_maximum"))
                        is_valid = False
                    elif decimal_value < SystemLimits.MIN_FUND_VALUE:
                        self.validation_warnings.append(f"{field} is quite low - please verify")
        
        # Cross-field validation
        fund_value_str = params.get('fund_value')
        surrender_value_str = params.get('surrender_value')
        
        if fund_value_str and surrender_value_str:
            try:
                fund_val = self._parse_currency(fund_value_str)
                surrender_val = self._parse_currency(surrender_value_str)
                
                if fund_val and surrender_val:
                    ratio = surrender_val / fund_val
                    if ratio > Decimal('1.2'):
                        self.validation_warnings.append(VALIDATION_MESSAGES.get('surrender_value_realistic'))
                    elif ratio < Decimal('0.5'):
                        self.validation_warnings.append("Surrender value is very low - high exit penalties may apply")
            except Exception:
                pass  # Already validated individually
        
        return is_valid
    
    def validate_age_fields(self, params: Dict[str, Any]) -> bool:
        """Validate age-related fields"""
        is_valid = True
        
        current_age = params.get('current_age')
        target_age = params.get('target_age')
        product_type = params.get('product_type')
        
        # Validate current_age
        if current_age:
            age_val = self._validate_integer_field(current_age, 'current_age')
            if age_val is None:
                is_valid = False
            else:
                if age_val < SystemLimits.MIN_AGE:
                    self.validation_errors.append(VALIDATION_MESSAGES.get('age_minimum'))
                    is_valid = False
                elif age_val > SystemLimits.MAX_AGE:
                    self.validation_errors.append(VALIDATION_MESSAGES.get('age_maximum'))
                    is_valid = False
        
        # Validate target_age
        if target_age:
            target_val = self._validate_integer_field(target_age, 'target_age')
            if target_val is None:
                is_valid = False
            else:
                if current_age:
                    current_val = self._validate_integer_field(current_age, 'current_age')
                    if current_val and target_val <= current_val:
                        self.validation_errors.append(VALIDATION_MESSAGES.get('target_age_greater'))
                        is_valid = False
                
                # Pension-specific age validation
                if product_type in PENSION_PRODUCTS and target_val < SystemLimits.MIN_PENSION_ACCESS_AGE:
                    self.validation_warnings.append(VALIDATION_MESSAGES.get('pension_access_age'))
        
        return is_valid
    
    def validate_term_fields(self, params: Dict[str, Any]) -> bool:
        """Validate investment term fields"""
        is_valid = True
        
        term_type = params.get('investment_term_type')
        
        if term_type == InvestmentTermType.YEARS.value:
            years = params.get('user_input_years')
            months = params.get('user_input_months')
            
            if years:
                years_val = self._validate_integer_field(years, 'user_input_years')
                if years_val is None:
                    is_valid = False
                elif years_val > SystemLimits.MAX_TERM_YEARS:
                    self.validation_errors.append(VALIDATION_MESSAGES.get('term_years_maximum'))
                    is_valid = False
                elif years_val == 0 and not months:
                    self.validation_errors.append(VALIDATION_MESSAGES.get('term_years_minimum'))
                    is_valid = False
            
            if months:
                months_val = self._validate_integer_field(months, 'user_input_months')
                if months_val is None:
                    is_valid = False
                elif months_val < 0 or months_val > 11:
                    self.validation_errors.append("Months must be between 0 and 11")
                    is_valid = False
        
        elif term_type == InvestmentTermType.UNTIL.value:
            end_date = params.get('end_date')
            if not end_date:
                self.validation_errors.append("End date is required when term type is 'until'")
                is_valid = False
        
        elif term_type == InvestmentTermType.AGE.value:
            if not params.get('current_age'):
                self.validation_errors.append("Current age is required when term type is 'age'")
                is_valid = False
            if not params.get('target_age'):
                self.validation_errors.append("Target age is required when term type is 'age'")
                is_valid = False
        
        return is_valid
    
    def validate_tax_fields(self, params: Dict[str, Any]) -> bool:
        """Validate tax-related fields with ISA awareness"""
        is_valid = True
        
        product_type = params.get('product_type')
        include_taxation = params.get('include_taxation')
        tax_band = params.get('tax_band')
        
        if product_type in ['isa', 'stocks_shares_isa']:
            if include_taxation:
                self.validation_warnings.append("ISAs are tax-exempt - tax analysis not needed (ignoring tax settings)")
            return True
        
        if product_type in ['investment_bond', 'unit_trust', 'oeic', 'investment_trust'] and include_taxation is False:
            self.validation_warnings.append("Investment products usually benefit from tax analysis")
        
        if product_type in ['pension', 'sipp'] and include_taxation is False:
            self.validation_warnings.append("Pension products usually benefit from tax analysis")
        
        # Validate tax band if tax analysis included (and not ISA)
        if include_taxation and not tax_band and product_type not in ['isa', 'stocks_shares_isa']:
            self.validation_errors.append("Tax band must be specified when including tax analysis")
            is_valid = False
        
        return is_valid
    
    def validate_product_specific_rules(self, params: Dict[str, Any]) -> bool:
        """Validate product-specific business rules"""
        is_valid = True
        
        product_type = params.get('product_type')
        
        if not product_type:
            return is_valid
        
        # Age requirements for age-sensitive products
        if product_type in AGE_SENSITIVE_PRODUCTS:
            if not params.get('current_age'):
                self.validation_errors.append(f"Age is required for {product_type} products")
                is_valid = False
        
        # Tax requirements for taxable products
        if product_type not in TAX_EXEMPT_PRODUCTS:
            include_tax = params.get('include_taxation')
            if include_tax is None:
                self.validation_warnings.append(f"Consider including tax analysis for {product_type} products")
        
        return is_valid
    
    def validate_all_fields(self, params: Dict[str, Any]) -> tuple[bool, List[str], List[str]]:
        """
        Run all validation rules
        Returns: (is_valid, errors, warnings)
        """
        self.clear_errors()
        
        product_type = params.get('product_type')
        
        # Run all validation categories
        results = [
            self.validate_required_fields(params, product_type),
            self.validate_date_fields(params),
            self.validate_currency_fields(params),
            self.validate_age_fields(params),
            self.validate_term_fields(params),
            self.validate_tax_fields(params),
            self.validate_product_specific_rules(params)
        ]
        
        is_valid = all(results)
        
        return is_valid, self.get_errors(), self.get_warnings()
    
    # Helper methods
    def _is_field_present(self, params: Dict[str, Any], field: str) -> bool:
        """Check if field is present and not empty"""
        value = params.get(field)
        if value is None:
            return False
        if isinstance(value, str) and value.strip().lower() in ['', 'none', 'not specified', 'null']:
            return False
        return True
    
    def _validate_date_format(self, date_str: str, field_name: str) -> Optional[date]:
        """Validate date format and return parsed date"""
        try:
            from workflow_system.utils.converters import DataTypeConverter
            converter = DataTypeConverter()
            return converter.to_database_date(date_str)
        except ValueError as e:
            self.validation_errors.append(f"Invalid date format for {field_name}: {str(e)}")
            return None
    
    def _validate_currency_amount(self, amount_str: str, field_name: str) -> Optional[Decimal]:
        """Validate currency amount and return parsed decimal"""
        try:
            from workflow_system.utils.converters import DataTypeConverter
            converter = DataTypeConverter()
            return converter.to_database_decimal(amount_str)
        except ValueError as e:
            self.validation_errors.append(f"Invalid amount for {field_name}: {str(e)}")
            return None
    
    def _validate_integer_field(self, value_str: str, field_name: str) -> Optional[int]:
        """Validate integer field and return parsed value"""
        try:
            from workflow_system.utils.converters import DataTypeConverter
            converter = DataTypeConverter()
            return converter.to_database_integer(value_str)
        except ValueError as e:
            self.validation_errors.append(f"Invalid number for {field_name}: {str(e)}")
            return None
    
    def _parse_currency(self, amount_str: str) -> Optional[Decimal]:
        """Parse currency string to decimal"""
        try:
            from workflow_system.utils.converters import DataTypeConverter
            converter = DataTypeConverter()
            return converter.to_database_decimal(amount_str)
        except ValueError:
            return None


# Standalone validation functions for backward compatibility
def validate_comprehensive_phase1(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive validation for Phase 1 parameters
    Returns validation result dictionary
    """
    validator = Phase1ValidationRules()
    is_valid, errors, warnings = validator.validate_all_fields(params)
    
    return {
        'is_valid': is_valid,
        'errors': errors,
        'warnings': warnings,
        'error_count': len(errors),
        'warning_count': len(warnings),
        'validation_summary': _create_validation_summary(is_valid, errors, warnings)
    }

def _create_validation_summary(is_valid: bool, errors: List[str], warnings: List[str]) -> str:
    """Create human-readable validation summary"""
    if is_valid and not warnings:
        return "✅ All validations passed successfully"
    elif is_valid and warnings:
        return f"✅ Validation passed with {len(warnings)} warning(s)"
    else:
        return f"❌ Validation failed with {len(errors)} error(s)"
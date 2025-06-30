"""
Field calculators for computed values based on other field values
File: workflow_system/phases/phase1_financial_input/field_calculators.py
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List
import json

from workflow_system.phases.phase1_financial_input.constants import (
    InvestmentTermType, TaxBand, AnalysisMode, TAX_RATES,
    PENSION_PRODUCTS, ISA_PRODUCTS, INVESTMENT_PRODUCTS, 
    TAX_EXEMPT_PRODUCTS, SystemLimits
)


class Phase1FieldCalculator:
    """Calculator for Phase 1 computed fields"""
    
    def __init__(self):
        self.calculation_errors = []
    
    def clear_errors(self):
        """Clear calculation errors"""
        self.calculation_errors = []
    
    def get_errors(self) -> List[str]:
        """Get calculation errors"""
        return self.calculation_errors.copy()
    
    def calculate_term_years(self, params: Dict[str, Any]) -> Optional[Decimal]:
        """
        Calculate term_years based on investment_term_type and related fields
        
        Logic:
        - If term_type = 'until': (end_date - valuation_date) / 365.25
        - If term_type = 'years': user_input_years + (user_input_months / 12)
        - If term_type = 'age': target_age - current_age
        """
        try:
            term_type = params.get('investment_term_type')
            valuation_date = params.get('valuation_date')
            
            if not term_type:
                return None
                
            if term_type == InvestmentTermType.UNTIL.value:
                end_date = params.get('end_date')
                if not end_date or not valuation_date:
                    return None
                    
                # Convert to date objects if they're strings
                if isinstance(valuation_date, str):
                    valuation_date = datetime.strptime(valuation_date, '%d/%m/%Y').date()
                if isinstance(end_date, str):
                    end_date = datetime.strptime(end_date, '%d/%m/%Y').date()
                    
                if end_date <= valuation_date:
                    self.calculation_errors.append("End date must be after valuation date")
                    return None
                    
                days_diff = (end_date - valuation_date).days
                years = Decimal(days_diff) / Decimal('365.25')
                return years.quantize(Decimal('0.01'))
                
            elif term_type == InvestmentTermType.YEARS.value:
                years = params.get('user_input_years', 0) or 0
                months = params.get('user_input_months', 0) or 0
                
                if years == 0 and months == 0:
                    self.calculation_errors.append("Term must be greater than zero")
                    return None
                    
                total_years = Decimal(years) + (Decimal(months) / 12)
                return total_years.quantize(Decimal('0.01'))
                
            elif term_type == InvestmentTermType.AGE.value:
                current_age = params.get('current_age')
                target_age = params.get('target_age')
                
                if not current_age or not target_age:
                    return None
                    
                if target_age <= current_age:
                    self.calculation_errors.append("Target age must be greater than current age")
                    return None
                    
                return Decimal(target_age - current_age)
                
        except Exception as e:
            self.calculation_errors.append(f"Error calculating term_years: {str(e)}")
            return None
        
        return None
    
    def calculate_initial_investment_value(self, params: Dict[str, Any]) -> Optional[Decimal]:
        """
        Calculate initial_investment_value based on performing_switch_analysis
        
        Logic:
        - If performing_switch_analysis = True: use surrender_value
        - If performing_switch_analysis = False: use fund_value
        """
        try:
            performing_switch = params.get('performing_switch_analysis')
            fund_value = params.get('fund_value')
            surrender_value = params.get('surrender_value')
            
            if performing_switch is True:
                return surrender_value
            elif performing_switch is False:
                return fund_value
            else:
                # Default to fund_value if switch analysis not specified
                return fund_value
                
        except Exception as e:
            self.calculation_errors.append(f"Error calculating initial_investment_value: {str(e)}")
            return None
    
    def calculate_analysis_mode(self, params: Dict[str, Any]) -> Optional[str]:
        """
        Calculate analysis_mode based on performing_switch_analysis
        
        Logic:
        - If performing_switch_analysis = True: "switching"
        - If performing_switch_analysis = False: "remodeling"
        """
        try:
            performing_switch = params.get('performing_switch_analysis')
            
            if performing_switch is True:
                return AnalysisMode.SWITCHING.value
            elif performing_switch is False:
                return AnalysisMode.REMODELING.value
            else:
                return None
                
        except Exception as e:
            self.calculation_errors.append(f"Error calculating analysis_mode: {str(e)}")
            return None
    
    def calculate_client_tax_rate(self, params: Dict[str, Any]) -> Optional[Decimal]:
        """
        Calculate client_tax_rate from tax_band
        
        Logic:
        - Convert tax_band enum to decimal rate (e.g., basic_rate_20 -> 0.20)
        """
        try:
            tax_band = params.get('tax_band')
            include_taxation = params.get('include_taxation')
            
            if not include_taxation or not tax_band:
                return None
                
            if tax_band in TAX_RATES:
                return TAX_RATES[tax_band]
            else:
                self.calculation_errors.append(f"Unknown tax band: {tax_band}")
                return None
                
        except Exception as e:
            self.calculation_errors.append(f"Error calculating client_tax_rate: {str(e)}")
            return None
    
    def calculate_performing_switch_analysis(self, params: Dict[str, Any]) -> Optional[bool]:
        """
        Auto-detect performing_switch_analysis based on user intent or keywords
        
        Logic:
        - Look for keywords like 'transfer', 'switch', 'move' to suggest switching
        - Look for keywords like 'optimize', 'rebalance' to suggest remodeling
        """
        try:
            # If explicitly set, use that value
            if 'performing_switch_analysis' in params:
                return params['performing_switch_analysis']
            
            # Try to auto-detect from product names or other text fields
            text_fields = [
                params.get('product_name', ''),
                params.get('provider_name', ''),
                # Could add user message analysis here
            ]
            
            combined_text = ' '.join(str(field).lower() for field in text_fields if field)
            
            switch_keywords = ['transfer', 'switch', 'move', 'change provider', 'new provider']
            remodel_keywords = ['optimize', 'rebalance', 'reallocate', 'improve', 'review funds']
            
            switch_score = sum(1 for keyword in switch_keywords if keyword in combined_text)
            remodel_score = sum(1 for keyword in remodel_keywords if keyword in combined_text)
            
            if switch_score > remodel_score:
                return True
            elif remodel_score > switch_score:
                return False
            else:
                # Default to remodeling (less disruptive)
                return False
                
        except Exception as e:
            self.calculation_errors.append(f"Error calculating performing_switch_analysis: {str(e)}")
            return None
    
    def calculate_missing_fields(self, params: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """
        Calculate which required fields are missing
        
        Logic:
        - Check each required field for None, empty string, or "not specified"
        """
        missing = []
        
        for field in required_fields:
            value = params.get(field)
            
            if value is None:
                missing.append(field)
            elif isinstance(value, str) and value.strip().lower() in ['', 'none', 'not specified', 'null']:
                missing.append(field)
            elif isinstance(value, (int, float, Decimal)) and value == 0:
                # For numeric fields, 0 might be considered missing depending on context
                if field in ['fund_value', 'surrender_value', 'current_age', 'target_age']:
                    missing.append(field)
                    
        return missing
    
    def calculate_data_quality_score(self, params: Dict[str, Any], all_fields: List[str]) -> int:
        """
        Calculate data quality score (0-100) based on field completion
        
        Logic:
        - Core fields have higher weight (70%)
        - Optional fields contribute remaining weight (30%)
        """
        try:
            from workflow_system.phases.phase1_financial_input.constants import CORE_REQUIRED_FIELDS
            
            total_fields = len(all_fields)
            if total_fields == 0:
                return 0
                
            # Count completed fields
            completed_fields = 0
            core_completed = 0
            
            for field in all_fields:
                value = params.get(field)
                is_completed = (
                    value is not None and 
                    str(value).strip().lower() not in ['', 'none', 'not specified', 'null']
                )
                
                if is_completed:
                    completed_fields += 1
                    if field in CORE_REQUIRED_FIELDS:
                        core_completed += 1
            
            # Calculate weighted score
            core_fields_count = len([f for f in CORE_REQUIRED_FIELDS if f in all_fields])
            if core_fields_count > 0:
                core_score = (core_completed / core_fields_count) * 70
                optional_score = (completed_fields / total_fields) * 30
                total_score = core_score + optional_score
            else:
                # Simple percentage if no core fields
                total_score = (completed_fields / total_fields) * 100
                
            return round(total_score)
            
        except Exception as e:
            self.calculation_errors.append(f"Error calculating data_quality_score: {str(e)}")
            return 0
    
    def calculate_completion_percentage(self, params: Dict[str, Any], all_fields: List[str]) -> Decimal:
        """
        Calculate simple completion percentage
        
        Logic:
        - Percentage of non-null fields out of total fields
        """
        try:
            if not all_fields:
                return Decimal('0')
                
            completed = sum(
                1 for field in all_fields
                if params.get(field) is not None and 
                str(params.get(field)).strip().lower() not in ['', 'none', 'not specified', 'null']
            )
            
            percentage = (Decimal(completed) / Decimal(len(all_fields))) * 100
            return percentage.quantize(Decimal('0.1'))
            
        except Exception as e:
            self.calculation_errors.append(f"Error calculating completion_percentage: {str(e)}")
            return Decimal('0')
    
    def calculate_validation_status(self, params: Dict[str, Any], missing_fields: List[str],  validation_errors: List[str]) -> str:
        """Calculate overall validation status with better logic"""
        try:
            # Critical errors = things that prevent completion
            critical_errors = [
                error for error in validation_errors
                if any(keyword in error.lower() for keyword in [
                    "must be", "required", "cannot", "invalid", "missing"
                ])
            ]
            
            # Warnings = issues that don't prevent completion
            warnings = [
                error for error in validation_errors
                if "tax-exempt" in error.lower() or "not needed" in error.lower()
            ]
            
            if critical_errors:
                return "failed"
            elif missing_fields:
                return "pending"
            elif warnings:
                return "completed_with_warnings"
            else:
                return "validated"
                
        except Exception as e:
            self.calculation_errors.append(f"Error calculating validation_status: {str(e)}")
            return "failed"
    
    def calculate_all_fields(self, params: Dict[str, Any], required_fields: List[str] = None) -> Dict[str, Any]:
        """
        Calculate all computed fields in one go
        
        Returns:
        - Dictionary with all calculated field values
        """
        self.clear_errors()
        
        if required_fields is None:
            from workflow_system.phases.phase1_financial_input.constants import CORE_REQUIRED_FIELDS
            required_fields = CORE_REQUIRED_FIELDS
        
        # Get all available field names for scoring
        all_available_fields = list(params.keys())
        
        calculated = {}
        
        # Calculate derived fields
        calculated['term_years'] = self.calculate_term_years(params)
        calculated['initial_investment_value'] = self.calculate_initial_investment_value(params)
        calculated['analysis_mode'] = self.calculate_analysis_mode(params)
        calculated['client_tax_rate'] = self.calculate_client_tax_rate(params)
        calculated['performing_switch_analysis'] = self.calculate_performing_switch_analysis(params)
        
        # Calculate validation fields
        calculated['missing_fields'] = self.calculate_missing_fields(params, required_fields)
        calculated['data_quality_score'] = self.calculate_data_quality_score(params, all_available_fields)
        calculated['completion_percentage'] = self.calculate_completion_percentage(params, all_available_fields)
        calculated['validation_status'] = self.calculate_validation_status(
            params, calculated['missing_fields'], self.get_errors()
        )
        
        # Convert missing_fields to JSON string for database storage
        if calculated['missing_fields']:
            calculated['missing_fields_json'] = json.dumps(calculated['missing_fields'])
        else:
            calculated['missing_fields_json'] = None
            
        # Store validation errors as JSON
        if self.get_errors():
            calculated['validation_errors'] = json.dumps(self.get_errors())
        else:
            calculated['validation_errors'] = None
        
        return calculated


# Business rule validators
class BusinessRuleValidator:
    """Validates business rules during field calculation"""
    
    @staticmethod
    def validate_pension_age_rules(params: Dict[str, Any]) -> List[str]:
        """Validate pension-specific age rules"""
        errors = []
        
        product_type = params.get('product_type')
        if product_type not in PENSION_PRODUCTS:
            return errors
            
        target_age = params.get('target_age')
        current_age = params.get('current_age')
        
        if target_age and target_age < SystemLimits.MIN_PENSION_ACCESS_AGE:
            errors.append(f"Pension benefits typically cannot be accessed before age {SystemLimits.MIN_PENSION_ACCESS_AGE}")
            
        if current_age and current_age >= SystemLimits.STATE_PENSION_AGE:
            errors.append("Client is already at state pension age - consider different analysis approach")
            
        return errors
    
    @staticmethod
    def validate_surrender_value_ratio(params: Dict[str, Any]) -> List[str]:
        """Validate surrender value compared to fund value"""
        errors = []
        
        fund_value = params.get('fund_value')
        surrender_value = params.get('surrender_value')
        
        if fund_value and surrender_value:
            ratio = surrender_value / fund_value
            
            if ratio > Decimal('1.2'):
                errors.append("Surrender value is unusually high compared to fund value - please verify")
            elif ratio < Decimal('0.5'):
                errors.append("Surrender value is very low compared to fund value - high exit penalties may apply")
                
        return errors
    
    @staticmethod
    def validate_tax_configuration(params: Dict[str, Any]) -> List[str]:
        """Validate tax configuration makes sense for product type"""
        errors = []
        
        product_type = params.get('product_type')
        include_taxation = params.get('include_taxation')
        tax_band = params.get('tax_band')
        
        # ISAs shouldn't have tax analysis
        if product_type in TAX_EXEMPT_PRODUCTS and include_taxation:
            errors.append(f"{product_type.upper()} products are tax-exempt - tax analysis not needed")
            
        # Pension products should usually include tax analysis
        if product_type in PENSION_PRODUCTS and include_taxation is False:
            errors.append("Pension products usually benefit from tax analysis for withdrawal planning")
            
        # If tax analysis included, tax band should be specified
        if include_taxation and not tax_band:
            errors.append("Tax band must be specified when including tax analysis")
            
        return errors
    
    @staticmethod
    def validate_all_business_rules(params: Dict[str, Any]) -> List[str]:
        """Run all business rule validations"""
        all_errors = []
        
        all_errors.extend(BusinessRuleValidator.validate_pension_age_rules(params))
        all_errors.extend(BusinessRuleValidator.validate_surrender_value_ratio(params))
        all_errors.extend(BusinessRuleValidator.validate_tax_configuration(params))
        
        return all_errors
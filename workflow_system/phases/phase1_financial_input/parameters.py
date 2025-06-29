"""
Enhanced Parameters for Phase 1: Core Input Validation and Initial Values
File: workflow_system/phases/phase1_financial_input/parameters.py (UPDATED)
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Union
from datetime import date
from decimal import Decimal

from workflow_system.phases.phase1_financial_input.constants import (
    ProductType, InvestmentTermType, TaxBand, AnalysisMode, SystemLimits
)


class FinancialInputValidationParams(BaseModel):
    """Enhanced parameters for Phase 1: Core Input Validation and Initial Values"""
    
    # ============================================================================
    # CORE FINANCIAL DATA (Always Required)
    # ============================================================================
    
    valuation_date: Optional[str] = Field(
        default=None,
        description="Valuation date in dd/mm/yyyy format - baseline date for all calculations",
        examples=["15/03/2024", "01/01/2024", "today", "31/12/2023"]
    )
    
    provider_name: Optional[str] = Field(
        default=None,
        description="Name of the financial provider managing the product",
        examples=["Aviva", "Standard Life", "Vanguard", "AJ Bell", "Hargreaves Lansdown", "Legal & General"]
    )
    
    product_name: Optional[str] = Field(
        default=None,
        description="Specific name/label of the financial product as designated by provider",
        examples=["Personal Pension Plan", "SIPP", "Stocks & Shares ISA", "Investment Bond", "Unit Trust"]
    )
    
    product_type: Optional[str] = Field(
        default=None,
        description="Regulatory classification of the financial product",
        examples=["pension", "sipp", "isa", "stocks_shares_isa", "investment_bond", "unit_trust", "oeic"]
    )
    
    fund_value: Optional[str] = Field(
        default=None,
        description="Current market value of the financial product in pounds",
        examples=["£50000", "50k", "fifty thousand", "£125,000", "200000"]
    )
    
    surrender_value: Optional[str] = Field(
        default=None,
        description="Amount receivable if product cashed in/transferred today",
        examples=["£48000", "45k", "same as fund value", "£95,000", "190000"]
    )
    
    # ============================================================================
    # INVESTMENT TERM CONFIGURATION
    # ============================================================================
    
    investment_term_type: Optional[str] = Field(
        default=None,
        description="Method to define investment analysis period: until date, for years, or until age",
        examples=["until", "years", "age"]
    )
    
    # Used when investment_term_type = "until"
    end_date: Optional[str] = Field(
        default=None,
        description="End date for analysis when term type is 'until' (dd/mm/yyyy format)",
        examples=["01/04/2030", "15/12/2035", "31/03/2040"]
    )
    
    # Used when investment_term_type = "years"
    user_input_years: Optional[str] = Field(
        default=None,
        description="Number of years for analysis when term type is 'years'",
        examples=["10", "15", "20", "25", "thirty"]
    )
    
    user_input_months: Optional[str] = Field(
        default=None,
        description="Additional months (0-11) when term type is 'years'",
        examples=["0", "6", "9", "11"]
    )
    
    # Used when investment_term_type = "age"
    current_age: Optional[str] = Field(
        default=None,
        description="Client's current age (required for pension and insurance products)",
        examples=["45", "forty-five", "aged 45", "45 years old", "35"]
    )
    
    target_age: Optional[str] = Field(
        default=None,
        description="Age client wants to reach for analysis when term type is 'age'",
        examples=["65", "67", "sixty", "retirement age", "55"]
    )
    
    # ============================================================================
    # TAX CONFIGURATION
    # ============================================================================
    
    include_taxation: Optional[str] = Field(
        default=None,
        description="Whether to include tax implications in analysis (not needed for ISAs)",
        examples=["yes", "no", "true", "false", "include tax", "exclude tax"]
    )
    
    tax_band: Optional[str] = Field(
        default=None,
        description="Client's current tax band for tax analysis",
        examples=["basic_rate_20", "higher_rate_40", "additional_rate_45", "20%", "40%", "45%"]
    )
    
    # ============================================================================
    # ANALYSIS TYPE CONFIGURATION
    # ============================================================================
    
    performing_switch_analysis: Optional[str] = Field(
        default=None,
        description="Whether analyzing product switching vs optimization within current product",
        examples=["yes", "no", "switch", "transfer", "optimize", "rebalance"]
    )
    
    # ============================================================================
    # COMPUTED/CALCULATED FIELDS (Auto-calculated, not user input)
    # ============================================================================
    
    # These fields are calculated automatically and should not be in user prompts
    term_years: Optional[Union[str, Decimal]] = Field(
        default=None,
        description="Calculated investment term in years (auto-calculated)",
        exclude=True
    )
    
    initial_investment_value: Optional[Union[str, Decimal]] = Field(
        default=None,
        description="Starting value for analysis - fund_value or surrender_value (auto-calculated)",
        exclude=True
    )
    
    analysis_mode: Optional[str] = Field(
        default=None,
        description="Analysis mode: switching or remodeling (auto-calculated)",
        exclude=True
    )
    
    client_tax_rate: Optional[Union[str, Decimal]] = Field(
        default=None,
        description="Tax rate as decimal from tax_band (auto-calculated)",
        exclude=True
    )
    
    missing_fields: Optional[List[str]] = Field(
        default=None,
        description="List of missing required fields (auto-calculated)",
        exclude=True
    )
    
    data_quality_score: Optional[int] = Field(
        default=None,
        description="Data quality score 0-100 (auto-calculated)",
        exclude=True
    )
    
    completion_percentage: Optional[Union[str, Decimal]] = Field(
        default=None,
        description="Completion percentage (auto-calculated)",
        exclude=True
    )
    
    validation_status: Optional[str] = Field(
        default=None,
        description="Overall validation status (auto-calculated)",
        exclude=True
    )
    
    validation_errors: Optional[List[str]] = Field(
        default=None,
        description="List of validation errors (auto-calculated)",
        exclude=True
    )
    
    # ============================================================================
    # FIELD GROUPINGS FOR VALIDATION
    # ============================================================================
    
    @classmethod
    def get_computed_fields(cls) -> List[str]:
        """Get list of computed/auto-calculated fields that should never be asked to users"""
        return [
            'term_years',
            'initial_investment_value', 
            'analysis_mode',
            'client_tax_rate',
            'missing_fields',
            'data_quality_score',
            'completion_percentage',
            'validation_status', 
            'validation_errors'
        ]

    
    
    
    @classmethod
    def get_user_input_fields(cls) -> List[str]:
        """Get list of fields that require user input (exclude computed fields)"""
        return [
            'valuation_date', 'provider_name', 'product_name', 'product_type',
            'fund_value', 'surrender_value', 'investment_term_type',
            'end_date', 'user_input_years', 'user_input_months',
            'current_age', 'target_age', 'include_taxation', 'tax_band',
            'performing_switch_analysis'
        ]
    
    @classmethod
    def get_core_required_fields(cls) -> List[str]:
        """Get list of core required fields (mandatory for all products)"""
        return [
            'valuation_date', 'provider_name', 'product_name', 'product_type',
            'fund_value', 'surrender_value', 'investment_term_type'
        ]
    
    @classmethod
    def get_conditional_required_fields(cls, product_type: str = None) -> List[str]:
        """Get additional required fields based on product type"""
        conditional = []
        
        if not product_type:
            return conditional
            
        # Pension products need age and tax info
        if product_type in ['pension', 'sipp']:
            conditional.extend(['current_age', 'include_taxation', 'tax_band'])
            
        # Investment products need tax info
        if product_type in ['investment_bond', 'unit_trust', 'oeic', 'investment_trust']:
            conditional.extend(['include_taxation', 'tax_band'])
            
        # Insurance products need age
        if product_type in ['life_insurance', 'endowment', 'whole_of_life', 'critical_illness_cover']:
            conditional.extend(['current_age'])
            
        return conditional
    
    @classmethod
    def get_term_specific_fields(cls, term_type: str = None) -> List[str]:
        """Get required fields based on investment term type"""
        if not term_type:
            return []
            
        if term_type == 'until':
            return ['end_date']
        elif term_type == 'years':
            return ['user_input_years']  # user_input_months is optional
        elif term_type == 'age':
            return ['current_age', 'target_age']
            
        return []
    
    # ============================================================================
    # VALIDATION RULES
    # ============================================================================
    
    @validator('fund_value', 'surrender_value', 'initial_investment_value', pre=True)
    def convert_currency_fields(cls, v):
        """Convert numeric values to strings for currency fields"""
        if v is None:
            return v
        return str(v)

    @validator('current_age', 'target_age', 'user_input_years', 'user_input_months', 'data_quality_score', pre=True)  
    def convert_numeric_fields(cls, v):
        """Convert numeric values to strings for numeric fields"""
        if v is None:
            return v
        return str(v)

    @validator('include_taxation', 'performing_switch_analysis', pre=True)
    def convert_boolean_fields(cls, v):
        """Convert boolean values to strings for boolean fields"""
        if v is None:
            return v
        if isinstance(v, bool):
            return "yes" if v else "no"
        return str(v)

    @validator('term_years', 'client_tax_rate', 'completion_percentage', pre=True)
    def convert_decimal_fields(cls, v):
        """Convert decimal/float values to strings for decimal fields"""
        if v is None:
            return v
        return str(v)
    
    
    @validator('product_type')
    def validate_product_type(cls, v):
        """Validate product type against allowed values"""
        if v is None:
            return v
            
        # Convert to lowercase and replace spaces/hyphens
        normalized = v.lower().strip().replace(' ', '_').replace('-', '_').replace('&', '_')
        
        # Check against ProductType enum values
        valid_types = [pt.value for pt in ProductType]
        if normalized not in valid_types:
            # Try common aliases
            aliases = {
                'stocks_shares_isa': 'stocks_shares_isa',
                'stocks_and_shares_isa': 'stocks_shares_isa',
                'personal_pension': 'pension',
                'workplace_pension': 'pension',
                'stakeholder_pension': 'pension'
            }
            normalized = aliases.get(normalized, normalized)
            
            if normalized not in valid_types:
                raise ValueError(f"Invalid product type. Must be one of: {', '.join(valid_types)}")
                
        return normalized
    
    @validator('investment_term_type')
    def validate_investment_term_type(cls, v):
        """Validate investment term type"""
        if v is None:
            return v
            
        normalized = v.lower().strip()
        valid_types = [itt.value for itt in InvestmentTermType]
        
        if normalized not in valid_types:
            raise ValueError(f"Invalid investment term type. Must be one of: {', '.join(valid_types)}")
            
        return normalized
    
    @validator('tax_band')
    def validate_tax_band(cls, v):
        """Validate tax band"""
        if v is None:
            return v
            
        # Handle percentage formats
        if '%' in str(v):
            v = str(v).replace('%', '').strip()
            if v == '20':
                return TaxBand.BASIC_RATE.value
            elif v == '40':
                return TaxBand.HIGHER_RATE.value
            elif v == '45':
                return TaxBand.ADDITIONAL_RATE.value
                
        normalized = str(v).lower().strip().replace(' ', '_')
        valid_bands = [tb.value for tb in TaxBand]
        
        if normalized not in valid_bands:
            raise ValueError(f"Invalid tax band. Must be one of: {', '.join(valid_bands)}")
            
        return normalized
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def get_all_missing_fields(self) -> List[str]:
        """Get all missing fields based on current values"""
        missing = []
        
        # Check core required fields
        for field in self.get_core_required_fields():
            value = getattr(self, field, None)
            if not value or str(value).strip().lower() in ['', 'none', 'not specified']:
                missing.append(field)
        
        # Check conditional fields based on product type
        if self.product_type:
            conditional_fields = self.get_conditional_required_fields(self.product_type)
            for field in conditional_fields:
                value = getattr(self, field, None)
                if not value or str(value).strip().lower() in ['', 'none', 'not specified']:
                    missing.append(field)
        
        # Check term-specific fields
        if self.investment_term_type:
            term_fields = self.get_term_specific_fields(self.investment_term_type)
            for field in term_fields:
                value = getattr(self, field, None)
                if not value or str(value).strip().lower() in ['', 'none', 'not specified']:
                    missing.append(field)
        
        return list(set(missing))  # Remove duplicates
    
    def is_complete(self) -> bool:
        """Check if all required fields are complete"""
        return len(self.get_all_missing_fields()) == 0
    
    def get_completion_summary(self) -> dict:
        """Get completion summary for user feedback"""
        user_fields = self.get_user_input_fields()
        completed_fields = []
        missing_fields = []
        
        for field in user_fields:
            value = getattr(self, field, None)
            if value and str(value).strip().lower() not in ['', 'none', 'not specified']:
                completed_fields.append(field)
            else:
                missing_fields.append(field)
        
        return {
            'total_fields': len(user_fields),
            'completed_fields': len(completed_fields),
            'missing_fields': len(missing_fields),
            'completion_percentage': round((len(completed_fields) / len(user_fields)) * 100, 1),
            'is_complete': self.is_complete(),
            'missing_field_names': self.get_all_missing_fields()
        }
    

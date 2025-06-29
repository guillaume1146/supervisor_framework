"""
Constants and enums for Phase 1: Core Input Validation and Initial Values
File: workflow_system/phases/phase1_financial_input/constants.py
"""

from enum import Enum
from decimal import Decimal
from typing import Dict, Any


class ProductType(Enum):
    """Financial product type classification"""
    PENSION = "pension"
    SIPP = "sipp" 
    ISA = "isa"
    STOCKS_SHARES_ISA = "stocks_shares_isa"
    INVESTMENT_BOND = "investment_bond"
    UNIT_TRUST = "unit_trust"
    OEIC = "oeic"
    INVESTMENT_TRUST = "investment_trust"
    LIFE_INSURANCE = "life_insurance"
    ENDOWMENT = "endowment"
    WHOLE_OF_LIFE = "whole_of_life"
    TERM_ASSURANCE = "term_assurance"
    CRITICAL_ILLNESS_COVER = "critical_illness_cover"
    INCOME_PROTECTION = "income_protection"
    HEALTH_INSURANCE = "health_insurance"
    OTHERS = "others"


class InvestmentTermType(Enum):
    """Investment term type classification"""
    UNTIL = "until"  # Until specific date
    YEARS = "years"  # For number of years
    AGE = "age"     # Until client reaches age


class TaxBand(Enum):
    """UK tax band classification"""
    BASIC_RATE = "basic_rate_20"      # 20%
    HIGHER_RATE = "higher_rate_40"    # 40%
    ADDITIONAL_RATE = "additional_rate_45"  # 45%


class AnalysisMode(Enum):
    """Analysis mode classification"""
    SWITCHING = "switching"      # Product switching analysis
    REMODELING = "remodeling"    # Portfolio optimization analysis


class GrowthRateType(Enum):
    """Growth rate type classification"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    GROWTH = "growth"


# System Configuration Constants
class SystemLimits:
    """System operational limits"""
    DECIMAL_PRECISION = 8
    PERCENTAGE_PRECISION = 4
    CURRENCY_PRECISION = 2
    MAX_TERM_YEARS = 60
    MIN_TERM_YEARS = Decimal('0.25')  # 3 months
    MAX_FUND_VALUE = Decimal('50000000')  # £50M
    MIN_FUND_VALUE = Decimal('1000')  # £1K
    MIN_AGE = 16
    MAX_AGE = 100
    MIN_PENSION_ACCESS_AGE = 55
    STATE_PENSION_AGE = 67


# Default Growth Rates
DEFAULT_GROWTH_RATES: Dict[str, Decimal] = {
    GrowthRateType.CONSERVATIVE.value: Decimal('0.02'),  # 2%
    GrowthRateType.MODERATE.value: Decimal('0.05'),      # 5%
    GrowthRateType.GROWTH.value: Decimal('0.08')         # 8%
}

DEFAULT_INFLATION_ADJUSTED_RATES: Dict[str, Decimal] = {
    GrowthRateType.CONSERVATIVE.value: Decimal('-0.005'),  # -0.5%
    GrowthRateType.MODERATE.value: Decimal('0.0294'),     # 2.94%
    GrowthRateType.GROWTH.value: Decimal('0.0588')        # 5.88%
}

# Tax Rates
TAX_RATES: Dict[str, Decimal] = {
    TaxBand.BASIC_RATE.value: Decimal('0.20'),     # 20%
    TaxBand.HIGHER_RATE.value: Decimal('0.40'),    # 40%
    TaxBand.ADDITIONAL_RATE.value: Decimal('0.45') # 45%
}

# Product Type Categories for validation
PENSION_PRODUCTS = {
    ProductType.PENSION.value,
    ProductType.SIPP.value
}

ISA_PRODUCTS = {
    ProductType.ISA.value,
    ProductType.STOCKS_SHARES_ISA.value
}

INVESTMENT_PRODUCTS = {
    ProductType.INVESTMENT_BOND.value,
    ProductType.UNIT_TRUST.value,
    ProductType.OEIC.value,
    ProductType.INVESTMENT_TRUST.value
}

INSURANCE_PRODUCTS = {
    ProductType.LIFE_INSURANCE.value,
    ProductType.ENDOWMENT.value,
    ProductType.WHOLE_OF_LIFE.value,
    ProductType.TERM_ASSURANCE.value,
    ProductType.CRITICAL_ILLNESS_COVER.value,
    ProductType.INCOME_PROTECTION.value,
    ProductType.HEALTH_INSURANCE.value
}

# Tax exempt products (no tax analysis needed)
TAX_EXEMPT_PRODUCTS = ISA_PRODUCTS

# Products requiring age validation
AGE_SENSITIVE_PRODUCTS = PENSION_PRODUCTS | INSURANCE_PRODUCTS

# Required fields by product type
REQUIRED_FIELDS_BY_PRODUCT: Dict[str, list] = {
    'common': [
        'valuation_date', 'provider_name', 'product_name', 
        'product_type', 'fund_value', 'surrender_value'
    ],
    'pension': [
        'current_age', 'investment_term_type', 'include_taxation', 'tax_band'
    ],
    'isa': [
        'investment_term_type'
    ],
    'investment': [
        'investment_term_type', 'include_taxation', 'tax_band'
    ],
    'insurance': [
        'current_age', 'investment_term_type'
    ]
}

# Core required fields (mandatory for all products)
CORE_REQUIRED_FIELDS = [
    'valuation_date',
    'provider_name', 
    'product_name',
    'product_type',
    'fund_value',
    'surrender_value',
    'investment_term_type'
]

# Validation error messages
VALIDATION_MESSAGES = {
    'valuation_date_required': "Valuation date is required for all analyses",
    'valuation_date_format': "Please enter date in dd/mm/yyyy format (e.g., 15/03/2024)",
    'provider_name_required': "Provider name is required to identify the product",
    'product_name_required': "Product name helps identify the specific financial product",
    'product_type_required': "Product type determines applicable rules and tax treatment",
    'fund_value_required': "Current fund value is required for all calculations",
    'fund_value_positive': "Fund value must be greater than £0",
    'fund_value_maximum': f"Fund value cannot exceed £{SystemLimits.MAX_FUND_VALUE:,}",
    'fund_value_minimum': f"Fund value must be at least £{SystemLimits.MIN_FUND_VALUE:,}",
    'surrender_value_required': "Surrender value is required for transfer analysis",
    'surrender_value_positive': "Surrender value must be greater than £0",
    'surrender_value_realistic': "Surrender value appears unusually high compared to fund value",
    'term_type_required': "Investment term type must be specified",
    'term_years_minimum': f"Investment term must be at least {SystemLimits.MIN_TERM_YEARS} years",
    'term_years_maximum': f"Investment term cannot exceed {SystemLimits.MAX_TERM_YEARS} years",
    'age_required': "Client age is required for pension and insurance products",
    'age_minimum': f"Client age must be at least {SystemLimits.MIN_AGE}",
    'age_maximum': f"Client age cannot exceed {SystemLimits.MAX_AGE}",
    'target_age_greater': "Target age must be greater than current age",
    'pension_access_age': f"Pension benefits typically cannot be accessed before age {SystemLimits.MIN_PENSION_ACCESS_AGE}",
    'end_date_future': "End date must be after valuation date",
    'tax_band_required': "Tax band is required for tax analysis",
}
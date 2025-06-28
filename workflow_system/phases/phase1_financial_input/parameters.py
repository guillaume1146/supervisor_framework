"""
Parameters for Phase 1: Core Input Validation and Initial Values
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from workflow_system.utils.validators import validate_date_format, validate_currency_amount


class FinancialInputValidationParams(BaseModel):
    """Parameters for Phase 1: Core Input Validation and Initial Values"""
    
    valuation_date: Optional[str] = Field(
        default=None,
        description="Valuation date in dd/mm/yyyy format (e.g., 15/03/2024, today, March 2024)",
        examples=["15/03/2024", "01/01/2024", "today", "31/12/2023"]
    )
    
    current_fund_value: Optional[str] = Field(
        default=None,
        description="Current fund value in pounds (e.g., £50000, 50k, fifty thousand)",
        examples=["£50000", "50k", "fifty thousand", "£125,000", "200000"]
    )
    
    annual_contribution: Optional[str] = Field(
        default=None,
        description="Annual contribution amount in pounds (e.g., £5000, 5k per year, monthly £400)",
        examples=["£5000", "5k", "£400 monthly", "monthly 400", "annual 6000"]
    )
    
    product_type: Optional[str] = Field(
        default=None,
        description="Type of financial product (pension, SIPP, ISA, investment bond, unit trust)",
        examples=["pension", "SIPP", "ISA", "investment bond", "unit trust"]
    )
    
    provider_name: Optional[str] = Field(
        default=None,
        description="Current provider name (e.g., Aviva, Standard Life, Vanguard)",
        examples=["Aviva", "Standard Life", "Vanguard", "AJ Bell", "Hargreaves Lansdown"]
    )
    
    income_withdrawal: Optional[str] = Field(
        default=None,
        description="Annual income withdrawal amount if applicable (e.g., £2000, none, not taking income)",
        examples=["£2000", "none", "not taking income", "monthly £500", "0"]
    )
    
    term_years: Optional[str] = Field(
        default=None,
        description="Investment term in years (e.g., 10 years, until retirement, 25)",
        examples=["10", "25", "until retirement", "10 years", "twenty years"]
    )
    
    client_age: Optional[str] = Field(
        default=None,
        description="Client age (e.g., 45, forty-five years old, aged 45)",
        examples=["45", "forty-five", "aged 45", "45 years old"]
    )

    @validator('valuation_date')
    def validate_date_format_field(cls, v):
        return v  # Keep simple for now, validation in utils

    @validator('current_fund_value', 'annual_contribution', 'income_withdrawal')
    def validate_currency_amounts_field(cls, v):
        return v  # Keep simple for now, validation in utils
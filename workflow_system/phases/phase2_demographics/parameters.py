"""
Parameters for Phase 2: Client Demographics and Income
"""

from pydantic import BaseModel, Field
from typing import Optional


class ClientDemographicsParams(BaseModel):
    """Parameters for Phase 2: Client Demographics and Income"""
    
    # Personal Information
    client_name: Optional[str] = Field(
        default=None,
        description="Full client name",
        examples=["John Smith", "Sarah Johnson", "Mr. Robert Brown"]
    )
    
    date_of_birth: Optional[str] = Field(
        default=None,
        description="Client date of birth in dd/mm/yyyy format",
        examples=["15/03/1978", "01/01/1980", "25/12/1975"]
    )
    
    employment_status: Optional[str] = Field(
        default=None,
        description="Current employment status",
        examples=["employed", "self-employed", "retired", "unemployed", "contractor"]
    )
    
    # Income Information
    annual_income: Optional[str] = Field(
        default=None,
        description="Annual gross income",
        examples=["£45000", "45k", "monthly £3500", "not disclosed"]
    )
    
    other_income: Optional[str] = Field(
        default=None,
        description="Other sources of income",
        examples=["rental income £12000", "pension £8000", "none", "dividends £2000"]
    )
    
    # Family Information
    marital_status: Optional[str] = Field(
        default=None,
        description="Marital status",
        examples=["single", "married", "divorced", "widowed", "partner"]
    )
    
    dependents: Optional[str] = Field(
        default=None,
        description="Number of dependents",
        examples=["none", "2 children", "1", "elderly parent", "0"]
    )
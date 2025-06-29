"""
Enhanced Phase 1: Core Input Validation and Initial Values
File: workflow_system/phases/phase1_financial_input/__init__.py (UPDATED)
"""

# Import enhanced parameters with all field definitions
from .parameters import FinancialInputValidationParams

# Import enhanced implementation with database integration
from .implementation import (
    financial_input_validation_workflow,
    Phase1WorkflowProcessor
)

# Import enhanced definition
from .definition import PHASE1_DEFINITION

# Import constants and enums
from .constants import (
    ProductType,
    InvestmentTermType, 
    TaxBand,
    AnalysisMode,
    SystemLimits,
    DEFAULT_GROWTH_RATES,
    DEFAULT_INFLATION_ADJUSTED_RATES,
    TAX_RATES,
    CORE_REQUIRED_FIELDS,
    REQUIRED_FIELDS_BY_PRODUCT,
    VALIDATION_MESSAGES
)

# Import database models
from .database_models import (
    FinancialInputValidationRecord,
    DATABASE_SCHEMA
)

# Import field calculators
from .field_calculators import (
    Phase1FieldCalculator,
    BusinessRuleValidator
)

# Import validation rules
from .validation_rules import (
    Phase1ValidationRules,
    validate_comprehensive_phase1
)

# Import calculations (enhanced)
from .calculations import (
    calculate_phase1_completion_score,
    assess_data_readiness
)

__all__ = [
    # Core phase components
    "FinancialInputValidationParams",
    "financial_input_validation_workflow", 
    "Phase1WorkflowProcessor",
    "PHASE1_DEFINITION",
    
    # Constants and enums
    "ProductType",
    "InvestmentTermType",
    "TaxBand", 
    "AnalysisMode",
    "SystemLimits",
    "DEFAULT_GROWTH_RATES",
    "DEFAULT_INFLATION_ADJUSTED_RATES",
    "TAX_RATES",
    "CORE_REQUIRED_FIELDS",
    "REQUIRED_FIELDS_BY_PRODUCT",
    "VALIDATION_MESSAGES",
    
    # Database integration
    "FinancialInputValidationRecord",
    "DATABASE_SCHEMA",
    
    # Processing components
    "Phase1FieldCalculator",
    "BusinessRuleValidator",
    "Phase1ValidationRules",
    "validate_comprehensive_phase1",
    
    # Calculations
    "calculate_phase1_completion_score",
    "assess_data_readiness"
]

# Phase metadata
__version__ = "2.0.0"
__description__ = "Enhanced Phase 1: Core Input Validation and Initial Values with database integration"
__phase_name__ = "financial_input_validation"
__supports_database__ = True
__supports_field_calculation__ = True
__supports_data_conversion__ = True

# Convenience functions for external usage
def get_phase_info() -> dict:
    """Get comprehensive phase information"""
    return {
        "name": __phase_name__,
        "version": __version__,
        "description": __description__,
        "supports_database": __supports_database__,
        "supports_field_calculation": __supports_field_calculation__,
        "supports_data_conversion": __supports_data_conversion__,
        "total_enum_types": 4,
        "total_constants": len(CORE_REQUIRED_FIELDS),
        "database_table": "financial_input_validation",
        "parameter_fields": len(FinancialInputValidationParams.get_user_input_fields()),
        "required_core_fields": len(FinancialInputValidationParams.get_core_required_fields())
    }

def get_supported_product_types() -> list:
    """Get list of supported product types"""
    return [pt.value for pt in ProductType]

def get_supported_term_types() -> list:
    """Get list of supported investment term types"""
    return [itt.value for itt in InvestmentTermType]

def get_supported_tax_bands() -> list:
    """Get list of supported tax bands"""
    return [tb.value for tb in TaxBand]

def validate_product_compatibility(product_type: str) -> dict:
    """
    Validate product type and return compatibility information
    
    Args:
        product_type: Product type to validate
        
    Returns:
        Dictionary with compatibility information
    """
    from .constants import (
        PENSION_PRODUCTS, ISA_PRODUCTS, INVESTMENT_PRODUCTS, 
        TAX_EXEMPT_PRODUCTS, AGE_SENSITIVE_PRODUCTS
    )
    
    result = {
        "is_valid": False,
        "product_type": product_type,
        "category": "unknown",
        "requires_age": False,
        "requires_tax_analysis": False,
        "is_tax_exempt": False,
        "additional_fields": []
    }
    
    if not product_type:
        result["errors"] = ["Product type is required"]
        return result
    
    # Normalize product type
    normalized = product_type.lower().strip()
    
    # Check if valid
    valid_types = [pt.value for pt in ProductType]
    if normalized not in valid_types:
        result["errors"] = [f"Invalid product type. Must be one of: {', '.join(valid_types)}"]
        return result
    
    result["is_valid"] = True
    result["product_type"] = normalized
    
    # Determine category and requirements
    if normalized in PENSION_PRODUCTS:
        result["category"] = "pension"
        result["requires_age"] = True
        result["requires_tax_analysis"] = True
        result["additional_fields"] = ["current_age", "include_taxation", "tax_band"]
        
    elif normalized in ISA_PRODUCTS:
        result["category"] = "isa" 
        result["is_tax_exempt"] = True
        result["additional_fields"] = []
        
    elif normalized in INVESTMENT_PRODUCTS:
        result["category"] = "investment"
        result["requires_tax_analysis"] = True
        result["additional_fields"] = ["include_taxation", "tax_band"]
        
    else:
        result["category"] = "other"
    
    # Check specific flags
    result["requires_age"] = normalized in AGE_SENSITIVE_PRODUCTS
    result["is_tax_exempt"] = normalized in TAX_EXEMPT_PRODUCTS
    
    return result

def create_sample_data(product_type: str = "pension") -> dict:
    """
    Create sample data for testing purposes
    
    Args:
        product_type: Type of product to create sample data for
        
    Returns:
        Dictionary with sample field values
    """
    from datetime import date, timedelta
    
    base_sample = {
        "valuation_date": "01/01/2024",
        "provider_name": "Standard Life",
        "product_name": "Personal Pension Plan",
        "product_type": product_type,
        "fund_value": "£50,000",
        "surrender_value": "£48,000",
        "investment_term_type": "age"
    }
    
    # Add product-specific fields
    compatibility = validate_product_compatibility(product_type)
    
    if compatibility.get("requires_age"):
        base_sample.update({
            "current_age": "45",
            "target_age": "65"
        })
    
    if compatibility.get("requires_tax_analysis"):
        base_sample.update({
            "include_taxation": "yes",
            "tax_band": "basic_rate_20"
        })
    
    if product_type in ["pension", "sipp"]:
        base_sample.update({
            "performing_switch_analysis": "no"
        })
    
    return base_sample

# Quick validation function for external use
def quick_validate(data: dict) -> dict:
    """
    Quick validation of Phase 1 data
    
    Args:
        data: Dictionary of field values
        
    Returns:
        Validation summary
    """
    try:
        # Create parameters object
        params = FinancialInputValidationParams(**data)
        
        # Get completion summary
        completion = params.get_completion_summary()
        
        # Run comprehensive validation
        validation_result = validate_comprehensive_phase1(data)
        
        return {
            "is_valid": validation_result["is_valid"] and completion["is_complete"],
            "completion_summary": completion,
            "validation_summary": validation_result,
            "ready_for_processing": validation_result["is_valid"] and completion["is_complete"]
        }
        
    except Exception as e:
        return {
            "is_valid": False,
            "error": str(e),
            "completion_summary": {"is_complete": False},
            "validation_summary": {"is_valid": False, "errors": [str(e)]},
            "ready_for_processing": False
        }
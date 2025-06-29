"""
Enhanced phase implementations package with database integration
File: workflow_system/phases/__init__.py (UPDATED)
"""

# Import Phase 1 enhanced definition and components
from .phase1_financial_input.definition import PHASE1_DEFINITION
from .phase1_financial_input import (
    FinancialInputValidationParams,
    financial_input_validation_workflow,
    Phase1WorkflowProcessor,
    ProductType,
    InvestmentTermType,
    TaxBand,
    AnalysisMode,
    SystemLimits,
    FinancialInputValidationRecord,
    Phase1FieldCalculator,
    BusinessRuleValidator,
    Phase1ValidationRules,
    get_phase_info as get_phase1_info,
    validate_product_compatibility,
    quick_validate as quick_validate_phase1
)

# Import Report Generation definition (legacy support)
from .report_generation.definition import REPORT_GENERATION_DEFINITION
from .report_generation import (
    GenerateReportParams,
    generate_report_workflow
)

__all__ = [
    # Phase definitions (for registry)
    "PHASE1_DEFINITION",
    "REPORT_GENERATION_DEFINITION",
    
    # Phase 1 enhanced components
    "FinancialInputValidationParams",
    "financial_input_validation_workflow", 
    "Phase1WorkflowProcessor",
    
    # Phase 1 enums and constants
    "ProductType",
    "InvestmentTermType",
    "TaxBand",
    "AnalysisMode",
    "SystemLimits",
    
    # Phase 1 database integration
    "FinancialInputValidationRecord",
    
    # Phase 1 processing components
    "Phase1FieldCalculator",
    "BusinessRuleValidator",
    "Phase1ValidationRules",
    
    # Phase 1 utility functions
    "get_phase1_info",
    "validate_product_compatibility",
    "quick_validate_phase1",
    
    # Report generation (legacy)
    "GenerateReportParams",
    "generate_report_workflow"
]

# Package metadata
__version__ = "2.0.0"
__description__ = "Enhanced workflow phases with database integration and comprehensive validation"

# Phase registry information
AVAILABLE_PHASES = {
    "phase1_financial_input": {
        "name": "financial_input_validation",
        "version": "2.0.0",
        "description": "Enhanced Phase 1: Core Input Validation and Initial Values",
        "supports_database": True,
        "supports_field_calculation": True,
        "supports_data_conversion": True,
        "definition": PHASE1_DEFINITION,
        "processor_class": Phase1WorkflowProcessor,
        "parameter_class": FinancialInputValidationParams,
        "database_record_class": FinancialInputValidationRecord
    },
    "report_generation": {
        "name": "generate_report",
        "version": "1.0.0", 
        "description": "Generate user reports and analytics",
        "supports_database": False,
        "supports_field_calculation": False,
        "supports_data_conversion": False,
        "definition": REPORT_GENERATION_DEFINITION,
        "processor_class": None,
        "parameter_class": GenerateReportParams,
        "database_record_class": None
    }
}

def get_available_phases() -> dict:
    """Get information about all available phases"""
    return AVAILABLE_PHASES.copy()

def get_enhanced_phases() -> list:
    """Get list of phases with enhanced features (database integration, etc.)"""
    return [
        phase_name for phase_name, info in AVAILABLE_PHASES.items()
        if info.get("supports_database", False)
    ]

def get_phase_capabilities(phase_name: str) -> dict:
    """Get capabilities of a specific phase"""
    phase_info = AVAILABLE_PHASES.get(phase_name)
    if not phase_info:
        return {"error": f"Phase '{phase_name}' not found"}
    
    return {
        "name": phase_info["name"],
        "version": phase_info["version"],
        "description": phase_info["description"],
        "capabilities": {
            "database_storage": phase_info.get("supports_database", False),
            "field_calculation": phase_info.get("supports_field_calculation", False),
            "data_conversion": phase_info.get("supports_data_conversion", False),
            "has_processor_class": phase_info.get("processor_class") is not None,
            "has_database_model": phase_info.get("database_record_class") is not None
        }
    }

def validate_phase_compatibility() -> dict:
    """Validate that all phases are properly configured"""
    results = {
        "all_valid": True,
        "phase_results": {},
        "summary": {
            "total_phases": len(AVAILABLE_PHASES),
            "enhanced_phases": 0,
            "legacy_phases": 0,
            "invalid_phases": 0
        }
    }
    
    for phase_name, phase_info in AVAILABLE_PHASES.items():
        phase_result = {
            "is_valid": True,
            "issues": [],
            "enhancements": []
        }
        
        # Check if definition exists
        if not phase_info.get("definition"):
            phase_result["is_valid"] = False
            phase_result["issues"].append("Missing phase definition")
        
        # Check if parameter class exists
        if not phase_info.get("parameter_class"):
            phase_result["issues"].append("Missing parameter class")
        
        # Count enhancement features
        if phase_info.get("supports_database"):
            phase_result["enhancements"].append("database_integration")
            results["summary"]["enhanced_phases"] += 1
        else:
            results["summary"]["legacy_phases"] += 1
            
        if phase_info.get("supports_field_calculation"):
            phase_result["enhancements"].append("field_calculation")
            
        if phase_info.get("supports_data_conversion"):
            phase_result["enhancements"].append("data_conversion")
        
        if not phase_result["is_valid"]:
            results["all_valid"] = False
            results["summary"]["invalid_phases"] += 1
        
        results["phase_results"][phase_name] = phase_result
    
    return results

# Convenience functions for common operations
def create_phase1_sample_data(product_type: str = "pension") -> dict:
    """Create sample data for Phase 1 testing"""
    from .phase1_financial_input import create_sample_data
    return create_sample_data(product_type)

def validate_phase1_data(data: dict) -> dict:
    """Quick validation of Phase 1 data"""
    return quick_validate_phase1(data)

def get_supported_product_types() -> list:
    """Get all supported product types from Phase 1"""
    from .phase1_financial_input import get_supported_product_types
    return get_supported_product_types()

def get_supported_term_types() -> list:
    """Get all supported investment term types from Phase 1"""
    from .phase1_financial_input import get_supported_term_types
    return get_supported_term_types()

def get_supported_tax_bands() -> list:
    """Get all supported tax bands from Phase 1"""
    from .phase1_financial_input import get_supported_tax_bands
    return get_supported_tax_bands()

# Package initialization
def _initialize_package():
    """Initialize the phases package with validation"""
    compatibility_result = validate_phase_compatibility()
    
    if not compatibility_result["all_valid"]:
        import warnings
        warnings.warn(
            f"Phase compatibility issues detected: "
            f"{compatibility_result['summary']['invalid_phases']} invalid phases",
            UserWarning
        )
    
    return compatibility_result

# Initialize on import
_PACKAGE_STATUS = _initialize_package()

def get_package_status() -> dict:
    """Get package initialization status"""
    return _PACKAGE_STATUS.copy()

# Export package status for external use
PACKAGE_INITIALIZATION_STATUS = _PACKAGE_STATUS
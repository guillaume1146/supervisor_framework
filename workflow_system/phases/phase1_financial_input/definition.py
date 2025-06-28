"""
Phase definition for Phase 1: Core Input Validation and Initial Values
"""

from workflow_system.workflows.base import PhaseDefinition
from .parameters import FinancialInputValidationParams
from .implementation import financial_input_validation_workflow

PHASE1_DEFINITION = PhaseDefinition(
    name="financial_input_validation",
    required_params=FinancialInputValidationParams,
    workflow_function=financial_input_validation_workflow,
    description="Phase 1: Core Input Validation and Initial Values - Collect and validate essential financial product information",
    timeout_seconds=300
)
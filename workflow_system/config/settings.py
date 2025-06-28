"""
Configuration classes and enums for the workflow system.
"""

from dataclasses import dataclass
from enum import Enum


class WorkflowError(Exception):
    """Base exception for workflow errors"""
    pass


class ParameterExtractionError(WorkflowError):
    """Exception raised when parameter extraction fails"""
    pass


class ValidationError(WorkflowError):
    """Exception raised when parameter validation fails"""
    pass


class StateTransitionError(WorkflowError):
    """Exception raised when state transition fails"""
    pass


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    COLLECTING_PARAMS = "collecting_params"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowConfig:
    """Configuration for the Enhanced Parameter Workflow"""
    max_iterations: int = 5
    parameter_extraction_retries: int = 3
    default_llm_model: str = "llama-3.3-70b-versatile"
    default_temperature: float = 0.7
    supervisor_temperature: float = 0.1  # Lower temperature for more consistent routing
    enable_auto_continuation: bool = True
    debug_mode: bool = False
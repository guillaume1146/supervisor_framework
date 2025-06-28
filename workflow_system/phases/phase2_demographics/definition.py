"""
Phase definition for Phase 2: Client Demographics and Income
"""

from workflow_system.workflows.base import PhaseDefinition
from .parameters import ClientDemographicsParams
from .implementation import client_demographics_workflow

PHASE2_DEFINITION = PhaseDefinition(
    name="client_demographics",
    required_params=ClientDemographicsParams,
    workflow_function=client_demographics_workflow,
    description="Phase 2: Client Demographics and Income - Collect client personal and income information",
    timeout_seconds=300
)
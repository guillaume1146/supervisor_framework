"""
Phase definition for Data Processing workflow
"""

from workflow_system.workflows.base import PhaseDefinition
from .parameters import ProcessDataParams
from .implementation import process_data_workflow

DATA_PROCESSING_DEFINITION = PhaseDefinition(
    name="process_data",
    required_params=ProcessDataParams,
    workflow_function=process_data_workflow,
    description="Process and analyze data from various sources",
    timeout_seconds=300
)
"""
Phase definition for Report Generation workflow
"""

from workflow_system.workflows.base import PhaseDefinition
from .parameters import GenerateReportParams
from .implementation import generate_report_workflow

REPORT_GENERATION_DEFINITION = PhaseDefinition(
    name="generate_report",
    required_params=GenerateReportParams,
    workflow_function=generate_report_workflow,
    description="Generate user reports and analytics",
    timeout_seconds=180
)

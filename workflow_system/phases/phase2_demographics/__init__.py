"""
Phase 2: Client Demographics and Income (Template)
"""

from .parameters import ClientDemographicsParams
from .implementation import client_demographics_workflow
from .definition import PHASE2_DEFINITION

__all__ = [
    "ClientDemographicsParams",
    "client_demographics_workflow",
    "PHASE2_DEFINITION"
]